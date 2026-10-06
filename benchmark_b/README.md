# Benchmark B: graph representation learning

**Does provenance information help a graph encoder, or is it ignored?** Three tasks over the released graphs, each run under protocols that differ *only* in how much of the provenance structure the encoder may use, so any gap is attributable to provenance rather than to model capacity. To our knowledge this is the first such comparison on a real city-scale multi-source graph.

> **Corrections (October 2026).** Extending Benchmark B during review exposed four errors in the July code and results, now fixed:
> 1. The cross-city height experiment kept the per-city standardized target column (`height`) in its inputs. Within-city results are unaffected.
> 2. The provenance-agnostic baseline used one weight matrix per relation, not the shared matrix described in July. Its gap to the aware encoder therefore measured coverage features and confidence weights, not source typing.
> 3. In T3, the training links stayed in the message-passing graph, so the encoders learned "already linked means match", which inverts at test time.
> 4. The T1b roof-material gain (macro-F1 0.283 to 0.316) was credited to the aware encoder. 0.283 is the linear probe and the agnostic GNN already reaches 0.314.
>
> The results below are the corrected ones; the July versions remain in the git history. The table "What changed" lists every affected number. The corrected code in this folder replaces the July code and figures.

---

## Tasks

| | Task | Target | Metric | Cities with labels |
| --- | --- | --- | --- | --- |
| **T1** | attribute imputation | authoritative building height | R² | all five |
| **T1b** | cross-source completion | ML roof-material class, for the buildings the external model did **not** label | macro-F1 | Hamburg |
| **T2** | node classification | cadastral building-function class | macro-F1 | Hamburg |
| **T2b** | node classification | roof-type class | macro-F1 | Hamburg, Helsinki |
| **T3** | link prediction | held-out `ENRICHED_BY` correspondence edges | ROC-AUC, Hits@1 | all five |

Label coverage differs per task and city by construction. That is a property of an open multi-source corpus rather than a gap to hide: roof type exists in two of five cities, building function in one, the ML layer in one. Report which cities contributed to each number. Labelled buildings used, after sentinel and composite-code cleanup:

| | Hamburg | Helsinki | New York | Tokyo | Zurich |
| --- | --: | --: | --: | --: | --: |
| Buildings | 388,267 | 2,980 | 1,083,437 | 2,005,762 | 102,668 |
| T1 height | 388,267 | 2,980 | 1,083,436 ¹ | 2,005,762 | 102,315 ¹ |
| T1b roof material (ML) | 194,799 | – | – | – | – |
| T2 building function | 388,267 | 94 ² | – | – | – |
| T2b roof type | 388,267 | 2,944 | – | – | – |
| T3 `ENRICHED_BY` pairs | 364,684 | 2,712 | 1,073,423 | 1,349,003 | 97,818 |
| Buildings with ≥ 2 OSM matches | 18,234 | 174 | 3,088 | 134,524 | 2,649 |

¹ All New York heights and 6,685 Zurich heights are the LoD2 bounding-box z-extent, because no measured height is available.
² Too few labels to use; building function is evaluated on Hamburg only.

**T3 casts the OSM-to-CityGML footprint matching problem as a learning task.** The existing fusion edges are the labels, so no separate annotation effort is needed. These labels are produced by our own overlap procedure, so T3 measures recovery of the correspondences, not their correctness. The same holds for T1b, whose labels come from an upstream model.

**Leakage control.**
- **Target removal.** Each predicted attribute is removed from the inputs, in within-city **and** cross-city runs (the July cross-city code did not do this; see Corrections). A dedicated ablation additionally removes its correlated counterpart, for instance storey count when predicting height.
- **T3.** The links used as supervision must not be in the message-passing graph. We hold 30 % of the training edges out of the graph and use them as supervision (PyG `disjoint_train_ratio=0.3`).
- **T1b.** The relevant leak is external: the roof-material classifier was trained on OpenStreetMap labels, so OSM-derived features may carry information about the target. OSM `roof:material` is therefore never a model input (OSM buildings contribute only roof *shape*, levels and position), and it must never be used as an evaluation label. On the released Hamburg graph only 3.5 % of labelled buildings carry a matched OSM `roof:material` tag at all. The graph adds only +0.033 macro-F1 over the attribute-only probe, the same order as on the other tasks, which is not a leakage signature. Whether the upstream model's OSM training labels leak through other features cannot be verified from the graph alone.

---

## The protocols

All variants share backbone, depth, and budget. Only the visible provenance differs.

