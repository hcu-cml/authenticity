# AuthentiCity suite verification report

- Input: `the generated nyc question set` (179 questions)
- Passed: **179**  Failed: **0**  (stability runs: 3)

| Category | Passed | Failed |
| -------- | ------ | ------ |
| aggregate | 7 | 0 |
| cross_source | 36 | 0 |
| infeasible | 33 | 0 |
| multihop | 12 | 0 |
| provenance | 21 | 0 |
| spatial | 70 | 0 |

This gate checks executability, determinism, and absence proofs, not phrasing quality. The complementary human review of a stratified 20.2 % sample is documented in benchmark_a/human_review/.