# AuthentiCity suite verification report

- Input: `the generated hamburg question set` (352 questions)
- Passed: **346**  Failed: **6**  (stability runs: 3)

| Category | Passed | Failed |
| -------- | ------ | ------ |
| aggregate | 17 | 0 |
| coverage | 24 | 0 |
| cross_source | 54 | 0 |
| filter_topk | 43 | 0 |
| infeasible | 27 | 6 |
| lod3 | 18 | 0 |
| multihop | 21 | 0 |
| provenance | 42 | 0 |
| spatial | 100 | 0 |

## Failures

- `inf_layer_absent_city__DEHHALKA100002LW__p0`: G4_not_absent (guard n=194799)
- `inf_layer_absent_city__DEHHALKA100002LW__p1`: G4_not_absent (guard n=194799)
- `inf_layer_absent_city__DEHHALKA100002LW__p2`: G4_not_absent (guard n=194799)
- `inf_layer_absent_city__DEHHALKA100002O7__p0`: G4_not_absent (guard n=194799)
- `inf_layer_absent_city__DEHHALKA100002O7__p1`: G4_not_absent (guard n=194799)
- `inf_layer_absent_city__DEHHALKA100002O7__p2`: G4_not_absent (guard n=194799)

This gate checks executability, determinism, and absence proofs, not phrasing quality. The complementary human review of a stratified 20.2 % sample is documented in benchmark_a/human_review/.