**Provenance-aware (full encoder).** Keep (i) source-typed nodes and relations (CityGML, OSM, ML-derived), (ii) confidence values as edge weights, and (iii) coverage and agreement node features (source presence, source count, best-match confidence). A canonical entity *c* aggregates evidence from its neighbors as

```
h'_c = sigma( W_self · h_c  +  sum_{e in N(c)}  (w_ce / sum_e' w_ce')  ·  W_s(e) · h_e )
```

where `w_ce` in [0,1] is the correspondence confidence (the Jaccard stored on the CityGML-to-OSM edge, normalized per target node) and `W_s(e)` is a source-specific projection, one relation-specific weight matrix per typed relation.

**Provenance-agnostic (baseline).** `w_ce = 1` and no coverage features, with **one weight matrix per relation** (heterogeneous GraphSAGE). This is the agnostic model in every table below. Removing source typing as well (`W_s(e) = W`, a single shared matrix) is the separate variant V5.

Because the weights are normalized per building, confidence weighting can only act on buildings with at least two OSM matches; a single match always gets weight 1. These are 4.7 % of buildings in Hamburg, 5.8 % in Helsinki, 0.3 % in New York, 6.7 % in Tokyo, and 2.6 % in Zurich.

**Ablation variants** (cross-city experiments):

| ID | Source typing | Confidence `w_ce` | Coverage features |
| --- | --- | --- | --- |
| V0 agnostic | per relation | 1 | no |
| V1 aware (full encoder) | per relation | Jaccard | yes |
| V2 | per relation | 1 | yes |
| V3 | per relation | Jaccard | no |
| V4 | shared W | Jaccard | no |
| V5 | shared W | 1 | no |

**T3 protocol.** For each seed:
1. A random 30 % of the `ENRICHED_BY` edges are held out as test positives and removed from the graph.
2. The remaining training edges are split once more: 70 % stay in the message-passing graph, and 30 % are removed from it and serve as supervision positives.
3. Negatives are, for every positive, the 5 nearest OSM buildings that are not a true match of that building.

The decoder is a dot product trained with binary cross-entropy. Hits@1 is the share of test positives scored above all five of their negatives.

## Splits

Released rather than described, so results are comparable:

- **Spatial**, the primary within-city protocol: labelled buildings are clustered into 5 spatial blocks with KMeans on their centroids (`center_x`, `center_y`; `n_init=10`, `random_state=seed`), and whole blocks are held out. This is 5-fold spatial cross-validation with out-of-fold predictions pooled, which tests every entity exactly once.
- **Cross-city**: leave-one-city-out, the distribution-shift protocol.
- **T3**: a random 30 % edge hold-out per seed, as above. The ambiguous-subset analysis instead uses component-disjoint 5-fold cross-validation, so no correspondence component is split between training and test.

Fold assignments (building `gml_id` → fold, per seed) and seed lists are released with the code. Report mean and standard deviation over 3 seeds for a survey table and over 10 seeds for a paired comparison. For paired comparisons, pair runs by seed (and held-out city) and report:
- a paired t-test;
- the Wilcoxon signed-rank test;
- Cohen's d_z;
- a 95 % confidence interval on the per-seed difference.

Treat a comparison as null when the interval contains zero or the effect size is negligible. Several of ours are, and are reported as such.

## Models evaluated

- **No-graph baselines:**
  - a linear probe: logistic or ridge regression on the node attributes;
  - LightGBM on the node attributes, with and without 1-hop neighbour aggregates.
- **Provenance-agnostic GNNs:** GraphSAGE and GAT.
- **Source-typed GNNs:** R-GCN, HAN, HGT and Simple-HGN (Lv et al., KDD 2021).
- **The confidence-weighted encoder** above.
- **Self-supervised:** DGI.
- **T3 only:** non-learned spatial-distance and attribute-similarity rules.

Shallow transductive methods (node2vec, metapath2vec) are excluded from the full-scale comparison because they cannot embed unseen entities, which the cross-city protocol requires.

Hyperparameters shared by all GNN variants: hidden dimension 64, two message-passing layers, dropout 0.3, Adam at learning rate 0.01, 150 epochs, no per-variant tuning, PyTorch Geometric, one NVIDIA RTX PRO 6000 (96 GB). Simple-HGN uses the same budget without tuning, whereas its original paper tunes learning rate and epochs.

---

## Results

### Within one city (Hamburg, 388 k buildings, spatial cross-validation, 3 seeds)

