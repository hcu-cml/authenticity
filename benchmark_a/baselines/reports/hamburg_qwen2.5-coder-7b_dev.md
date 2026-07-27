# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/hamburg_dev.jsonl`  (99 questions: 89 feasible, 10 infeasible)
- **Execution accuracy (feasible): 19.1%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 6 | 33.3% |
| coverage | 6 | 0.0% |
| cross_source | 15 | 26.7% |
| filter_topk | 15 | 6.7% |
| lod3 | 4 | 100.0% |
| multihop | 6 | 33.3% |
| provenance | 13 | 0.0% |
| spatial | 24 | 16.7% |

## Execution errors

- `agg_avg_height__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, ',' or '}' (line 1, column 35 (offset: 34))
"MATCH (b:Building {osm_height: IS NOT NULL})"
                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `agg_avg_height__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, ',' or '}' (line 1, column 35 (offset: 34))
"MATCH (b:Building {osm_height: IS NOT NULL})"
                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `agg_median_height__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, ',' or '}' (line 1, column 35 (offset: 34))
"MATCH (b:Building {osm_height: IS NOT NULL})"
                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__3.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'WHEREtoFloat': expected a graph pattern, ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'USING', 'WHERE', 'WITH' or <EOF> (line 2, column 1 (offset: 39))
"WHEREtoFloat(b.osm_height) > 3.0"
 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__8.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'WHEREtoFloat': expected a graph pattern, ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'USING', 'WHERE', 'WITH' or <EOF> (line 2, column 1 (offset: 39))
"WHEREtoFloat(b.osm_height) > 8.0"
 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `topk_tallest__5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'apoc.text.toDouble' (line 1, column 32 (offset: 31))
"MATCH (b:Building {osm_height: apoc.text.toDouble(b.osm_height)})"
                                ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `topk_tallest__10__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Variable `osm_height` not defined (line 1, column 51 (offset: 50))
"MATCH (b:Building {osm_height: apoc.text.toDouble(osm_height)})"
                                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_compound__3.0_Flat_Roof__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '{': expected an expression, ')' or ',' (line 2, column 49 (offset: 67))
"WHERE b.osm_height > 3.0 AND EXISTS(b.roof_type {name: 'Flat Roof'})"
                                                 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_compound__8.0_Flat_Roof__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Variable `RoofType` not defined (line 2, column 46 (offset: 64))
"WHERE b.osm_height > 8.0 AND b.has_roof_type(RoofType {name: 'Flat Roof'})"
                                              ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `multihop_function_avg_height__p0`: CypherTypeError: {neo4j_code: Neo.ClientError.Statement.TypeError} {message: AVG(NodeProperty(1,133)) can only handle numerical values, duration, or null, but received: String} {gql_status: 22N38} {gql_status_description: error: data exception - invalid function argument. Invalid argument to the function AVG(NodeProperty(1,133)).}
- `multihop_building_parts__p0`: QUERY_TIMEOUT: {neo4j_code: Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration} {message: The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout. } {gql_status: 25N14} {gql_status_description: error: invalid transaction state - transaction termination client error. The transaction has been terminated. Retry your operation in a new transaction, and you should see a successful result. Reason: The transaction has not completed within the timeout specified at its start by the client. You may want to retry with a longer timeout.}
- `spatial_bbox_agg__POLYGON((466355.917_5917__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: The property existence syntax `... exists(variable.property)` is no longer supported. Please use `variable.property IS NOT NULL` instead. (line 2, column 7 (offset: 53))
"WHERE EXISTS(b.height) // Assuming 'height' is a property on the Building node"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_agg__POLYGON((526983.8435_594__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'ST_INTERSECTS': expected an expression, 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 2, column 18 (offset: 64))
"WHERE d.bbox_wkt ST_INTERSECTS POLYGON((526983.8435 5946574.7075, 587611.77 5946574.7075, 587611.77 5975921.492, 526983.8435 5975921.492, 526983.8435 5946574.7075))"
                  ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__565336.46,5934209.53_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Type mismatch: expected Map, Node or Relationship but was Boolean, Float, Integer, Number, Point, String, Duration, Date, Time, LocalTime, LocalDateTime, DateTime, Vector, List<Boolean>, List<Float>, List<Integer>, List<Number>, List<Point>, List<String>, List<Duration>, List<Date>, List<Time>, List<LocalTime>, List<LocalDateTime> or List<DateTime> (line 2, column 67 (offset: 110))
"WHERE poi.pos_list = '565336.46 5934209.53' AND distance(point(poi.pos_list), point('565336.46,5934209.53')) <= 50"
                                                                   ^} {gql_status: 22G03} {gql_status_description: error: data exception - invalid value type}
- `spatial_within_distance_point__565336.46,5934209.53_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Type mismatch: expected Map, Node or Relationship but was Boolean, Float, Integer, Number, Point, String, Duration, Date, Time, LocalTime, LocalDateTime, DateTime, Vector, List<Boolean>, List<Float>, List<Integer>, List<Number>, List<Point>, List<String>, List<Duration>, List<Date>, List<Time>, List<LocalTime>, List<LocalDateTime> or List<DateTime> (line 3, column 87 (offset: 155))
"WHERE ST_Distance_Sphere(point({longitude: 565336.46, latitude: 5934209.53}), point(fp.pos_list)) <= 100"
                                                                                       ^} {gql_status: 22G03} {gql_status_description: error: data exception - invalid value type}