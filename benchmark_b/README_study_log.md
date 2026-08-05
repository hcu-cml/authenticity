# Study log & lab guide — provenance-aware urban graph embeddings

A companion for building the representation-learning benchmark on your Neo4j graph. It has three
purposes: **map each pipeline step to the theory** (so running a query means something), **anticipate the
struggles** so you recognise them by their cause, and give you a **log to fill in** as you go. If you run
this with a Claude Code agent, point it at this file and have it append to §2 and §3 with what actually
happened.

Files this refers to: `citygml_osm_graph_embedding_benchmark.ipynb` (notebook 1: tutorial + single-graph
method spectrum), `provenance_aware_representation_learning.ipynb` (notebook 2: multi-source, agnostic vs
aware, matching, cross-city), `benchname_representation_learning_section.tex` (your paper section).

---

## 1. The pipeline as a theory map

Read this once; refer back to it whenever a step feels mechanical.

1. **Neo4j extraction.** Not maths yet, but it *defines* the object. A heterogeneous graph is
   `G = (V, E, τ, X)`: node types `τ(v)`, typed relations `r = (τ_src, rel, τ_dst)`, and per-type feature
   matrices. Your schema query *is* you reading off `τ` and the relations.
2. **`HeteroData` construction.** The formal object in memory: for each node type `t` a matrix
   `X_t ∈ R^{n_t × d_t}` (note `d_t` differs per type — that is what "heterogeneous" means), and for each
   relation `r` an `edge_index` = the sparse adjacency `A_r`.
3. **Featurisation.** Z-score numerics, one-hot categoricals. Message passing and linear probes both
   assume comparable scales; unscaled height (metres) vs area (m²) lets one feature dominate the dot
   products. Never include a feature derived from the label (leakage).
4. **Splits.** Random assumes examples are i.i.d. In cities they are **not**: neighbours share materials
   and heights (spatial autocorrelation), so a random split leaks test labels through the graph. The
   *spatial-block* split removes that leakage; the *cross-city* split tests domain transfer. This axis is
   also the **transductive vs inductive** distinction — shallow embeddings can only score nodes seen at
   training time; GNNs can embed unseen ones.
5. **Shallow embeddings (node2vec / metapath2vec).** Encoder = a lookup table (one free vector per node).
   Objective = skip-gram over random walks: maximise `log σ(z_u·z_v)` for nodes co-occurring on a walk,
   minus negative samples. Uses **no features**; transductive. metapath2vec just constrains the walk to a
   type template (the "provenance metapath").
6. **Message-passing GNN.** Encoder = a function of features + neighbourhood:
   `h_v' = σ(W_self h_v + AGG_{u∈N(v)} W h_u)`. Inductive. Variants differ in `AGG`: GraphSAGE (mean),
   GAT (attention weights), R-GCN (a separate `W_r` per relation), HGT (typed transformer attention).