| Model | Roof type (macro-F1) | Building function (macro-F1) | Height (R²) |
| --- | --: | --: | --: |
| Linear probe, attributes only | 0.504 ± .000 | 0.329 ± .000 | 0.666 ± .000 |
| DGI, self-supervised | 0.516 ± .007 | 0.409 ± .002 | 0.683 ± .002 |
| GraphSAGE, agnostic | 0.556 ± .000 | 0.462 ± .000 | 0.730 ± .002 |
| GAT, agnostic | 0.531 ± .000 | 0.365 ± .001 | 0.676 ± .001 |
| HGT, source-typed | 0.541 ± .002 | 0.393 ± .007 | 0.714 ± .005 |
| HAN, source-typed | 0.460 ± .003 | 0.208 ± .004 | 0.416 ± .026 |
| R-GCN, source-typed | 0.558 ± .000 | 0.470 ± .003 | 0.713 ± .004 |
| Confidence-weighted, aware | 0.559 ± .001 | **0.476 ± .001** | **0.732 ± .000** |
| LightGBM, attributes | 0.558 ± .000 | 0.421 ± .000 | 0.700 ± .000 |
| LightGBM + 1-hop neighbour aggregates | **0.585 ± .002** | 0.458 ± .002 | 0.728 ± .007 |
| Simple-HGN | 0.547 ± .001 | 0.440 ± .001 | 0.658 ± .025 |

Height retains the collinear storey count here; the ablation that removes it is separate. Reruns of the probe, GraphSAGE and the aware encoder with the corrected code reproduce the first rows within 0.002. LightGBM with neighbour aggregates is the best roof-type model and within 0.005 of the aware encoder on height.

**In distribution, provenance awareness is statistically consistent but negligible in magnitude.** Over 10 seeds the aware encoder improves height 0.729 to 0.733, roof type 0.556 to 0.558, and building function 0.464 to 0.474. Each change is significant under a paired t-test (p < 0.02), yet none exceeds 0.010 absolute. Because the agnostic baseline already has one weight matrix per relation, this gap measures the coverage features and confidence weights together, not source typing. Removing only the confidence weights moves every in-distribution task by at most 0.001, with no significant effect on height (p = 0.21) or building function (p = 0.59) and a negligible 0.0006 on roof type (p = 0.02).

### Across cities (T1 height, leave-one-city-out, R², 10 seeds, target removed from all inputs)

| Held out | n | probe | V0 | V1 | V2 | V3 | V4 | V5 | own city |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Hamburg | 388,267 | **0.325** | 0.129 ± .035 | 0.147 ± .038 | 0.139 ± .050 | 0.136 ± .037 | 0.169 ± .045 | 0.144 ± .041 | 0.733 |
| Helsinki | 2,980 | **0.104** | −0.038 ± .036 | 0.014 ± .030 | 0.022 ± .028 | −0.035 ± .031 | −0.039 ± .044 | −0.037 ± .034 | 0.461 |
| New York | 1,083,437 | 0.252 | 0.277 ± .013 | 0.256 ± .023 | 0.257 ± .028 | 0.278 ± .016 | **0.293 ± .017** | 0.285 ± .015 | 0.407 |
| Tokyo | 2,005,762 | **0.001** | −0.081 ± .025 | −0.019 ± .030 | −0.033 ± .035 | −0.078 ± .021 | −0.089 ± .030 | −0.099 ± .035 | 0.399 |
| Zurich | 102,668 | 0.167 | 0.254 ± .023 | 0.308 ± .029 | **0.311 ± .021** | 0.274 ± .015 | 0.257 ± .022 | 0.133 ± .062 | 0.269 |
| Mean over cities | | **0.170** | 0.108 ± .014 | 0.141 ± .014 | 0.139 ± .015 | 0.115 ± .014 | 0.118 ± .016 | 0.085 ± .015 | |

The probe is a no-graph ridge baseline pooled over the training cities. *Own city* is the single-city spatial cross-validation reference from the paper's cross-city table. Paired effects, mean over cities (10 seeds, paired by seed and held-out city):

| Question | Comparison | Difference [95 % CI] | p (t / Wilcoxon) | d_z | Verdict |
| --- | --- | --- | --- | --: | --- |
| Confidence weighting (typed) | V1 − V2 | +0.002 [−0.005, +0.008] | 0.536 / 0.695 | +0.20 | null |
| Coverage features | V1 − V3 | +0.026 [+0.009, +0.043] | 0.007 / 0.014 | +1.10 | gain |
| Coverage without confidence | V2 − V0 | +0.031 [+0.015, +0.048] | 0.002 / 0.004 | +1.34 | gain |
| Confidence without coverage | V3 − V0 | +0.007 [−0.003, +0.017] | 0.150 / 0.193 | +0.50 | null |
| Full aware vs agnostic | V1 − V0 | +0.033 [+0.018, +0.048] | 6.2e-04 / 0.002 | +1.62 | gain |
| Confidence with shared W | V4 − V5 | +0.033 [+0.024, +0.042] | 1.2e-05 / 0.002 | +2.74 | gain (Zurich, Hamburg only) |
| Source typing | V0 − V5 | +0.023 [+0.008, +0.038] | 0.007 / 0.010 | +1.11 | gain (Zurich only) |

