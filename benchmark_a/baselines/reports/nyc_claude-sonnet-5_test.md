# Evaluation report — claude_code_subagent/claude-sonnet-5

- Input: `benchmark_a/baselines/eval_subsets/nyc_test.jsonl`  (18 questions: 14 feasible, 4 infeasible)
- **Execution accuracy (feasible): 50.0%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 100.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| cross_source | 3 | 33.3% |
| multihop | 1 | 0.0% |
| provenance | 2 | 100.0% |
| spatial | 8 | 50.0% |

## Execution errors

- `spatial_isolated__POLYGON((584961.10984060__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Procedure.ProcedureCallFailed} {message: Failed to invoke procedure `spatial.withinDistance`: Caused by: org.neo4j.graphdb.TransactionTerminatedException: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 52N37} {gql_status_description: error: procedure exception - procedure execution error. Execution of the procedure spatial.withinDistance() failed.}
- `spatial_isolated__POLYGON((600285.58896561__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Procedure.ProcedureCallFailed} {message: Failed to invoke procedure `spatial.withinDistance`: Caused by: org.neo4j.graphdb.TransactionTerminatedException: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 52N37} {gql_status_description: error: procedure exception - procedure execution error. Execution of the procedure spatial.withinDistance() failed.}