# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/tokyo_dev.jsonl`  (77 questions: 67 feasible, 10 infeasible)
- **Execution accuracy (feasible): 6.0%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 6 | 33.3% |
| cross_source | 11 | 18.2% |
| filter_topk | 10 | 0.0% |
| lod3 | 1 | 0.0% |
| multihop | 8 | 0.0% |
| provenance | 9 | 0.0% |
| spatial | 22 | 0.0% |

## Execution errors

- `agg_avg_height__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Variable `exists` not defined (line 1, column 28 (offset: 27))
"MATCH (b:Building {height: exists})"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `agg_median_height__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'OF': expected an expression, ',', 'AS', 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 2, column 28 (offset: 65))
"RETURN percentileDisc(0.5) OF b.height AS median_height"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__7.0__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'greater_than' (line 1, column 28 (offset: 27))
"MATCH (b:Building {height: greater_than(7.0)})"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__7.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'greater_than' (line 1, column 28 (offset: 27))
"MATCH (b:Building {height: greater_than(7.0)})"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__8.0__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'greater_than' (line 1, column 28 (offset: 27))
"MATCH (b:Building {height: greater_than(8.0)})"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `filter_taller_than__8.0__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'greater_than' (line 1, column 28 (offset: 27))
"MATCH (b:Building {height: greater_than(8.0)})"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_agg__POLYGON((-48814.75481391__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_contains' (line 2, column 7 (offset: 64))
"WHERE st_contains(st_polygon([[-48814.7548139157, -53996.535346736775], [-20407.384714955533, -53996.535346736775], [-20407.384714955533, -36747.609899070085], [-48814.7548139157, -36747.609899070085], [-48814.7548139157, -53996.535346736775]]), st_polygon(fp.coordinates))"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_agg__POLYGON((-20407.38471495__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_contains' (line 2, column 7 (offset: 64))
"WHERE st_contains(st_polygon([[-20407.384714955533, -36747.609899070085], [7999.985384004634, -36747.609899070085], [7999.985384004634, -19498.6844514034], [-20407.384714955533, -19498.6844514034], [-20407.384714955533, -36747.609899070085]]), st_polygon(fp.coordinates))"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_neighbours__bldg_0000019b-2a5b-413a-__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Distance_Sphere' (line 6, column 7 (offset: 267))
"WHERE ST_Distance_Sphere(point(g1), point(g2)) <= 100"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_neighbours__bldg_000002e4-0c5f-4f8b-__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Type mismatch: expected Map, Node or Relationship but was Boolean, Float, Integer, Number, Point, String, Duration, Date, Time, LocalTime, LocalDateTime, DateTime, Vector, List<Boolean>, List<Float>, List<Integer>, List<Number>, List<Point>, List<String>, List<Duration>, List<Date>, List<Time>, List<LocalTime>, List<LocalDateTime> or List<DateTime> (line 3, column 47 (offset: 136))
"WHERE b1 <> b2 AND ST_Distance_Sphere(point(b1.centroid), point(b2.centroid)) <= 100"
                                               ^} {gql_status: 22G03} {gql_status_description: error: data exception - invalid value type}
- `spatial_within_distance_point__-8305.01,-50303.03_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Too many parameters for function 'point' (line 2, column 28 (offset: 46))
"WITH b, ST_Distance_Sphere(point(-8305.01, -50303.03), b.location) AS distance"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__-8305.01,-50303.03_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Too many parameters for function 'point' (line 3, column 26 (offset: 88))
"WHERE ST_Distance_Sphere(point(-8305.01, -50303.03), centroid) <= 100"
                          ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__-16755.68,-26363.55_50__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Too many parameters for function 'point' (line 2, column 28 (offset: 46))
"WITH b, ST_Distance_Sphere(point(-16755.68, -26363.55), b.location) AS distance"
                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_within_distance_point__-16755.68,-26363.55_100__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Too many parameters for function 'point' (line 3, column 26 (offset: 88))
"WHERE ST_Distance_Sphere(point(-16755.68, -26363.55), centroid) <= 100"
                          ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_knearest__bldg_0000019b-2a5b-413a-_5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: 'distance' has been replaced by 'point.distance' (line 5, column 15 (offset: 175))
"RETURN b2.id, distance(point({x: sourceLocation[0].longitude, y: sourceLocation[0].latitude}), point({x: b2.location.longitude, y: b2.location.latitude})) AS distance"
               ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}