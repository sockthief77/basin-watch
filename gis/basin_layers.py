#!/usr/bin/env python3
"""
Athabasca Basin map-layer builder.

Pulls every layer behind the Basin Watch map from the Saskatchewan ArcGIS
services, writes full-resolution GeoJSON for ArcGIS Pro, and writes a small
simplified bundle (map_bundle.json) that the newsletter map is built from.

Runs automatically every morning via .github/workflows/gis-export.yml, on
GitHub's own runners - those aren't behind the egress allowlist that blocks
gis.saskatchewan.ca from the Claude sandbox and from a laptop's own network
sandbox, so this no longer needs a human's machine to be awake. Still runnable
by hand anywhere with a normal network path to gis.saskatchewan.ca:

    python basin_layers.py            # everything
    python basin_layers.py --quick    # skip EM conductors (much faster)

Everything is clipped to the basin window (112W-102W, 56.5N-60.2N) except
province-wide tenure and the claims layer built from it (section 8b) - both
deliberately kept province-wide; the client engine's own northOK() filter
clips them for display.
"""
import json, os, sys, math, re, time, urllib.request, urllib.parse, datetime

EGIS = "https://gis.saskatchewan.ca/egis/rest/services/Economy"
ARC  = "https://gis.saskatchewan.ca/arcgis/rest/services"
ALTA = "https://gis.energy.gov.ab.ca/arcgis/rest/services/wms/SREM_Metallic/MapServer"
ALTA_WATER = "https://geospatial.alberta.ca/titan/rest/services/environment/base_water_feature/MapServer"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "exports")
PAGE = 1000
WIN  = (-112.0, 56.5, -102.0, 60.2)          # xmin, ymin, xmax, ymax
# Wider than WIN on the west side (WIN stops at 112W, which clips the Alberta side of
# the basin), cut hard at 58N to drop unrelated Fort McMurray oil-sands-area features.
# Validated 2026-09-08 for Alberta Tenure (section 11); reused as-is 2026-09-09 for
# Alberta lakes (section 6c) - single source of truth for "the Alberta side of the
# basin window", don't let a second copy drift from this one.
ABWIN = (-114.5, 58.0, -109.0, 60.2)

# Saskatchewan's western border with Alberta follows the 4th Meridian, 110d00'00" W,
# essentially exactly straight for this stretch. ABWIN's own east edge (-109.0, above)
# is deliberately a degree past this real border - fine for a bbox "is this feature
# anywhere near the basin" pre-filter, but if an Alberta lake polygon that qualifies for
# ABWIN is used un-clipped, its geometry can extend a full degree east of the real
# border, directly overlapping Saskatchewan's own (differently-generalized) lake
# geometry in that strip - added 2026-09-11 after a screenshot showed exactly that: a
# visible seam/mismatch over Lake Athabasca where the two sources meet. See section 6c.
BORDER_LON = -110.0


def get(url, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "basin-layers/1.0"})
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)
        except Exception as e:
            last = e
            if i < retries - 1:
                print(f"  retry {i+1}/{retries-1} after: {e}")
                time.sleep(3)
    raise last


def q(base, where="1=1", fields="*", geometry=True, window=False, label="", page=None, extra=None):
    page = page or PAGE
    feats, offset = [], 0
    while True:
        p = {"where": where, "outFields": fields,
             "returnGeometry": "true" if geometry else "false",
             "outSR": 4326, "f": "json",
             "resultOffset": offset, "resultRecordCount": page}
        if window:
            p.update({"geometry": "%f,%f,%f,%f" % WIN,
                      "geometryType": "esriGeometryEnvelope",
                      "inSR": 4326, "spatialRel": "esriSpatialRelIntersects"})
        if extra:
            p.update(extra)
        url = base + "/query?" + urllib.parse.urlencode(p)
        try:
            d = get(url)
        except Exception as e:
            print(f"  ! {label or base} FAILED at offset {offset}: {type(e).__name__}: {e}")
            print(f"    url: {url}")
            return feats
        if "error" in d:
            err = d["error"]
            print(f"  ! {label or base} FAILED at offset {offset}: "
                  f"code {err.get('code')}: {err.get('message')} {err.get('details') or ''}")
            print(f"    url: {url}")
            return feats
        b = d.get("features", [])
        feats += b
        if label:
            print(f"  {label}: {len(feats)}", flush=True)
        if len(b) < page:
            return feats
        offset += page


def ms(v):
    if not v:
        return None
    try:
        return datetime.datetime.fromtimestamp(v/1000, datetime.timezone.utc).strftime("%Y-%m-%d")
    except (OSError, ValueError, OverflowError):
        # Windows' fromtimestamp rejects some out-of-range epoch values that Linux
        # tolerates (seen on a live run: a handful of tenure records have a bad
        # EFFECTIVED/GOODSTANDI value). Don't crash the whole export over one field.
        return None


def esri_to_gj(feats):
    out = []
    for f in feats:
        g, geom = f.get("geometry") or {}, None
        if g.get("x") is not None:
            geom = {"type": "Point", "coordinates": [g["x"], g["y"]]}
        elif "rings" in g:
            geom = ({"type": "Polygon", "coordinates": g["rings"]} if len(g["rings"]) == 1
                    else {"type": "MultiPolygon", "coordinates": [[r] for r in g["rings"]]})
        elif "paths" in g:
            geom = ({"type": "LineString", "coordinates": g["paths"][0]} if len(g["paths"]) == 1
                    else {"type": "MultiLineString", "coordinates": g["paths"]})
        out.append({"type": "Feature", "properties": f.get("attributes", {}), "geometry": geom})
    return {"type": "FeatureCollection", "features": out}


def save(name, gj):
    p = os.path.join(OUT, name + ".geojson")
    json.dump(gj, open(p, "w"))
    print(f"  -> {name}.geojson ({len(gj['features'])})")


