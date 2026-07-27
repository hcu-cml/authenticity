# AuthentiCity suite verification report

- Input: `the generated tokyo question set` (297 questions)
- Passed: **291**  Failed: **6**  (stability runs: 3)

| Category | Passed | Failed |
| -------- | ------ | ------ |
| aggregate | 23 | 0 |
| cross_source | 45 | 0 |
| filter_topk | 35 | 0 |
| infeasible | 27 | 6 |
| lod3 | 3 | 0 |
| multihop | 30 | 0 |
| provenance | 30 | 0 |
| spatial | 98 | 0 |

## Failures

- `inf_interior_lod__bldg_000094ef-deb4-4a1f-__p0`: G4_not_absent (guard n=1)
- `inf_interior_lod__bldg_000094ef-deb4-4a1f-__p1`: G4_not_absent (guard n=1)
- `inf_interior_lod__bldg_000094ef-deb4-4a1f-__p2`: G4_not_absent (guard n=1)
- `inf_interior_lod__bldg_0000e4e9-a69f-4e4a-__p0`: G4_not_absent (guard n=1)
- `inf_interior_lod__bldg_0000e4e9-a69f-4e4a-__p1`: G4_not_absent (guard n=1)
- `inf_interior_lod__bldg_0000e4e9-a69f-4e4a-__p2`: G4_not_absent (guard n=1)

This gate checks executability, determinism, and absence proofs, not phrasing quality. The complementary human review of a stratified 20.2 % sample is documented in benchmark_a/human_review/.