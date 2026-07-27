# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/zurich_dev.jsonl`  (75 questions: 65 feasible, 10 infeasible)
- **Execution accuracy (feasible): 9.2%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 6 | 33.3% |
| cross_source | 14 | 28.6% |
| filter_topk | 8 | 0.0% |
| multihop | 3 | 0.0% |
| provenance | 12 | 0.0% |
| spatial | 22 | 0.0% |

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
- `filter_taller_than__7.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'WHEREtoFloat': expected a graph pattern, ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'USING', 'WHERE', 'WITH' or <EOF> (line 2, column 1 (offset: 39))
"WHEREtoFloat(b.osm_height) > 7.0"
 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__9.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'WHEREtoFloat': expected a graph pattern, ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'USING', 'WHERE', 'WITH' or <EOF> (line 2, column 1 (offset: 39))
"WHEREtoFloat(b.osm_height) > 9.0"
 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `topk_tallest__5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, ',' or '}' (line 1, column 35 (offset: 34))
"MATCH (b:Building {osm_height: IS NOT NULL})"
                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `topk_tallest__5__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, ',' or '}' (line 1, column 35 (offset: 34))
"MATCH (b:Building {osm_height: IS NOT NULL})"
                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `topk_tallest__10__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, ',' or '}' (line 1, column 35 (offset: 34))
"MATCH (b:Building {osm_height: IS NOT NULL})"
                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `topk_tallest__10__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'OR': expected ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 2, column 61 (offset: 79))
"RETURN b.name AS building_name, b.height AS building_height OR b.osm_height AS building_height"
                                                             ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_neighbours__ID_00001DB9-565B-4C0A-B2__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 2, column 28 (offset: 110))
"WHERE id(b1) <> id(b2) AND distance(point({x: b1.location.x, y: b1.location.y}), point({x: b2.location.x, y: b2.location.y})) <= 100"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2693476.26,1279116.11_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance' (line 2, column 7 (offset: 64))
"WHERE ST_Distance(point({x: 2693476.26, y: 1279116.11}), fp.location) <= 50"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2693476.26,1279116.11_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Too many parameters for function 'point' (line 3, column 19 (offset: 117))
"WHERE ST_Distance(point(2693476.26, 1279116.11), building_location) <= 100"
                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2681824.32,1253198.78_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance' (line 2, column 7 (offset: 64))
"WHERE ST_Distance(point({x: 2681824.32, y: 1253198.78}), fp.location) <= 50"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2681824.32,1253198.78_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance' (line 2, column 7 (offset: 64))
"WHERE ST_Distance(point({x: 2681824.32, y: 1253198.78}), fp.location) <= 100"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__ID__5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Variable `id` not defined (line 8, column 15 (offset: 170))
"  nodeFilter: id <> 'ID_'"
               ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}