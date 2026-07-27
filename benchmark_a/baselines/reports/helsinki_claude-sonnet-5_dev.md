# Evaluation report — claude_code_subagent/claude-sonnet-5-subagent

- Input: `benchmark_a/baselines/eval_subsets/helsinki_dev.jsonl`  (92 questions: 82 feasible, 10 infeasible)
- **Execution accuracy (feasible): 56.1%**
- **Over-refusal rate (feasible questions wrongly refused): 4.9%**
- **Infeasibility recall (correctly refused / total infeasible): 90.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 8 | 50.0% |
| coverage | 2 | 0.0% |
| cross_source | 15 | 40.0% |
| filter_topk | 15 | 66.7% |
| multihop | 6 | 33.3% |
| provenance | 12 | 50.0% |
| spatial | 24 | 75.0% |