**Cross-city height transfer is hard, and confidence weighting does not help under distribution shift either.**
- **No model reaches its own-city reference except on Zurich,** and the no-graph probe is the best model on Hamburg, Helsinki and Tokyo.
- **The full aware encoder beats the agnostic baseline on Helsinki, Tokyo and Zurich** (p < 1e-4 each), ties on Hamburg, and is worse on New York (−0.021, p = 0.025).
- **That gain comes from the coverage features.** Removing only the confidence weights is null on average and in four of five cities (Tokyo +0.014, p = 0.027).
- **Source typing, and confidence with a shared matrix, are not general effects.** They are significant on average only because the shared-matrix variant V5 collapses on Zurich (0.133 ± 0.062). Both are null in the other cities, except that confidence with a shared matrix is also significant on Hamburg (+0.025).

**Roof-type transfer** is possible only on the Hamburg-Helsinki pair (macro-F1, merged 3-class, 10 seeds):

| Held out | constant "flat" | V0 | V1 | V2 | V3 |
| --- | --: | --: | --: | --: | --: |
| Hamburg | 0.221 | 0.204 ± .002 | 0.207 ± .005 | 0.205 ± .003 | 0.204 ± .003 |
| Helsinki | 0.332 | 0.332 ± .006 | 0.337 ± .016 | 0.336 ± .015 | 0.334 ± .012 |

Every variant scores at or below always predicting "flat", and every paired difference is null. The Helsinki test set is 99 % flat roofs (2,917 of 2,944), so this pair is a label-shift failure case and cannot discriminate between encoders.

### Cross-source completion (T1b, Hamburg)

This task predicts the roughly 50 % of Hamburg buildings the external ML model did not label.
- **Results:** the linear probe reaches macro-F1 0.283, the agnostic GNN 0.314, and the aware encoder 0.316.
- **The graph helps; provenance barely does.** The gain is concentrated in the `concrete` class (F1 0.01 to 0.10), and the provenance-specific gain is only +0.002.
- **Rare classes:** `metal` (4.4 %) and `glass` (1.7 %) are unpredictable for every method at this label density.

### Matching (T3): distance stays strongest, provenance helps the encoders

An `ENRICHED_BY` edge is *defined* by footprint overlap (median Jaccard 0.842), so a spatial-distance rule is a strong baseline. ROC-AUC (Hits@1 in brackets) with the 5 nearest unlinked OSM buildings as negatives, random 30 % edge hold-out, 3 seeds:

| City | Distance rule | Attribute rule | Attribute encoder | GraphSAGE | Aware | Aware − GraphSAGE AUC [95 % CI] |
| --- | --: | --: | --: | --: | --: | --: |
| Hamburg | **0.967** (0.987) | 0.539 (0.035) | 0.553 (0.128) | 0.826 (0.451) | 0.865 (0.507) | +0.039 [+0.025, +0.053] |
| Helsinki | **0.952** (0.962) | 0.563 (0.089) | 0.565 (0.168) | 0.789 (0.430) | 0.830 (0.473) | +0.042 [+0.015, +0.068] |
| New York | **0.996** (0.998) | 0.500 (0.000) | 0.501 (0.039) | 0.844 (0.431) | 0.848 (0.435) | +0.004 [+0.004, +0.005] |
| Tokyo | **0.952** (0.975) | 0.501 (0.004) | 0.505 (0.058) | 0.789 (0.376) | 0.838 (0.420) | +0.048 [+0.047, +0.050] |
| Zurich | **0.974** (0.977) | 0.494 (0.013) | 0.535 (0.103) | 0.806 (0.409) | 0.845 (0.461) | +0.039 [+0.032, +0.045] |

The attribute rule compares building height with OSM levels. With the supervision links removed from the message-passing graph, the learned encoders reach 0.79 to 0.87 and the aware encoder beats GraphSAGE in every city. In New York the gap is only +0.004, because just 0.3 % of buildings there have more than one OSM match.

