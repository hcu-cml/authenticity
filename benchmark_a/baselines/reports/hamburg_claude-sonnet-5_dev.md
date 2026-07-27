# Evaluation report — claude_code_subagent/claude-sonnet-5-subagent

- Input: `benchmark_a/baselines/eval_subsets/hamburg_dev.jsonl`  (99 questions: 89 feasible, 10 infeasible)
- **Execution accuracy (feasible): 60.7%**
- **Over-refusal rate (feasible questions wrongly refused): 6.7%**
- **Infeasibility recall (correctly refused / total infeasible): 90.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 6 | 83.3% |
| coverage | 6 | 50.0% |
| cross_source | 15 | 40.0% |
| filter_topk | 15 | 66.7% |
| lod3 | 4 | 100.0% |
| multihop | 6 | 66.7% |
| provenance | 13 | 30.8% |
| spatial | 24 | 75.0% |