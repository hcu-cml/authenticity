# Human review of the question suite

The machine gates (G1 to G4) prove that a gold query executes, is deterministic, and returns something. They cannot prove that it means what the question asks. That is what this review is for, and it earned its place: it found a defect that all four gates had passed.

## The sample

`human_review_sample.csv`, 282 of 1,394 questions (**20.2 %**), drawn deterministically by a hash-based stratified selection over category, difficulty, city, and language (no RNG, so the sample is reproducible), including 22 non-English rows. Regenerate it with:

```bash
python ../harness/build_review_sample.py --fraction 0.20
```

Columns: `qid`, `template_id`, `category`, `city`, `lang`, `difficulty`, `feasible`, `question`, `gold_cypher`, `guard`, `gold_answer`, plus the two reviewer columns. Gold cells for held-out test questions read `<withheld: held-out test split>`, since the test gold is not published; the reviewers worked on the unredacted sheet.

Reviewers judged two things per question, accept or reject, without free editing: is the gold answer correct for the question as asked, and is the natural-language phrasing sound.

The shipped CSV is the sampling frame, with the `reviewer_verdict` and `reviewer_notes` columns left empty: the review was conducted on this sample and its outcome is recorded per template below, not as a per-row transcript. The sample itself is reproducible from the command above, so the frame can be checked independently of the verdicts.

## Outcome

The review was carried out by the paper authors over the frozen suite. One rejection, with a single root cause spanning six templates, and two accepted-with-note observations:

**Rejected and fixed: the proximity and window gold.** `spatial_neighbours`, `spatial_within_distance_point`, `spatial_knearest`, `spatial_near_amenity_tallest`, `spatial_near_water`, and `spatial_isolated` were flagged for returning results that did not match the question. Root cause: `spatial.withinDistance(layer, point, d)` interprets `d` as kilometres against a geographic layer, while the `features` R-tree stores Cartesian coordinates in the city's metric CRS, so the effective radius collapsed to a few metres. Measured on Hamburg: the exact `spatial_knearest` gold returned an empty result for a building whose five nearest neighbors are 7.5 to 27.8 m away, and across 2,000 sampled buildings it never returned five. Two slot providers were degenerate for a related reason: `bbox_wkt` sliced the raw dataset bounding box into quarters, but a handful of far-west outliers stretch Hamburg's bounding box to roughly 121 km while 94 % of buildings sit in one quarter, so one of the two windows was empty; and `spatial_isolated` drew its window from the dense city core, where no building lacks a neighbor within 100 m, so its answer was zero on every city.

**Why the gates missed it.** A `count(...)` gold always returns exactly one row, so G3 saw a non-empty result while the value was systematically wrong, and the ranked templates carried `allow_empty`, so an empty ranking was permitted by design. Determinism held, because a wrong query is wrong reproducibly.

**The fix.** `spatial_knearest` became a true top-k over `point.distance`, which is metres on Cartesian points, and returns exactly k regardless of local density (about 0.8 s on 388 k buildings, verified on 2 M). The four radius templates became an R-tree window in true metres plus an exact `point.distance <= R` recheck, which is the idiom the already-correct density templates used, so the R-tree remains genuinely exercised. `bbox_wkt` now draws windows from the building-coordinate percentile box, guaranteeing populated windows on any city, and `spatial_isolated` uses a new provider that samples buildings, counts each one's neighbors within 100 m through the R-tree, and centres the window on the sparsest. Suite regenerated and re-verified live on all five graphs; template and instance counts unchanged.

**Accepted with a note, no change:**

- `agg_helsinki_avg_floor_area` and `agg_helsinki_avg_year_built` return one context column beyond the requested average (`count(b) AS n`). Scoring is multiset and column-name insensitive over value tuples, and the reviewer judged the extra column harmless in the gold. Note that a *model* returning an extra column does fail, which is stated in the evaluation rules.
- `topk_most_storeys` on Tokyo returns buildings with `storeys_above_ground = 9999`, which is 225,776 buildings (11.3 %) and equals the column maximum. This is a PLATEAU source sentinel, sibling of the `-9999` height sentinel, stored verbatim under the lossless-ingest principle. The gold is correct with respect to the stored graph, so it stands, and the sentinel is documented as a data property in [../../LIMITATIONS.md](../../LIMITATIONS.md). Filtering the sentinels inside storey templates is a deliberate future change, not a silent one.

All other reviewed questions were accepted without change.

## What this establishes, and what it does not

It answers "who checked the gold?" with something falsifiable: a stratified fifth of the suite, reviewed by hand, with the one material finding named, root-caused, fixed, and re-verified. It does not claim independent third-party review, and it does not claim native-speaker certification of the German and Japanese variants; both are stated as limitations. Note also that the cached baseline runs predate this fix, which is spelled out in [../baselines/README.md](../baselines/README.md).
