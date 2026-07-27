# Evaluation report — claude_code_subagent/claude-sonnet-5

- Input: `benchmark_a/baselines/eval_subsets/zurich_test.jsonl`  (24 questions: 20 feasible, 4 infeasible)
- **Execution accuracy (feasible): 60.0%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 100.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| cross_source | 4 | 25.0% |
| filter_topk | 1 | 100.0% |
| multihop | 1 | 0.0% |
| provenance | 4 | 100.0% |
| spatial | 10 | 60.0% |