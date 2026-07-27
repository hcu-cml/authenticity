# Evaluation report — claude_code_subagent/claude-sonnet-5-subagent

- Input: `benchmark_a/baselines/eval_subsets/helsinki_test.jsonl`  (32 questions: 28 feasible, 4 infeasible)
- **Execution accuracy (feasible): 42.9%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 50.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 1 | 100.0% |
| coverage | 3 | 33.3% |
| cross_source | 5 | 20.0% |
| filter_topk | 3 | 33.3% |
| multihop | 3 | 100.0% |
| provenance | 3 | 100.0% |
| spatial | 10 | 20.0% |