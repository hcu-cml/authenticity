# Evaluation report — ollama/qwen2.5-coder:7b

- Input: `benchmark_a/baselines/eval_subsets/helsinki_test.jsonl`  (32 questions: 28 feasible, 4 infeasible)
- **Execution accuracy (feasible): 10.7%**
- **Over-refusal rate (feasible questions wrongly refused): 0.0%**
- **Infeasibility recall (correctly refused / total infeasible): 0.0%**

Note: precision is reported as recall here because this run only scores the infeasible subset in isolation (a REFUSE on a feasible question is tracked separately as over-refusal, not folded into this pool) — precision/recall/F1 over the full mixed set is computed once dev+test results across categories are combined (E4).

| Category | n | EX |
| -------- | - | -- |
| aggregate | 1 | 100.0% |
| coverage | 3 | 0.0% |
| cross_source | 5 | 0.0% |
| filter_topk | 3 | 0.0% |
| multihop | 3 | 33.3% |
| provenance | 3 | 33.3% |
| spatial | 10 | 0.0% |

## Execution errors

- `spatial_bbox_count__POLYGON((2.54977485E7_66__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'ST_Within' (line 2, column 7 (offset: 25))
"WHERE ST_Within(b.location, st_polygon("
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((2.54977485E7_66__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.bbox_wkt, 'POLYGON((2.54977485E7 6676278.095, 2.5497751524499997E7 6676278.095, 2.5497751524499997E7 6676282.33, 2.54977485E7 6676282.33, 2.54977485E7 6676278.095))')"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((2.5497751524499__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_within' (line 2, column 7 (offset: 25))
"WHERE st_within(point({x: 25497751.524499997, y: 6676282.33}), b.bbox) OR"
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_count__POLYGON((2.5497751524499__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Unknown function 'st_intersects' (line 2, column 7 (offset: 64))
"WHERE st_intersects(fp.geometry, st_polygon(["
       ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_bbox_tallest__POLYGON((2.5497751524499__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '6676282.33': expected an expression or ')' (line 1, column 84 (offset: 83))
"MATCH (b:Building)-[:LOCATED_IN]->(d:District {bbox: POLYGON((2.5497751524499997E7 6676282.33, 2.5497754549E7 6676282.33, 2.5497754549E7 6676286.565, 2.5497751524499997E7 6676286.565, 2.5497751524499997E7 6676282.33))})"
                                                                                    ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((2.5497177211E7___p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '{': expected an expression, ')' or ',' (line 3, column 24 (offset: 62))
"    MATCH (b2:Building {osm_id: b1.osm_id})"
                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `spatial_isolated__POLYGON((2.54972156255E7__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '{': expected an expression, ')' or ',' (line 3, column 24 (offset: 62))
"    MATCH (b2:Building {osm_id: b1.osm_id})"
                        ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `xsrc_pois_in_building__BID_55de4f26-4b56-4bbc-a__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input 'WITHIN': expected an expression, 'ORDER BY', 'CALL', 'CREATE', 'LOAD CSV', 'DELETE', 'DETACH', 'FINISH', 'FOREACH', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REMOVE', 'RETURN', 'SET', 'SKIP', 'UNION', 'UNWIND', 'USE', 'WITH' or <EOF> (line 3, column 31 (offset: 215))
"WHERE enrichedEntity.location WITHIN building.bbox"
                               ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `prov_multi_matched__p0`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: Variable `id` not defined (line 2, column 64 (offset: 123))
"WHERE EXISTS((b)-[:ENRICHED_BY]->(osmFeature2:OsmFeature WHERE id <> osmFeature1.id))"
                                                                ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}
- `cov_share__p1`: CypherSyntaxError: {neo4j_code: Neo.ClientError.Statement.SyntaxError} {message: The property existence syntax `... exists(variable.property)` is no longer supported. Please use `variable.property IS NOT NULL` instead. (line 2, column 9 (offset: 27))
"WITH b, EXISTS(b.roof_type) AS hasRoofType"
         ^} {gql_status: 42001} {gql_status_description: error: syntax error or access rule violation - invalid syntax}