# Exact prompts and raw model responses

`<city>/batch_*_prompt.txt` is the complete text sent to the commercial model for that batch, byte for byte, and `<city>/batch_*_response_raw.txt` is what came back, unedited. `test_batch_prompt.txt` and its response are the same for the held-out split. Nothing here is paraphrased or cleaned up: markdown fences the model added are still present, and were stripped only at parse time.

They are here so that "closed book, schema only" is checkable rather than asserted.

## What each prompt contains

1. The per-city schema text, byte-identical to [../../../schema/](../../../schema/), which is the same file every other backend receives for that city. This is the whole point of the comparison: context parity across backends.
2. The closed-book constraints: no database access, no tool use, no retrieval, answer only from the schema given.
3. The Cypher rules the harness states to every model: the spatial procedures that exist, return exactly the requested columns, add a deterministic `id` tie-break to ranked answers, prefer the authoritative attribute over a crowd-sourced one unless the question says otherwise.
4. The batch's questions.

## Batching, and the tradeoff it makes

Roughly 25 independent questions were sent per call instead of one call per question, which turned about 100 calls per city into about four. Each prompt instructs the model to answer every question independently, using only the schema and rules given, uninfluenced by the other questions in the batch.

This is a documented engineering tradeoff, not a claim of equivalence: answering many similar questions in one pass could plausibly make a model more internally consistent than fully isolated calls would. The effect was not measured. A single-question-per-call pilot preceded this run and its outcomes were consistent with the batched run, which is evidence, not proof. If you evaluate a model with per-question isolation, say so; the difference is a real experimental variable.

## Excluded questions

Each run excluded questions whose gold reads a property that exists only on another city's graph. On those, a model told to refuse when the information is absent from its schema correctly refuses, and counting that as an over-refusal would be a scoring artifact rather than a finding. The exclusions were established by checking each property against the live graph, not against the sampled schema text.

The exact question set each run was scored on is shipped in [../eval_subsets/](../eval_subsets/), which is the authoritative record: per-city counts are in [../README.md](../README.md). Those templates have since been brought under the declarative requirement gate, so on the released suite they no longer instantiate off their home city, and the exclusion step is no longer needed.

## One prompt-authoring mistake, for the record

On the first dispatch of a Tokyo question about interior rooms, the prompt inadvertently hinted at a schema-introspection gap (Tokyo has exactly one `Room` node in a 2 M-building graph, rare enough that the schema sampler omitted the corresponding relationship). It was caught before scoring, and the question was re-dispatched cleanly with no hint and no extra access. The model then refused, which is the correct behavior given the text it was shown, and it was scored as a legitimate refusal rather than excluded. The clean prompt is the one in this directory.