**Ambiguous subset: which partner is the right one?** Among the 18,234 Hamburg buildings with at least two OSM matches, each building's primary (largest-overlap) OSM partner is ranked against its other overlapping partners (`t3_matching/t3_nm_matching.py`). All edges of these buildings are masked from the message-passing graph. The metrics are mean rank-AUC and Hits@1 per building, over 3 seeds.

| Scorer | Rank-AUC | Hits@1 |
| --- | --: | --: |
| Chance | 0.500 | 0.407 |
| Distance rule | 0.747 | 0.640 |
| **Attribute rule** (building height vs. OSM levels) | **0.935** | **0.925** |
| GraphSAGE (with / without position) | 0.526 / 0.521 | 0.429 / 0.426 |
| Aware (with / without position) | 0.533 / 0.536 | 0.437 / 0.440 |

- **Distance is no longer decisive here,** because all candidates overlap the building.
- **The attribute rule is genuine.** It reaches 0.934 Hits@1 even on the 11,075 buildings where every candidate carries an OSM level tag, so it does not exploit missing tags.
- **The learned encoders stay near chance.** They do not use the cross-source attribute signal that actually disambiguates these correspondences. With the July protocol they scored 0.483 to 0.489; the correction lifts them only slightly.
- **Open challenge:** attribute-aware `n:m` matching. Both heuristics are provided as reference baselines.

A different negative definition shows the same encoders behave very differently on this subset (component-disjoint 5-fold CV, one seed, link vs. no link):

| Negatives | Distance | Attribute rule | GraphSAGE | Aware |
| --- | --: | --: | --: | --: |
| 5 nearest unlinked OSM buildings | 0.924 | 0.558 | 0.896 | 0.905 |
| Unlinked OSM buildings of the same correspondence component | 0.724 | 0.491 | 0.612 | 0.673 |

Deciding whether a pair is linked at all is mostly geometric. Deciding which of several linked partners is the primary one is mostly attribute-driven, and that is where the encoders fail.

### Qualitative

The paper's t-SNE figure (`figures/fig_prov_tsne.pdf`) shows the T3 embeddings. We measure it by 10-NN label purity in the full embedding (50,000 Hamburg buildings; `fig_prov_tsne_metrics.json`):

| | OSM coverage (chance 0.747) | ML roof-material coverage (chance 0.500) |
| --- | --: | --: |
| Agnostic | 0.897 | **0.862** |
| Aware | **0.997** | 0.790 |

- **The aware encoder isolates buildings without an OSM match.** This is largely by construction, since its coverage features include the match count.
- **That cluster also lacks the ML roof-material layer, which is a property of the data rather than the encoder.** Only 15.5 % of buildings without an OSM match have an ML label, against 56.4 % of matched buildings (φ = 0.29).
- **The agnostic encoder separates ML coverage better.**

The July figure had two problems, both fixed: it was made with the buggy T3 protocol, and its "OSM coverage" panel showed the `osm_shared` flag (12.4 % of buildings) instead of "has an OSM match" (84.9 %).

---

## What changed (July versus October 2026)

| Claim | July | Corrected |
| --- | --- | --- |
| Cross-city height, Hamburg held out: agnostic, aware | 0.270, 0.548 | 0.129, 0.147 |
| Cross-city, aware minus agnostic, mean over cities | +0.090 | +0.033, from the coverage features |
| Cross-city best model | aware on four of five cities | probe on three of five cities |
| Confidence weighting under distribution shift | open hypothesis | null on average and in four of five cities |
| T1b gain credited to the aware encoder | 0.283 to 0.316 | probe 0.283, agnostic 0.314, aware 0.316 (+0.002) |
| T3 learned encoders, ROC-AUC | at most 0.57 | 0.79 to 0.87 |
| T3 ambiguous subset (primary partner) | distance 0.75, attribute rule 0.94, encoders 0.47 to 0.49 | distance 0.75, attribute rule 0.94 (unchanged), encoders 0.52 to 0.54: still near chance |
| Roof-type transfer | no meaningful gap | all variants at or below the constant predictor |
| t-SNE "OSM coverage" panel | `osm_shared` flag, buggy T3 protocol | real OSM-match flag, corrected protocol |
| "Attribute-only MLP" | MLP | linear probe (logistic or ridge regression) |
| Agnostic baseline | shared weight matrix | one weight matrix per relation; shared matrix is V5 |
| Spatial folds (description) | fixed grid | KMeans blocks, as implemented |

Single-city results (the within-city table and the in-distribution ablation) are unaffected.

---

## Reimplementing a task from the graph

Everything needed is in the released dumps; no derived artifact is required.

