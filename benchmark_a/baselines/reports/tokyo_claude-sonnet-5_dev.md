# Evaluation report — claude_code_subagent/claude_subagent_full

- Input: `benchmark_a/baselines/eval_subsets/tokyo_dev.jsonl`  (77 questions: 67 feasible, 10 infeasible)
- **Execution accuracy (feasible): 53.7%**
- **Over-refusal rate (feasible questions wrongly refused): 1.5%**
- **Infeasibility recall (correctly refused / total infeasible): 90.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 6 | 83.3% |
| cross_source | 11 | 45.5% |
| filter_topk | 10 | 60.0% |
| lod3 | 1 | 0.0% |
| multihop | 8 | 50.0% |
| provenance | 9 | 44.4% |
| spatial | 22 | 54.5% |

## Execution errors

- `spatial_bbox_agg__POLYGON((-20407.38471495__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_knearest__bldg_0000019b-2a5b-413a-_5__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_knearest__bldg_0000019b-2a5b-413a-_10__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_knearest__bldg_000002e4-0c5f-4f8b-_5__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_knearest__bldg_000002e4-0c5f-4f8b-_10__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}