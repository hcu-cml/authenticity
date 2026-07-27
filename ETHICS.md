# Ethics, privacy, and responsible use

AuthentiCity describes the built environment. Its instances are buildings, geometry, and administrative attributes, not people. That removes most, but not all, of the ethical surface of an urban dataset, and this file states what remains.

## Personal data

**No personal data is collected, inferred, or published.** There are no names of residents or owners, no occupancy, no household or demographic attributes, and no imagery of people. All six upstream sources are already published open data.

Two places deserve explicit statements:

- **Addresses.** Street name, postcode, and city appear on building nodes under the `addr_*` namespace, copied from the primary OpenStreetMap match, and the `bldg:address` subtree of the authoritative sources is preserved verbatim. A building address is public information in every jurisdiction covered here and is already published by both the cadastral providers and OpenStreetMap. No address is linked to a person.
- **Points of interest.** `HAS_POI` edges attach OpenStreetMap points to the building that contains them, which includes shop, amenity, and operator tags. These describe businesses and public facilities as OpenStreetMap publishes them. Where an OSM contributor tagged a private individual's name (for example as an operator of a small business), that value is carried through unchanged, as it is in every OSM extract. We did not add such information and do not enrich it.

Because there are no human data subjects, the datasheet questions on informed consent, ethical review, data-subject notification, retention, and revocation do not apply. Anyone who nonetheless wants a specific OSM value removed should ask OpenStreetMap: the upstream project is the right place for that correction, and the next AuthentiCity release will reflect it.

## Uses we consider out of scope

- **Inferring anything about residents of specific buildings.** The dataset is not a proxy for who lives where, and combining it with population or income data at building level to profile individuals is contrary to its intent.
- **Presenting derived layers as survey-grade.** ML-predicted roof materials and reconstructed LoD3 facades are marked as predicted and reconstructed precisely so they can be excluded where authoritative evidence is required. Using a prediction as if it were a cadastral fact, in a regulatory, insurance, valuation, or enforcement context, is a misuse the provenance model exists to prevent.
- **Targeting.** Building-level attributes plus precise geometry could support physical targeting of specific structures. This information is already public in each source; aggregating it does not make it more sensitive, but it does make it more convenient, and that convenience should not be used for harm.

## Bias and representativeness

**Geographic bias.** Five cities, all in high-income economies with well-funded mapping agencies, chosen because they publish open 3D city models. Regions without such publication are absent, which biases the corpus toward places with strong cadastral infrastructure. Conclusions about "cities" in general do not follow from it.

**Crowd-sourcing bias.** OpenStreetMap coverage and detail follow contributor density, which correlates with city centres, wealth, and community activity. The share of OSM features that match an authoritative building ranges from 5.5 % (Zurich) to 43.9 % (New York); the unmatched remainder is kept as net-new knowledge with an explicit reason, not discarded. Any analysis using OSM completeness as a signal is partly measuring where mappers are active.

**Prediction bias.** The roof-material classifier inherits the biases of its training imagery and of the OpenStreetMap labels it was trained on, which are themselves unevenly distributed. Its per-material pixel coverage is released as a confidence signal so that low-confidence predictions can be filtered rather than trusted uniformly.

**Coverage is not a negative observation.** Roof material covers 50.2 % of Hamburg buildings and 0 % elsewhere; LoD3 covers 17 buildings. Absence means not covered. Reading it as "this building has no predicted material" would turn a data gap into a false factual claim, which is why coverage is explicit throughout and why the benchmark includes coverage-aware and infeasible categories.

## Environmental cost

Building the five graphs took 6.64 h wall clock on one workstation ([docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)); the released dumps mean nobody needs to repeat it. The baseline evaluations use a 7 B local model and a cached commercial-model run, both small compared with training-scale workloads. Representation-learning baselines were trained on a single GPU. We release cached model outputs specifically so that reproducing our numbers requires no inference at all.

## Dual use and licensing ethics

The strongest ethical obligation attached to this dataset is a licensing one: OpenStreetMap contributors' work is under ODbL, and the authoritative sources require attribution. Stripping provenance to make the data more convenient would break both the license and the dataset's purpose. [DATA_LICENSES.md](DATA_LICENSES.md) states what attribution and share-alike require in practice.

## Reporting a concern

Email the corresponding author: Huynh Duc An Son Nguyen, <son.nguyen@hcu-hamburg.de>, or open an issue on this repository. Concerns about a specific upstream value are best raised with the upstream provider, and we will carry the correction into the next release.
