# Lossless CityGML round-trip census

Does the graph preserve the source document, or only a convenient projection of it? Each source file is ingested into Neo4j, exported back to CityGML from the graph alone, and the two documents are compared at four levels: every element local name, every `(attribute, value)` pair, every leaf text node, and every coordinate token.

The bar is semantic completeness rather than byte identity: `gml:pos` against `gml:posList` encoding may differ and element order within a feature is not significant, since the comparison is over multisets. The appearance and material module is out of scope and excluded from every count.

Two reference models cover the two axes that matter. FZK-Haus exercises every level of detail; the Railway Scene exercises every thematic module. "Missing (naive)" is a documented baseline from a naive CityGML-to-graph mapping, kept to show what the fidelity-preserving mapping actually buys; it is not re-derivable now, because that mapping was replaced.

## Axis 1: level of detail (FZK-Haus, LoD 0 to 4)

| LoD | Dominant new construct | Source instances | Missing, naive mapping | Missing, released mapping |
| --: | --- | --: | --: | --: |
| 0 | footprint, roof edge, address | 117 | 79 | **0** |
| 1 | `lod1Solid` | 193 | 145 | **0** |
| 2 | typed boundary surfaces | 276 | 53 | **0** |
| 3 | openings, composite surfaces | 5,306 | 828 | **0** |
| 4 | full interior, orientable surfaces | 275,366 | 270,887 | **0** |

A naive mapping loses up to 270,887 instances at LoD4. The released mapping loses none at any level.

## Axis 2: thematic modules (Railway Scene LoD3)

52 top-level features across ten CityGML modules. LandUse is also supported but does not occur in this scene.

| Module | Features | Distinctive construct exercised | Missing |
| --- | --: | --- | --: |
| Building | 3 | LoD3 openings, boundary surfaces, installations | **0** |
| Bridge | 4 | nested construction elements, installations | **0** |
| Tunnel | 4 | nested installations, closure surfaces | **0** |
| Transportation | 10 | surface-only LoD geometry (Railway) | **0** |
| Vegetation | 15 | solitary objects, `lodN` geometry | **0** |
| CityFurniture | 11 | `lodN` geometry | **0** |
| WaterBody | 1 | water boundary surfaces | **0** |
| Relief | 1 | native TIN (`TriangulatedSurface`) | **0** |
| CityObjectGroup | 1 | XLink group membership | **0** |
| GenericCityObject | 2 | typed generic attributes | **0** |
| **Total** | **52** | ten CityGML modules | **0** |

Instance-level totals for that scene:

| Level | Source instances | Missing |
| --- | --: | --: |
| elements | 243,254 | 0 |
| attributes | 487 | 0 |
| leaf texts | 1,194 | 0 |
| coordinate tokens | 937,167 | 0 |
| **Total** | **1,182,102** | **0** |

## What this gate does and does not establish

It establishes that the mapping is information-preserving over full LoD and full module coverage, which is the licence to store coordinates verbatim and never round them. That in turn is what makes geometric gold answers stable: nothing was rounded on the way in, so nothing shifts on the way out.

It does not re-export the whole 6.4 GB Hamburg file on every release, and it says nothing about whether a source document is itself correct. Source defects are handled by the anomaly gate instead, and preserved rather than repaired; see `stats_control_<city>.md` and [../LIMITATIONS.md](../LIMITATIONS.md).

Reproduce with `eval/roundtrip_census.py` from the construction pipeline ([pykci](https://github.com/hcu-cml/pykci)), which compares a source GML against its export and exits non-zero on any missing instance.