**Features available.** Geometry statistics per building (footprint area from the ground surface, height, storey counts, boundary-surface and polygon counts, bounding-box extent, centroid), thematic attributes as available per city, and the provenance columns. For the aware protocol the provenance columns are the point:
- `source` on every node and edge;
- `osm_*` mirrored scalars, including `osm_match_type`, `osm_match_count` and `osm_best_jaccard`;
- the `ENRICHED_BY` properties `jaccard`, `overlap_ratio`, `intersection_area`, `match_type` and `is_primary`;
- the prediction coverages `predicted_roof_material_<i>_coverage`;
- the reconstruction confidence on `HAS_LOD3_FACADE`.

Note that `osm_shared` flags a building whose OSM counterpart is shared with other CityGML buildings. It does **not** mean "has an OSM match"; use the presence of an `ENRICHED_BY` edge for that.

**Features the reference implementation uses.**
- **Building:** `measured_height`, log footprint area, `storeys_above_ground` (with a presence mask), `ground_z`.
- **Aware protocol only, additionally:** `osm_match_count`, `osm_best_jaccard`, `osm_shared`, `lod3_confidence`, `lod3_enriched`.
- **OsmBuilding:** centroid, one-hot `osm_roof_shape`, `osm_building_levels`.
- **OsmPOI:** centroid.
- **Edges:** `ENRICHED_BY` (weight `jaccard`) and `HAS_POI`, plus reverse edges.

Numeric features are z-scored per city. Label nodes (roof type, function) are read only to build targets and never enter the graph.

**Backend-neutral tables.** `python ../tools/export_tables.py --out export/hamburg` writes node and edge tables (CSV, or Parquet with `pyarrow` installed) with the provenance columns as first-class fields. This is the fastest path to a PyTorch Geometric or DGL loader without a Neo4j dependency in the training loop.

**Spatial folds.** Cluster the labelled buildings' centroids (`center_x`, `center_y`) into 5 blocks with KMeans (`n_init=10`, `random_state=seed`) and hold out whole blocks. The released fold files make this exact.

**Sentinels.** Treat |`measured_height`| ≥ 9999 and |`storeys_above_ground`| ≥ 9999 as missing (Tokyo uses ±9999), and non-positive values as missing, before using either as a feature or a target. Where measured height is missing, the reference code falls back to the bounding-box z-extent. Tokyo's sentinels silently corrupt a height regression otherwise, which is exactly what happened to us before they were detected: an ingestion pipeline must check for implausible placeholders, not only for nulls.

**Targets.** Remove the target column, and any rescaled copy of it such as a per-city standardized version, from the inputs in every protocol, including cross-city runs.

**T3 negatives and supervision.** State how you sample negatives. Nearest-neighbour negatives make the task nearly trivial for a distance rule, so report the distance rule alongside any learned model. Keep the supervision links out of the message-passing graph, or the encoder learns that an existing link implies a match.

## Code

How to set up, run and extend the code. Layout of this directory (paths are relative, so keep the structure):

```
benchmark_b/
├── README.md                          this file
├── requirements.txt
├── _setup_paths.py                    puts the subfolders below on sys.path (imported by every script)
├── shared/
│   ├── neo4j_loader.py                Neo4j -> PyG HeteroData loader + graph cache (graph_<city>.pt)
│   ├── s5_train.py                    models, training loops, T2 classification, out-of-fold predictions
│   └── splits.py                      spatial KMeans-block folds, label merging (3-class roof type, top-k function)
├── t1_imputation/
│   ├── t1_regression.py               T1 height / storeys regression
│   ├── paired_singlecity.py           10-seed paired agnostic-vs-aware tests, Hamburg (in-distribution)
│   └── paired_ablation_singlecity.py  10-seed confidence-weighting ablation, Hamburg (in-distribution)
├── t2_classification/
│   ├── run_full_experiments.py        July driver for the within-city survey tables
│   └── compute_missing.py             GAT / HGT / DGI cells of the within-city table
├── t3_matching/
│   ├── t3_matching.py                 T3 link prediction (protocol="disjoint" = corrected, default)
│   └── t3_nm_matching.py              ambiguous-subset evaluation (--protocol disjoint|legacy)
├── crosscity/
│   └── s8_crosscity.py                combining city graphs for leave-one-city-out
├── figures/
│   ├── make_fig_prov_tsne.py          t-SNE figure + fig_prov_tsne_metrics.json
│   ├── fig_prov_tsne.pdf
│   └── fig_prov_tsne_metrics.json
├── notebooks/                         exploratory notebooks (July)
├── graph_<city>.pt                    (not committed) graph caches, written by neo4j_loader.py
└── experiments/
    ├── code/                          one script per experiment + reproduce.py (below)
    ├── release/                       seeds.json, environment.txt, label_availability.{md,csv}
    ├── results/                       per-run results (*_runs.jsonl / *_runs.csv) + TABLES.md
    └── targets/                       (not committed) cached targets per city, written by extract_targets.py
```