7. **Provenance-aware aggregation (the section's Eq. 1).**
   `h_c' = σ(W_self h_c + Σ_{e∈N(c)} (w_ce / Σ w) · W_{s(e)} h_e)`, where `w_ce` is the correspondence
   **confidence** and `s(e)` the **source** of evidence `e`. Agnostic sets `w_ce = 1` and `W_{s(e)} = W`
   and merges evidence into one node. Coverage/agreement enter as node features. Hypothesis: the extra
   information helps most where sources disagree and on the matching task.
8. **Tasks & decoders (encoder–decoder view).** Node classification: softmax head + cross-entropy.
   Regression (height/storeys): scalar head + MSE. Matching: a *decoder* scores a pair,
   `score(a,b) = z_a·z_b`, trained with binary cross-entropy — link prediction / entity resolution.
9. **Evaluation as controlled experiment.** Under imbalance, accuracy flatters the majority class →
   report **macro-F1**. Ranking/matching → **ROC-AUC, AP, Hits@k**. Report **mean ± std over seeds**.
   Each ablation (confidence on/off, coverage on/off, source-typing on/off) is a controlled comparison
   isolating one variable — that is the whole game of a benchmark paper.

---

## 2. Step checklist (fill in `observed` as you go)

```
[ ] S0  Confirm the Desktop DBMS bolt URI + credentials (which port is it actually on?)
        expected: bolt://localhost:7687 (or 7688 if the system service holds 7687)
        observed:

[ ] S1  Schema queries (apoc.meta.schema / nodeTypeProperties / relTypeProperties / triple counts)
        expected: node labels, relation types, and — crucially — whether a confidence/source
                  property exists anywhere
        observed:

[ ] S2  Target distributions (roof material / use / roof shape counts; height & storeys coverage+range)
        expected: imbalanced categorical targets; some numeric coverage < 100%
        observed:

[ ] S3  Write load_from_neo4j(); assert HeteroData shapes (per-type feature dims, edge counts)
        theory note: this is you instantiating G = (V, E, τ, X)
        observed:

[ ] S4  Build splits (random + spatial-block); sanity-check train/val/test sizes
        theory note: watch that the spatial split keeps whole regions together
        observed:

[ ] S5  T2 node classification, provenance-agnostic  -> record macro-F1
        observed:

[ ] S6  Add provenance (source-typing / confidence / coverage) -> record the delta
        theory note: Eq. 1; is the gap positive? on which classes?
        observed:

[ ] S7  T3 cross-source matching with HARD negatives -> AUC / AP / Hits@1, agnostic vs aware
        (only if the correspondence layer exists in this dump — see §3 item 3)
        observed:

[ ] S8  Cross-city transfer (once the multi-city DB is available)
        observed:

[ ] S9  Fill paper Table 1 (graph stats) and the results tables; export the four figures
        observed:
```

---

## 3. Anticipated struggles and *why* (the study section)

Each is written cause-first, because the cause is the concept worth keeping.

1. **`apoc.meta.*` → "There is no procedure with the name ..."**
   Cause: APOC isn't installed/enabled in this DBMS. Fix: use the plain fallbacks (`db.labels()`,
   `db.relationshipTypes()`, `MATCH (n) RETURN labels(n), count(*)`). Concept: Neo4j procedure libraries
   are per-DBMS plugins, not part of the core query language.

2. **Desktop instance won't start: `bind ... 127.0.0.1:7687 Address already in use`.**
   Cause: the system `neo4j` service and the Desktop DBMS both want the default Bolt port. Fix: stop one,
   or move Desktop's `server.bolt.listen_address`. (You hit this already.) Concept: one process per port;
   two DBMSs can't share defaults.

3. **No `confidence` / `source` anywhere in this dump.**
   Cause: the provenance/correspondence layer (canonical entities ↔ source evidence, confidence edges)
   is a property of the *multi-city* benchmark database, and may not be in this single Hamburg export.
   Fix: run T1/T2 (attribute prediction, node classification) now; defer T3 (matching) and the
   agnostic-vs-aware contrast to the DB that has the provenance edges. Concept: the provenance model is
   what makes the paper novel — if it's absent, the "aware" arm has nothing to be aware *of* yet.

4. **`to_homogeneous()` / feature-dim errors when merging types.**
   Cause: heterogeneous node types have different `d_t`, so you can't stack them naïvely. Fix: keep
   `HeteroData` and use per-relation message passing (`to_hetero`, R-GCN, HGT), or project each type to a
   shared width first. Concept: heterogeneity is a feature, not a nuisance — the models exist precisely to
   handle different `d_t`.

5. **GNN "trains" but loss doesn't move / params look uninitialised.**
   Cause: PyG lazy modules (`Linear(-1, ...)`, `SAGEConv((-1,-1), ...)`) only materialise their weights on
   the first forward pass; if you build the optimizer before that forward, it optimises nothing. Fix: run
   one `with torch.no_grad(): model(...)` to initialise, *then* create the optimizer (the notebooks do
   this). Concept: lazy shape inference.

6. **`import Node2Vec` works, but `.loader(...)` throws at runtime.**
   Cause: the biased-random-walk sampler lives in `torch_cluster`, a compiled extension separate from the
   PyG core. Fix: install the matching wheel (`pip install torch_cluster -f https://data.pyg.org/whl/torch-<ver>+cpu.html`).
   Concept: node2vec's whole objective is walk-based, so no walk kernel → no node2vec.

