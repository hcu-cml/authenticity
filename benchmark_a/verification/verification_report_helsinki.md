# AuthentiCity suite verification report

- Input: `the generated helsinki question set` (319 questions)
- Passed: **319**  Failed: **0**  (stability runs: 3)

| Category | Passed | Failed |
| -------- | ------ | ------ |
| aggregate | 29 | 0 |
| cross_source | 54 | 0 |
| filter_topk | 43 | 0 |
| infeasible | 33 | 0 |
| multihop | 27 | 0 |
| provenance | 33 | 0 |
| spatial | 100 | 0 |

This gate checks executability, determinism, and absence proofs, not phrasing quality. The complementary human review of a stratified 20.2 % sample is documented in benchmark_a/human_review/.