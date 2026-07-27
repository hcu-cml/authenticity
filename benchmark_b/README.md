# Benchmark B: graph representation learning

**Does provenance information help a graph encoder, or is it ignored?** Three tasks over the released graphs, each run under two protocols that differ *only* in how much of the provenance structure the encoder may use, so any gap is attributable to provenance awareness rather than to model capacity. To our knowledge this is the first such comparison on a real city-scale multi-source graph.

> **Status of the code.** The task definitions, protocols, splits, and results below are final and are what the paper reports. The training code is maintained by a coauthor and is being prepared for release in this directory; until it lands, this file is the specification, and the loader interface below is enough to reimplement any task against the released graphs. See "Code release" at the end.

---

## Tasks

| | Task | Target | Metric | Cities with labels |
| --- | --- | --- | --- | --- |
| **T1** | attribute imputation | authoritative building height | R² | all five |
| **T1b** | cross-source completion | ML roof-material class, for the buildings the external model did **not** label | macro-F1 | Hamburg |
| **T2** | node classification | cadastral building-function class | macro-F1 | Hamburg |
| **T2b** | node classification | roof-type class | macro-F1 | Hamburg, Helsinki |
| **T3** | link prediction | held-out `ENRICHED_BY` correspondence edges | ROC-AUC | all five |

Label coverage differs per task and city by construction, and that is itself a property of an open multi-source corpus rather than a gap to hide: roof type exists in two of five cities, building function in one, the ML layer in one. Report which cities contributed to each number.

**T3 casts the OSM-to-CityGML footprint matching problem as a learning task.** The existing fusion edges are the labels, so no separate annotation effort is needed, and the ambiguous `n:m` subset is the interesting regime.

**Leakage control.** Each predicted attribute is removed from the inputs. A dedicated ablation additionally removes its correlated counterpart, for instance storey count when predicting height. For T1b the relevant leak is external: the roof-material classifier was trained on OpenStreetMap labels, so OSM-derived features carry information about the target. Run and report both variants, with and without the OSM layer as input. On the released Hamburg graph only 3.5 % of labeled buildings carry a matched OSM `roof:material` tag, which bounds the leakage without removing the concern.

---

## The two protocols

Both share backbone, depth, and budget. Only the visible provenance differs.

**Provenance-agnostic.** Flatten the multi-source graph into canonical entities: merge source-specific evidence, remove edge confidences, discard source labels. This is how existing urban graphs are consumed, and it is the baseline the comparison is against.

**Provenance-aware.** Keep (i) source-typed nodes and relations (CityGML, OSM, ML-derived), (ii) confidence values as edge weights, and (iii) coverage and agreement node features (source presence, source count, best-match confidence). A canonical entity *c* aggregates evidence from its neighbors as

```
h'_c = sigma( W_self · h_c  +  sum_{e in N(c)}  (w_ce / sum_e' w_ce')  ·  W_s(e) · h_e )
```

where `w_ce` in [0,1] is the correspondence confidence (the Jaccard stored on the CityGML-to-OSM edge, normalized per target node) and `W_s(e)` is a source-specific projection, one relation-specific weight matrix per typed relation. Setting `w_ce = 1` and `W_s(e) = W` recovers mean-pooled GraphSAGE, which is exactly the agnostic variant.

## Splits

Released rather than described, so results are comparable:

- **Spatial**, the primary within-city protocol: hold out entire spatial tiles. A single hold-out is high variance at city scale, so use **5-fold spatial cross-validation** with out-of-fold predictions pooled, which tests every entity exactly once.
- **Cross-city**: leave-one-city-out, the distribution-shift protocol.

Report mean and standard deviation over 3 seeds for a survey table and over 10 seeds for a paired comparison. For agnostic-against-aware comparisons, pair runs by seed and report a paired t-test, the Wilcoxon signed-rank test, Cohen's d_z, and a 95 % confidence interval on the per-seed difference. Treat a comparison as null when the interval contains zero or the effect size is negligible; several of ours are, and are reported as such.

