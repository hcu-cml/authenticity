"""
RELEASE NOTE (public repository)
-------------------------------
This is the benchmark's template module with one modification: the gold
Cypher (and guard) queries of the held-out test templates are replaced by
the string "<withheld: gold query of a held-out test template>".
Every other part of the module is unchanged, so
`generate_questions.py` reproduces the public development split end to end
against a restored city graph. Regenerating the held-out test split needs
the unredacted module, which the authors keep private; see
benchmark_a/README.md ('Held-out test split').
"""

"""
templates.py — schema-grounded question templates for the AuthentiCity benchmark.

Each template instantiates into one or more benchmark questions by filling
slots with values read from the live graph (see generate_questions.py), so
questions are always grounded in data that actually exists. Gold Cypher is
authored per template with {slot} placeholders; literals are inlined at
generation time (no query parameters), matching the project rule that
displayed queries must be copy-pasteable.

Full inventory (81 templates: the original 65 per bench/QUESTION_SUITE_DESIGN.md
B1 spec, plus 16 added 2026-07-19 to exercise per-city native thematic content
that the original 65 left untouched -- see QUESTION_SUITE_DESIGN.md §4.11).

Categories (paper Table `tab:categories`):
  aggregate    — schema grounding, standard retrieval           (Tier 1)
  filter_topk  — filters, top-k ranking                         (Tier 1)
  multihop     — traversal over the compact schema              (Tier 1)
  spatial      — bbox / proximity / geometric predicates         (Tier 1)
  cross_source — OSM vs authoritative agreement/disagreement    (Tier 1)
  provenance   — source and confidence constraints              (Tier 1)
  coverage     — partial-coverage-aware aggregation             (Tier 2, Hamburg)
  lod3         — facade/interior showcase                       (Tier 2, Hamburg)
  infeasible   — unanswerable; gold behaviour is to refuse      (Tier 1)

Template fields:
  id            stable template id
  category      one of the above
  tier          1 or 2 (2 = needs the Hamburg deep-fusion layers)
  difficulty    1–5 (rubric in QUESTION_SUITE_DESIGN.md §5)
  feasible      False => infeasible category; gold answer is REFUSE
  nl            list of NL paraphrases with {slot} placeholders
  gold_cypher   gold query with {slot} placeholders (None if infeasible)
  gold_sql      always None. A parallel SQL/3DCityDB relational gold is OUT OF
                SCOPE for this paper by design: the benchmark evaluates against
                the property graph only (see the paper's Task Family A
                rationale, subsec:query_tasks). Field kept for possible future
                work, not a pending deliverable.
  slots         {slot_name: provider_name}; providers below
  allow_empty   verified result may be an empty list (default False)
  guard         for infeasible templates: Cypher that MUST return the row
                {n: 0}, proving the question is truly unanswerable. May use
                the same {slot} placeholders as `nl` — the generator formats
                it with the same slot combination.

Templates whose only slot is a per-city presence check (e.g. Hamburg-only
`lod3_*`/`cov_*`, Tokyo-only `tokyo_jp_*`) self-gate: their provider returns
no rows on a city that lacks the layer, so the template is silently skipped
there (per the "grounded slots" design principle) rather than needing an
explicit city allowlist.

NEARBY_BUILDING note: proximity edges are intentionally OFF for every
release graph (opt-in --nearby-edges only; see CLAUDE.md /
REINGEST_CAMPAIGN.md §8). All proximity templates below therefore use
`spatial.withinDistance`/`point.distance` over the `features` R-tree layer,
never the edge.

Height sentinel note: some sources stamp a missing-value sentinel on
`measured_height` (PLATEAU/Tokyo uses -9999); it is kept verbatim in the graph
but must be excluded from every statistic (project convention `> -999`, matching
`eval/stats_control.py` HEIGHT_SENTINEL and `bench/osm_citygml_conflict_analysis.py`).
Every gold query that AGGREGATES height (avg/median/percentile/mean-deviation) or
derives a threshold from the height distribution therefore guards with
`measured_height > -999` rather than a bare `IS NOT NULL`. Max/"tallest" templates
need no guard (a -9999 floor is never the maximum), and `> {threshold}` filters
exclude the sentinel transitively once the threshold provider is sentinel-safe.
"""

# --------------------------------------------------------------------------
# Slot providers — each is a Cypher query returning rows with a `value`
# column; the generator caches results and samples up to N values per slot.
# Providers returning no rows disable the templates that depend on them
# (logged as a warning), so missing layers degrade gracefully.
# --------------------------------------------------------------------------
PROVIDERS = {
    # thematic values
    "district": "MATCH (d:District) RETURN d.id AS value ORDER BY value",
    "function_name": (
        "MATCH (:Building)-[:HAS_FUNCTION]->(f:BuildingFunction) "
        "WHERE f.name IS NOT NULL RETURN DISTINCT f.name AS value ORDER BY value"
    ),
    "roof_type_name": (
        "MATCH (:Building)-[:HAS_ROOF_TYPE]->(r:RoofType) "
        "WHERE r.name IS NOT NULL RETURN DISTINCT r.name AS value ORDER BY value"
    ),
    "material": (
        "MATCH (b:Building) WHERE b.predictedroofmaterial IS NOT NULL "
        "RETURN DISTINCT b.predictedroofmaterial AS value ORDER BY value"
    ),
    # numeric thresholds derived from the height distribution (25/50/75th pct)
    "height_threshold": (
        "MATCH (b:Building) WHERE b.measured_height > -999 "
        "WITH percentileCont(b.measured_height, 0.25) AS p25, "
        "     percentileCont(b.measured_height, 0.50) AS p50, "
        "     percentileCont(b.measured_height, 0.75) AS p75 "
        "UNWIND [round(p25), round(p50), round(p75)] AS value RETURN DISTINCT value"
    ),
    "topk": "UNWIND [5, 10, 20] AS value RETURN value",
    "deviation_m": "UNWIND [3, 5] AS value RETURN value",
    "jaccard_min": "UNWIND [0.5, 0.8] AS value RETURN value",
    "radius_m": "UNWIND [50, 100, 200] AS value RETURN value",
    # a building that actually hosts POIs (for containment questions)
    "poi_building": (
        "MATCH (b:Building)-[:HAS_POI]->(:OsmFeature) "
        "WITH b, count(*) AS n_poi ORDER BY n_poi DESC LIMIT 5 "
        "RETURN b.id AS value"
    ),
    # any building with location, used as a proximity anchor (no NEARBY_BUILDING
    # dependency — see module docstring)
    "nearby_building": (
        "MATCH (b:Building) WHERE b.location IS NOT NULL "
        "RETURN b.id AS value ORDER BY b.id LIMIT 5"
    ),
    # any building with at least one boundary surface (generic anchor for
    # non-proximity single-building questions)
    "any_building": (
        "MATCH (b:Building)-[:HAS_BOUNDARY]->(:BoundarySurface) "
        "WITH DISTINCT b RETURN b.id AS value ORDER BY b.id LIMIT 5"
    ),
    # a building centroid rendered as an "x,y" string, for point-radius queries
    "building_centroid_xy": (
        "MATCH (b:Building) WHERE b.center_x IS NOT NULL AND b.center_y IS NOT NULL "
        "RETURN toString(round(b.center_x * 100) / 100.0) + ',' "
        "+ toString(round(b.center_y * 100) / 100.0) AS value ORDER BY b.id LIMIT 5"
    ),
    # a small (500m x 500m) window centred on a real building, for O(candidates^2)
    # density/pairwise templates where a whole-city per-row procedure-call scan
    # is intractable (spatial_dense_pairs/spatial_isolated — see their comments)
    "small_bbox_wkt": (
        "MATCH (b:Building) WHERE b.center_x IS NOT NULL AND b.center_y IS NOT NULL "
        "WITH b ORDER BY b.id LIMIT 3 "
        "WITH b.center_x - 250 AS x0, b.center_y - 250 AS y0, "
        "     b.center_x + 250 AS x1, b.center_y + 250 AS y1 "
        "RETURN 'POLYGON((' + toString(x0) + ' ' + toString(y0) + ', ' + toString(x1) + ' ' + toString(y0) + ', ' "
        "       + toString(x1) + ' ' + toString(y1) + ', ' + toString(x0) + ' ' + toString(y1) + ', ' "
        "       + toString(x0) + ' ' + toString(y0) + '))' AS value"
    ),
    # a genuinely LOW-DENSITY 500 m window, for spatial_isolated. The dense-core
    # small_bbox_wkt above is wrong there: it centres on the lowest-id buildings,
    # which sit in the built-up core where every building has a <100 m neighbour, so
    # the isolated-count is trivially 0 on every city (found in the spatial audit).
    # A plain "off-centre"/periphery pick doesn't help either — isolation follows
    # LOCAL density, not distance from the map centre (the extreme-periphery windows
    # are still clustered). So: sample a bounded, deterministic (id-ordered) set of
    # buildings, count each one's neighbours within 100 m via the R-tree, and centre
    # the window on the sparsest three. Dense megacities legitimately still yield 0
    # (no isolated buildings exist); sparse cities (e.g. Helsinki: 9 isolated of
    # 2,980) surface real isolation. Bounded LIMIT keeps it viable on 2 M-node graphs.
    "sparse_bbox_wkt": (
        "MATCH (b:Building) WHERE b.center_x IS NOT NULL WITH b ORDER BY b.id LIMIT 3000 "
        "CALL (b) { "
        "  CALL spatial.intersects('features', 'POLYGON((' "
        "  + toString(b.center_x-100)+' '+toString(b.center_y-100)+',' + toString(b.center_x+100)+' '+toString(b.center_y-100)+',' "
        "  + toString(b.center_x+100)+' '+toString(b.center_y+100)+',' + toString(b.center_x-100)+' '+toString(b.center_y+100)+',' "
        "  + toString(b.center_x-100)+' '+toString(b.center_y-100)+'))') YIELD node "
        "  WITH sum(CASE WHEN node:Building AND node.id <> b.id THEN 1 ELSE 0 END) AS nn RETURN nn "
        "} "
        "WITH b, nn ORDER BY nn ASC, b.id ASC LIMIT 3 "
        "RETURN 'POLYGON((' + toString(b.center_x-250) + ' ' + toString(b.center_y-250) + ', ' "
        "       + toString(b.center_x+250) + ' ' + toString(b.center_y-250) + ', ' + toString(b.center_x+250) + ' ' + toString(b.center_y+250) + ', ' "
        "       + toString(b.center_x-250) + ' ' + toString(b.center_y+250) + ', ' + toString(b.center_x-250) + ' ' + toString(b.center_y-250) + '))' AS value"
    ),
    # Two sub-windows drawn from the BUILDING-COORDINATE distribution (10/50/90
    # percentiles per axis), not the raw dataset bbox. The dataset bbox can be far
    # larger than the built-up area (e.g. Hamburg: a handful of far-west outliers
    # stretch it to ~121 km wide while 94% of buildings sit in one quarter), so
    # slicing the raw bbox into quarters yields empty windows and trivially-0/None
    # gold answers for every bbox_* template. Percentile windows follow the actual
    # building density, so both windows are guaranteed populated on any city.
    "bbox_wkt": (
        "MATCH (b:Building) WHERE b.center_x IS NOT NULL AND b.center_y IS NOT NULL "
        "WITH percentileCont(b.center_x, 0.1) AS x0, percentileCont(b.center_x, 0.5) AS xm, "
        "     percentileCont(b.center_x, 0.9) AS x2, percentileCont(b.center_y, 0.1) AS y0, "
        "     percentileCont(b.center_y, 0.5) AS ym, percentileCont(b.center_y, 0.9) AS y2 "
        "WITH [[x0, y0, xm, ym], [xm, ym, x2, y2]] AS windows "
        "UNWIND windows AS w "
        "RETURN 'POLYGON((' + w[0] + ' ' + w[1] + ', ' + w[2] + ' ' + w[1] + ', ' "
        "       + w[2] + ' ' + w[3] + ', ' + w[0] + ' ' + w[3] + ', ' + w[0] + ' ' + w[1] + '))' AS value"
    ),
    # a water-body OSM feature centroid rendered as an "x,y" string, for a
    # single bounded point-radius query (see spatial_near_water: iterating
    # spatial.withinDistance once per water feature does not scale — found
    # stuck for 15+ minutes on Tokyo's much larger `features` R-tree even
    # with only ~3,500 water features, despite completing in under 3
    # minutes on Hamburg/Zurich)
    "water_centroid_xy": (
        "MATCH (o:OsmFeature {osm_kind: 'water'}) "
        "WHERE o.center_x IS NOT NULL AND o.center_y IS NOT NULL "
        "RETURN toString(round(o.center_x * 100) / 100.0) + ',' "
        "+ toString(round(o.center_y * 100) / 100.0) AS value ORDER BY o.id LIMIT 5"
    ),
    # OSM POI kinds present in this city (for spatial x cross-source composition)
    "amenity": (
        "MATCH (o:OsmFeature) WHERE o.osm_amenity IS NOT NULL "
        "RETURN DISTINCT o.osm_amenity AS value ORDER BY value LIMIT 8"
    ),
    # a building with a confirmed primary OSM match reporting a name
    "named_osm_building": (
        "MATCH (b:Building)-[:ENRICHED_BY {is_primary: true}]->(o:OsmFeature) "
        "WHERE o.name IS NOT NULL WITH DISTINCT b LIMIT 5 RETURN b.id AS value ORDER BY b.id"
    ),
    # a building with both an authoritative and an OSM height on record
    "dual_height_building": (
        "MATCH (b:Building)-[:ENRICHED_BY {is_primary: true}]->(o:OsmFeature) "
        "WHERE o.osm_height IS NOT NULL AND b.measured_height > -999 "
        "WITH DISTINCT b LIMIT 5 RETURN b.id AS value ORDER BY b.id"
    ),
    # a building carrying reconstructed LoD3 facade detail (Hamburg only —
    # empty everywhere else, so lod3_* templates self-gate). LoD3 facades
    # attach via the dedicated HAS_LOD3_FACADE edge onto a node that is
    # BOTH :BoundarySurface and :Lod3Facade, not via the ordinary
    # HAS_BOUNDARY edge (which stays LoD2-only, never overwritten).
    "lod3_building": (
        "MATCH (b:Building)-[:HAS_LOD3_FACADE]->(:BoundarySurface)-[:HAS_OPENING]->(:Opening) "
        "WITH DISTINCT b RETURN b.id AS value ORDER BY b.id LIMIT 5"
    ),
    # a building with at least one interior Room (Hamburg LoD3/4 only)
    "room_building": (
        "MATCH (b:Building)-[:HAS_INTERIOR_ROOM]->(:Room) "
        "WITH DISTINCT b RETURN b.id AS value ORDER BY b.id LIMIT 5"
    ),
    # a district name guaranteed not to exist (for the false-premise template)
    "fake_district": (
        "MATCH (d:District) WITH collect(d.id) AS ids "
        "RETURN 'DISTRICT_DOES_NOT_EXIST_' + toString(size(ids)) AS value"
    ),
    # Tokyo-only Japanese-keyed generic attribute (self-gates on other cities)
    "jp_district_plan": (
        "MATCH (b:Building) WHERE b.`地区計画` IS NOT NULL "
        "RETURN DISTINCT b.`地区計画` AS value ORDER BY value LIMIT 5"
    ),
    # -- added in the per-city native-content pass (2026-07-19): providers for --
    # -- templates that exercise previously-unused thematic properties --------
    "street_name": (
        "MATCH (b:Building) WHERE b.addr_street IS NOT NULL "
        "RETURN DISTINCT b.addr_street AS value ORDER BY value LIMIT 5"
    ),
    "confidence_threshold": "UNWIND [0.5, 0.8] AS value RETURN value",
}

