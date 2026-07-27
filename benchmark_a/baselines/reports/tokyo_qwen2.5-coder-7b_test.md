# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/tokyo_test.jsonl`  (26 questions: 24 feasible, 2 infeasible)
- **Execution accuracy (feasible): 12.5%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 2 | 50.0% |
| cross_source | 5 | 0.0% |
| filter_topk | 3 | 0.0% |
| multihop | 1 | 100.0% |
| provenance | 3 | 33.3% |
| spatial | 10 | 0.0% |

## Execution errors

- `spatial_bbox_count__POLYGON((-48814.75481391__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_polygon' (line 2, column 9 (offset: 27))
"WITH b, st_polygon(["
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((-48814.75481391__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input ']': expected an expression, ')' or ',' (line 2, column 259 (offset: 316))
"WHERE st_intersects(fp.geometry, st_polygon([[-48814.7548139157, -53996.535346736775], [-20407.384714955533, -53996.535346736775], [-20407.384714955533, -36747.609899070085], [-48814.7548139157, -36747.609899070085], [-48814.7548139157, -53996.535346736775]]]))"
                                                                                                                                                                                                                                                                   ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((-20407.38471495__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 3, column 7 (offset: 74))
"WHERE st_intersects(st_polygon([[-20407.384714955533, -36747.609899070085], [7999.985384004634, -36747.609899070085], [7999.985384004634, -19498.6844514034], [-20407.384714955533, -19498.6844514034], [-20407.384714955533, -36747.609899070085]]), st_polygonFromWKT(bs.geometry.wkt))"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((-20407.38471495__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 3, column 7 (offset: 75))
"WHERE st_intersects(st_envelope(fp.geometry), st_polygon([[-20407.384714955533, -36747.609899070085], [7999.985384004634, -36747.609899070085], [7999.985384004634, -19498.6844514034], [-20407.384714955533, -19498.6844514034], [-20407.384714955533, -36747.609899070085]]))"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_tallest__POLYGON((-48814.75481391__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input ',': expected an expression or ')' (line 1, column 104 (offset: 103))
"MATCH (b:Building)-[:LOCATED_IN]->(d:District {boundary: POLYGON((-48814.7548139157 -53996.535346736775, -20407.384714955533 -53996.535346736775, -20407.384714955533 -36747.609899070085, -48814.7548139157 -36747.609899070085, -48814.7548139157 -53996.535346736775))})"
                                                                                                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_tallest__POLYGON((-20407.38471495__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input ',': expected an expression or ')' (line 2, column 72 (offset: 118))
"WHERE d.bounding_box = POLYGON((-20407.384714955533 -36747.609899070085, 7999.985384004634 -36747.609899070085, 7999.985384004634 -19498.6844514034, -20407.384714955533 -19498.6844514034, -20407.384714955533 -36747.609899070085))"
                                                                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_roof_complexity__5__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'g': expected an expression (line 2, column 20 (offset: 83))
"WHERE s IN (SELECT g FROM (UNWIND b.has_lod_surface AS g) WHERE g IS NOT NULL AND g:GeometryPolygon)"
                    ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_roof_complexity__10__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'g': expected an expression (line 2, column 20 (offset: 83))
"WHERE s IN (SELECT g FROM (UNWIND b.has_lod_surface AS g) WHERE g IS NOT NULL AND g:GeometryPolygon)"
                    ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((-8555.010135286__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '{': expected an expression, ')' or ',' (line 3, column 24 (offset: 62))
"    MATCH (b2:Building {id: b1.id})"
                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((-17005.67500263__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input ':': expected an expression (line 3, column 26 (offset: 124))
"    MATCH (b2:Building)-[:HAS_FOOTPRINT]->(fp2:GeometryPolygon)"
                          ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `xsrc_mean_abs_deviation__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: The property existence syntax `... exists(variable.property)` is no longer supported. Please use `variable.property IS NOT NULL` instead. (line 2, column 7 (offset: 54))
"WHERE EXISTS(b.height_osm) AND EXISTS(b.height_surveyed)"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `prov_secondary_edges__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'NOT': expected an expression, 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 2, column 15 (offset: 31))
"WHERE type(r) NOT IN ['HAS_LOD_SOLID', 'HAS_LOD_SURFACE', 'LOCATED_IN', 'PART_OF', 'ENRICHED_BY', 'HAS_BOUNDARY', 'HAS_POI', 'HAS_OUTER_INSTALLATION', 'HAS_FOOTPRINT', 'HAS_INTERIOR_RING', 'HAS_LOD_GEOMETRY', 'HAS_NESTED']"
               ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `tokyo_jp_numeric_attr__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'apoc.number.between' (line 1, column 37 (offset: 36))
"MATCH (b:Building {lod3_confidence: apoc.number.between(0, 1)})"
                                     ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}