Not committed because of size, and regenerated by the scripts:
- the graph caches (about 1.7 GB);
- the cached targets (86 MB);
- the per-city fold files (77 MB): `python b5_package.py` writes them to `experiments/release/splits/`;
- the T3/T1b prediction exports (`b3_export_*.py`).

### Setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # torch 2.11 + cu128 (needed for Blackwell / sm_120), PyG 2.8, LightGBM 4.7
```

The exact environment of the reported runs is in `experiments/release/environment.txt`:
- Python 3.12, torch 2.11.0+cu128, torch_geometric 2.8.0.post1, LightGBM 4.7.0;
- NVIDIA RTX PRO 6000 Blackwell (96 GB), driver 580.178.04.

Older CUDA wheels (cu124) do not run on Blackwell GPUs.

### Data prerequisites

There are two one-time steps, each requiring the city's graph to be live in Neo4j. After both, nothing needs Neo4j.

1. **Graph cache.** From `benchmark_b/`: `python shared/neo4j_loader.py --database <city> --cache graph_<city>.pt` writes the PyG `HeteroData` graph per city. Credentials come from `.env` (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`), which is never committed. Loading the five released dumps gives 3,583,114 buildings in total.
2. **Targets.** `python experiments/code/extract_targets.py <city>` writes `targets/<city>.npz`: height and storeys with sentinels removed, `gml_id`, upstream roof material, and OSM match type, all in the graph's node order. The script aborts unless every row matches the cached graph, compared on each building's raw centroid. `python experiments/code/extract_osm_ids.py hamburg` does the same for Hamburg's OSM ids, which T3 exports need.

### Reproducing the results (one command per table)

Run from `experiments/code/` with the venv active:

| Command | Produces | Runs | GPU time* |
| --- | --- | --: | --: |
| `python reproduce.py table6` | within-city survey, Hamburg (roof type, building function, height), 3 seeds | — | not measured |
| `python reproduce.py table7` | cross-city height, **corrected** (target removed), probe/V0/V1/V5, 10 seeds | 200 | ~2 h |
| `python reproduce.py table7_july` | the submitted (leaky) July protocol, for comparison only | 150 | ~1.5 h |
| `python reproduce.py table17` | roof-type transfer Hamburg ↔ Helsinki, V0/V1, 3 seeds | 12 | < 5 min |
| `python reproduce.py t3` | T3 matching, 5 cities, 3 seeds, corrected and July protocol | 120 | ~0.4 h |
| `python reproduce.py b1` | full cross-city ablation V0–V5 + probe, both protocols, 10 seeds | 700 | ~7 h |
| `python reproduce.py b2` | roof-type transfer ablation V0–V3, 10 seeds | 80 | ~10 min |
| `python reproduce.py b4` | LightGBM, LightGBM + 1-hop, Simple-HGN (+ anchor reruns), 3 seeds | 54 | ~1.5 h |
| `python reproduce.py report` | aggregates all runs into `results/*.csv` and `results/TABLES.md` (paired statistics) | — | seconds |

\* Wall-clock on the RTX PRO 6000 while sharing the GPU with another job; peak VRAM ≤ 16.3 GB (Simple-HGN), ≤ 14 GB for everything else.

All run scripts append one JSON line per run to `results/<experiment>_runs.jsonl` and are resumable: an interrupted run continues where it stopped. Each line records task, protocol, city or held-out city, variant or method, seed, metrics, runtime, peak VRAM and the code hash. `make_report.py` turns these into CSVs and the paired-statistics tables:
- mean per-seed difference with 95 % CI;
- paired t-test and Wilcoxon signed-rank p;
- Cohen's d_z;
- a verdict (null if the CI contains 0).

### Experiment scripts (`experiments/code/`)

