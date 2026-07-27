# AuthentiCity suite verification report

- Input: `the generated zurich question set` (259 questions)
- Passed: **259**  Failed: **0**  (stability runs: 3)

| Category | Passed | Failed |
| -------- | ------ | ------ |
| aggregate | 14 | 0 |
| cross_source | 48 | 0 |
| filter_topk | 19 | 0 |
| infeasible | 33 | 0 |
| multihop | 15 | 0 |
| provenance | 36 | 0 |
| spatial | 94 | 0 |

This gate checks executability, determinism, and absence proofs, not phrasing quality. The complementary human review of a stratified 20.2 % sample is documented in benchmark_a/human_review/.