## Models evaluated

Attribute-only MLP; provenance-agnostic GraphSAGE and GAT; source-typed R-GCN, HAN, and HGT; the confidence-weighted encoder above; self-supervised DGI; and, for T3, non-learned spatial-distance and attribute-similarity baselines. Shallow transductive methods (node2vec, metapath2vec) are excluded from the full-scale comparison because they cannot embed unseen entities, which the cross-city protocol requires.

Hyperparameters shared by the agnostic and aware variants: hidden dimension 64, two message-passing layers, dropout 0.3, Adam at learning rate 0.01, 150 epochs, PyTorch Geometric, one NVIDIA RTX PRO 6000 (96 GB).

---

## Results

### Within one city (Hamburg, 388 k buildings, spatial cross-validation, 3 seeds)

| Model | Roof type (macro-F1) | Building function (macro-F1) | Height (R²) |
| --- | --: | --: | --: |
| MLP, attributes only | 0.504 ± .000 | 0.329 ± .000 | 0.666 ± .000 |
| DGI, self-supervised | 0.516 ± .007 | 0.409 ± .002 | 0.683 ± .002 |
| GraphSAGE, agnostic | 0.556 ± .000 | 0.462 ± .000 | 0.730 ± .002 |
| GAT, agnostic | 0.531 ± .000 | 0.365 ± .001 | 0.676 ± .001 |
| HGT, source-typed | 0.541 ± .002 | 0.393 ± .007 | 0.714 ± .005 |
| HAN, source-typed | 0.460 ± .003 | 0.208 ± .004 | 0.416 ± .026 |
| R-GCN, source-typed | 0.558 ± .000 | 0.470 ± .003 | 0.713 ± .004 |
| **Confidence-weighted, aware** | **0.559 ± .001** | **0.476 ± .001** | **0.732 ± .000** |

Height retains the collinear storey count here; the ablation that removes it is separate.

**In distribution, provenance awareness is statistically consistent but negligible in magnitude.** Over 10 seeds the aware encoder improves height 0.729 to 0.733, roof type 0.556 to 0.558, and building function 0.464 to 0.474, each significant under a paired t-test (p < 0.02) yet at most 0.010 absolute. R-GCN, which is source-typed but not confidence-weighted, stays within about 0.02 of the full encoder on all three tasks.

That points at source *typing* rather than confidence *weighting* as the origin of the effect, which we tested rather than asserted: removing only the confidence weights, leaving typing, coverage features, and architecture unchanged, moves every in-distribution task by at most 0.001, with no significant effect on height (p = 0.21) or building function (p = 0.59) and a negligible 0.0006 on roof type (p = 0.02). **Falsifiable hypothesis, stated as such:** source typing and confidence weighting are separable, and confidence weighting is redundant with source typing in distribution but not under distribution shift. Testing the second half requires the same ablation under leave-one-city-out and is open work.

### Across cities (T1 height, leave-one-city-out, R², 10 seeds)

| Held out | n | no-graph probe | agnostic | aware | own-city reference |
| --- | --: | --: | --: | --: | --: |
| Hamburg | 388,267 | −0.145 | 0.270 ± .170 | **0.548 ± .071** | 0.733 |
| Helsinki | 2,980 | −0.000 | **0.516 ± .016** | 0.500 ± .029 | 0.461 |
| New York | 1,083,437 | **0.258** | 0.167 ± .034 | 0.188 ± .024 | 0.407 |
| Tokyo | 2,005,762 | −0.484 | 0.011 ± .130 | **0.082 ± .063** | 0.399 |
| Zurich | 102,668 | −0.011 | 0.581 ± .035 | **0.601 ± .037** | 0.269 |

