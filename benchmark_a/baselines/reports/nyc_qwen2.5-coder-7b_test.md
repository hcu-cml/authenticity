# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/nyc_test.jsonl`  (18 questions: 14 feasible, 4 infeasible)
- **Execution accuracy (feasible): 14.3%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| cross_source | 3 | 0.0% |
| multihop | 1 | 0.0% |
| provenance | 2 | 100.0% |
| spatial | 8 | 0.0% |

## Execution errors

- `spatial_bbox_count__POLYGON((563089.37507543__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_polygonFromText' (line 2, column 9 (offset: 27))
"WITH b, st_polygonFromText('POLYGON((563089.3750754362 4483353.736483538, 586412.655668248 4483353.736483538, 586412.655668248 4506694.387437572, 563089.3750754362 4506694.387437572, 563089.3750754362 4483353.736483538))') AS bbox"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((563089.37507543__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.bbox_wkt, 'POLYGON((563089.3750754362 4483353.736483538, 586412.655668248 4483353.736483538, 586412.655668248 4506694.387437572, 563089.3750754362 4506694.387437572, 563089.3750754362 4483353.736483538))')"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((586412.65566824__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '4506694.387437572': expected an expression or ')' (line 3, column 32 (offset: 89))
"     POLYGON((586412.655668248 4506694.387437572,"
                                ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((586412.65566824__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.bbox_wkt, 'POLYGON((586412.655668248 4506694.387437572, 609735.9362610596 4506694.387437572, 609735.9362610596 4530035.038391606, 586412.655668248 4530035.038391606, 586412.655668248 4506694.387437572))')"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((584961.10984060__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '{': expected an expression, ')' or ',' (line 3, column 24 (offset: 62))
"    MATCH (b2:Building {id: b1.id})"
                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((600285.58896561__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '{': expected an expression, ')' or ',' (line 3, column 24 (offset: 121))
"    MATCH (b2:Building {lod3_confidence: apoc.convert.toFloat(b.lod3_confidence)})"
                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `xsrc_pois_in_building__gml_GN8NMRP1EO7N7IUN84E2__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Within' (line 2, column 7 (offset: 86))
"WHERE ST_Within(p.location, b.boundary)"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `xsrc_pois_in_building__gml_5UIJ8C1OFN6XG9PMFR6G__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Within' (line 3, column 7 (offset: 91))
"WHERE ST_Within(p.location, b.boundary)"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}