TEMPLATES = [
    # ------------------------------------------------------------------ #
    # aggregate (Tier 1)                                                 #
    # ------------------------------------------------------------------ #
    {
        "id": "agg_count_buildings",
        "category": "aggregate", "tier": 1, "difficulty": 1, "feasible": True,
        "nl": [
            "How many buildings does the dataset contain?",
            "What is the total number of buildings in the city model?",
            "What is the building count for this dataset?",
        ],
        "gold_cypher": "MATCH (b:Building) RETURN count(b) AS n",
        "gold_sql": None, "slots": {},
    },
    {
        "id": "agg_avg_height",
        "category": "aggregate", "tier": 1, "difficulty": 1, "feasible": True,
        "nl": [
            "What is the average measured building height in meters?",
            "How tall is a building on average in this dataset?",
            "On average, how high are the buildings, in meters?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.measured_height > -999 "
            "RETURN round(avg(b.measured_height) * 100) / 100.0 AS avg_height_m"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "agg_max_storeys",
        "category": "aggregate", "tier": 1, "difficulty": 1, "feasible": True,
        "nl": [
            "What is the highest number of storeys above ground of any building?",
            "What is the maximum number of above-ground storeys recorded for any building?",
            "Across all buildings, what is the largest storeys-above-ground value?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "agg_median_height",
        "category": "aggregate", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "What is the median measured building height?",
            "What is the median value of the measured building heights?",
            "Find the median height among all buildings with a recorded height.",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.measured_height > -999 "
            "RETURN round(percentileCont(b.measured_height, 0.5) * 100) / 100.0 AS median_height_m"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "agg_dataset_extent",
        "category": "aggregate", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "What rectangular extent does the dataset cover, in kilometers?",
            "What is the width and height of the dataset's bounding box, in kilometers?",
            "How large an area, in kilometers, does the dataset's bounding rectangle span?",
        ],
        "gold_cypher": (
            "MATCH (ds:Dataset) "
            "RETURN round((ds.bbox_max_x - ds.bbox_min_x) / 100.0) / 10.0 AS width_km, "
            "round((ds.bbox_max_y - ds.bbox_min_y) / 100.0) / 10.0 AS height_km"
        ),
        "gold_sql": None, "slots": {},
    },
    # ------------------------------------------------------------------ #
    # filter / top-k (Tier 1)                                            #
    # ------------------------------------------------------------------ #
    {
        "id": "filter_taller_than",
        "category": "filter_topk", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many buildings are taller than {height_threshold} meters?",
            "Count the buildings whose measured height exceeds {height_threshold} m.",
            "How many buildings have a measured height above {height_threshold} meters?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.measured_height > {height_threshold} "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {"height_threshold": "height_threshold"},
    },
    {
        "id": "topk_tallest",
        "category": "filter_topk", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "List the {topk} tallest buildings with their heights.",
            "Which are the {topk} highest buildings in the dataset?",
            "What are the {topk} tallest buildings and their heights?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.measured_height IS NOT NULL "
            "RETURN b.id AS id, b.measured_height AS height_m "
            "ORDER BY b.measured_height DESC, b.id ASC LIMIT {topk}"
        ),
        "gold_sql": None, "slots": {"topk": "topk"}, "allow_empty": True,
    },
    {
        "id": "filter_by_function",
        "category": "filter_topk", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many buildings have the function '{function_name}'?",
            "How many buildings are classified with the function '{function_name}'?",
            "Count the buildings whose building function is '{function_name}'.",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:HAS_FUNCTION]->(f:BuildingFunction {{name: '{function_name}'}}) "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {"function_name": "function_name"},
    },
    {
        "id": "filter_compound",
        "category": "filter_topk", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings taller than {height_threshold} m have roof type '{roof_type_name}'?",
            "Count the buildings with roof type '{roof_type_name}' that are taller than {height_threshold} m.",
            "How many buildings exceed {height_threshold} m in height and have the roof type '{roof_type_name}'?",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:HAS_ROOF_TYPE]->(r:RoofType {{name: '{roof_type_name}'}}) "
            "WHERE b.measured_height > {height_threshold} "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None,
        "slots": {"height_threshold": "height_threshold", "roof_type_name": "roof_type_name"},
    },
    {
        "id": "topk_most_storeys",
        "category": "filter_topk", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "List the {topk} buildings with the most storeys above ground.",
            "Which {topk} buildings have the highest number of storeys above ground?",
            "What are the {topk} buildings with the greatest storeys-above-ground count?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {"topk": "topk"}, "allow_empty": True,
    },
    {
        "id": "filter_missing_height",
        "category": "filter_topk", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many buildings have no recorded height?",
            "For how many buildings is the measured height missing?",
            "Count the buildings without a recorded measured height.",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    # ------------------------------------------------------------------ #
    # multihop (Tier 1)                                                  #
    # ------------------------------------------------------------------ #
    {
        "id": "multihop_rooftype_distribution",
        "category": "multihop", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "Show the distribution of roof types across all buildings.",
            "How many buildings are there per roof type?",
            "Break down the number of buildings by roof type.",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:HAS_ROOF_TYPE]->(r:RoofType) "
            "RETURN r.name AS roof_type, count(b) AS n ORDER BY n DESC, roof_type ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "multihop_function_avg_height",
        "category": "multihop", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the average building height per building function?",
            "For each building function, what is the average building height?",
            "Group the buildings by function and report the average height in each group.",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:HAS_FUNCTION]->(f:BuildingFunction) "
            "WHERE b.measured_height > -999 "
            "RETURN f.name AS function, round(avg(b.measured_height) * 100) / 100.0 AS avg_height_m, "
            "count(b) AS n ORDER BY n DESC, function ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "multihop_district_counts",
        "category": "multihop", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many buildings are located in each district?",
            "Break down the number of buildings per district.",
            "For each district, how many buildings does it contain?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "multihop_building_parts",
        "category": "multihop", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "Which buildings consist of more than one building part?",
            "Which buildings are composed of two or more building parts?",
            "List the buildings that have more than one building part.",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:HAS_BUILDING_PART]->(:BuildingPart) "
            "WITH b, count(*) AS n_parts WHERE n_parts >= 2 "
            "RETURN b.id AS id, n_parts ORDER BY n_parts DESC, id ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "multihop_boundary_census",
        "category": "multihop", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many boundary surfaces of each type does building {any_building} have?",
            "For building {any_building}, how many boundary surfaces of each type are there?",
            "Break down building {any_building}'s boundary surfaces by surface type.",
        ],
        "gold_cypher": (
            "MATCH (:Building {{id: '{any_building}'}})-[:HAS_BOUNDARY]->(s:BoundarySurface) "
            "RETURN s.surface_type AS surface_type, count(s) AS n ORDER BY n DESC, surface_type ASC"
        ),
        "gold_sql": None, "slots": {"any_building": "any_building"},
    },
    {
        "id": "multihop_district_top_function",
        "category": "multihop", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "What is the most common building function in district {district}?",
            "In district {district}, which building function occurs most often?",
            "Which building function is most frequent among buildings in district {district}?",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:LOCATED_IN]->(:District {{id: '{district}'}}) "
            "MATCH (b)-[:HAS_FUNCTION]->(f:BuildingFunction) "
            "RETURN f.name AS function, count(b) AS n ORDER BY n DESC, function ASC LIMIT 1"
        ),
        "gold_sql": None, "slots": {"district": "district"}, "allow_empty": True,
    },
    # ------------------------------------------------------------------ #
    # spatial (Tier 1) — THE core wedge                                  #
    # ------------------------------------------------------------------ #
    {
        "id": "spatial_bbox_count",
        "category": "spatial", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings lie inside the bounding box {bbox_wkt}?",
            "Count the buildings whose footprint intersects the window {bbox_wkt}.",
            "How many buildings fall within the window {bbox_wkt}?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {"bbox_wkt": "bbox_wkt"},
    },
    {
        "id": "spatial_bbox_tallest",
        "category": "spatial", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "Which is the tallest building inside the bounding box {bbox_wkt}?",
            "Within the window {bbox_wkt}, which building is the tallest?",
            "What is the tallest building whose footprint falls inside {bbox_wkt}?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {"bbox_wkt": "bbox_wkt"}, "allow_empty": True,
    },
    {
        "id": "spatial_bbox_agg",
        "category": "spatial", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the average building height inside the window {bbox_wkt}?",
            "Within the bounding box {bbox_wkt}, what is the average building height?",
            "For buildings inside {bbox_wkt}, what is the mean measured height?",
        ],
        "gold_cypher": (
            "CALL spatial.intersects('features', '{bbox_wkt}') YIELD node "
            "WITH node WHERE node:Building AND node.measured_height > -999 "
            "RETURN round(avg(node.measured_height) * 100) / 100.0 AS avg_height_m, count(node) AS n"
        ),
        "gold_sql": None, "slots": {"bbox_wkt": "bbox_wkt"},
    },
    {
        "id": "spatial_neighbours",
        "category": "spatial", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings stand within 100 meters of building {nearby_building}?",
            "Within 100 meters of building {nearby_building}, how many other buildings are there?",
            "Count the buildings located within 100 m of building {nearby_building}.",
        ],
        "gold_cypher": (
            # R-tree window in TRUE metres (a +/-100 m box around the anchor in the
            # dataset's metric CRS), then an exact circular recheck via point.distance.
            # NB: spatial.withinDistance's radius arg is km against a geographic layer
            # and mis-scales on this Cartesian-metre `features` layer (returns ~0), so
            # a metre-box intersects + point.distance is the correct proximity idiom.
            "MATCH (b0:Building {{id: '{nearby_building}'}}) WITH b0, b0.location AS c "
            "CALL spatial.intersects('features', 'POLYGON((' "
            "+ toString(c.x-100)+' '+toString(c.y-100)+',' + toString(c.x+100)+' '+toString(c.y-100)+',' "
            "+ toString(c.x+100)+' '+toString(c.y+100)+',' + toString(c.x-100)+' '+toString(c.y+100)+',' "
            "+ toString(c.x-100)+' '+toString(c.y-100)+'))') YIELD node "
            "WITH b0, node WHERE node:Building AND node.id <> b0.id "
            "AND point.distance(b0.location, node.location) <= 100 "
            "RETURN count(node) AS n"
        ),
        "gold_sql": None, "slots": {"nearby_building": "nearby_building"},
    },
    {
        "id": "spatial_within_distance_point",
        "category": "spatial", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings lie within {radius_m} m of the point ({building_centroid_xy})?",
            "Count the buildings within {radius_m} meters of the point ({building_centroid_xy}).",
            "How many buildings are located no more than {radius_m} m from ({building_centroid_xy})?",
        ],
        "gold_cypher": (
            # +/-{radius_m} m R-tree window (metric CRS) then exact point.distance circle.
            "WITH split('{building_centroid_xy}', ',') AS xy "
            "WITH point({{x: toFloat(xy[0]), y: toFloat(xy[1])}}) AS p "
            "CALL spatial.intersects('features', 'POLYGON((' "
            "+ toString(p.x-{radius_m})+' '+toString(p.y-{radius_m})+',' + toString(p.x+{radius_m})+' '+toString(p.y-{radius_m})+',' "
            "+ toString(p.x+{radius_m})+' '+toString(p.y+{radius_m})+',' + toString(p.x-{radius_m})+' '+toString(p.y+{radius_m})+',' "
            "+ toString(p.x-{radius_m})+' '+toString(p.y-{radius_m})+'))') YIELD node "
            "WITH p, node WHERE node:Building AND point.distance(p, node.location) <= {radius_m} "
            "RETURN count(node) AS n"
        ),
        "gold_sql": None,
        "slots": {"building_centroid_xy": "building_centroid_xy", "radius_m": "radius_m"},
    },
    {
        "id": "spatial_knearest",
        "category": "spatial", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "Which {topk} buildings are closest to building {nearby_building}?",
            "What are the {topk} nearest buildings to building {nearby_building}?",
            "List the {topk} buildings closest in distance to building {nearby_building}.",
        ],
        "gold_cypher": (
            # True k-nearest-neighbour: a distance ranking, not a radius window, so it
            # returns exactly {topk} regardless of local density (a fixed-radius prefilter
            # under-delivers where fewer than k buildings fall in the radius). One label
            # scan + top-k over point.distance (metric CRS); ~0.8 s on 388 k buildings.
            # (spatial.withinDistance is unusable here — its km radius mis-scales on the
            # Cartesian-metre `features` layer; see spatial_neighbours.)
            "MATCH (b0:Building {{id: '{nearby_building}'}}) "
            "MATCH (node:Building) WHERE node.id <> b0.id AND node.location IS NOT NULL "
            "RETURN node.id AS id, round(point.distance(b0.location, node.location) * 100) / 100.0 AS distance_m "
            "ORDER BY distance_m ASC, id ASC LIMIT {topk}"
        ),
        "gold_sql": None,
        "slots": {"nearby_building": "nearby_building", "topk": "topk"},
    },
    {
        "id": "spatial_bbox_by_rooftype",
        "category": "spatial", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "Within the window {bbox_wkt}, how many buildings are there per roof type?",
            "For the window {bbox_wkt}, break down the buildings by roof type.",
            "Inside the bounding box {bbox_wkt}, how many buildings does each roof type have?",
        ],
        "gold_cypher": (
            "CALL spatial.intersects('features', '{bbox_wkt}') YIELD node "
            "WITH node WHERE node:Building "
            "MATCH (node)-[:HAS_ROOF_TYPE]->(r:RoofType) "
            "RETURN r.name AS roof_type, count(node) AS n ORDER BY n DESC, roof_type ASC"
        ),
        "gold_sql": None, "slots": {"bbox_wkt": "bbox_wkt"}, "allow_empty": True,
    },
    {
        "id": "spatial_near_amenity_tallest",
        "category": "spatial", "tier": 1, "difficulty": 5, "feasible": True,
        "nl": [
            "What is the tallest building within {radius_m} m of a {amenity} point of interest?",
            "Within {radius_m} meters of a {amenity} POI, which building is the tallest?",
            "Which is the tallest building located within {radius_m} m of an amenity of type {amenity}?",
        ],
        "gold_cypher": (
            # Per amenity POI: a +/-{radius_m} m R-tree window (metric CRS) then an exact
            # point.distance circle, unioned across all POIs of this type, tallest overall.
            "MATCH (o:OsmFeature {{osm_amenity: '{amenity}'}}) WITH o, o.location AS c "
            "CALL spatial.intersects('features', 'POLYGON((' "
            "+ toString(c.x-{radius_m})+' '+toString(c.y-{radius_m})+',' + toString(c.x+{radius_m})+' '+toString(c.y-{radius_m})+',' "
            "+ toString(c.x+{radius_m})+' '+toString(c.y+{radius_m})+',' + toString(c.x-{radius_m})+' '+toString(c.y+{radius_m})+',' "
            "+ toString(c.x-{radius_m})+' '+toString(c.y-{radius_m})+'))') YIELD node "
            "WITH o, node WHERE node:Building AND node.measured_height IS NOT NULL "
            "AND point.distance(o.location, node.location) <= {radius_m} "
            "RETURN node.id AS id, node.measured_height AS height_m "
            "ORDER BY node.measured_height DESC, node.id ASC LIMIT 1"
        ),
        "gold_sql": None,
        "slots": {"amenity": "amenity", "radius_m": "radius_m"}, "allow_empty": True,
    },
    {
        # One water feature per instantiation (bounded point-radius query),
        # not a scan over every water OsmFeature in the city — see the
        # water_centroid_xy provider comment.
        "id": "spatial_near_water",
        "category": "spatial", "tier": 1, "difficulty": 5, "feasible": True,
        "nl": [
            "How many buildings stand within {radius_m} m of the water feature at ({water_centroid_xy})?",
            "Count the buildings within {radius_m} meters of the water feature located at ({water_centroid_xy}).",
            "How many buildings are within {radius_m} m of the water feature centered at ({water_centroid_xy})?",
        ],
        "gold_cypher": (
            # +/-{radius_m} m R-tree window (metric CRS) around the water centroid, then
            # exact point.distance circle.
            "WITH split('{water_centroid_xy}', ',') AS xy "
            "WITH point({{x: toFloat(xy[0]), y: toFloat(xy[1])}}) AS p "
            "CALL spatial.intersects('features', 'POLYGON((' "
            "+ toString(p.x-{radius_m})+' '+toString(p.y-{radius_m})+',' + toString(p.x+{radius_m})+' '+toString(p.y-{radius_m})+',' "
            "+ toString(p.x+{radius_m})+' '+toString(p.y+{radius_m})+',' + toString(p.x-{radius_m})+' '+toString(p.y+{radius_m})+',' "
            "+ toString(p.x-{radius_m})+' '+toString(p.y-{radius_m})+'))') YIELD node "
            "WITH p, node WHERE node:Building AND point.distance(p, node.location) <= {radius_m} "
            "RETURN count(DISTINCT node) AS n"
        ),
        "gold_sql": None,
        "slots": {"water_centroid_xy": "water_centroid_xy", "radius_m": "radius_m"},
    },
    {
        "id": "spatial_roof_complexity",
        "category": "spatial", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "Which {topk} buildings have the most roof polygons?",
            "What are the {topk} buildings with the highest number of roof polygons?",
            "List the {topk} buildings whose roofs have the most polygons.",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {"topk": "topk"}, "allow_empty": True,
    },
    {
        # Scoped to a small (500m) window rather than the whole city: a
        # per-building spatial.withinDistance call across all N buildings is
        # an O(N) procedure-call scan that does not finish in reasonable time
        # on real city graphs (found during verification on Hamburg, 388k
        # buildings — killed after ~4h). Candidate set from one small window
        # is bounded (tens-hundreds of buildings), so the O(candidates^2)
        # in-memory pair check is fast regardless of city size.
        "id": "spatial_dense_pairs",
        "category": "spatial", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "Within the window {small_bbox_wkt}, how many pairs of buildings stand less than 10 meters apart?",
            "In the window {small_bbox_wkt}, count the pairs of buildings that are less than 10 m apart.",
            "How many building pairs within {small_bbox_wkt} are closer than 10 meters to each other?",
        ],
        "gold_cypher": (
            "CALL spatial.intersects('features', '{small_bbox_wkt}') YIELD node "
            "WITH node WHERE node:Building "
            "WITH collect(node) AS bldgs "
            "UNWIND bldgs AS a UNWIND bldgs AS b "
            "WITH a, b WHERE a.id < b.id AND point.distance(a.location, b.location) < 10 "
            "RETURN count(*) AS n"
        ),
        "gold_sql": None, "slots": {"small_bbox_wkt": "small_bbox_wkt"},
    },
    {
        # Same scoping rationale as spatial_dense_pairs above. "Isolated" is
        # evaluated relative to the window's candidate set (a building near
        # the window edge may have an out-of-window neighbour not counted) —
        # an accepted approximation to keep the gold query tractable at any
        # city scale; the NL is scoped to the window to make this explicit.
        "id": "spatial_isolated",
        "category": "spatial", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "Within the window {small_bbox_wkt}, how many buildings have no other building within 100 meters?",
            "In the window {small_bbox_wkt}, count the buildings with no neighboring building within 100 m.",
            "How many buildings inside {small_bbox_wkt} have no other building closer than 100 meters?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {"small_bbox_wkt": "sparse_bbox_wkt"},
    },
    # ------------------------------------------------------------------ #
    # cross_source (Tier 1)                                              #
    # ------------------------------------------------------------------ #
    {
        "id": "xsrc_height_disagreement",
        "category": "cross_source", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "Which buildings have an OSM height that differs from the surveyed height by more than {deviation_m} meters?",
            "Find buildings where crowd-sourced and authoritative height disagree by over {deviation_m} m.",
            "List the buildings where the OSM-reported height and the surveyed height differ by more than {deviation_m} m.",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[r:ENRICHED_BY {{is_primary: true}}]->(o:OsmFeature) "
            "WHERE o.osm_height IS NOT NULL AND b.measured_height > -999 "
            "AND abs(toFloat(o.osm_height) - b.measured_height) > {deviation_m} "
            "RETURN b.id AS id, b.measured_height AS surveyed_m, "
            "toFloat(o.osm_height) AS osm_m "
            "ORDER BY abs(toFloat(o.osm_height) - b.measured_height) DESC, id ASC"
        ),
        "gold_sql": None, "slots": {"deviation_m": "deviation_m"},
        "allow_empty": True,
    },
    {
        "id": "xsrc_unenriched_gap",
        "category": "cross_source", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings have no OpenStreetMap counterpart at all?",
            "Count the buildings that received no OSM enrichment.",
            "How many buildings were not matched to any OpenStreetMap feature?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE NOT (b)-[:ENRICHED_BY]->(:OsmFeature) "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "xsrc_pois_in_building",
        "category": "cross_source", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "Which points of interest are located inside building {poi_building}?",
            "What OpenStreetMap points of interest fall inside building {poi_building}?",
            "List the POIs located within the footprint of building {poi_building}.",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {"poi_building": "poi_building"},
    },
    {
        "id": "xsrc_mean_abs_deviation",
        "category": "cross_source", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "What is the mean absolute difference between OSM and surveyed building heights over all primary matches?",
            "Averaged over all primary matches, what is the mean absolute height difference between OSM and the cadastre?",
            "What is the average absolute deviation between crowd-sourced and surveyed heights, over the primary OSM matches?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "xsrc_reverse_gap",
        "category": "cross_source", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many OSM buildings have no cadastral counterpart?",
            "Count the OSM building features that have no matching cadastral building.",
            "How many OpenStreetMap buildings were not matched to any cadastral building?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "xsrc_name_lookup",
        "category": "cross_source", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "What is the OSM name of building {named_osm_building}?",
            "According to OpenStreetMap, what is building {named_osm_building} called?",
            "What name does OSM record for building {named_osm_building}?",
        ],
        "gold_cypher": (
            "MATCH (:Building {{id: '{named_osm_building}'}})-[:ENRICHED_BY {{is_primary: true}}]->(o:OsmFeature) "
            "RETURN o.name AS osm_name"
        ),
        "gold_sql": None, "slots": {"named_osm_building": "named_osm_building"},
    },
    {
        "id": "xsrc_levels_vs_storeys",
        "category": "cross_source", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "Which buildings report a different floor count in OSM than in the cadastre?",
            "For which buildings do the OSM floor count and the cadastral storey count disagree?",
            "List the buildings where the OSM building-levels value differs from the cadastral storeys-above-ground value.",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "xsrc_agreement_rate",
        "category": "cross_source", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "For buildings where both sources report a height, what share agree within 1 meter?",
            "Among buildings with both an OSM and a surveyed height, what fraction agree to within 1 meter?",
            "What percentage of dual-sourced height buildings have OSM and cadastral heights within 1 m of each other?",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:ENRICHED_BY {{is_primary: true}}]->(o:OsmFeature) "
            "WHERE b.measured_height > -999 AND o.osm_height IS NOT NULL "
            "WITH count(*) AS total, "
            "count(CASE WHEN abs(toFloat(o.osm_height) - b.measured_height) <= 1.0 THEN 1 END) AS agree "
            "RETURN agree, total, "
            "CASE WHEN total = 0 THEN null ELSE round(1000.0 * agree / total) / 10.0 END AS agreement_pct"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "xsrc_net_new_by_kind",
        "category": "cross_source", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What does OpenStreetMap add that the cadastre lacks? Count unmatched OSM features per kind.",
            "Break down the unmatched OpenStreetMap features by kind.",
            "For each OSM feature kind, how many unmatched (cadastre-less) features are there?",
        ],
        "gold_cypher": (
            "MATCH (o:OsmFeature) WHERE o.matched = false "
            "RETURN o.osm_kind AS kind, count(o) AS n ORDER BY n DESC, kind ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    # ------------------------------------------------------------------ #
    # provenance (Tier 1)                                                #
    # ------------------------------------------------------------------ #
    {
        "id": "prov_high_confidence",
        "category": "provenance", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings have a primary OSM match with a Jaccard overlap of at least {jaccard_min}?",
            "Count buildings whose best OSM correspondence reaches Jaccard {jaccard_min} or higher.",
            "How many buildings have a primary OSM correspondence with Jaccard overlap {jaccard_min} or above?",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[r:ENRICHED_BY {{is_primary: true}}]->(:OsmFeature) "
            "WHERE r.jaccard >= {jaccard_min} RETURN count(DISTINCT b) AS n"
        ),
        "gold_sql": None, "slots": {"jaccard_min": "jaccard_min"},
    },
    {
        # DELIBERATE convention, verified 2026-07-22 -- do NOT "fix" this to
        # traverse ENRICHED_BY instead. Reading the mirrored per-building
        # b.osm_match_type is the opposite convention from xsrc_height_disagreement
        # /xsrc_agreement_rate/prov_source_qualified_value (which traverse the
        # {is_primary:true} edge to the OsmFeature), and was flagged during E1/E2
        # as a possible gold-authoring inconsistency. It is not: a building with
        # multiple ENRICHED_BY edges (1:n/n:1/n:m) would be counted once PER EDGE
        # if this aggregated r.match_type instead, badly overcounting exactly the
        # categories this question is about. Empirically confirmed on the live
        # Tokyo graph (2026-07-22): aggregating the per-edge property gives
        # n:1=48,801 / n:m=424,740 vs the true per-building n:1=22,288 /
        # n:m=241,579 (148,930 Tokyo buildings have >1 ENRICHED_BY edge). The
        # opposite convention on the height/value templates is ALSO deliberate,
        # for the opposite reason: there is no double-counting risk there (each
        # row is one building's disagreement, not a case tally), so they prefer
        # the traversal-verified o.osm_height over the mirrored b.osm_height in
        # case the mirror and the current primary-edge selection ever diverge
        # (checked empirically on Tokyo: 0 divergences found in 61,869 buildings,
        # so this is a defensive choice, not a fix for an observed bug). Rule of
        # thumb for future templates: prefer the per-building mirror when the
        # question is a per-building tally/distribution (avoids multi-edge
        # double-counting); prefer the edge traversal when the question needs a
        # specific matched OsmFeature's own value.
        "id": "prov_match_cases",
        "category": "provenance", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How are the OSM-to-cadastre building matches distributed over the correspondence cases (1:1, 1:n, n:1, n:m)?",
            "Break down the buildings by OSM-to-cadastre correspondence case (1:1, 1:n, n:1, n:m).",
            "How many buildings fall into each match-case category (1:1, 1:n, n:1, n:m)?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.osm_match_type IS NOT NULL "
            "RETURN b.osm_match_type AS match_case, count(b) AS n "
            "ORDER BY n DESC, match_case ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "prov_multi_matched",
        "category": "provenance", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings are matched by two or more OSM features?",
            "Count the buildings with two or more OSM correspondences.",
            "How many buildings have at least two matching OSM features?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "prov_only_authoritative",
        "category": "provenance", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "Using only authoritative cadastral data, what is the average building height?",
            "Restricting to authoritative cadastral data only, what is the average building height?",
            "What is the mean building height, considering only the authoritative source?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "prov_source_qualified_value",
        "category": "provenance", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "What is the height of building {dual_height_building} according to each available source?",
            "For building {dual_height_building}, what height does each source report?",
            "What are the authoritative and OSM-reported heights for building {dual_height_building}?",
        ],
        "gold_cypher": (
            "MATCH (b:Building {{id: '{dual_height_building}'}})-[r:ENRICHED_BY {{is_primary: true}}]->(o:OsmFeature) "
            "RETURN b.measured_height AS authoritative_height_m, "
            "toFloat(o.osm_height) AS osm_height_m, r.jaccard AS match_jaccard"
        ),
        "gold_sql": None, "slots": {"dual_height_building": "dual_height_building"},
        "allow_empty": True,
    },
    {
        "id": "prov_weakest_matches",
        "category": "provenance", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "List the {topk} least confident primary OSM matches.",
            "Which {topk} primary OSM matches have the lowest confidence?",
            "What are the {topk} weakest primary correspondences by Jaccard confidence?",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[r:ENRICHED_BY {{is_primary: true}}]->(:OsmFeature) "
            "WHERE r.jaccard IS NOT NULL "
            "RETURN b.id AS id, round(r.jaccard * 1000) / 1000.0 AS jaccard "
            "ORDER BY r.jaccard ASC, b.id ASC LIMIT {topk}"
        ),
        "gold_sql": None, "slots": {"topk": "topk"}, "allow_empty": True,
    },
    {
        "id": "prov_secondary_edges",
        "category": "provenance", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many non-primary correspondence edges does the fusion graph keep?",
            "Count the ENRICHED_BY edges that are not marked as primary.",
            "How many non-primary OSM correspondence edges exist in the graph?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    # ------------------------------------------------------------------ #
    # coverage (Tier 2 — needs the ML-predicted roof-material layer)     #
    # ------------------------------------------------------------------ #
    {
        "id": "cov_share",
        "category": "coverage", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "What share of buildings has a predicted roof material at all?",
            "For what fraction of the buildings is a roof-material prediction available?",
            "What proportion of buildings carry a predicted roof material?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "cov_material_distribution",
        "category": "coverage", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "Show the distribution of predicted roof materials over the buildings that have a prediction.",
            "Among the buildings with a roof-material prediction, break down the materials by count.",
            "For the covered buildings, how many fall into each predicted roof-material class?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "cov_material_avg_height",
        "category": "coverage", "tier": 2, "difficulty": 4, "feasible": True,
        "nl": [
            "What is the average height of buildings with predicted roof material '{material}'? Note that predictions cover only part of the buildings.",
            "Among buildings predicted to have roof material '{material}', what is the average height? (Note: predictions only cover part of the buildings.)",
            "For buildings whose predicted roof material is '{material}', what is the mean measured height? Remember predictions are partial-coverage.",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.predictedroofmaterial = '{material}' "
            "AND b.measured_height > -999 "
            "RETURN round(avg(b.measured_height) * 100) / 100.0 AS avg_height_m, count(b) AS n"
        ),
        "gold_sql": None, "slots": {"material": "material"},
    },
    {
        "id": "cov_trap_citywide",
        "category": "coverage", "tier": 2, "difficulty": 4, "feasible": True,
        "nl": [
            "How many buildings have a predicted '{material}' roof?",
            "Count the buildings predicted to have a '{material}' roof.",
            "How many buildings are classified as having a '{material}' roof by the prediction model?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) "
            "WITH count(b) AS n_total, "
            "count(CASE WHEN b.predictedroofmaterial IS NOT NULL THEN 1 END) AS n_covered, "
            "count(CASE WHEN b.predictedroofmaterial = '{material}' THEN 1 END) AS n_matching "
            "RETURN n_matching, n_covered, n_total, round(1000.0 * n_covered / n_total) / 10.0 AS coverage_pct"
        ),
        "gold_sql": None, "slots": {"material": "material"},
    },
    {
        "id": "cov_by_district",
        "category": "coverage", "tier": 2, "difficulty": 4, "feasible": True,
        "nl": [
            "Report the roof-material prediction coverage per district.",
            "For each district, what is the roof-material prediction coverage?",
            "Break down roof-material prediction coverage by district.",
        ],
        "gold_cypher": (
            "MATCH (b:Building)-[:LOCATED_IN]->(d:District) "
            "WITH d, count(b) AS n_total, "
            "count(CASE WHEN b.predictedroofmaterial IS NOT NULL THEN 1 END) AS n_covered "
            "RETURN d.id AS district, n_covered, n_total, "
            "round(1000.0 * n_covered / n_total) / 10.0 AS coverage_pct "
            "ORDER BY coverage_pct DESC, district ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    # ------------------------------------------------------------------ #
    # lod3 (Tier 2 — Hamburg reconstructed facade/interior showcase)     #
    # self-gates: the lod3_building/room_building providers are empty on #
    # every city without the layer, so these templates instantiate only  #
    # on Hamburg.                                                        #
    # ------------------------------------------------------------------ #
    {
        "id": "lod3_window_count",
        "category": "lod3", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "How many windows does building {lod3_building} have?",
            "Count the windows recorded for building {lod3_building}.",
            "How many window openings does building {lod3_building}'s LoD3 facade have?",
        ],
        "gold_cypher": (
            "MATCH (:Building {{id: '{lod3_building}'}})-[:HAS_LOD3_FACADE]->(:BoundarySurface)"
            "-[:HAS_OPENING]->(o:Opening {{opening_type: 'Window'}}) "
            "RETURN count(o) AS n"
        ),
        "gold_sql": None, "slots": {"lod3_building": "lod3_building"},
    },
    {
        "id": "lod3_door_count",
        "category": "lod3", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "How many doors does building {lod3_building} have?",
            "Count the doors recorded for building {lod3_building}.",
            "How many door openings does building {lod3_building}'s LoD3 facade have?",
        ],
        "gold_cypher": (
            "MATCH (:Building {{id: '{lod3_building}'}})-[:HAS_LOD3_FACADE]->(:BoundarySurface)"
            "-[:HAS_OPENING]->(o:Opening {{opening_type: 'Door'}}) "
            "RETURN count(o) AS n"
        ),
        "gold_sql": None, "slots": {"lod3_building": "lod3_building"},
    },
    {
        "id": "lod3_openings_per_wall",
        "category": "lod3", "tier": 2, "difficulty": 5, "feasible": True,
        "nl": [
            "Which wall of building {lod3_building} has the most openings?",
            "For building {lod3_building}, which wall surface has the greatest number of openings?",
            "What is the wall of building {lod3_building} with the highest opening count?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {"lod3_building": "lod3_building"}, "allow_empty": True,
    },
    {
        "id": "lod3_room_count",
        "category": "lod3", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "How many rooms does building {room_building} contain?",
            "Count the rooms recorded for building {room_building}.",
            "How many interior rooms does building {room_building} have?",
        ],
        "gold_cypher": (
            "MATCH (:Building {{id: '{room_building}'}})-[:HAS_INTERIOR_ROOM]->(r:Room) "
            "RETURN count(r) AS n"
        ),
        "gold_sql": None, "slots": {"room_building": "room_building"},
    },
    # ------------------------------------------------------------------ #
    # infeasible (Tier 1) — gold behaviour is REFUSE; guard proves the   #
    # referenced information is really absent from the graph             #
    # ------------------------------------------------------------------ #
    {
        "id": "inf_renovation_year",
        "category": "infeasible", "tier": 1, "difficulty": 3, "feasible": False,
        "nl": [
            "In which year was each building last renovated?",
            "List the most recent renovation year per building.",
            "What was the last renovation year for each building?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {},
        "guard": (
            "MATCH (b:Building) WHERE b.renovation_year IS NOT NULL "
            "RETURN count(b) AS n"
        ),
    },
    {
        "id": "inf_energy_class",
        "category": "infeasible", "tier": 1, "difficulty": 3, "feasible": False,
        "nl": [
            "How many buildings have energy efficiency class A?",
            "Show the distribution of energy certificates across buildings.",
            "What energy efficiency class is recorded for each building?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {},
        "guard": (
            "MATCH (b:Building) WHERE b.energy_class IS NOT NULL "
            "RETURN count(b) AS n"
        ),
    },
    {
        "id": "inf_residents",
        "category": "infeasible", "tier": 1, "difficulty": 3, "feasible": False,
        "nl": [
            "How many people live in each building?",
            "What is the resident count per building?",
            "How many residents live in each building?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {},
        "guard": (
            "MATCH (b:Building) WHERE b.resident_count IS NOT NULL "
            "RETURN count(b) AS n"
        ),
    },
    {
        # NOTE: on Hamburg this same NL is FEASIBLE (see cov_* above) — the
        # guard checks citywide layer presence, so on Hamburg it will fail
        # to prove absence (n > 0) and the question is correctly dropped by
        # the verification gate there. That contrast (feasible on Hamburg,
        # infeasible on the other four cities) is deliberate — see
        # QUESTION_SUITE_DESIGN.md §4.9 (inf_layer_absent_city).
        "id": "inf_layer_absent_city",
        "category": "infeasible", "tier": 1, "difficulty": 4, "feasible": False,
        "nl": [
            "What roof material is predicted for building {any_building}?",
            "According to the ML prediction, what roof material does building {any_building} have?",
            "What is the predicted roof material of building {any_building}?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {"any_building": "any_building"},
        "guard": (
            "<withheld: gold query of a held-out test template>"
        ),
    },
    {
        # Mirror of lod3_room_count — same NL, guard proves no LoD3/4
        # interior data exists citywide. Feasible only on Hamburg (dropped
        # there by the verification gate, symmetric to inf_layer_absent_city).
        "id": "inf_interior_lod",
        "category": "infeasible", "tier": 1, "difficulty": 4, "feasible": False,
        "nl": [
            "How many rooms does building {any_building} have?",
            "Count the rooms in building {any_building}.",
            "How many interior rooms are recorded for building {any_building}?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {"any_building": "any_building"},
        "guard": (
            "<withheld: gold query of a held-out test template>"
        ),
    },
    {
        "id": "inf_false_premise",
        "category": "infeasible", "tier": 1, "difficulty": 3, "feasible": False,
        "nl": [
            "How many buildings are in the district '{fake_district}'?",
            "Count the buildings located in the district '{fake_district}'.",
            "How many buildings does the district '{fake_district}' contain?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {"fake_district": "fake_district"},
        "guard": (
            "MATCH (d:District {{id: '{fake_district}'}}) RETURN count(d) AS n"
        ),
    },
    {
        "id": "inf_temporal",
        "category": "infeasible", "tier": 1, "difficulty": 3, "feasible": False,
        "nl": [
            "How much did the average building height change between 2020 and 2024?",
            "Between 2020 and 2024, how did the average building height change?",
            "What was the change in mean building height from 2020 to 2024?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {},
        "guard": (
            "MATCH (ds:Dataset) WHERE ds.snapshot_year IS NOT NULL OR ds.version_year IS NOT NULL "
            "RETURN count(ds) AS n"
        ),
    },
    {
        "id": "inf_owner",
        "category": "infeasible", "tier": 1, "difficulty": 3, "feasible": False,
        "nl": [
            "Who owns building {any_building}?",
            "Who is the owner of building {any_building}?",
            "Which person or entity owns building {any_building}?",
        ],
        "gold_cypher": None, "gold_sql": None, "slots": {"any_building": "any_building"},
        "guard": (
            "MATCH (b:Building) WHERE b.owner IS NOT NULL RETURN count(b) AS n"
        ),
    },
    # ------------------------------------------------------------------ #
    # multilingual schema-bridging (Tokyo only) — the gold query itself   #
    # must use Japanese property keys; self-gates via jp_district_plan    #
    # (empty on every non-Tokyo city).                                   #
    # ------------------------------------------------------------------ #
    {
        "id": "tokyo_jp_key_lookup",
        "category": "multihop", "tier": 1, "difficulty": 4, "feasible": True,
        # the Japanese phrasing lives in LANG_VARIANTS (lang="ja"), not here --
        # this "nl" list is the 3 accepted ENGLISH paraphrases (policy §7).
        "nl": [
            "Which buildings belong to the district plan '{jp_district_plan}'?",
            "List the buildings that are part of the district plan '{jp_district_plan}'.",
            "What buildings fall under the district plan '{jp_district_plan}'?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.`地区計画` = '{jp_district_plan}' "
            "RETURN b.id AS id ORDER BY b.id"
        ),
        "gold_sql": None, "slots": {"jp_district_plan": "jp_district_plan"}, "allow_empty": True,
    },
    {
        "id": "tokyo_jp_key_distribution",
        "category": "multihop", "tier": 1, "difficulty": 4, "feasible": True,
        # the Japanese phrasing lives in LANG_VARIANTS (lang="ja").
        "nl": [
            "How many buildings are there per district plan?",
            "Break down the number of buildings by district plan.",
            "For each district plan, how many buildings belong to it?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.`地区計画` IS NOT NULL "
            "RETURN b.`地区計画` AS district_plan, count(b) AS n ORDER BY n DESC, district_plan ASC"
        ),
        # unlike tokyo_jp_key_lookup this has no slot to self-gate on, so on
        # every non-Tokyo city it legitimately returns zero groups
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "tokyo_jp_numeric_attr",
        "category": "aggregate", "tier": 1, "difficulty": 4, "feasible": True,
        # the Japanese phrasing lives in LANG_VARIANTS (lang="ja").
        "nl": [
            "What is the average floor-area conversion factor across buildings?",
            "On average, what value does the floor-area conversion factor take across buildings?",
            "What is the mean floor-area conversion factor recorded for the buildings?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"        ),
        "gold_sql": None, "slots": {},
    },
    # ------------------------------------------------------------------ #
    # Per-city native-content pass (added 2026-07-19). Found by cross-    #
    # referencing tex/current/tables/<city>_content_metrics.json against #
    # this file: significant thematic properties with real per-city      #
    # coverage that no template touched. All self-gate via WHERE ... IS  #
    # NOT NULL / a presence-checking provider — no explicit city         #
    # allowlist needed. See KDD_PAPER_NOTES.md step B7 and               #
    # bench/QUESTION_SUITE_DESIGN.md §4.11 for the rationale per item.   #
    # ------------------------------------------------------------------ #
    {
        # addr_* lands on Building via OSM SHARED_THEMATIC copy-through
        # (ingest_osm.py); present across Hamburg/Zurich/Helsinki/NYC at
        # varying coverage but never previously queried.
        "id": "xsrc_addr_coverage",
        "category": "cross_source", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "For how many buildings is a street address known?",
            "How many buildings have a recorded street address?",
            "Count the buildings for which a street address is available.",
        ],
        "gold_cypher": (
            "MATCH (b:Building) "
            "WITH count(b) AS total, count(b.addr_street) AS with_addr "
            "RETURN with_addr, total, round(1000.0 * with_addr / total) / 10.0 AS coverage_pct"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "xsrc_buildings_by_street",
        "category": "cross_source", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "Which buildings are on street '{street_name}'?",
            "List the buildings located on '{street_name}'.",
            "Which buildings have their address on the street '{street_name}'?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.addr_street = '{street_name}' "
            "RETURN b.id AS id ORDER BY b.id"
        ),
        "gold_sql": None, "slots": {"street_name": "street_name"},
    },
    {
        # Deliberately NOT a semantic-agreement check: osm_roof_shape
        # (free-text OSM tags, e.g. "gabled") and roof_type_code/RoofType.name
        # (ALKIS-coded vocabulary) use different vocabularies with no
        # existing fold-mapping in this project (unlike roof MATERIAL, which
        # bench/osm_citygml_conflict_analysis.py does fold) -- a naive string
        # equality would misreport near-total "disagreement" as a vocabulary
        # artifact, not a real finding. This asks the honest, defensible
        # question: how often is roof shape independently reported by BOTH
        # sources at all (dual-reporting coverage), not whether they agree.
        "id": "xsrc_dual_roof_reporting",
        "category": "cross_source", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings have both an authoritative roof type and a crowd-sourced OSM roof shape recorded?",
            "Count the buildings for which both an authoritative roof type and an OSM roof shape are recorded.",
            "How many buildings have a roof type on record from the cadastre as well as a roof shape from OSM?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.roof_type_code IS NOT NULL AND b.osm_roof_shape IS NOT NULL "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        # Reads the pre-computed LoD3 reconstruction-confidence scalar
        # directly (Hamburg only) instead of the graph traversal the other
        # lod3_* templates use -- this is the paper's own confidence-carrying
        # provenance thesis, applied to its own reconstructed layer, and was
        # sitting unused.
        "id": "prov_lod3_confidence",
        "category": "provenance", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the reconstruction confidence and method for building {lod3_building}'s LoD3 facade?",
            "For building {lod3_building}, what confidence and method were used to reconstruct its LoD3 facade?",
            "What reconstruction method and confidence value apply to building {lod3_building}'s LoD3 facade?",
        ],
        "gold_cypher": (
            "MATCH (b:Building {{id: '{lod3_building}'}}) WHERE b.lod3_confidence IS NOT NULL "
            "RETURN b.lod3_confidence AS confidence, b.lod3_method AS method, b.lod3_source AS source"
        ),
        "gold_sql": None, "slots": {"lod3_building": "lod3_building"},
    },
    {
        "id": "prov_lod3_high_confidence_count",
        "category": "provenance", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "How many LoD3-reconstructed buildings have a reconstruction confidence of at least {confidence_threshold}?",
            "Count the LoD3-reconstructed buildings whose confidence is {confidence_threshold} or higher.",
            "How many buildings have an LoD3 reconstruction confidence at or above {confidence_threshold}?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.lod3_confidence >= {confidence_threshold} "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {"confidence_threshold": "confidence_threshold"},
    },
    {
        # predicted_roof_material_count already stores this directly;
        # the multi-material tail (Hamburg: 570 buildings w/ 2, 26 w/ 3) was
        # never asked about despite being exactly the kind of confidence/
        # coverage nuance the coverage category exists to test.
        "id": "cov_multi_material_count",
        "category": "coverage", "tier": 2, "difficulty": 3, "feasible": True,
        "nl": [
            "How many buildings have more than one predicted roof material?",
            "Count the buildings with more than one predicted roof-material class.",
            "How many buildings were predicted to have multiple roof materials?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.predicted_roof_material_count >= 2 "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        # Structural fix for a real blind spot: every OTHER cross_source
        # template requires a real authoritative height (b.measured_height
        # > -999), which silently excludes exactly NYC's most interesting
        # case (97.5% OSM height coverage, 0% authoritative height -- OSM is
        # not a supplement there, it is the only height signal at all).
        # Cross-city by construction: returns real rows on NYC, and on any
        # other city with a partial gap between the two coverages (e.g.
        # Hamburg's 3,460 osm_height records don't all overlap
        # measured_height). "No authoritative height" includes both a NULL
        # measured_height and the -9999 missing-value sentinel (Tokyo), so
        # the sentinel is treated as missing here too, mirroring the > -999
        # guard the aggregating templates use.
        "id": "xsrc_osm_only_height_stats",
        "category": "cross_source", "tier": 1, "difficulty": 4, "feasible": True,
        "nl": [
            "For buildings with no authoritative height on record, what does OpenStreetMap alone report as the average height?",
            "Among buildings lacking an authoritative height, what average height does OpenStreetMap alone report?",
            "For buildings with no surveyed height, what is the mean OSM-reported height?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE (b.measured_height IS NULL OR b.measured_height <= -999) "
            "AND b.osm_height IS NOT NULL "
            "RETURN round(avg(toFloat(b.osm_height)) * 100) / 100.0 AS avg_osm_height_m, count(b) AS n"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        # storeys_below_ground is populated for every Tokyo building
        # (bldg:storeysBelowGround) but no template ever read it -- only
        # storeys_above_ground was queried anywhere.
        "id": "filter_has_basement",
        "category": "filter_topk", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many buildings have at least one storey below ground?",
            "Count the buildings that have one or more below-ground storeys.",
            "How many buildings report a basement, i.e. at least one storey below ground?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.storeys_below_ground IS NOT NULL "
            "AND b.storeys_below_ground >= 1 RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        # Tokyo-only (self-gates: `町_丁目コード` empty elsewhere). Extends
        # the multilingual schema-bridging axis beyond the 2 templates that
        # already used 地区計画/延べ面積換算係数 -- Tokyo carries several more
        # substantial Japanese-keyed fields that were unused.
        "id": "multihop_jp_town_code_top",
        "category": "multihop", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "Which 10 town/block codes (町丁目コード) have the most buildings?",
            "What are the top 10 town/block codes (町丁目コード) by building count?",
            "List the 10 town/block codes (町丁目コード) with the highest number of buildings.",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.`町_丁目コード` IS NOT NULL "
            "RETURN b.`町_丁目コード` AS town_code, count(b) AS n "
            "ORDER BY n DESC, town_code ASC LIMIT 10"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "filter_redevelopment_district",
        "category": "filter_topk", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many buildings belong to a legally-designated redevelopment-promotion district plan (再開発等促進区を定める地区計画)?",
            "Count the buildings that belong to a redevelopment-promotion district plan (再開発等促進区を定める地区計画).",
            "How many buildings are recorded as part of a legally-designated redevelopment-promotion district plan?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.`再開発等促進区を定める地区計画` IS NOT NULL "
            "RETURN count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        # Helsinki-only (self-gates: `kerrosala` empty elsewhere). Helsinki
        # is the attribute-richest city (median 43 source keys/building,
        # CITY_CONTENT_TABLES.md) but almost none of its ~30 native Finnish
        # cadastral fields had a template -- this and the next three add the
        # highest-value ones (floor area, construction year, material,
        # integration method).
        "id": "agg_helsinki_avg_floor_area",
        "category": "aggregate", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the average total floor area (kerrosala) of the buildings, in square meters?",
            "On average, how much total floor area (kerrosala) do the buildings have, in square meters?",
            "What is the mean floor area, in square meters, recorded as kerrosala for the buildings?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.kerrosala IS NOT NULL "
            "RETURN round(avg(toFloat(b.kerrosala)) * 100) / 100.0 AS avg_floor_area_m2, count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "agg_helsinki_avg_year_built",
        "category": "aggregate", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the average construction year (valmistunut) of the buildings?",
            "On average, in what year (valmistunut) were the buildings constructed?",
            "What is the mean construction year recorded as valmistunut across the buildings?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.valmistunut IS NOT NULL "
            "RETURN round(avg(toInteger(b.valmistunut))) AS avg_year_built, count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        "id": "multihop_helsinki_material_distribution",
        "category": "multihop", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "What is the distribution of building materials (rakennusaine) across buildings?",
            "Break down the buildings by building material (rakennusaine).",
            "How many buildings are there per recorded building material (rakennusaine)?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        # Verified live on Helsinki 2026-07-22 (freeze top-up; gold_answer
        # avg_storeys=3.65, max=17, n=1931). Helsinki's NATIVE storey count.
        # The cross-city storey templates read storeys_above_ground, which
        # Helsinki carries on only 92 buildings; its real storey field
        # `kerroksia` covers 1,931 -- the SAME concept in a different native
        # field, i.e. the paper's schema-heterogeneity point.
        "id": "agg_helsinki_avg_storeys",
        "category": "aggregate", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the average number of storeys (kerroksia) of the buildings, and how many buildings report it?",
            "On average, how many storeys (kerroksia) do the buildings have, and for how many buildings is this recorded?",
            "What is the mean storey count (kerroksia) across the buildings, and how many report a value?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        # Verified live on Helsinki 2026-07-22 (freeze top-up; gold_answer
        # avg_volume_m3=12823.16, n=1743). Native building volume, a thematic
        # dimension no other city reports, distinct from floor area (kerrosala)
        # already covered.
        "id": "agg_helsinki_avg_volume",
        "category": "aggregate", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the average building volume (tilavuus) in cubic metres, and how many buildings report it?",
            "On average, what is the recorded building volume (tilavuus) in cubic metres, and how many buildings have a value?",
            "What is the mean volume in cubic metres (tilavuus) for the buildings that report one?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.tilavuus IS NOT NULL "
            "RETURN round(avg(toFloat(b.tilavuus)) * 100) / 100.0 AS avg_volume_m3, count(b) AS n"
        ),
        "gold_sql": None, "slots": {},
    },
    {
        # A second, distinct provenance axis: Helsinki's OWN pre-existing
        # record-linkage metadata from before pykci ever touched the data
        # (matching_mode/integration_date/overlap_* -- "provenance about a
        # prior provenance"), separate from pykci's OSM ENRICHED_BY fusion.
        # NOTE (verified live 2026-07-22): on this graph matching_mode is a
        # single constant value ('1', n=2846), as are the co-occurring
        # overlap_db_to_file/overlap_file_to_db (100) and area_diff (0) --
        # apparently one integration batch recording one outcome. A dedicated
        # match-quality template on the overlap fields was tried and dropped
        # for being a degenerate duplicate of this template's count (see
        # multihop_helsinki_building_status below for what replaced it).
        "id": "prov_helsinki_integration_method",
        "category": "provenance", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "How are the buildings distributed across the data-matching methods (matching_mode) used during their source integration?",
            "Break down the buildings by data-matching method (matching_mode) used at source integration.",
            "For each integration matching_mode, how many buildings were processed with it?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.matching_mode IS NOT NULL "
            "RETURN b.matching_mode AS matching_mode, count(b) AS n ORDER BY n DESC, matching_mode ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        # Verified live on Helsinki 2026-07-22 (freeze top-up). Not a provenance
        # axis after all: `matching_mode`/`overlap_db_to_file`/`overlap_file_to_db`/
        # `area_diff` turned out to be a SINGLE constant batch (matching_mode='1',
        # overlap=100, area_diff=0 for all 2,846 buildings that carry them --
        # verified via live distinct-value counts, not assumed), so a
        # match-quality template on those fields would be a degenerate "average
        # of a constant" duplicating prov_helsinki_integration_method's count
        # with no new information. `rakennuksen_tila` (building lifecycle
        # status), by contrast, has real variance (4 values, live-verified
        # distribution 1921/245/8/2) and standard, unambiguous terminology
        # (active/planned/under construction/demolished), so it replaced the
        # match-quality template as the third native addition.
        "id": "multihop_helsinki_building_status",
        "category": "multihop", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "What is the distribution of building lifecycle status (rakennuksen_tila) across buildings, e.g. active, planned, under construction, or demolished?",
            "Break down the buildings by lifecycle status (rakennuksen_tila) -- active, planned, under construction, or demolished.",
            "How many buildings fall into each lifecycle status (rakennuksen_tila) category?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        # Zurich-only (self-gates: `herkunft_jahr` empty elsewhere). A THIRD
        # distinct provenance axis: swissBUILDINGS3D's own native data-vintage/
        # lineage fields (herkunft = "origin" in German) -- record-level
        # source-year metadata that pykci's own ENRICHED_BY provenance model
        # does not capture, on-thesis for the paper and previously unused.
        "id": "prov_zurich_data_vintage",
        "category": "provenance", "tier": 1, "difficulty": 3, "feasible": True,
        "nl": [
            "What is the distribution of source survey years (herkunft_jahr) across the buildings?",
            "Break down the buildings by source survey year (herkunft_jahr).",
            "How many buildings does each recorded survey year (herkunft_jahr) have?",
        ],
        "gold_cypher": (
            "MATCH (b:Building) WHERE b.herkunft_jahr IS NOT NULL "
            "RETURN b.herkunft_jahr AS source_year, count(b) AS n ORDER BY n DESC, source_year ASC"
        ),
        "gold_sql": None, "slots": {}, "allow_empty": True,
    },
    {
        "id": "prov_zurich_revised_count",
        "category": "provenance", "tier": 1, "difficulty": 2, "feasible": True,
        "nl": [
            "How many buildings have a recorded reason for revision (grund_aenderung), i.e. were updated at least once?",
            "Count the buildings with a recorded revision reason (grund_aenderung).",
            "For how many buildings is a reason for revision (grund_aenderung) on record?",
        ],
        "gold_cypher": (
            "<withheld: gold query of a held-out test template>"
        ),
        "gold_sql": None, "slots": {},
    },
]

# ==========================================================================
# Multilingual dimension (QUESTION_SUITE_DESIGN.md §4.10 / §7).
# --------------------------------------------------------------------------
# Two DISTINCT mechanisms, both surfaced through this one dict and tagged via
# the `lang` field on the emitted question record (generate_questions.py):
#
# 1. Language VARIANTS -- a translation, not a paraphrase, of a template
#    that is otherwise identical across languages: same slots, same gold
#    query (gold is language-independent; only the NL asking for it changes).
#    The 10 designated templates below are the 2 lowest-difficulty templates
#    per category from aggregate/filter_topk/multihop/spatial/cross_source
#    (the cross-city-safe "common attribute subset" categories, §6) that are
#    ALSO answerable on all 5 cities per the REQUIRES gate -- verified live:
#    an initial pick of the literal 2-easiest-by-difficulty-number
#    (multihop_rooftype_distribution, xsrc_addr_coverage) turned out to be
#    gated OUT on Tokyo (no RoofType/HAS_ROOF_TYPE, no OSM-copied
#    addr_street there), which would have made their Japanese translation
#    permanently inert; swapped for multihop_boundary_census and
#    xsrc_unenriched_gap, confirmed to fire on Tokyo. Each gets a German
#    translation (instantiated on all 5 cities) and, since Tokyo is the
#    project's non-Latin-schema city, also a Japanese translation
#    (instantiated on Tokyo only).
# 2. Schema-BRIDGING templates (the 3 tokyo_jp_* templates above) -- these
#    are Tokyo-specific to begin with (cross_city: false, the gold query
#    itself indexes a Japanese property key), so only a Japanese variant is
#    added here; their 3 accepted "nl" paraphrases stay English-only.
#
# Translations are LLM-authored (this file), not yet independently verified
# by a native/fluent speaker -- exactly the documented fallback in §4.10
# ("LLM translation + back-translation check + mark as such in the
# datasheet") pending author review. Every {slot} placeholder below was
# checked to match the owning template's declared `slots` exactly (same
# programmatic check used for the paraphrase expansion, §7) before this dict
# was wired into the generator.
LANG_VARIANTS = {
    # ---- 10 designated cross-city templates: de (all cities) + ja (Tokyo) ----
    "agg_count_buildings": {
        "de": "Wie viele Gebäude enthält der Datensatz?",
        "ja": "このデータセットには建物が何棟含まれていますか。",
    },
    "agg_avg_height": {
        "de": "Wie hoch sind die Gebäude im Durchschnitt, in Metern?",
        "ja": "建物の平均的な高さ（メートル）はどれくらいですか。",
    },
    "filter_taller_than": {
        "de": "Wie viele Gebäude sind höher als {height_threshold} Meter?",
        "ja": "高さが{height_threshold}メートルを超える建物は何棟ありますか。",
    },
    "topk_tallest": {
        "de": "Nennen Sie die {topk} höchsten Gebäude mit ihren Höhen.",
        "ja": "最も高い建物を{topk}棟、その高さとともに挙げてください。",
    },
    "multihop_boundary_census": {
        "de": "Wie viele Grenzflächen jedes Typs hat Gebäude {any_building}?",
        "ja": "建物{any_building}には、種類ごとにいくつの境界面がありますか。",
    },
    "multihop_district_counts": {
        "de": "Wie viele Gebäude befinden sich in jedem Stadtbezirk?",
        "ja": "各地区にはそれぞれ何棟の建物がありますか。",
    },
    "spatial_bbox_count": {
        "de": "Wie viele Gebäude liegen innerhalb des Suchfensters {bbox_wkt}?",
        "ja": "境界ボックス{bbox_wkt}の内側にある建物は何棟ですか。",
    },
    "spatial_neighbours": {
        "de": "Wie viele Gebäude stehen innerhalb von 100 Metern um Gebäude {nearby_building}?",
        "ja": "建物{nearby_building}から100メートル以内にある建物は何棟ですか。",
    },
    "xsrc_name_lookup": {
        "de": "Wie lautet der OSM-Name des Gebäudes {named_osm_building}?",
        "ja": "建物{named_osm_building}のOSM上の名称は何ですか。",
    },
    "xsrc_unenriched_gap": {
        "de": "Wie viele Gebäude haben überhaupt kein Gegenstück in OpenStreetMap?",
        "ja": "OpenStreetMapに対応する地物が全くない建物は何棟ありますか。",
    },
    # ---- Tokyo schema-bridging templates: ja only (English stays in "nl") ----
    "tokyo_jp_key_lookup": {
        "ja": "地区計画『{jp_district_plan}』に属する建物はどれですか。",
    },
    "tokyo_jp_key_distribution": {
        "ja": "地区計画ごとの建物数を教えてください。",
    },
    "tokyo_jp_numeric_attr": {
        "ja": "建物の延べ面積換算係数の平均値はいくらですか。",
    },
}

# ==========================================================================
# Per-city requirement gate (v1.0 freeze).
# --------------------------------------------------------------------------
# Not every feasible template is answerable on every city: a city's source may
# carry no authoritative height (New York), no storey / function / roof-type
# classification (Zurich, New York, Tokyo), no ML roof-material layer or LoD3
# facades (everywhere but Hamburg), or a native attribute unique to one source
# (Helsinki `kerrosala`, Zurich `herkunft_jahr`, Tokyo `地区計画` ...). A
# template whose gold query reads such a token would otherwise instantiate an
# UNANSWERABLE question on the cities that lack it -- exactly the leak the eval
# runs had to remove by hand, city by city, in the (non-reproducible)
# questions_<city>_*_contextfair.jsonl files.
#
# REQUIRES declares, per template, the graph tokens its gold query presupposes.
# The generator (generate_questions.py) instantiates a template on a city ONLY
# when that city's live graph satisfies every requirement, so generation is
# deterministic and identical for anyone who reruns it -- the precondition for
# the paper's "fixed splits" claim. Feasible templates not listed here have no
# city-varying dependency and instantiate everywhere.
#
# Cities that lack a requirement still exercise the SAME kind of question, and
# the refusal behaviour, through the generic infeasible templates
# (inf_layer_absent_city, inf_interior_lod), whose guard proves the layer is
# absent -- so no per-template infeasible mirror is needed here.
#
# Token kind is inferred from the name:
#   ALL_UPPER  -> relationship type   (HAS_FUNCTION, HAS_ROOF_TYPE, ...)
#   CamelCase  -> node label          (RoofType, BuildingFunction, Room, ...)
#   otherwise  -> Building property    (measured_height, addr_street, 地区計画)
#
# A property used ONLY inside `IS NULL` (a question ABOUT absence) is NOT a
# requirement -- so xsrc_osm_only_height_stats (New York's OSM-only-height
# showcase: `measured_height IS NULL AND osm_height IS NOT NULL`) is absent
# below on purpose. filter_missing_height IS listed: its whole answer is the
# measured_height property, so it is gated to cities where that property exists.
#
# Derived 2026-07-22 by auditing every gold_cypher against the measured
# per-city building_key_histogram in tex/current/tables/<city>_content_metrics.json.
REQUIRES = {
    "agg_avg_height": ["measured_height"],
    "agg_helsinki_avg_floor_area": ["kerrosala"],
    "agg_helsinki_avg_storeys": ["kerroksia"],
    "agg_helsinki_avg_volume": ["tilavuus"],
    "agg_helsinki_avg_year_built": ["valmistunut"],
    "agg_max_storeys": ["storeys_above_ground"],
    "agg_median_height": ["measured_height"],
    "cov_by_district": ["predictedroofmaterial"],
    "cov_material_avg_height": ["measured_height", "predictedroofmaterial"],
    "cov_material_distribution": ["predictedroofmaterial"],
    "cov_multi_material_count": ["predicted_roof_material_count"],
    "cov_share": ["predictedroofmaterial"],
    "cov_trap_citywide": ["predictedroofmaterial"],
    "filter_by_function": ["BuildingFunction", "HAS_FUNCTION"],
    "filter_compound": ["HAS_ROOF_TYPE", "RoofType", "measured_height"],
    "filter_has_basement": ["storeys_below_ground"],
    "filter_missing_height": ["measured_height"],
    "filter_redevelopment_district": ["再開発等促進区を定める地区計画"],
    "filter_taller_than": ["measured_height"],
    "lod3_door_count": ["HAS_LOD3_FACADE"],
    "lod3_openings_per_wall": ["HAS_LOD3_FACADE"],
    "lod3_room_count": ["HAS_INTERIOR_ROOM", "Room"],
    "lod3_window_count": ["HAS_LOD3_FACADE"],
    "multihop_district_top_function": ["BuildingFunction", "HAS_FUNCTION"],
    "multihop_function_avg_height": ["BuildingFunction", "HAS_FUNCTION", "measured_height"],
    "multihop_building_parts": ["HAS_BUILDING_PART", "BuildingPart"],
    "multihop_helsinki_building_status": ["rakennuksen_tila"],
    "multihop_helsinki_material_distribution": ["rakennusaine"],
    "multihop_jp_town_code_top": ["町_丁目コード"],
    "multihop_rooftype_distribution": ["HAS_ROOF_TYPE", "RoofType"],
    "prov_helsinki_integration_method": ["matching_mode"],
    "prov_lod3_confidence": ["lod3_confidence", "lod3_method", "lod3_source"],
    "prov_lod3_high_confidence_count": ["lod3_confidence"],
    "prov_only_authoritative": ["measured_height"],
    "prov_source_qualified_value": ["measured_height"],
    "prov_zurich_data_vintage": ["herkunft_jahr"],
    "prov_zurich_revised_count": ["grund_aenderung"],
    "tokyo_jp_key_distribution": ["地区計画"],
    "tokyo_jp_key_lookup": ["地区計画"],
    "tokyo_jp_numeric_attr": ["延べ面積換算係数"],
    "spatial_bbox_agg": ["measured_height"],
    "spatial_bbox_by_rooftype": ["HAS_ROOF_TYPE", "RoofType"],
    "spatial_bbox_tallest": ["measured_height"],
    "spatial_near_amenity_tallest": ["measured_height"],
    "topk_most_storeys": ["storeys_above_ground"],
    "topk_tallest": ["measured_height"],
    "xsrc_addr_coverage": ["addr_street"],
    "xsrc_agreement_rate": ["measured_height"],
    "xsrc_buildings_by_street": ["addr_street"],
    "xsrc_dual_roof_reporting": ["roof_type_code"],
    "xsrc_height_disagreement": ["measured_height"],
    "xsrc_levels_vs_storeys": ["storeys_above_ground"],
    "xsrc_mean_abs_deviation": ["measured_height"],
}


def _token_kind(tok):
    """Classify a REQUIRES token by name: relationship / label / property."""
    if tok.isupper():          # HAS_FUNCTION, HAS_ROOF_TYPE, HAS_LOD3_FACADE ...
        return "edge"
    if tok[:1].isupper():      # RoofType, BuildingFunction, Room, Lod3Facade ...
        return "label"
    return "prop"              # measured_height, addr_street, 地区計画, ...


def graph_presence(sess):
    """Probe a live graph for exactly the tokens REQUIRES cares about.

    Returns (present_props, present_labels, present_edges) as sets. Each probe
    is a `LIMIT 1` existence check (cheap even on the 2M-building graphs) and,
    crucially, tests actual node/edge PRESENCE rather than db.labels() /
    db.relationshipTypes(), which can still list a label whose nodes were all
    deleted. Building-property presence is IS NOT NULL on a Building.
    """
    props, labels, edges = set(), set(), set()
    for tok in {t for toks in REQUIRES.values() for t in toks}:
        kind = _token_kind(tok)
        if kind == "prop":
            q = "MATCH (b:Building) WHERE b.`%s` IS NOT NULL RETURN 1 AS x LIMIT 1" % tok
            if sess.run(q).single() is not None:
                props.add(tok)
        elif kind == "label":
            if sess.run("MATCH (n:`%s`) RETURN 1 AS x LIMIT 1" % tok).single() is not None:
                labels.add(tok)
        else:
            if sess.run("MATCH ()-[r:`%s`]->() RETURN 1 AS x LIMIT 1" % tok).single() is not None:
                edges.add(tok)
    return props, labels, edges


def satisfies_requirements(template_id, present_props, present_labels, present_edges):
    """True if every REQUIRES token of the template is present in the graph."""
    for tok in REQUIRES.get(template_id, []):
        kind = _token_kind(tok)
        if kind == "edge" and tok not in present_edges:
            return False
        if kind == "label" and tok not in present_labels:
            return False
        if kind == "prop" and tok not in present_props:
            return False
    return True
