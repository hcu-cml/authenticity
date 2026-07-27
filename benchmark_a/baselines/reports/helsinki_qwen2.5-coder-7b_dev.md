# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/helsinki_dev.jsonl`  (92 questions: 82 feasible, 10 infeasible)
- **Execution accuracy (feasible): 14.6%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 8 | 25.0% |
| coverage | 2 | 0.0% |
| cross_source | 15 | 26.7% |
| filter_topk | 15 | 20.0% |
| multihop | 6 | 50.0% |
| provenance | 12 | 0.0% |
| spatial | 24 | 0.0% |

## Execution errors

- `agg_avg_height__p1`: CypherTypeError: {neo4j_code: Neo.ClientError.Statement.TypeError} {message: AVG(NodeProperty(0,217)) can only handle numerical values, duration, or null, but received: String} {gql_status: 22N38} {gql_status_description: error: data exception - invalid function argument. Invalid argument to the function AVG(NodeProperty(0,217)).}
- `agg_median_height__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'OF': expected an expression, ',', 'AS', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 2, column 28 (offset: 89))
"RETURN percentileDisc(0.5) OF b.height AS median_height"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__4.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '4.0': expected a node label/relationship type name, '$', '%' or '(' (line 1, column 42 (offset: 41))
"MATCH (b:Building {height: greater_than: 4.0})"
                                          ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__10.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'WHEREtoFloat': expected a graph pattern, ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'USING', 'WHERE', 'WITH' or <EOF> (line 2, column 1 (offset: 40))
"WHEREtoFloat(b.osm_height) > 10.0"
 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_neighbours__BID_001328a4-3279-492c-9__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 3, column 7 (offset: 105))
"WHERE distance(b.location, otherBuilding.location) <= 100"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_neighbours__BID_0019d516-d07e-4315-9__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 3, column 38 (offset: 136))
"WHERE id(otherBuilding) <> id(b) AND distance(point({x: b.location.x, y: b.location.y}), point({x: otherBuilding.location.x, y: otherBuilding.location.y})) <= 100"
                                      ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2.549742721E7,6674530.98_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Centroid' (line 2, column 9 (offset: 27))
"WITH b, ST_Centroid(b.location) AS centroid"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2.549742721E7,6674530.98_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance' (line 2, column 9 (offset: 27))
"WITH b, ST_Distance(b.location, point({x: 2.549742721E7, y: 6674530.98})) AS distance"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2.549746563E7,6674718.64_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Centroid' (line 2, column 9 (offset: 27))
"WITH b, ST_Centroid(b.location) AS centroid"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__2.549746563E7,6674718.64_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance' (line 2, column 9 (offset: 27))
"WITH b, ST_Distance(b.location, point({x: 2.549746563E7, y: 6674718.64})) AS distance"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__BID_001328a4-3279-492c-9_5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 4, column 15 (offset: 118))
"RETURN b2.id, distance(b1.location, b2.location) AS distance_m"
               ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__BID_001328a4-3279-492c-9_10__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance' (line 5, column 17 (offset: 207))
"RETURN other_b, ST_Distance(target_location, other_b.location) AS distance"
                 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__BID_0019d516-d07e-4315-9_5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 4, column 12 (offset: 115))
"RETURN b2, distance(b1.location, b2.location) AS distance_m"
            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__BID_0019d516-d07e-4315-9_10__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Variable `b` not defined (line 5, column 29 (offset: 205))
"RETURN other_b.id, distance(b.location, other_b.location) AS distance_m"
                             ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_by_rooftype__POLYGON((2.54977485E7_66__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_contains' (line 2, column 7 (offset: 57))
"WHERE st_contains(st_polygon([2.54977485E7, 6676278.095, 2.5497751524499997E7, 6676278.095, 2.5497751524499997E7, 6676282.33, 2.54977485E7, 6676282.33, 2.54977485E7, 6676278.095]), b.location)"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}