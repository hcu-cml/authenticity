# Limitations

Stated plainly, because a benchmark is only useful if its boundaries are known. Nothing here is a defect to be fixed before use; each item is a property of the dataset that changes how a result should be interpreted.

## Coverage and scope

**Five cities, three continents, one deep-fusion city.** All four provenance layers exist for Hamburg only. Helsinki, Zurich, New York, and Tokyo carry the authoritative layer plus whole-city OSM fusion. Findings may not transfer to regions with different cadastral traditions or different OpenStreetMap community density. The binding constraint on the ML-predicted layer is availability of inference imagery, not of code.

**Uneven attribute coverage across cities, by source design.** Roof type exists in two of five cities, cadastral building function in one, storey counts in three. New York's source model carries no authoritative height at all. A result reported only on the best-covered city would misrepresent the corpus, which is why per-city numbers are released rather than a single average.

**Release extents differ by more than an order of magnitude.** Helsinki is an inner-city core (14 km², 2,980 buildings); Hamburg's bounding box spans a federal state (7,117 km²); Zurich is a canton-wide tile scatter. Cross-city comparisons of absolute counts compare release boundaries as much as cities.

**Source vintages span 2016 to 2025 and are not harmonized.** Each city's graph reflects its own source date. Comparing building stock across cities compares differently dated snapshots.

**Tokyo is scoped to the PLATEAU B-core modules** (`bldg`, `tran`, `brid`, `frn`, `veg`, `wtr`) and is predominantly LoD1. Land use, terrain, underground structures, and the PLATEAU ADE extensions are excluded by design.

## Data properties that will surprise a naive query

**Source sentinels are preserved, not repaired.** Tokyo uses `-9999` for missing `measuredHeight` (36,071 buildings) and `9999` for storey counts (225,776 buildings, 11.3 % of the city, equal to the column maximum). Under the lossless-ingest principle these are stored verbatim. Any aggregate over height or storeys on Tokyo must exclude them; the benchmark's gold queries guard height aggregates with `> -999`, and the storey templates deliberately do not, with the caveat documented. A model that returns the sentinel as "the tallest building" is reproducing the data faithfully and failing the question.

**Upstream encoding damage is preserved.** The Helsinki export carries corrupted Finnish diacritics (1,490 Unicode replacement characters across 283 values). The integrity gates confirm we preserved them faithfully; we did not attempt to guess the intended characters.

**No materialized proximity edges.** Building-to-building proximity edges explode edge counts at city scale and slow both ingest and query, so they are opt-in in the pipeline and off in every released graph. Proximity must be answered at query time through the R-tree layers and centroid distances. This is deliberate and uniform across cities.

**Per-city coordinate reference systems.** There is no single global CRS. Every metric computation must use the city's own CRS, and the R-tree layers store Cartesian metres, which is not what a geographic-layer spatial procedure assumes. This exact mismatch produced a gold-query defect during construction (see [CHANGELOG.md](CHANGELOG.md)).

**Non-unique source identifiers were resolved, not erased.** Where a source repeats a `gml:id`, the graph either deduplicates (identical content) or splits onto a synthesized id with the original in `source_gml_id`. A query that assumes `Building.id` equals the published `gml:id` will be right almost everywhere and wrong for 61 Helsinki, 40 Zurich, and 468 Tokyo buildings.

## Benchmark A limitations

**Template-generated questions.** 1,394 instances come from 84 templates with three accepted paraphrases each and slot values read from the live graph. This buys grounding and verifiability at the cost of the phrasing diversity a hand-authored suite would have. Linguistic variety is documented rather than claimed: per-category, per-difficulty, and per-language counts ship with the suite.

**Smaller than single-source text-to-query suites.** Comparable benchmarks have 10 k to 27 k questions. The size here follows from the requirement that every question be verified against a real city-scale graph, with gold answers materialized and infeasibility guard-proven. The scaling path (more slot samples per template, more cities) needs no redesign.

**Multilingual variants are author-produced, not native-speaker certified.** German variants across all cities and Japanese variants on Tokyo (95 instances) were authored and checked against the gold, but a native-fluency review is future work.

**Gold answers encode one defensible output shape.** Several questions admit more than one reasonable result shape (a bare fraction against a count-plus-coverage triple, for instance). Scoring is multiset and column-name insensitive, but a model returning extra columns or a differently rounded value scores wrong. Where this occurred in the baselines it is diagnosed per question in the baseline reports rather than silently absorbed.

**Baselines predate the spatial gold correction.** The released suite carries corrected proximity gold; the cached baseline runs were scored against the earlier version of those five templates. Affected questions and the effect on the reported numbers are enumerated in [benchmark_a/baselines/README.md](benchmark_a/baselines/README.md).

**Two model families, not a leaderboard.** One commercial frontier model and one local open-weight model, both closed book with schema-only context. This is a dataset paper's reference point, not a survey of models.

## Benchmark B limitations

**Matching as link prediction is intrinsically bounded.** An `ENRICHED_BY` edge is *defined* by footprint overlap, so the quantity that defines the label cannot be a decoder feature. A spatial-distance rule reaches 0.95 to 0.996 ROC-AUC on nearest-neighbor negatives while learned encoders reach at most 0.57. The informative regime is the ambiguous n:m subset, where distance is uninformative, a trivial attribute rule still reaches 0.94, and every learned encoder collapses to chance.

**Roof-material circularity.** The roof-material classifier was trained using OpenStreetMap labels, so OSM-derived features leak information about that target. Both protocol variants (with and without the OSM layer as input) must be reported, and the ML-versus-OSM agreement figure is not independent validation. On the released Hamburg graph only 3.5 % of labeled buildings carry a matched OSM `roof:material` tag, which bounds the leakage without removing it.

**Provenance-aware gains are small in distribution.** Within a single city the aware encoder improves on the agnostic baseline consistently but by at most 0.010 absolute. Source typing, not confidence weighting, appears to carry that effect: removing confidence weights while keeping source typing changes every in-distribution task by at most 0.001. The clear gains appear under distribution shift (leave-one-city-out), where the ablation has not yet been run. Provenance-aware representation learning is posed as an open problem, not solved.

**Transductive shallow baselines were excluded** from the full-scale comparison because they cannot embed unseen entities, which the cross-city protocol requires.

## Engineering limitations

**Restoring the large graphs needs real hardware.** Tokyo's store is 99 GiB and wants a generous Neo4j page cache. Hamburg is the smallest full-stack city and the right place to start. Sizing guidance is in [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

**Neo4j version coupling.** The dumps are written by Neo4j 2025.10.1 and load only into that version or newer. Spatial questions additionally require the Neo4j Spatial plugin; without it the R-tree procedures are unavailable and the spatial category cannot be evaluated.

**Some spatial gold queries are expensive on the largest graphs.** Even correctly written R-tree queries can take tens of seconds over Tokyo's 2 M buildings, and a query shape that issues one spatial procedure call per row does not scale at all. Timeouts observed in the baselines on New York and Tokyo are a property of that scale, not of the question, and are reported as `errored` rather than hidden.