**Under distribution shift the aware encoder helps, and on Hamburg it also halves the variance** (standard deviation 0.170 to 0.071). It improves on four of five held-out cities, with Helsinki tied within noise. The probe column is a no-graph baseline pooled over the training cities and is not comparable to the single-city attribute probe in the table above. Roof-type transfer, possible only on the Hamburg-Helsinki pair, shows no meaningful gap between the encoders.

### Cross-source completion (T1b, Hamburg)

Predicting the roughly 50 % of Hamburg buildings the external ML model did not label gives the aware encoder its clearest single-city edge: macro-F1 0.283 to 0.316, concentrated in the `concrete` class. The circularity check above supports reading this as structural rather than leakage.

### Matching (T3): learned encoders lose to trivial rules, for a structural reason

An `ENRICHED_BY` edge is *defined* by footprint overlap (median Jaccard 0.842), so the quantity that creates the label cannot be a decoder feature. On the default nearest-neighbor negatives a spatial-distance rule reaches ROC-AUC 0.95 to 0.996 while every learned encoder reaches at most 0.57.

The informative regime is the ambiguous `n:m` subset, where one building overlaps several OSM candidates and distance is uninformative. There the distance rule drops to 0.75 AUC, **a trivial attribute rule (building height against OSM levels) still reaches 0.94, and every learned encoder collapses to chance (0.47 to 0.49 AUC over 18,234 Hamburg cases)**. Current encoders exploit geometry and ignore the cross-source attribute signal that actually disambiguates correspondences. We ship the distance and attribute heuristics as reference baselines and pose attribute-aware `n:m` matching as an open challenge.

### Qualitative

In the T3 embedding space the aware encoder separates OSM-matched buildings into a distinct region where the agnostic encoder does not, and the ML-coverage and OSM-coverage gaps co-locate, indicating that the two missingness patterns are correlated rather than independent. That restructuring is invisible in the supervised metrics.

---

## Reimplementing a task from the graph

Everything needed is in the released dumps; no derived artifact is required.

**Features.** Geometry statistics per building (footprint area from the ground surface, height, storey counts, boundary-surface and polygon counts, bounding-box extent, centroid), thematic attributes as available per city, and the provenance columns. For the aware protocol the provenance columns are the point: `source` on every node and edge, `osm_*` mirrored scalars with `osm_match_type`, `osm_match_count`, `osm_best_jaccard`, the `ENRICHED_BY` properties `jaccard`, `overlap_ratio`, `intersection_area`, `match_type`, `is_primary`, the prediction coverages `predicted_roof_material_<i>_coverage`, and the reconstruction confidence on `HAS_LOD3_FACADE`.

**Backend-neutral tables.** `python ../tools/export_tables.py --out export/hamburg` writes node and edge tables (CSV, or Parquet with `pyarrow` installed) with those provenance columns as first-class fields, which is the fastest path to a PyTorch Geometric or DGL loader without a Neo4j dependency in the training loop.

**Spatial folds.** Assign each building to a tile from its centroid (`center_x`, `center_y`) on a fixed grid in the city's metric CRS, then hold out whole tiles. Grid size is a parameter; keep it fixed across models and report it.

**Sentinels.** Filter `measured_height <= -999` and `storeys_above_ground = 9999` before using either as a feature or a target. Tokyo's sentinels silently corrupt a height regression otherwise, which is exactly what happened to us before they were detected: an ingestion pipeline must check for implausible placeholders, not only for nulls.

**T3 negatives.** State how you sample them. Nearest-neighbor negatives make the task nearly trivial for a distance rule; the `n:m` subset is where the difficulty lives. Report both.

## Code release

The training and evaluation code (loaders, the confidence-weighted encoder, the split generators, the baselines, and the ablations) is being prepared for release in this directory. Until it appears, treat the specification above as the contract; the numbers are reproducible from it, and the graphs it needs are already public. If you are implementing it and something in the specification is underdetermined, open an issue and we will pin it down rather than leave you guessing.
