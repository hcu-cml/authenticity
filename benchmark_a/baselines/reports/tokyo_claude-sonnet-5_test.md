# Evaluation report — claude_code_subagent/claude_subagent

- Input: `benchmark_a/baselines/eval_subsets/tokyo_test.jsonl`  (26 questions: 24 feasible, 2 infeasible)
- **Execution accuracy (feasible): 41.7%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 100.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 2 | 50.0% |
| cross_source | 5 | 20.0% |
| filter_topk | 3 | 33.3% |
| multihop | 1 | 100.0% |
| provenance | 3 | 100.0% |
| spatial | 10 | 30.0% |

## Execution errors

- `spatial_bbox_count__POLYGON((-20407.38471495__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_bbox_count__POLYGON((-20407.38471495__p1`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_bbox_tallest__POLYGON((-20407.38471495__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_isolated__POLYGON((-8555.010135286__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Procedure.ProcedureCallFailed} {message: Failed to invoke procedure `spatial.intersects`: Caused by: org.neo4j.graphdb.TransactionTerminatedException: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 52N37} {gql_status_description: error: procedure exception - procedure execution error. Execution of the procedure spatial.intersects() failed.}
- `spatial_isolated__POLYGON((-17005.67500263__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Procedure.ProcedureCallFailed} {message: Failed to invoke procedure `spatial.intersects`: Caused by: org.neo4j.graphdb.TransactionTerminatedException: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 52N37} {gql_status_description: error: procedure exception - procedure execution error. Execution of the procedure spatial.intersects() failed.}