7. **Random-split scores look suspiciously high.**
   Cause: spatial autocorrelation — a train neighbour reveals its test neighbour's label. Fix: trust the
   *spatial-block* number instead; report both and treat the drop as a result. Concept: the i.i.d.
   assumption fails for spatial data; this is the single most important methodological point of your
   section.

8. **Accuracy is high but the model clearly ignores rare classes.**
   Cause: class imbalance; accuracy rewards predicting the majority. Fix: report **macro-F1** and inspect
   per-class F1. Concept: the metric encodes what you care about.

9. **`.numpy()` on a CUDA tensor, or garbled results after a GNN run.**
   Cause: moving the master `HeteroData` to the GPU in place then doing CPU ops on it. Fix: keep the
   master on CPU and build per-run device dicts (the notebooks are written this way). Concept: tensors
   carry a device; mixing silently corrupts or errors.

10. **Matching AUC ≈ 1.0 — too good.**
    Cause: random negatives are trivially separable (a far-away OSM node never matches). Fix: use **hard**
    negatives — spatially adjacent but non-matching candidates (notebook 2 samples these). Concept:
    entity resolution is only interesting on confusable pairs; easy negatives measure nothing.

11. **Cross-city transfer collapses.**
    Cause: covariate/label shift — feature scales and class priors differ between cities. Fix: standardise
    consistently (per-city or jointly, and say which), and discuss it as domain shift rather than model
    failure. Concept: this is exactly the transfer problem your section frames as the headline experiment.

12. **`LogisticRegression` convergence warning in the probe.**
    Cause: unscaled embeddings / too few iterations. Fix: `max_iter` up, features already standardised.
    Minor, but a reminder that the *probe* is itself a model with assumptions.

---

## 4. Running this as a Claude Code agent (without giving up the learning)

- **Setup.** Put the two notebooks, the `.tex` section, and this file in one repo; open Claude Code there.
  You've already run the Claude CLI in containers, so nothing new here.
- **Preserve hands-on learning.** Tell the agent explicitly: *propose queries and explain the theory, let
  me run the Cypher and the first training pass myself; you write the glue code and fix tracebacks.* Do
  the conceptual steps (S1, S4, S5–S6) by hand; delegate the mechanical ones (S3 loader, harness plumbing).
- **Database access.** Put creds in env vars (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`), not in
  committed code; confirm the Desktop DBMS's Bolt port first. Start with read-only queries.
- **Have it keep the log.** Ask the agent to append to a `PROGRESS.md` after each step: *what was
  attempted, what broke, the fix, and the theory link.* §2 and §3 here are the template — the real log
  then reflects your actual session, which is the study artefact you wanted.
- **Guardrails.** Review commands before approving; it's your machine, so local execution is fine, but
  keep the agent from committing secrets or force-pushing.

**CLAUDE.md starter** (drop in the repo root so the agent has context):

```
Goal: build a provenance-aware graph-representation-learning benchmark on our Neo4j urban KG.
Tasks: T1 multi-source attribute prediction, T2 node classification, T3 cross-source matching.
Key contrast: provenance-agnostic vs provenance-aware embeddings (source typing, confidence-weighted
message passing per Eq.1, coverage features).
Files: two notebooks (tutorial + provenance) and benchname_representation_learning_section.tex.
Working style: explain the theory and PROPOSE queries/steps; let me execute the conceptual ones. Keep a
PROGRESS.md log (attempt / error / fix / theory link). Don't include label-derived features. Use the
spatial-block split, not just random. Report macro-F1 (not accuracy) and mean±std over seeds.
```

---

## 5. If you stay in this chat instead

You don't need the agent to make progress — the schema-query outputs from S1–S2 (plus a couple of example
nodes) are enough for me to write you a real `load_from_neo4j()` and fill Table 1 with your true counts.
Claude Code mainly buys you a faster run/verify loop and a self-writing log; the reasoning and the section
we can finish either way.
