# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/nyc_dev.jsonl`  (49 questions: 39 feasible, 10 infeasible)
- **Execution accuracy (feasible): 10.3%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 3 | 66.7% |
| cross_source | 8 | 25.0% |
| multihop | 3 | 0.0% |
| provenance | 9 | 0.0% |
| spatial | 16 | 0.0% |

## Execution errors

- `multihop_building_parts__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: A pattern expression should only be used in order to test the existence of a pattern. It can no longer be used inside the function size(), an alternative is to replace size() with COUNT {}. (line 2, column 14 (offset: 32))
"WITH b, size((b)-[:HAS_BOUNDARY]->()) AS boundary_count"
              ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_neighbours__gml_0004F7HL773S7RHQKNZZ__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 3, column 28 (offset: 116))
"WHERE id(b1) <> id(b2) AND distance(b1.location, b2.location) <= 100"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_neighbours__gml_0006DE955I2I8YDHQLQY__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 3, column 28 (offset: 116))
"WHERE id(b1) <> id(b2) AND distance(b1.location, b2.location) <= 100"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__585211.11,4503701.94_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Too many parameters for function 'point' (line 2, column 33 (offset: 51))
"WITH b, ST_Distance(b.location, POINT(585211.11, 4503701.94)) AS distance"
                                 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__585211.11,4503701.94_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Centroid' (line 2, column 9 (offset: 27))
"WITH b, ST_Centroid(b.location) AS centroid"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__600535.59,4510221.03_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance' (line 2, column 9 (offset: 27))
"WITH b, ST_Distance(b.location, point({x: 600535.59, y: 4510221.03})) AS distance"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__600535.59,4510221.03_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Too many parameters for function 'point' (line 2, column 56 (offset: 74))
"WITH b, distance(point({x: 600535.59, y: 4510221.03}), point(b.center_x, b.center_y)) AS dist"
                                                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__gml_0004F7HL773S7RHQKNZZ_5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 7, column 18 (offset: 342))
"RETURN building, distance(building.location, target_location) AS distance"
                  ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__gml_0004F7HL773S7RHQKNZZ_10__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'AS': expected a graph pattern, ',', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'USING', 'WHERE', 'WITH' or <EOF> (line 1, column 73 (offset: 72))
"MATCH (b:Building {gml_id: 'gml_0004F7HL773S7RHQKNZZBQHZE6XZCCY12H7I'}) AS sourceBuilding,"
                                                                         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__gml_0006DE955I2I8YDHQLQY_5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Variable `b` not defined (line 5, column 29 (offset: 205))
"RETURN other_b.id, distance(b.location, other_b.location) AS distance"
                             ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__gml_0006DE955I2I8YDHQLQY_10__p0`: ClientError: {neo4j_code: Neo.ClientError.Procedure.ProcedureNotFound} {message: There is no procedure with the name `spatial.proximity` registered for this database instance. Please ensure you've spelled the procedure name correctly and that the procedure is properly deployed.} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_near_water__586797.37,4514731.05_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 4, column 7 (offset: 138))
"WHERE distance(p.location, w.location) <= 50"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_near_water__586797.37,4514731.05_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 4, column 7 (offset: 138))
"WHERE distance(p.location, w.location) <= 100"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_near_water__586625.2,4514296.54_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 4, column 7 (offset: 137))
"WHERE distance(p.location, w.location) <= 50"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_near_water__586625.2,4514296.54_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 4, column 7 (offset: 137))
"WHERE distance(p.location, w.location) <= 100"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}