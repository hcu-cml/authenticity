# Evaluation report — claude_code_subagent/claude-sonnet-5

- Input: `benchmark_a/baselines/eval_subsets/zurich_dev.jsonl`  (75 questions: 65 feasible, 10 infeasible)
- **Execution accuracy (feasible): 61.5%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 90.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 6 | 83.3% |
| cross_source | 14 | 35.7% |
| filter_topk | 8 | 50.0% |
| multihop | 3 | 100.0% |
| provenance | 12 | 58.3% |
| spatial | 22 | 72.7% |