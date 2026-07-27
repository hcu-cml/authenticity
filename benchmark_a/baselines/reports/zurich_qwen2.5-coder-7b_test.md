# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/zurich_test.jsonl`  (24 questions: 20 feasible, 4 infeasible)
- **Execution accuracy (feasible): 15.0%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| cross_source | 4 | 0.0% |
| filter_topk | 1 | 0.0% |
| multihop | 1 | 0.0% |
| provenance | 4 | 50.0% |
| spatial | 10 | 10.0% |

## Execution errors

- `spatial_bbox_count__POLYGON((2668076.375_122__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '1224001.7138999999': expected an expression or ')' (line 3, column 57 (offset: 112))
"WHERE ST_Within(building_location, POLYGON((2668076.375 1224001.7138999999, 2694352.789550001 1224001.7138999999, 2694352.789550001 1254014.7397499997, 2668076.375 1254014.7397499997, 2668076.375 1224001.7138999999)))"
                                                         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((2668076.375_122__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.location, st_polygon(["
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((2694352.7895500__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'WITHIN': expected an expression, 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 2, column 18 (offset: 36))
"WHERE b.location WITHIN POLYGON((2694352.789550001 1254014.7397499997, 2720629.2041000016 1254014.7397499997, 2720629.2041000016 1284027.7655999996, 2694352.789550001 1284027.7655999996, 2694352.789550001 1254014.7397499997))"
                  ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((2694352.7895500__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.location, st_polygon(["
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_tallest__POLYGON((2668076.375_122__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '1224001.7138999999': expected an expression or ')' (line 1, column 75 (offset: 74))
"MATCH (b:Building)-[:LOCATED_IN]->(d:District {bbox: POLYGON((2668076.375 1224001.7138999999, 2694352.789550001 1224001.7138999999, 2694352.789550001 1254014.7397499997, 2668076.375 1254014.7397499997, 2668076.375 1224001.7138999999))})"
                                                                           ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_tallest__POLYGON((2694352.7895500__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '1254014.7397499997': expected an expression or ')' (line 1, column 81 (offset: 80))
"MATCH (b:Building)-[:LOCATED_IN]->(d:District {bbox: POLYGON((2694352.789550001 1254014.7397499997, 2720629.2041000016 1254014.7397499997, 2720629.2041000016 1284027.7655999996, 2694352.789550001 1284027.7655999996, 2694352.789550001 1254014.7397499997))})"
                                                                                 ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((2681574.3183500__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '1252948.7803000007': expected an expression or ')' (line 1, column 60 (offset: 59))
"MATCH (b1:Building {footprint: POLYGON((2681574.3183500003 1252948.7803000007, 2682074.3183500003 1252948.7803000007, 2682074.3183500003 1253448.7803000007, 2681574.3183500003 1253448.7803000007, 2681574.3183500003 1252948.7803000007))})"
                                                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `prov_only_authoritative__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'AVGtoFloat' (line 2, column 8 (offset: 45))
"RETURN AVGtoFloat(b.osm_height) AS average_building_height"
        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `prov_zurich_revised_count__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, ',' or '}' (line 1, column 40 (offset: 39))
"MATCH (b:Building {grund_aenderung: IS NOT NULL})"
                                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}