# ---------- geometry helpers ----------
def perp(p, a, b):
    if a == b:
        return math.hypot(p[0]-a[0], p[1]-a[1])
    t = max(0, min(1, ((p[0]-a[0])*(b[0]-a[0]) + (p[1]-a[1])*(b[1]-a[1])) /
                   ((b[0]-a[0])**2 + (b[1]-a[1])**2)))
    return math.hypot(p[0]-(a[0]+t*(b[0]-a[0])), p[1]-(a[1]+t*(b[1]-a[1])))


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    dmax, idx = 0, 0
    for i in range(1, len(pts)-1):
        d = perp(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        return dp(pts[:idx+1], tol)[:-1] + dp(pts[idx:], tol)
    return [pts[0], pts[-1]]


def rnd(pts, nd=4):
    return [[round(x, nd), round(y, nd)] for x, y in pts]


def ring_area(r):
    s = 0
    for i in range(len(r)-1):
        s += r[i][0]*r[i+1][1] - r[i+1][0]*r[i][1]
    return abs(s)/2 * math.cos(math.radians(58.5))


def clip_ring(ring, win):
    """Sutherland-Hodgman clip of a polygon ring to an axis-aligned bbox.

    Without this, ring_area() on an un-clipped ring can rank a huge
    province-wide rock unit ahead of the actual basin unit just because it
    happens to poke a corner into the query window - most of its area lies
    outside the window and isn't the basin at all."""
    xmin, ymin, xmax, ymax = win

    def clip_edge(poly, inside, intersect):
        if not poly:
            return []
        out = []
        prev = poly[-1]
        prev_in = inside(prev)
        for cur in poly:
            cur_in = inside(cur)
            if cur_in:
                if not prev_in:
                    out.append(intersect(prev, cur))
                out.append(cur)
            elif prev_in:
                out.append(intersect(prev, cur))
            prev, prev_in = cur, cur_in
        return out

    def isect_x(p1, p2, x):
        t = (x - p1[0]) / (p2[0] - p1[0])
        return [x, p1[1] + t * (p2[1] - p1[1])]

    def isect_y(p1, p2, y):
        t = (y - p1[1]) / (p2[1] - p1[1])
        return [p1[0] + t * (p2[0] - p1[0]), y]

    poly = ring
    poly = clip_edge(poly, lambda p: p[0] >= xmin, lambda a, b: isect_x(a, b, xmin))
    poly = clip_edge(poly, lambda p: p[0] <= xmax, lambda a, b: isect_x(a, b, xmax))
    poly = clip_edge(poly, lambda p: p[1] >= ymin, lambda a, b: isect_y(a, b, ymin))
    poly = clip_edge(poly, lambda p: p[1] <= ymax, lambda a, b: isect_y(a, b, ymax))
    return poly


def inwin(x, y):
    return WIN[0] <= x <= WIN[2] and WIN[1] <= y <= WIN[3]


def pts_bundle(feats, keys, nd=4):
    out = []
    for f in feats:
        g = f.get("geometry") or {}
        if g.get("x") is None or not inwin(g["x"], g["y"]):
            continue
        a = f.get("attributes", {})
        rec = {"x": round(g["x"], nd), "y": round(g["y"], nd)}
        for short, full in keys.items():
            v = a.get(full)
            if v not in (None, ""):
                rec[short] = v
        out.append(rec)
    return out


def name_of(a):
    for k in ("NAME", "NAME_1", "PLACE_NAME", "MUNICIPALITY", "COMMUNITY",
              "GEONAME", "LABEL", "DESCRIPTION", "UMNM", "CSDNAME",
              "OFFICIAL_NAME", "LAKNAMEEN"):
        if a.get(k):
            return a[k]
    return ""


def main():
    quick = "--quick" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    B = {"generated": datetime.date.today().isoformat()}

    # ---- 1. uranium deposits ----
    print("uranium deposits (defined resources)")
    dep = q(f"{EGIS}/Mineral_Exploration/FeatureServer/2",
            "SYMBOLOGY_GROUPING = 'Uranium' AND RESERVESRESOURCES = 'Yes'",
            "NAME,STATUS,PRIMARYCOMMODITIES,PRODUCTION,SMDI", label="deposits")
    save("deposits", esri_to_gj(dep))
    B["deposits"] = pts_bundle(dep, {"n": "NAME", "s": "STATUS", "p": "PRODUCTION", "id": "SMDI"})

    # ---- 2. mines and mills ----
    print("mine locations")
    mines = q(f"{EGIS}/Mineral_Exploration/FeatureServer/1", "1=1", "*", label="mines")
    save("mines", esri_to_gj(mines))
    mb = []
    for f in mines:
        g = f.get("geometry") or {}
        if g.get("x") is None or not inwin(g["x"], g["y"]):
            continue
        a = f.get("attributes", {})
        blob = " ".join(str(v) for v in a.values() if v).upper()
        mb.append({"x": round(g["x"], 4), "y": round(g["y"], 4),
                   "n": name_of(a) or "mine",
                   "u": 1 if "URANIUM" in blob else 0,
                   "ml": 1 if "MILL" in blob else 0,
                   "st": a.get("STATUS") or a.get("SYMBOLOGY_STATUS") or ""})
    B["mines"] = mb

    # ---- 3. towns, settlements, communities ----
    print("towns and settlements")
    places = []
    for lid, kind in ((0, "City"), (2, "Town"), (5, "Northern Community"),
                      (6, "Northern Settlement"), (7, "Hamlet")):
        fs = q(f"{ARC}/UrbanAreas/MapServer/{lid}", "1=1", "*", window=True, label=f"places L{lid}")
        for f in fs:
            g = f.get("geometry") or {}
            if g.get("x") is None or not inwin(g["x"], g["y"]):
                continue
            places.append({"x": round(g["x"], 4), "y": round(g["y"], 4),
                           "n": name_of(f.get("attributes", {})), "k": kind})
    # airports catch places like Points North Landing
    ap = q(f"{ARC}/Transportation/MapServer/2", "1=1", "*", window=True, label="airports")
    for f in ap:
        g = f.get("geometry") or {}
        if g.get("x") is None or not inwin(g["x"], g["y"]):
            continue
        nm = name_of(f.get("attributes", {}))
        if nm and not any(p["n"].upper() == nm.upper() for p in places):
            places.append({"x": round(g["x"], 4), "y": round(g["y"], 4), "n": nm, "k": "Airstrip"})
    B["places"] = places
    print(f"  places bundled: {len(places)}")

    # ---- 4. highways ----
    print("highways")
    roads = []
    for lid in (133, 134):   # full-detail Primary Highways, Secondary Highways
        roads += q(f"{ARC}/Transportation/MapServer/{lid}", "1=1", "*", window=True,
                    label=f"roads L{lid}", page=200)
    save("roads", esri_to_gj(roads))
    hb = []
    for f in roads:
        a = f.get("attributes", {})
        # Route number/name, added 2026-09-12 - name_of()/a.get("ROUTE") never matched
        # anything on this service (confirmed: every prior bundle shipped "n":"" for
        # every single highway segment, silently, since nothing downstream ever
        # asserted a highway actually had a name), so highway labelling was never
        # actually possible before this fix, only quietly broken. The service's real
        # fields (confirmed 2026-09-12 against .../MapServer/133?f=json and 134?f=json):
        # RTNUMBER1 ("Route Number 1", e.g. "905") is what's normally sign-posted and
        # what a reader would recognize, so it's preferred; RTENAME1EN ("Route Name
        # English 1") is the fallback for any segment with a name but no number.
        rtn = (a.get("RTNUMBER1") or "").strip()
        rtname = (a.get("RTENAME1EN") or "").strip()
        label = ("Hwy " + rtn) if rtn else (rtname or name_of(a) or "")
        for path in (f.get("geometry") or {}).get("paths", []):
            simp = dp(path, 0.004)
            if len(simp) >= 2:
                hb.append({"n": label, "p": rnd(simp, 3)})
    B["highways"] = hb
    n_named_hw = sum(1 for h in hb if h["n"])
    print(f"  highway segments bundled: {len(hb)} ({n_named_hw} carry a route label)")

    # ---- 5. basin outline: NOT derived here ----
    # A surveyed Athabasca_Basin_outline.shp was supplied (the real basin polygon,
    # not a bedrock-geology guess). It was converted once and merged directly into
    # BASIN_BUNDLE.basin on the live page. Deriving it from Million_Scale_Geology was
    # tried and dropped - bedrock geology maps the basin cover as dozens of separate
    # formation codes/groups, so heuristics kept picking the wrong unit. Do not resurrect
    # that logic; this bundle simply does not set the "basin" key, so a merge that only
    # copies present keys leaves the real outline untouched. If the basin ever needs
    # updating, redo it from a fresh shapefile the same way, not from this endpoint.

    # ---- 6. deposit footprints ----
    print("deposit footprints")
    fp = q(f"{EGIS}/Regional_Datasets_and_Compilations/FeatureServer/5", "1=1", "*", label="footprints")
    save("footprints", esri_to_gj(fp))
    fb = []
    for f in fp:
        for r in (f.get("geometry") or {}).get("rings", []):
            s = dp(r, 0.002)
            if len(s) > 2:
                fb.append({"a": name_of(f.get("attributes", {})), "r": rnd(s, 4)})
    B["footprints"] = fb

    # ---- 6b. major lakes (background layer) ----
    # NOTE 2026-09-07 (attempt 3): attempt 1 fixed the confirmed "1=1" bug
    # (this layer 400s on a bare 1=1). Attempt 2 dropped the server-side
    # window entirely on the theory that window+envelope was broken for this
    # layer specifically - that made it WORSE (0 features again), because
    # without a window this pulls literally every lake in the province with
    # full-resolution geometry, and that's large enough to blow past the
    # request timeout before page 1 even finishes - confirmed independently:
    # the same unwindowed+geometry query timed out when tested standalone.
    # Reverting to window=True (matches how places/roads/footprints already
    # query successfully) with the OBJECTID>=0 fix kept, plus a server-side
    # maxAllowableOffset to generalize the geometry so the payload per page
    # stays small regardless. If this STILL comes back at 0, the diagnostic
    # print below will show the raw feature count and any query error text -
    # copy that line back verbatim, since it's the one thing that can't be
    # tested from the Claude side (gis.saskatchewan.ca is blocked from both
    # the cloud sandbox and the device bridge; only this machine's own
    # network can reach it).
    print("major lakes")
    lk = q(f"{ARC}/Hydrography/MapServer/80", "OBJECTID>=0", "OBJECTID,LAKNAMEEN,NHNAREA",
           window=True, label="lakes", page=300, extra={"maxAllowableOffset": 0.002})
    print(f"  lakes: {len(lk)} raw features returned")
    save("lakes", esri_to_gj(lk))

    # ---- 6b-ii. named-water-feature gazetteer (added 2026-09-13) ----
    # Hydrography/MapServer/80's own LAKNAMEEN field is blank - literally a single space
    # character, not an empty string, confirmed by querying the exact feature directly -
    # for every big, well-known lake tested: Wollaston Lake, Reindeer Lake, others. It
    # isn't a stray gap either: several of the biggest un-named polygons this layer
    # returns have bounding boxes spanning multiple degrees of longitude, well past the
    # real extent of any single lake, meaning this "coarsest scale group" tier appears to
    # dissolve multiple adjacent lakes into one polygon at this generalization level -
    # there's no name to recover from LAKNAMEEN for those at all, dissolved or not.
    # Saskatchewan's GeoHub separately publishes SaskNamesDatabaseWater, a point
    # gazetteer of officially named water features (field TOPONYM) - confirmed directly
    # against two of the biggest gaps: Wollaston Lake (598114E/6458687N UTM13, 273,268 ha
    # per its own HECTARES field) and Reindeer Lake (649106E/6343982N, 477,542 ha), both
    # matching their real published surface areas closely. Pulled once here, windowed the
    # same as every other background layer, and matched to each lake ring by simple
    # point-in-ring containment (gazetteer_name() below) whenever LAKNAMEEN comes back
    # blank/whitespace-only - this doesn't touch anything that already has a real name.
    print("named water features (gazetteer)")
    wnames = q(f"{ARC}/SaskNamesDatabaseWater/MapServer/0", "1=1", "TOPONYM,HECTARES",
               window=True, label="water names", page=500)
    name_pts = []
    for f in wnames:
        g = f.get("geometry") or {}
        attrs = f.get("attributes", {})
        nm = (attrs.get("TOPONYM") or "").strip()
        if nm and g.get("x") is not None:
            try:
                ha = float(attrs.get("HECTARES") or 0)
            except (TypeError, ValueError):
                ha = 0.0
            name_pts.append((nm, g["x"], g["y"], ha))
    print(f"  named water points: {len(name_pts)}")

    def point_in_ring(x, y, ring):
        inside = False
        n = len(ring)
        j = n - 1
        for i in range(n):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > y) != (yj > y):
                xin = (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
                if x < xin:
                    inside = not inside
            j = i
        return inside

    def gazetteer_name(ring):
        """Best-effort fallback name for a lake ring whose own LAKNAMEEN is blank:
        among every gazetteer point that falls inside it, the one with the largest
        HECTARES value. Fixed 2026-09-13 after a real mismatch was found live: the
        Hydrography service's coarsest generalization tier dissolves/simplifies
        outlines loosely enough that a big lake's own outline can also enclose a
        much smaller neighbour's single gazetteer point - e.g. Tazin Lake (36,511 ha,
        several TOPONYM points scattered across its area) versus tiny Godfrey Lake
        (65.65 ha) sitting at its northern tip - and taking whichever point matched
        first named the whole polygon after the small lake instead of the real, much
        larger one. Preferring the largest HECTARES on a multi-match resolves that:
        a small satellite lake only wins if it's the ONLY match, not merely the
        first one tested. Returns '' (genuinely unnamed) if nothing matches - never
        guessed, only ever a real TOPONYM from the source."""
        best_nm, best_ha = "", -1.0
        for nm, x, y, ha in name_pts:
            if point_in_ring(x, y, ring) and ha > best_ha:
                best_nm, best_ha = nm, ha
        return best_nm

    def _segs_cross(a1, a2, b1, b2):
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        d1, d2 = cross(b1, b2, a1), cross(b1, b2, a2)
        d3, d4 = cross(a1, a2, b1), cross(a1, a2, b2)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    def ring_self_intersects(ring):
        """O(n^2) proper-crossing count with a cheap bbox pre-filter per segment pair -
        added 2026-09-13 after a few major lakes (several dissolved-looking 'blob'
        shapes, one large enough to have been mistaken for Tazin Lake during
        investigation) turned out to have real, measurable self-crossings after
        simplification. Root cause not fully pinned down (most likely over-aggressive
        generalization on very complex Shield-lake-district shapes, either this
        service's own server-side maxAllowableOffset or this script's own dp()
        simplification, possibly both) - rather than chase that further, this counts
        actual self-crossings in the shipped (post-simplification) ring and rejects
        only the ones that are badly tangled, not the ones with a couple of
        cosmetically-invisible micro-crossings.

        A plain "any crossing at all" test was tried first and rejected 49 of 55 real
        lakes, including Lake Athabasca - almost every DP-simplified ring of a genuinely
        complex, legitimate shoreline carries a handful of sub-pixel self-crossings from
        the simplification itself (confirmed: Lake Athabasca has 5, on a 289-point ring,
        invisible at any normal zoom). What distinguishes an actually broken shape isn't
        having ANY crossings, it's having MANY, relative to its point count - the
        confirmed-broken shapes found this way ran 72-180 crossings against a similar
        few-hundred to ~1000-point ring (7-26% of points involved in a crossing), while
        every legitimately fine lake/river tested stayed under 5%. count > max(10,
        0.1*n) draws the line comfortably inside that gap. Runs on the small (~tens to
        low hundreds of points) simplified ring, not the raw one, so the O(n^2) cost
        stays negligible against this section's own SMDI scrape elsewhere in the file."""
        n = len(ring)
        if n < 4:
            return False
        segs = [(ring[i], ring[(i + 1) % n]) for i in range(n)]
        boxes = [(min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])) for a, b in segs]
        count = 0
        limit = max(10, int(0.1 * n))
        for i in range(n):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue  # adjacent pair, wraps around - shares an endpoint, not a crossing
                bi, bj = boxes[i], boxes[j]
                if bi[1] < bj[0] or bj[1] < bi[0] or bi[3] < bj[2] or bj[3] < bi[2]:
                    continue  # bounding boxes don't overlap - can't cross
                if _segs_cross(segs[i][0], segs[i][1], segs[j][0], segs[j][1]):
                    count += 1
                    if count > limit:
                        return True
        return False

    # ---- 6c. Alberta lakes (added 2026-09-09) ----
    # Saskatchewan Hydrography only carries Saskatchewan features, so any lake crossing
    # the AB/SK border (Lake Athabasca itself, among others) was hard-truncated right at
    # the provincial line. Alberta Environment & Parks runs its own water-feature service;
    # layer 70 ("Lake/River (2M)") is the closest generalization tier to Saskatchewan's
    # own "coarsest scale group" (layer 80) used above - matched by eye against the other
    # scale tiers (69/71/72), not vetted pixel-for-pixel against layer 80's generalization,
    # so revisit if the two sides look mismatched in density once rendered. Reprojects out
    # of Alberta 10TM (EPSG:3400) the same way section 11's Alberta Tenure query does -
    # outSR=4326 on the request, no client-side transform needed. Small enough (few
    # thousand features province-wide at this generalization) to pull unwindowed and
    # filter here, same reasoning section 11 uses for Alberta Tenure.
    print("Alberta lakes")
    ab_lk = q(f"{ALTA_WATER}/70", "1=1", "OBJECTID,NAME,FEATURE_TYPE", label="ab_lakes", page=500)
    print(f"  ab_lakes: {len(ab_lk)} raw features returned")
    if ab_lk:
        save("ab_lakes", esri_to_gj(ab_lk))

    lakes_ranked = []
    for f in lk:
        g = f.get("geometry") or {}
        rings = g.get("rings", [])
        if not rings:
            continue
        best = max(rings, key=ring_area)  # drop small interior/adjacent slivers
        lakes_ranked.append((ring_area(best), name_of(f.get("attributes", {})), best))
    for f in ab_lk:
        g = f.get("geometry") or {}
        rings = g.get("rings", [])
        if not rings:
            continue
        big = max(rings, key=len)
        if not any(ABWIN[0] <= x <= ABWIN[2] and ABWIN[1] <= y <= ABWIN[3] for x, y in big):
            continue  # outside the Alberta basin window - see ABWIN definition at top
        best = max(rings, key=ring_area)
        # Clip to strictly west of the real AB/SK border (see BORDER_LON above) - ABWIN's
        # own east edge is a degree too generous for this, and an unclipped ring here was
        # overlapping Saskatchewan's own lake geometry right at the border, producing a
        # visible seam where the two differently-generalized sources met.
        best = clip_ring(best, (-180.0, -90.0, BORDER_LON, 90.0))
        if len(best) < 3:
            continue  # this feature turned out to lie entirely on the Saskatchewan side -
                       # SK's own layer 80 (queried above) already covers that ground
        lakes_ranked.append((ring_area(best), name_of(f.get("attributes", {})), best))
    lakes_ranked.sort(key=lambda t: -t[0])
    lb = []
    skipped_bad = 0
    named_from_gazetteer = 0
    rivers_prioritized = 0
    # Widened 40 -> 55 on 2026-09-09 so the added Alberta lakes get their own room
    # instead of just displacing smaller Saskatchewan lakes out of the cut. As of
    # 2026-09-13 this loop no longer hard-slices the top 55 candidates up front - a
    # self-intersecting one is skipped and doesn't burn a slot, so the 55 shipped are
    # always the 55 biggest GOOD shapes, not just the 55 biggest.
    #
    # Cap raised 55 -> 60 and a river priority pass added, 2026-09-13, after Clearwater
    # River (a real, named feature on this same Hydrography layer, with its own
    # provincial park along it) turned out to be ranked well outside the top 55 and so
    # never shipped at all. Root cause: this whole selection is ranked by RING AREA, which
    # systematically disadvantages a long, narrow river against a round lake of the same
    # geographic significance - a river can be enormously important and still have a
    # small polygon footprint. Fix: any candidate whose own government-supplied name
    # (LAKNAMEEN, via name_of()) contains "river" is pulled to the FRONT of the ranking,
    # ahead of area-only sorting, so a named river competes for a guaranteed slot instead
    # of only the slots an unnamed or lake-sized area would win it.
    #
    # That fix still shipped without Clearwater River on the map (caught the same day,
    # user-reported). Root cause: LAKNAMEEN is blank - a single space, not missing, see
    # the gazetteer note above - for nearly every feature at this generalization tier,
    # named rivers very much included, so the LAKNAMEEN-only check above almost never
    # actually fired; it only worked for the handful of candidates that happened to carry
    # a real LAKNAMEEN value. Clearwater River's own candidate ring has a blank LAKNAMEEN,
    # so it never got flagged as a river pre-cut and lost on area alone like before.
    #
    # Fix: also flag a candidate as a river if a gazetteer point whose TOPONYM contains
    # "river" falls inside its ring - the same gazetteer used for post-cut naming
    # (gazetteer_name() above), just consulted earlier, before the cut decides who
    # survives, not only after. Kept cheap on purpose, given the standing runtime
    # concern on this script (a prior run took 25 minutes): river_pts below is
    # pre-filtered to only the gazetteer's "river" points (a handful province-wide,
    # not all ~500 named-water points), and a candidate's bounding box is checked
    # against those few points BEFORE ever running the O(ring length) point-in-ring
    # test - so the added cost is a handful of cheap box comparisons per candidate,
    # not a full gazetteer_name() lookup (which tests every point) run on every
    # candidate ahead of the cut.
    river_pts = [(nm, x, y, ha) for nm, x, y, ha in name_pts if "river" in nm.lower()]
    def _is_named_river(nm, ring):
        if "river" in (nm or "").lower():
            return True
        if not river_pts:
            return False
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
        for pname, x, y, ha in river_pts:
            if minx <= x <= maxx and miny <= y <= maxy and point_in_ring(x, y, ring):
                return True
        return False
    lakes_ranked = (sorted([t for t in lakes_ranked if _is_named_river(t[1], t[2])], key=lambda t: -t[0])
                    + sorted([t for t in lakes_ranked if not _is_named_river(t[1], t[2])], key=lambda t: -t[0]))
    LAKE_CAP = 60
    for a, nm, r in lakes_ranked:
        if len(lb) >= LAKE_CAP:
            break
        s2 = dp(r, 0.003)
        if len(s2) <= 2:
            continue
        if ring_self_intersects(s2):
            skipped_bad += 1
            print(f"  ! lake skipped, self-intersecting after simplification "
                  f"(area~{a:.4f}, name={nm!r})")
            continue
        if _is_named_river(nm, r):
            rivers_prioritized += 1
        nm2 = nm if (nm or "").strip() else gazetteer_name(s2)
        if nm2 and not (nm or "").strip():
            named_from_gazetteer += 1
        lb.append({"n": nm2 or "", "a": round(a, 1), "r": rnd(s2, 4)})
    B["lakes"] = lb
    print(f"  lakes bundled: {len(lb)} ({len(lk)} SK candidates, {len(ab_lk)} AB candidates, "
          f"{skipped_bad} skipped as self-intersecting, {named_from_gazetteer} named from the gazetteer, "
          f"{rivers_prioritized} named rivers guaranteed a slot ahead of area ranking)")

    # ---- 7. radioactive boulders -> cps grid ----
    # Static historical dataset (boulder occurrences logged over decades) - the true
    # count barely moves run to run, so a healthy fetch should always land close to
    # its documented ~6,600. BOULDER_FLOOR guards against a failed/partial query
    # (q() swallows a network/DNS failure and just returns whatever it has so far,
    # by design - see q()'s own docstring) silently posing as "the real count is
    # near zero today." Added 2026-09-10 after exactly that happened on a live run:
    # the query failed outright, bo came back [], and boulder_grid/boulder_total
    # would otherwise have been written as empty/0 for this export - map-pipeline's
    # merge guard caught the grid (an empty list) but boulder_total, a plain int,
    # slipped through as an unguarded 0 and broke the Boulder Heat toggle on the
    # live site. Withholding both keys here, at the source, means a bad fetch never
    # produces a number for the merge step to have to second-guess in the first
    # place - a missing key is left untouched by the merge, a present-but-wrong
    # value has to be caught downstream, which is a strictly harder job.
    print("radioactive boulders")
    BOULDER_FLOOR = 1000  # documented count is ~6,591; well below half is not a real day
    bo = q(f"{EGIS}/Regional_Datasets_and_Compilations/FeatureServer/4", "1=1",
           "BOULDER_ID,YEAR,LITHOLOGY,CLUSTER_,CPS,BACKGROUND,CPS_RANGE,U308_ASSAY_RESULTS",
           label="boulders")
    save("boulders", esri_to_gj(bo))
    if len(bo) < BOULDER_FLOOR:
        print(f"  ! boulders: only {len(bo)} returned (expected ~6,591) - treating as a "
              f"failed/partial query, NOT writing boulder_grid/boulder_total this run "
              f"(existing live values will be kept by the merge step)")
    else:
        grid = {}
        for f in bo:
            g = f.get("geometry") or {}
            if g.get("x") is None:
                continue
            cps = f["attributes"].get("CPS") or 0
            k = (round(g["x"]/0.04), round(g["y"]/0.02))
            c = grid.setdefault(k, {"n": 0, "mx": 0, "s": 0})
            c["n"] += 1; c["mx"] = max(c["mx"], cps); c["s"] += cps
        B["boulder_grid"] = [{"x": round(k[0]*0.04, 4), "y": round(k[1]*0.02, 4),
                              "n": v["n"], "mx": round(v["mx"]), "av": round(v["s"]/v["n"])}
                             for k, v in grid.items()]
        B["boulder_total"] = len(bo)

    # ---- 7b. uranium geochemistry (lake sediment + till/soil) -> ppm grid ----
    # Two Saskatchewan Geological Survey point layers, both carry a plain U_PPM field
    # and both come back through outSR=4326 like everything else here, so they combine
    # into one grid the same way boulder_grid does (same cell size, same n/mx/av shape).
    # Layer 1 = SGS Lake Sediment Geochemistry (~3,000 samples, 1975-78). Layer 4 =
    # SGS/GSC Surficial Geochemistry Analyses (~12,700 till/soil samples). The GSC's
    # separate "GSC Lake Sediment Analyses" layer (federal NGR program, field name is
    # "U" not "U_PPM") is a different compilation with unconfirmed overlap against
    # layer 1 - deliberately not included yet, so lake coverage isn't double-counted.
    #
    # Both static historical surveys are pulled and floor-checked SEPARATELY before
    # being combined, for the same reason as the boulder floor above: a merged grid
    # built from one healthy source plus one silently-failed source is NON-empty
    # (so a downstream "was it empty?" guard never notices) but is missing an entire
    # category of coverage - exactly what happened 2026-09-10 when the lake-sediment
    # query failed, till/soil succeeded, and the resulting geochem_grid quietly lost
    # 932 cells (the whole southwest-basin quadrant) while still looking like a
    # normal, non-empty, "real" update. There's no good way to recombine one fresh
    # source with the OTHER source's stale-but-good data after the fact (this export
    # doesn't carry the previous run's per-source split, only the final combined
    # grid) - so if either source looks broken, the safe move is to withhold the
    # whole combined layer this run and keep whatever's already live, rather than
    # publish a plausible-looking but silently incomplete grid.
    print("uranium geochemistry (lake sediment + till/soil)")
    LAKESED_FLOOR = 500     # documented count is ~3,000
    TILLSOIL_FLOOR = 2000   # documented count is ~12,700
    ls = q(f"{EGIS}/Analytical_and_Rock_Property_Data/FeatureServer/1", "U_PPM IS NOT NULL",
           "SAMPLE_NO,EASTING,NORTHING,U_PPM", label="lake sediment U")
    ti = q(f"{EGIS}/Analytical_and_Rock_Property_Data/FeatureServer/4", "U_PPM IS NOT NULL",
           "SAMPLE_NUMBER_ID,UTM_EASTING,UTM_NORTHING,U_PPM", label="till/soil U")
    if len(ls) < LAKESED_FLOOR or len(ti) < TILLSOIL_FLOOR:
        print(f"  ! geochem: lake sed. {len(ls)} (expected ~3,000), till/soil {len(ti)} "
              f"(expected ~12,700) - at least one source looks like a failed/partial "
              f"query, NOT writing geochem_grid/geochem_total this run (existing live "
              f"values will be kept by the merge step)")
    else:
        gc_samples = []
        for f in ls:
            g = f.get("geometry") or {}
            u = f["attributes"].get("U_PPM")
            if g.get("x") is None or u is None:
                continue
            gc_samples.append((g["x"], g["y"], u))
        for f in ti:
            g = f.get("geometry") or {}
            u = f["attributes"].get("U_PPM")
            if g.get("x") is None or u is None:
                continue
            gc_samples.append((g["x"], g["y"], u))

        ggrid = {}
        for x, y, u in gc_samples:
            if not inwin(x, y):
                continue
            k = (round(x/0.04), round(y/0.02))
            c = ggrid.setdefault(k, {"n": 0, "mx": 0, "s": 0})
            c["n"] += 1; c["mx"] = max(c["mx"], u); c["s"] += u
        B["geochem_grid"] = [{"x": round(k[0]*0.04, 4), "y": round(k[1]*0.02, 4),
                              "n": v["n"], "mx": round(v["mx"], 2), "av": round(v["s"]/v["n"], 2)}
                             for k, v in ggrid.items()]
        B["geochem_total"] = len(gc_samples)
        print(f"  geochem samples: {len(gc_samples)} ({len(ls)} lake sed. + {len(ti)} till/soil), "
              f"{len(B['geochem_grid'])} grid cells in window")

    # ---- 8. mineral tenure polygons ----
    print("mineral tenure polygons (all active dispositions)")
    tn = q(f"{ARC}/Economy/Mineral_Tenure_Crown_Dispositions/FeatureServer/0", "1=1",
           "DISPOSIT_1,OWNERS,EFFECTIVED,GOODSTANDI,DISPOSIT_3", label="tenure", page=200)
    save("tenure", esri_to_gj(tn))
    tb = []
    for f in tn:
        a = f["attributes"]
        rings = (f.get("geometry") or {}).get("rings", [])
        if not rings:
            continue
        s = dp(max(rings, key=len), 0.0008)
        if len(s) < 3:
            continue
        tb.append({"d": a.get("DISPOSIT_1"), "o": a.get("OWNERS") or "",
                   "e": ms(a.get("EFFECTIVED")), "st": a.get("DISPOSIT_3"),
                   "x": ms(a.get("GOODSTANDI")),  # good-standing expiry date - when it opens back up to staking
                   "r": rnd(s, 4)})
    B["tenure"] = tb

    # ---- 8b. new claims (14-day staking window) - added 2026-09-12 ----
    # Closes the "two pipelines" gap: this used to be computed by hand, every
    # morning, inside the uranium-brief skill's own session - a separate
    # EFFECTIVED-window ArcGIS query, plus a per-claim coordinate lookup for
    # anything not yet in the tenure snapshot the session happened to have. That
    # meant data/bundle.json's own "claims" key (what basinwatch.ca's map
    # actually shows) was never touched by anything and sat frozen at whatever a
    # one-time seed put there, while the two claude.ai pages got a fresh (but
    # differently-sourced) claims list every day - three surfaces, two different
    # answers. Computing it here instead means it comes from the exact same
    # live query as `tenure` above (no second ArcGIS round-trip), lands in
    # data/bundle.json automatically every morning at 07:30 Regina, and is the
    # one and only place "new claims" ever gets computed - see
    # claude/map-pipeline.md and claude/claim-monitor-state.md in the Basin
    # Watch project for the incident this fixes.
    #
    # Window: trailing 14 calendar days, today inclusive - matches the
    # uranium-brief skill's "Staking window" constant (widened from 7 days
    # 2026-09-11). Recomputed from scratch every run, not diffed against a
    # previous snapshot - unlike the lapsed-claims layer below, a claim doesn't
    # need "was this new since last time" tracking, just "is it still inside
    # the trailing 14 days as of today."
    #
    # Deliberately province-wide, same as `tenure` above (this file's own
    # docstring: "province-wide tenure" is the deliberate exception to the
    # basin-window clip everything else gets). The client engine's own
    # CLAIMS_F filter (`northOK()` in site/shell.html) already excludes
    # out-of-basin staking - e.g. the Flin Flon-area GEM OIL block, ~370 km
    # outside the basin, appeared in this same window in September 2026 - at
    # render time, so this section doesn't need to duplicate that filter here.
    # `corp` uses the same keyword test the map's own legend/colour code has
    # documented (but never had a real producer for) since it shipped:
    # URANIUM, RESOURCES, GEM OIL, CORP, LTD, INC anywhere in the holder string.
    print("new claims (trailing 14-day EFFECTIVED window)")
    CORP_KEYWORDS = ("URANIUM", "RESOURCES", "GEM OIL", "CORP", "LTD", "INC")

    def is_corp_holder(owner):
        u = (owner or "").upper()
        return any(k in u for k in CORP_KEYWORDS)

    # 13 days back, not 14: "trailing 14 calendar days, today inclusive" spans
    # 14 days total only when the cutoff itself is the 14th day (e.g. run on
    # 2026-09-12, window is 2026-08-30 through 2026-09-12 inclusive - that's
    # 13 days back from today, not 14). Caught by a synthetic boundary test
    # before this shipped - see the test in this change's own notes.
    cutoff_date = datetime.date.today() - datetime.timedelta(days=13)
    cutoff_ms = int(datetime.datetime.combine(
        cutoff_date, datetime.time.min, tzinfo=datetime.timezone.utc
    ).timestamp() * 1000)

    # Restricted to claims that also made it into `tb` (tenure) above, added
    # 2026-09-13 - found live: MC00024178 (Gary Clayton Dunn, staked 2026-09-11)
    # appeared in `claims` with no matching `tenure` entry at all, so the client
    # engine's own "no matching tenure polygon" fallback drew it as a bare
    # circle marker forever, at every zoom, instead of a shaped claim outline.
    # Root cause: this loop's own geometry guard (`if not rings: continue`) is
    # weaker than the tenure loop's above (`if len(s) < 3: continue`, checked
    # AFTER Douglas-Peucker simplification) - a claim whose polygon is small or
    # sliver-shaped enough to simplify down to under 3 points is correctly
    # dropped from `tenure` but was still passing this loop's own, looser
    # check and landing in `claims` anyway. Rather than duplicate the DP
    # rejection rule a second time and risk the two drifting apart again, this
    # just requires a claim to already be present in `tb` - the two lists can
    # now never disagree about which dispositions exist.
    tenure_ids = {t["d"] for t in tb if t.get("d")}
    claims_out = []
    for f in tn:
        a = f["attributes"]
        eff = a.get("EFFECTIVED")
        if not eff or eff < cutoff_ms:
            continue
        if a.get("DISPOSIT_1") not in tenure_ids:
            continue
        rings = (f.get("geometry") or {}).get("rings", [])
        if not rings:
            continue
        ring = max(rings, key=len)
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        claims_out.append({
            "d": a.get("DISPOSIT_1"),
            "o": a.get("OWNERS") or "",
            "x": round((min(xs) + max(xs)) / 2, 4),
            "y": round((min(ys) + max(ys)) / 2, 4),
            "e": ms(eff),
            "corp": is_corp_holder(a.get("OWNERS")),
        })
    B["claims"] = claims_out
    n_corp = sum(1 for c in claims_out if c["corp"])
    print(f"  claims: {len(claims_out)} staked in the trailing 14 days "
          f"({n_corp} corporate, {len(claims_out)-n_corp} individual)")

    # ---- 9. EM conductors ----
    if not quick:
        print("EM conductors (slow, ~28k lines)")
        co = q(f"{EGIS}/Regional_Datasets_and_Compilations/FeatureServer/7", "1=1",
               "ID,YEAR,SURVEY_TYPE,CONDUCTOR_TYPE,FILE_NUMBER,Shape__Length", label="conductors")
        save("conductors", esri_to_gj(co))
        cb = []
        for f in co:
            a = f["attributes"]
            for path in (f.get("geometry") or {}).get("paths", []):
                s = dp(path, 0.004)
                if len(s) >= 2:
                    cb.append({"y": a.get("YEAR"), "t": (a.get("CONDUCTOR_TYPE") or "")[:18],
                               "sv": (a.get("SURVEY_TYPE") or "")[:18],
                               "L": round(a.get("Shape__Length") or 0), "p": rnd(s, 3)})
        B["conductors"] = cb

    # ---- 10. Lapsed dispositions (Layer 3) - "recently lapsed" map layer ----
    # Layer 3 does NOT share layer 0's field list: only DISPOSIT_1, OWNERS, DISPOSITIO
    # exist here (no EFFECTIVED, no DISPOSIT_3 - asking for those 400s, confirmed
    # 2026-09-07). OBJECTID is not sequential on this layer, so change detection diffs
    # on DISPOSIT_1 (the stable claim number) against the PREVIOUS run's snapshot
    # (lapsed_state.json in this same exports folder), not on OBJECTID and not on a
    # simple count. Every currently-lapsed disposition is written to the bundle each
    # run, each tagged "new": 1 only if it wasn't in the previous snapshot - the map
    # only draws the "new": 1 ones, so the very first run after this shipped seeds the
    # baseline with everything tagged "new": 0 (nothing to diff against yet) and shows
    # zero on the map; the delta becomes real starting the run after that.
    print("lapsed dispositions (Layer 3)")
    lp = q(f"{ARC}/Economy/Mineral_Tenure_Crown_Dispositions/FeatureServer/3", "1=1",
           "DISPOSIT_1,OWNERS,DISPOSITIO", label="lapsed", page=500)
    save("lapsed", esri_to_gj(lp))

    state_path = os.path.join(OUT, "lapsed_state.json")
    prev = {}
    if os.path.exists(state_path):
        try:
            prev = json.load(open(state_path))
        except (json.JSONDecodeError, OSError):
            prev = {}
    prev_set = set(prev.get("dispositions", []))

    lb2, cur_set = [], set()
    for f in lp:
        a = f["attributes"]
        d = a.get("DISPOSIT_1")
        if not d:
            continue
        cur_set.add(d)
        rings = (f.get("geometry") or {}).get("rings", [])
        if not rings:
            continue
        s = dp(max(rings, key=len), 0.0008)
        if len(s) < 3:
            continue
        lb2.append({"d": d, "o": a.get("OWNERS") or "", "st": a.get("DISPOSITIO") or "",
                    "new": 1 if (prev_set and d not in prev_set) else 0, "r": rnd(s, 4)})
    B["lapsed"] = lb2

    newly_lapsed = (cur_set - prev_set) if prev_set else set()
    re_staked = (prev_set - cur_set) if prev_set else set()
    print(f"  lapsed: {len(cur_set)} current, {len(newly_lapsed)} newly lapsed since last run, "
          f"{len(re_staked)} left the lapsed register (re-staked or moved) since last run")
    if prev_set:
        if newly_lapsed:
            nl = sorted(newly_lapsed)
            print("  newly lapsed:", ", ".join(nl[:20]), "..." if len(nl) > 20 else "")
        if re_staked:
            rs = sorted(re_staked)
            print("  left lapsed register:", ", ".join(rs[:20]), "..." if len(rs) > 20 else "")
    else:
        print("  (no previous snapshot on disk - this run seeds the baseline; "
              "'new' flags are all 0 this time, the map layer will show nothing until "
              "the next run)")
    json.dump({"date": datetime.date.today().isoformat(), "dispositions": sorted(cur_set)},
              open(state_path, "w"))

    # ---- 11. Alberta metallic & industrial minerals agreements ----
    # Alberta's basin extension is not on MARS/GeoAtlas. Tenure there is held as
    # "Metallic and Industrial Minerals Agreements" on the province's own ArcGIS
    # service (~715 province-wide) - small enough to pull unwindowed and filter
    # here, which also avoids the server-side envelope this host is fussy about.
    #
    # This layer has NO registration/effective date, only TermDate (expiry), so new
    # staking CANNOT be watermark-detected the way Saskatchewan claims are. Change
    # detection is a set diff on AgreementNumber against the previous run's snapshot
    # (ab_state.json), exactly the method section 10 uses for lapsed claims - so the
    # first run seeds the baseline with every "new" flag at 0 and the delta only
    # becomes real on the run after that.
    #
    # DesignatedRepresentative is the holder of record, and it is not the same thing
    # as the beneficial owner: Rea is registered to ORANO CANADA INC. even though
    # GoldMining holds 75%. Do not report Alberta holdings by company from this field
    # alone.
    print("Alberta metallic & industrial minerals agreements")
    ab = q(f"{ALTA}/0", "1=1",
           "AgreementNumber,AgreementType,AgreementName,DesignatedRepresentative,TermDate",
           label="alberta", page=500)
    print(f"  alberta: {len(ab)} raw features returned")
    if ab:
        save("alberta_tenure", esri_to_gj(ab))

    # Wider than WIN on the west side (WIN stops at 112W, which clips the Alberta
    # side of the basin - Rea and Dragon Lake sit around 110-112W), but cut hard at
    # 58N on the south side. Confirmed on the first live run 2026-09-08: a 55.5N floor
    # returned 246 agreements of which 142 were Hammerstone Infrastructure Materials
    # limestone/aggregate tenure at 56.7-57.8N around Fort McMurray, plus Suncor,
    # Cenovus and Athabasca Oil - oil sands country, not the basin. At 58N those
    # vanish and 74 remain, all rock-hosted minerals permits and leases: ATHA Energy
    # 41, 1818403 Alberta Ltd. 16, Dahrouge Geological Consulting 6, Orano 3.
    ab_state = os.path.join(OUT, "ab_state.json")
    abprev = {}
    if os.path.exists(ab_state):
        try:
            abprev = json.load(open(ab_state))
        except (json.JSONDecodeError, OSError):
            abprev = {}
    abprev_set = set(abprev.get("agreements", []))

    abb, ab_cur = [], set()
    for f in ab:
        a = f["attributes"]
        num = a.get("AgreementNumber")
        if num:
            ab_cur.add(num)
        rings = (f.get("geometry") or {}).get("rings", [])
        if not rings:
            continue
        big = max(rings, key=len)
        if not any(ABWIN[0] <= x <= ABWIN[2] and ABWIN[1] <= y <= ABWIN[3] for x, y in big):
            continue
        s2 = dp(big, 0.0008)
        if len(s2) < 3:
            continue
        abb.append({"d": num, "o": a.get("DesignatedRepresentative") or "",
                    "n": a.get("AgreementName") or "", "t": a.get("AgreementType") or "",
                    "x": ms(a.get("TermDate")),
                    "new": 1 if (abprev_set and num not in abprev_set) else 0,
                    "r": rnd(s2, 4)})
    B["ab_tenure"] = abb

    ab_new = (ab_cur - abprev_set) if abprev_set else set()
    ab_gone = (abprev_set - ab_cur) if abprev_set else set()
    print(f"  alberta: {len(ab_cur)} agreements province-wide, {len(abb)} inside the basin window, "
          f"{len(ab_new)} new since last run, {len(ab_gone)} gone")
    if abprev_set:
        if ab_new:
            print("  new Alberta agreements:", ", ".join(sorted(ab_new)[:20]))
        if ab_gone:
            print("  Alberta agreements gone:", ", ".join(sorted(ab_gone)[:20]))
    else:
        print("  (no previous Alberta snapshot - this run seeds the baseline)")
    if ab_cur:
        json.dump({"date": datetime.date.today().isoformat(), "agreements": sorted(ab_cur)},
                  open(ab_state, "w"))

    # ---- 12. Restricted lands (MARS "unavailable for staking") - CORRECTED 2026-09-09 ----
    # Earlier version of this section pulled from four GENERAL-PURPOSE gis.saskatchewan.ca
    # layers (ParksAsLegislated, AboriginalLands, Planning, UrbanAreas) as a best guess at
    # MARS's six restriction categories, and documented Crown reserves / manual restrictions
    # as having no known public layer. BOTH of those were wrong, found by inspecting the
    # live MARS map's own JS layer object in a browser (mars.isc.ca loads
    # window.map.layers, one of which is the ArcGIS Dynamic Map Service layer actually
    # driving its "Restriction"/"Prohibition" colouring):
    #
    #   https://iscmaps.isc.ca/arcgis/rest/services/MARS/RestrictionsProhibitions/MapServer
    #
    # This ONE service carries all six categories as named sublayers, confirmed directly
    # from the loaded layer object (`l.sublayers` titles): Parks(6), Crown Reserves for
    # Minerals(7), Indian Reserves(8), Urban Municipalities(9), Land Claims(10), Manual
    # Restrictions(11) - plus a Dispositions(0) and Permit_Exclusion(12) sublayer not used
    # here. This is the authoritative source MARS itself draws from, so it should match
    # what a user sees circled on mars.isc.ca exactly - unlike the old gis.saskatchewan.ca
    # substitutes, which are separately-maintained general GIS layers that may cover
    # different ground.
    #
    # iscmaps.isc.ca is blocked from the cloud container and the linked-device sandbox,
    # same as gis.saskatchewan.ca (confirmed: curl gets connection reset through the
    # egress proxy) - this section is not run by the automated GitHub Actions pipeline,
    # else in this file.
    #
    # Field names on these six sublayers are NOT yet confirmed (no way to query them
    # ahead of time from a blocked network) - outFields="*" is used so this doesn't
    # depend on guessing a field name, and best_restricted_name() below tries a list of
    # common candidates, falling back to the layer's own category name. The per-layer
    # "fields=[...]" line this run prints is worth reading once and, if a real name field
    # turns out to exist under an unlisted key, adding it to the candidate list.
    print("restricted lands (MARS RestrictionsProhibitions - all six categories)")
    MARS_RP = "https://iscmaps.isc.ca/arcgis/rest/services/MARS/RestrictionsProhibitions/MapServer"
    RESTRICTED_SRC = [
        ("park",         f"{MARS_RP}/6"),
        ("crownreserve", f"{MARS_RP}/7"),
        ("reserve",      f"{MARS_RP}/8"),
        ("urban",        f"{MARS_RP}/9"),
        ("claim",        f"{MARS_RP}/10"),
        ("manual",       f"{MARS_RP}/11"),
    ]
    TY_LABEL = {"park": "Park", "crownreserve": "Crown Reserve for Minerals",
                "reserve": "Indian Reserve", "urban": "Urban Municipality",
                "claim": "Land Claim", "manual": "Manual Restriction"}

    def best_restricted_name(a, ty):
        for k in ("NAME", "LABEL", "PARKNM", "PARK_NAME", "IRNM", "IRBANDNAME",
                  "RESERVE_NAME", "UMNM", "MUNICIPALITY", "ID_NUMBER", "DESCRIPTION",
                  "RESTRICTION", "RESTRICTION_TYPE", "COMMENT", "COMMENTS"):
            v = a.get(k)
            if v:
                return str(v)
        for k, v in a.items():
            if v and isinstance(v, str) and re.search(r"NAME|NM$|LABEL|DESC", k, re.I):
                return v
        return TY_LABEL[ty]

    restricted = []
    for ty, base in RESTRICTED_SRC:
        feats = q(base, "OBJECTID>=0", "*", window=True, label=f"restricted:{ty}")
        n_kept = 0
        sample_fields = sorted(feats[0]["attributes"].keys()) if feats else None
        for f in feats:
            a = f.get("attributes", {})
            rings = (f.get("geometry") or {}).get("rings", [])
            if not rings:
                continue
            nm = best_restricted_name(a, ty)
            for r in rings:
                s = dp(r, 0.001)
                if len(s) > 2:
                    restricted.append({"ty": ty, "n": nm, "r": rnd(s, 4)})
                    n_kept += 1
        print(f"  restricted:{ty}: {len(feats)} raw, {n_kept} rings kept, fields={sample_fields}")
    B["restricted"] = restricted
    print(f"  restricted lands bundled: {len(restricted)} polygons across all 6 MARS "
          f"categories (park/crownreserve/reserve/urban/claim/manual)")

    # ---- 13. SMDI uranium occurrences (grade scraped from detail-page text) ----
    # The Mineral Deposits Index (same service section 1 uses) carries every uranium-tagged
    # SMDI record, not just named deposits with defined resources - occurrences, prospects
    # and bare "mineral location" showings. None of that carries a structured grade field;
    # the only place a percent-U3O8 or ppm-U figure exists is as free narrative text on each
    # record's own detail page (mineraldeposits.saskatchewan.ca/Home/Viewdetails/<SMDI>).
    # This section scrapes and regex-parses those pages. Best-effort only: figures are
    # whatever number reads highest on the page, may come from an old radiometric/gamma
    # survey rather than a chemical assay (flagged when detectable from nearby words), and
    # a handful of pages will misparse or parse nothing. Never present these as verified
    # assay grades without that caveat - see map-pipeline.md.
    #
    # Cached by SMDI number in exports/smdi_grade_cache.json so a re-run only scrapes NEW
    # records, not the full ~1,550 again. First run is slow (~15-20 min at one request
    # every quarter second) - that's expected, not a hang. Checkpointed every 100 scrapes
    # so a killed run doesn't lose progress.
    print("SMDI uranium occurrences (grade scrape)")
    CACHE_PATH = os.path.join(OUT, "smdi_grade_cache.json")
    try:
        grade_cache = json.load(open(CACHE_PATH))
    except Exception:
        grade_cache = {}

    smdi_recs = q(f"{EGIS}/Mineral_Exploration/FeatureServer/2",
                  "SYMBOLOGY_GROUPING = 'Uranium'",
                  "SMDI,NAME,STATUS,PRODUCTION,RESERVESRESOURCES,WEBLINK", label="smdi")

    PCT_RANGE_RE = re.compile(r"(\d+\.?\d*)\s*(?:to|-|–)\s*(\d+\.?\d*)\s*%\s*U3?O8", re.I)
    PCT_RE       = re.compile(r"(\d+\.?\d*)\s*%\s*U3?O8", re.I)
    PPM_RE       = re.compile(r"(\d[\d,]*\.?\d*)\s*ppm\s*e?U3?O8|(\d[\d,]*\.?\d*)\s*ppm\s*U\b", re.I)
    GAMMA_WORDS  = re.compile(r"gamma|radiometric|spectrometer|downhole|cps|counts per second|probe|scintillometer", re.I)
    U3O8_TO_U_PPM = 8480.0   # 1% U3O8 by mass = 8,480 ppm U

    def parse_grade(text):
        best_ppm, best_pct, best_assay = None, None, None
        def consider(pct_v, ppm_v, start):
            nonlocal best_ppm, best_pct, best_assay
            if best_ppm is None or ppm_v > best_ppm:
                assay = not GAMMA_WORDS.search(text[max(0, start - 80):start])
                best_pct, best_ppm, best_assay = pct_v, ppm_v, assay
        for m in PCT_RANGE_RE.finditer(text):
            v = max(float(m.group(1)), float(m.group(2)))
            consider(v, v * U3O8_TO_U_PPM, m.start())
        for m in PCT_RE.finditer(text):
            v = float(m.group(1))
            consider(v, v * U3O8_TO_U_PPM, m.start())
        for m in PPM_RE.finditer(text):
            raw = (m.group(1) or m.group(2) or "").replace(",", "")
            if not raw:
                continue
            v = float(raw)
            consider(v / U3O8_TO_U_PPM, v, m.start())
        return (round(best_pct, 4) if best_pct is not None else None,
                round(best_ppm, 1) if best_ppm is not None else None,
                best_assay)

    def get_text(url):
        req = urllib.request.Request(url, headers={"User-Agent": "basin-layers/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8", "ignore")
        return re.sub(r"<[^>]+>", " ", raw)

    smdi_out, n_scraped, n_cached, n_failed = [], 0, 0, 0
    for f in smdi_recs:
        g = f.get("geometry") or {}
        if g.get("x") is None or not inwin(g["x"], g["y"]):
            continue
        a = f.get("attributes", {})
        sid = str(a.get("SMDI") or "").strip()
        if not sid:
            continue
        if sid in grade_cache:
            c = grade_cache[sid]
            pct, ppm, assay = c.get("pct"), c.get("ppm"), c.get("assay")
            n_cached += 1
        else:
            url = a.get("WEBLINK") or f"https://mineraldeposits.saskatchewan.ca/Home/Viewdetails/{sid}"
            try:
                pct, ppm, assay = parse_grade(get_text(url))
            except Exception:
                pct, ppm, assay = None, None, None
                n_failed += 1
            grade_cache[sid] = {"pct": pct, "ppm": ppm, "assay": assay}
            n_scraped += 1
            time.sleep(0.25)
            if n_scraped % 100 == 0:
                print(f"  scraped {n_scraped} new pages so far ({n_cached} from cache)...", flush=True)
                json.dump(grade_cache, open(CACHE_PATH, "w"))
        rec = {"x": round(g["x"], 4), "y": round(g["y"], 4), "n": a.get("NAME") or "",
               "s": a.get("STATUS") or "", "id": sid}
        if pct is not None:
            rec["pct"] = pct
        if ppm is not None:
            rec["ppm"] = ppm
        if assay is not None:
            rec["assay"] = 1 if assay else 0
        smdi_out.append(rec)

    json.dump(grade_cache, open(CACHE_PATH, "w"))
    save("smdi", esri_to_gj(smdi_recs))
    B["smdi"] = smdi_out
    n_with_grade = sum(1 for r in smdi_out if "ppm" in r)
    print(f"  smdi: {len(smdi_out)} occurrences in window, {n_scraped} scraped this run, "
          f"{n_cached} from cache, {n_failed} failed, {n_with_grade} carry a parsed grade")

    p = os.path.join(OUT, "map_bundle.json")
    json.dump(B, open(p, "w"))
    print(f"\nmap_bundle.json  {os.path.getsize(p)/1e6:.1f} MB")
    for k in ("tenure", "claims", "deposits", "mines", "places", "highways", "footprints",
              "lakes", "boulder_grid", "geochem_grid", "conductors", "lapsed", "ab_tenure",
              "restricted", "smdi"):
        print(f"  {k:14s} {len(B.get(k, [])):>7,}")
    print("\nDone. Tell Claude the bundle is ready.")


if __name__ == "__main__":
    main()
