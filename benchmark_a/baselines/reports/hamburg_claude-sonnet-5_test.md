# Evaluation report — claude_code_subagent/claude-sonnet-5

- Input: `benchmark_a/baselines/eval_subsets/hamburg_test.jsonl`  (31 questions: 29 feasible, 2 infeasible)
- **Execution accuracy (feasible): 58.6%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 100.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 1 | 100.0% |
| coverage | 3 | 33.3% |
| cross_source | 5 | 20.0% |
| filter_topk | 3 | 33.3% |
| lod3 | 2 | 100.0% |
| multihop | 2 | 100.0% |
| provenance | 3 | 100.0% |
| spatial | 10 | 60.0% |