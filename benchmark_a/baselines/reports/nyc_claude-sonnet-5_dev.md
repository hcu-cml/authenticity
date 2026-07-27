# Evaluation report — claude_code_subagent/claude-sonnet-5

- Input: `benchmark_a/baselines/eval_subsets/nyc_dev.jsonl`  (49 questions: 39 feasible, 10 infeasible)
- **Execution accuracy (feasible): 69.2%**
- **Over-refusal rate (feasible questions wrongly refused): 2.6%**
- **Infeasibility recall (correctly refused / total infeasible): 90.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 3 | 66.7% |
| cross_source | 8 | 62.5% |
| multihop | 3 | 66.7% |
| provenance | 9 | 66.7% |
| spatial | 16 | 75.0% |