| Script | What it does |
| --- | --- |
| `b1_crosscity_ablation.py` | Leave-one-city-out T1 height for variants V0–V5 and the probe. `--protocols guarded` removes the target column (correct); `t7` keeps it (July behaviour). `--variants`, `--seeds` select subsets |
| `b2_roof_transfer.py` | Hamburg ↔ Helsinki roof-type transfer (merged 3-class), variants V0–V3, plus the constant-predictor reference |
| `b4_baselines.py` | LightGBM (attributes; + 1-hop aggregates: per relation into Building, the mean of the neighbours' features and log(1 + degree)) and Simple-HGN on the Table 6 tasks and folds; registers `lgbm`, `lgbm_1hop`, `simplehgn` as methods |
| `t3_rerun.py` | T3 for all cities and scorers (distance, attribute rule, no-graph encoder, GraphSAGE, aware) under `--protocols disjoint,legacy` |
| `t3_matching_legacy_snapshot.py` | Frozen copy of the July `t3_matching.py`, kept for provenance only |
| `make_report.py` | Per-run JSONL → `results/*.csv` + `results/TABLES.md` |
| `b5_package.py` | Writes `experiments/release/`: fold assignments per city, task and seed; label-availability matrix; seeds; environment |
| `b3_export_roofmat.py` | Roof-material predictions for every Hamburg building: spatial-CV out-of-fold and imputation, for probe / V0 / V1 / R-GCN / LightGBM + 1-hop |
| `b3_export_matching.py` | Scores every Hamburg `ENRICHED_BY` edge plus its 5 nearest unlinked OSM buildings with all T3 scorers (component-disjoint 5-fold CV) |
| `score_b3.py` | Scores those exports against manually verified labels (`--rset`, `--mset`) once they exist |
| `extract_targets.py`, `extract_osm_ids.py` | One-time target / id extraction from Neo4j (see Data prerequisites) |
| `reproduce.py` | One command per table (above) |

### Seeds, splits and leakage guards

- **Seeds** (`experiments/release/seeds.json`): 0–2 for single-city tables, B4 and T3; 0–9 for cross-city (B1) and roof transfer (B2). `S.set_seed(seed)` runs before every fit.
- **Spatial folds** (`splits.py`): KMeans with 5 clusters (`n_init=10`, `random_state=seed`) on the labelled buildings' centroids, whole blocks held out. `experiments/code/b5_package.py` writes the assignments to `experiments/release/splits/<city>_folds.csv.gz` (`gml_id` → fold, per task and seed).
- **Target removal:** `building_features(..., drop=[target])` in every protocol. B1's `t7` protocol exists only to reproduce the July numbers.
- **T3:** `t3_matching.train_encoder(protocol="disjoint")` holds 30 % of the training edges out of the message-passing graph as supervision. `protocol="legacy"` reproduces the July bug and must not be used for new results.
- **T1b:** an assertion in `b3_export_roofmat.py` checks that no OSM roof-material feature is an input.

### Figures

`make_fig_prov_tsne.py` uses the corrected T3 protocol and the real OSM-match flag (≥ 1 `ENRICHED_BY` edge, not `osm_shared`). It writes `fig_prov_tsne.pdf` and `fig_prov_tsne_metrics.json` with the k-NN purity numbers quoted in the caption.

The July cross-city, matching and results figures are removed, because they were built on the leaky cross-city protocol and the buggy T3 protocol. Their history is in git.

### Changes in this version (October 2026)

- `t3_matching/t3_matching.py`: `train_encoder(protocol=...)`. The default `"disjoint"` keeps supervision edges out of the message-passing graph; `"legacy"` reproduces the July bug and must not be used for new results.
- `crosscity/s8_crosscity.py`: `crosscity_eval_regression(..., drop=("height",))` now removes the target column by default; the July default left it in. The reported cross-city numbers come from `experiments/code/b1_crosscity_ablation.py`, which implements the runs itself.
- `figures/make_fig_prov_tsne.py`: corrected protocol and OSM-match flag; writes the metrics file.
- `t3_matching/t3_nm_matching.py`: trains through `t3_matching.train_encoder`, so the corrected protocol applies (`--protocol legacy` reproduces the July numbers); output `t3_nm_matching_<protocol>.json`, both copied to `experiments/results/`.
- **New:** `experiments/` (all scripts, per-run results and release files behind the corrected tables).
- **Removed** (superseded; history in git):
  - `crosscity/crosscity_paired.py` and `crosscity/crosscity_partial_3city.py`: the July cross-city ablation with the target column in the inputs, replaced by `b1_crosscity_ablation.py`;
  - `results.json`: July numbers, replaced by `experiments/results/`;
  - the July cross-city, matching and results figures and their scripts, which were built on the old protocols.

### Known limitations

- T3 and T1b labels are generated by our own overlap procedure and an upstream model. Scores measure label recovery, not correctness. `score_b3.py` is ready for verified labels; none are included yet.
- Wall-clock runtimes are upper bounds, because the GPU was shared during the reported runs.

If something in the specification is underdetermined, open an issue and we will pin it down rather than leave you guessing.
