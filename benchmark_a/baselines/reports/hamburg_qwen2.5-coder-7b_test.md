# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/hamburg_test.jsonl`  (31 questions: 29 feasible, 2 infeasible)
- **Execution accuracy (feasible): 20.7%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 1 | 100.0% |
| coverage | 3 | 0.0% |
| cross_source | 5 | 0.0% |
| filter_topk | 3 | 0.0% |
| lod3 | 2 | 0.0% |
| multihop | 2 | 50.0% |
| provenance | 3 | 66.7% |
| spatial | 10 | 20.0% |

## Execution errors

- `spatial_bbox_count__POLYGON((466355.917_5917__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.pos_list, 'POLYGON((466355.917 5917227.923, 526983.8435 5917227.923, 526983.8435 5946574.7075, 466355.917 5946574.7075, 466355.917 5917227.923))')"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((526983.8435_594__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_polygonFromText' (line 2, column 9 (offset: 27))
"WITH b, st_polygonFromText('POLYGON((526983.8435 5946574.7075, 587611.77 5946574.7075, 587611.77 5975921.492, 526983.8435 5975921.492, 526983.8435 5946574.7075))') AS bbox"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((526983.8435_594__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.pos_list, 'POLYGON((526983.8435 5946574.7075, 587611.77 5946574.7075, 587611.77 5975921.492, 526983.8435 5975921.492, 526983.8435 5946574.7075))')"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((565086.45800000__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input ':': expected an expression (line 5, column 29 (offset: 361))
"    MATCH (other:Building)-[:HAS_FOOTPRINT]->(other_fp:GeometryPolygon)"
                             ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((560172.571_5943__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '5943187.8865': expected an expression or ')' (line 3, column 83 (offset: 217))
"AND EXISTS((b1)-[:HAS_FOOTPRINT]->(:GeometryPolygon {polygon: POLYGON((560172.571 5943187.8865, 560672.571 5943187.8865, 560672.571 5943687.8865, 560172.571 5943687.8865, 560172.571 5943187.8865))}))"
                                                                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `cov_share__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'count': expected an expression (line 4, column 44 (offset: 156))
"       count(DISTINCT b) * 100.0 / (SELECT count(DISTINCT id) FROM Building) AS percentage"
                                            ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `cov_share__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: The property existence syntax `... exists(variable.property)` is no longer supported. Please use `variable.property IS NOT NULL` instead. (line 2, column 9 (offset: 27))
"WITH b, EXISTS(b.roof_type) AS hasRoofType"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `lod3_openings_per_wall__DEHHALKA4Ti000DB__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: A pattern expression should only be used in order to test the existence of a pattern. It can no longer be used inside the function size(), an alternative is to replace size() with COUNT {}. (line 2, column 20 (offset: 140))
"WITH bs, l3f, size((l3f)-[:HAS_OPENING]->()) AS openingCount"
                    ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `lod3_openings_per_wall__DEHHALKAJ0000opO__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: A pattern expression should only be used in order to test the existence of a pattern. It can no longer be used inside the function size(), an alternative is to replace size() with COUNT {}. (line 2, column 19 (offset: 137))
"WITH bs, gs, size((gs)-[:HAS_SURFACE_MEMBER]->(:Lod3Facade)-[:HAS_OPENING]->()) AS num_openings"
                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}