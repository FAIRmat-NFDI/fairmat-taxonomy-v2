# representation — FAIRmat taxonomy module

How material-science measurement data is *shaped*, as OWL 2 DL.

The FAIRmat taxonomy says **what** a material property is —
`tax:ElectronicBandGap`, `tax:Morphology`, `tax:Porosity`. It says
nothing about the form the measurement arrives in. A band gap can be a
single number, a spectrum, or a map across a wafer. This module supplies
that missing half: six shapes a measurement can take, aligned with W3C
RDF Data Cube and QUDT.

```
tax:Morphology ──has_image_representation──▶ rep:Image ──▶ DSD ──▶ axes + signal ──▶ kinds + units
```

---

## Contents

```
representation.ttl            the OWL 2 DL TBox        — what exists
representation.shacl.ttl      SHACL shapes + unit map  — what is allowed
README.md                     this file
SPARQL_USAGE.md               queries, with real output

examples/                     one standalone ABox per case, valid and invalid
  scalar-valid-kelvin-abox.ttl
  scalar-invalid-metre-abox.ttl
  profile-spectrum-valid-abox.ttl
  profile-spectrum-invalid-seconds-abox.ttl
  profile-spectrum-invalid-missing-unit-abox.ttl
  profile-spectrum-invalid-kind-as-unit-abox.ttl
  profile-spectrum-invalid-intensity-ev-abox.ttl
  profile-timeseries-valid-second-abox.ttl
  profile-depth-valid-nanometre-abox.ttl
  profile-depth-warn-micrometre-abox.ttl
  image-valid-micrometre-abox.ttl
  image-invalid-seconds-abox.ttl
  image-invalid-two-units-abox.ttl
  volume-valid-micrometre-abox.ttl

test/
  representation_test.py      load → check → write reports.md
  reports.md                  generated

tbox-illustration/            Mermaid walks through the TBox
  overview.md                 read first
  scalar.md  profile.md  image.md  volume.md
  class-hierarchy.md          the class tree and the qb bridges

CHANGELOG/                    what changed, and why
```

## Quick start

```bash
pip install rdflib pyshacl
python test/representation_test.py
```

```
PASS  image-invalid-seconds-abox.ttl          conforms=False REP-UNIT-001, REP-UNIT-014  observations=ok
PASS  image-valid-micrometre-abox.ttl         conforms=True  -  observations=ok
...
14/14 matched. Report written to test/reports.md
```

---

## The model

Five layers. Each exists because something must not be repeated.

| layer | class | holds | scope |
|---|---|---|---|
| taxonomy | `tax:MaterialProperty` | what is being measured | the science |
| data | `rep:Scalar` … `rep:VolumeData` | `rep:rank`, pointer to schema | one dataset |
| schema | `rep:DataStructureDefinition` | which components, in what order | shared by all datasets of the same shape |
| component | `rep:Axis`, `rep:Signal` | quantity kind, default unit | global, one IRI per concept |
| observation | `rep:Observation`, `qb:Observation` | axis coordinates and measured signal values | one point in a dataset |

Between schema and component sits `qb:ComponentSpecification` — a
per-dataset node carrying `qb:order`, `rep:extent` and `rep:hasUnit`.
Those are facts about *this* dataset, and the canonical component is a
shared singleton that must not carry them.

**Example values are lifted into RDF observations.** Each example now
contains concrete rows linked to its dataset with `qb:dataSet`; the
canonical component IRIs (`rep:energy`, `rep:x`, `rep:intensity`, and
so on) are used as predicates. Production arrays may still remain in
HDF5 when lifting every cell would be impractical.

### Rank determines type

`rep:Scalar`, `rep:Profile`, `rep:Image` and `rep:VolumeData` are
defined by `owl:equivalentClass` on the `rep:rank` value, so a reasoner
derives the type. `rep:Spectrum`, `rep:TimeSeries` and `rep:DepthProfile`
are primitive — rank 1 cannot tell a spectrum from a time series, so the
producer asserts which.

| type | rank | axes, slowest first | signal |
|---|---|---|---|
| `rep:Scalar` | 0 | — | `rep:temperature` |
| `rep:Spectrum` | 1 | `rep:energy` | `rep:intensity` |
| `rep:TimeSeries` | 1 | `rep:time` | `rep:intensity` |
| `rep:DepthProfile` | 1 | `rep:depth` | `rep:intensity` |
| `rep:Image` | 2 | `rep:y`, `rep:x` | `rep:intensity` |
| `rep:VolumeData` | 3 | `rep:z`, `rep:y`, `rep:x` | `rep:intensity` |

The axis set is fixed per type. A rank-2 dataset uses `rep:y` and
`rep:x` — no other pair is valid. Ordering is slowest-first, matching
NumPy C-order and the NeXus `<axis>_indices` convention.

### The canonical vocabulary

Eight IRIs, and an ABox never mints its own. `rep:energy` is the same
IRI in every spectrum in the store, which is what lets one query serve
the whole knowledge graph.

| component | role | quantity kind | default unit |
|---|---|---|---|
| `rep:energy` | Axis | `qk:Energy` | `unit:EV` |
| `rep:time` | Axis | `qk:Time` | `unit:SEC` |
| `rep:depth` | Axis | `qk:Length` | `unit:NanoM` |
| `rep:x` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:y` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:z` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:intensity` | Signal | `tax:Intensity` | `unit:COUNT` |
| `rep:temperature` | Signal | `qk:Temperature` | `unit:K` |

`tax:Intensity` is locally minted — QUDT has no term for uncalibrated
detector signal.

---

# The six representations

Each section below gives the data as a scientist would see it, then the
exact RDF, then the unit rule. Diagrams: `tbox-illustration/`.

## Scalar — rank 0

A single measured number. No axis: there is nothing to scan over.

**Data.** A thermocouple reading during a melting-point determination.

| temperature |
|---|
| 1811.0 |

**RDF** — `examples/scalar-valid-kelvin-abox.ttl`

```turtle
ex:melting_point a tax:MeltingTemperature ;
    rep:has_scalar_representation ex:tc_reading .

ex:tc_reading a rep:Scalar , qb:DataSet ;
    rep:rank "0"^^xsd:nonNegativeInteger ;
    qb:structure ex:dsd_03 .

ex:dsd_03 a rep:DataStructureDefinition , qb:DataStructureDefinition ;
    qb:component ex:cs_03_temperature .

ex:cs_03_temperature a qb:ComponentSpecification ;
    qb:measure rep:temperature ;
    rep:hasUnit unit:K .

ex:obs_03_000 a rep:Observation , qb:Observation ;
    qb:dataSet ex:tc_reading ;
    rep:temperature "1811.0"^^xsd:double .
```

One component specification, and it is a measure. The rank-0 case is
often modelled badly by inventing a length-1 axis to make it look like
the others; this module does not.

**Units.** `qk:Temperature` → `unit:K`.
See `tbox-illustration/scalar.md`.

---

## Spectrum — rank 1, axis `rep:energy`

**Data.** An XPS survey scan.

| energy (eV) | intensity (count) |
|---|---|
| 0.0 | 120 |
| 0.5 | 134 |
| 1.0 | 129 |
| … | … |

**RDF** — `examples/profile-spectrum-valid-abox.ttl`

```turtle
ex:core_level_spectrum a tax:Spectra ;
    rep:has_spectrum_representation ex:xps_survey .

ex:xps_survey a rep:Spectrum , qb:DataSet ;
    rep:rank "1"^^xsd:nonNegativeInteger ;
    qb:structure ex:dsd_01 .

ex:dsd_01 a rep:DataStructureDefinition , qb:DataStructureDefinition ;
    qb:component ex:cs_01_energy , ex:cs_01_intensity .

ex:cs_01_energy a qb:ComponentSpecification ;
    qb:dimension rep:energy ;
    qb:order "0"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:EV .

ex:cs_01_intensity a qb:ComponentSpecification ;
    qb:measure rep:intensity ;
    rep:hasUnit unit:COUNT .

ex:obs_01_000 a rep:Observation , qb:Observation ;
    qb:dataSet ex:xps_survey ;
    rep:energy "0.0"^^xsd:double ;
    rep:intensity "120"^^xsd:nonNegativeInteger .
```

**Units.** Axis `qk:Energy` → `unit:EV`. Signal `tax:Intensity` →
`unit:COUNT`.

---

## TimeSeries — rank 1, axis `rep:time`

**Data.** A photoluminescence decay curve.

| time (s) | intensity (count) |
|---|---|
| 0.0 | 4820 |
| 0.1 | 3910 |
| 0.2 | 3170 |
| … | … |

**RDF** — `examples/profile-timeseries-valid-second-abox.ttl`

```turtle
ex:carrier_lifetime a tax:CarrierLifetime ;
    rep:has_timeseries_representation ex:decay_curve .

ex:decay_curve a rep:TimeSeries , qb:DataSet ;
    rep:rank "1"^^xsd:nonNegativeInteger ;
    qb:structure ex:dsd_14 .

ex:dsd_14 a rep:DataStructureDefinition , qb:DataStructureDefinition ;
    qb:component ex:cs_14_time , ex:cs_14_intensity .

ex:cs_14_time a qb:ComponentSpecification ;
    qb:dimension rep:time ;
    qb:order "0"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:SEC .

ex:cs_14_intensity a qb:ComponentSpecification ;
    qb:measure rep:intensity ;
    rep:hasUnit unit:COUNT .

ex:obs_14_000 a rep:Observation , qb:Observation ;
    qb:dataSet ex:decay_curve ;
    rep:time "0.0"^^xsd:double ;
    rep:intensity "4820"^^xsd:nonNegativeInteger .
```

**Units.** `qk:Time` → `unit:SEC`.

---

## DepthProfile — rank 1, axis `rep:depth`

**Data.** A SIMS depth profile through a surface layer.

| depth (nm) | intensity (count) |
|---|---|
| 0.0 | 9120 |
| 2.5 | 8740 |
| 5.0 | 6210 |
| … | … |

**RDF** — `examples/profile-depth-valid-nanometre-abox.ttl`

```turtle
ex:depth_composition a tax:ElementalComposition ;
    rep:has_depthprofile_representation ex:sims_depth .

ex:sims_depth a rep:DepthProfile , qb:DataSet ;
    rep:rank "1"^^xsd:nonNegativeInteger ;
    qb:structure ex:dsd_08 .

ex:dsd_08 a rep:DataStructureDefinition , qb:DataStructureDefinition ;
    qb:component ex:cs_08_depth , ex:cs_08_intensity .

ex:cs_08_depth a qb:ComponentSpecification ;
    qb:dimension rep:depth ;
    qb:order "0"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:NanoM .

ex:cs_08_intensity a qb:ComponentSpecification ;
    qb:measure rep:intensity ;
    rep:hasUnit unit:COUNT .

ex:obs_08_000 a rep:Observation , qb:Observation ;
    qb:dataSet ex:sims_depth ;
    rep:depth "0.0"^^xsd:double ;
    rep:intensity "9120"^^xsd:nonNegativeInteger .
```

**Units.** `qk:Length` → `unit:NanoM`. Note this is *narrower* than for
Image below, despite the identical quantity kind. That gap is the
reason the SHACL has two layers.

---

## Image — rank 2, axes `rep:y`, `rep:x`

**Data.** An SEM intensity map, 3 × 4 pixels. Axis values µm, cells
counts.

| y \ x | 0.0 | 0.5 | 1.0 | 1.5 |
|---|---|---|---|---|
| **0.0** | 120 | 118 | 131 | 127 |
| **0.5** | 119 | 145 | 162 | 130 |
| **1.0** | 121 | 133 | 128 | 125 |

**RDF** — `examples/image-valid-micrometre-abox.ttl`

```turtle
ex:surface_morphology a tax:Morphology ;
    rep:has_image_representation ex:sem_map .

ex:sem_map a rep:Image , qb:DataSet ;
    rep:rank "2"^^xsd:nonNegativeInteger ;
    qb:structure ex:dsd_06 .

ex:dsd_06 a rep:DataStructureDefinition , qb:DataStructureDefinition ;
    qb:component ex:cs_06_y , ex:cs_06_x , ex:cs_06_intensity .

ex:cs_06_y a qb:ComponentSpecification ;
    qb:dimension rep:y ;
    qb:order "0"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:MicroM .

ex:cs_06_x a qb:ComponentSpecification ;
    qb:dimension rep:x ;
    qb:order "1"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:MicroM .

ex:cs_06_intensity a qb:ComponentSpecification ;
    qb:measure rep:intensity ;
    rep:hasUnit unit:COUNT .

ex:obs_06_y0_x0 a rep:Observation , qb:Observation ;
    qb:dataSet ex:sem_map ;
    rep:y "0.0"^^xsd:double ;
    rep:x "0.0"^^xsd:double ;
    rep:intensity "120"^^xsd:nonNegativeInteger .
```

`rep:extent` on the dataset is 12; on `rep:y` it is 3, on `rep:x` it is
4. The signal never carries an extent — it is always the product of the
axis extents, so stating it would be a second source of truth.

**Units.** `qk:Length` → `unit:MicroM`, `unit:NanoM`.

---

## VolumeData — rank 3, axes `rep:z`, `rep:y`, `rep:x`

**Data.** A tomography reconstruction, 2 slices of 2 × 3.

| z | y \ x | 0.0 | 0.5 | 1.0 |
|---|---|---|---|---|
| **0.0** | **0.0** | 120 | 118 | 131 |
| **0.0** | **0.5** | 119 | 145 | 162 |
| **1.0** | **0.0** | 122 | 117 | 129 |
| **1.0** | **0.5** | 118 | 140 | 158 |

**RDF** — `examples/volume-valid-micrometre-abox.ttl`

```turtle
ex:pore_structure a tax:Porosity ;
    rep:has_volume_representation ex:tomo .

ex:tomo a rep:VolumeData , qb:DataSet ;
    rep:rank "3"^^xsd:nonNegativeInteger ;
    qb:structure ex:dsd_10 .

ex:dsd_10 a rep:DataStructureDefinition , qb:DataStructureDefinition ;
    qb:component ex:cs_10_z , ex:cs_10_y , ex:cs_10_x , ex:cs_10_intensity .

ex:cs_10_z a qb:ComponentSpecification ;
    qb:dimension rep:z ;
    qb:order "0"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:MicroM .

ex:cs_10_y a qb:ComponentSpecification ;
    qb:dimension rep:y ;
    qb:order "1"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:MicroM .

ex:cs_10_x a qb:ComponentSpecification ;
    qb:dimension rep:x ;
    qb:order "2"^^xsd:nonNegativeInteger ;
    rep:hasUnit unit:MicroM .

ex:cs_10_intensity a qb:ComponentSpecification ;
    qb:measure rep:intensity ;
    rep:hasUnit unit:COUNT .

ex:obs_10_z0_y0_x0 a rep:Observation , qb:Observation ;
    qb:dataSet ex:tomo ;
    rep:z "0.0"^^xsd:double ;
    rep:y "0.0"^^xsd:double ;
    rep:x "0.0"^^xsd:double ;
    rep:intensity "120"^^xsd:nonNegativeInteger .
```

**Naming.** The class is `rep:VolumeData`, not `rep:Volume`, and carries
`owl:disjointWith tax:Volume`. `tax:Volume` already exists in the base
taxonomy as a structural property — the space a material occupies. A 3D
data cube is a different thing, and the collision is worth ruling out
explicitly.

**Units.** `qk:Length` → `unit:MicroM`, `unit:NanoM`.

---

# Units

Every component carries two edges: what it measures, and what it is
measured in.

```turtle
rep:energy  rep:hasQuantityKind  qk:Energy ;
            rep:hasUnit          unit:EV .
```

That is the whole model. `rep:hasQuantityKind` gives the quantity kind,
`rep:hasUnit` gives the unit, and SHACL checks the two agree.

The unit is *not* chained behind the kind — there is no
`qk:Energy → unit:EV` triple in the ontology. A kind does not have one
unit; energy is measured in eV, joules or hartrees depending on who is
asking. `rep:hasUnit` is functional, so hanging it off the kind would
turn the second option into a contradiction rather than an
alternative. Both edges start at the component, where the answer is
actually single-valued.

## The canonical defaults

`representation.ttl` declares six unit individuals, one per component:

| component | quantity kind | unit |
|---|---|---|
| `rep:energy` | `qk:Energy` | `unit:EV` |
| `rep:time` | `qk:Time` | `unit:SEC` |
| `rep:depth` | `qk:Length` | `unit:NanoM` |
| `rep:x`, `rep:y`, `rep:z` | `qk:Length` | `unit:MicroM` |
| `rep:temperature` | `qk:Temperature` | `unit:K` |
| `rep:intensity` | `tax:Intensity` | `unit:COUNT` |

A dataset that needs a different unit states it on its own
`qb:ComponentSpecification`, beside `qb:order` and `rep:extent`. Same
property, same validation.

## What you can write today

The `shp:permitsUnit` table in `representation.shacl.ttl`. Ordinary RDF
— queryable without a validator, see `SPARQL_USAGE.md` Q2.

| quantity kind | permitted units |
|---|---|
| `qk:Temperature` | `unit:K` |
| `qk:Length` | `unit:NanoM`, `unit:MicroM` |
| `qk:Time` | `unit:SEC` |
| `qk:Energy` | `unit:EV` |
| `tax:Intensity` | `unit:COUNT` |

Length is the only kind with two, because a depth axis works in
nanometres and an image axis in micrometres.

> **This list is what the module uses today, as of September 2026, and
> it will grow without notice.** It is not a survey of what QUDT offers
> and not a claim that nothing else is valid — millimetres, keV and
> minutes are all perfectly real units that simply have no dataset
> asking for them yet. Adding one is a single triple in
> `representation.shacl.ttl`: no shape edit, no TBox change, no
> reasoning to redo. Query the table rather than memorising it.

It happens to match the six declared unit individuals exactly right
now. That is where the module starts, not a rule — the first dataset
that needs millimetres grows the SHACL table and leaves the TBox alone.
The permitted set is a closed-world statement and OWL has no closed
world, which is why it lives in the shapes file and only there.

`qk:Temperature` lists kelvin alone. Non-absolute scales raise a
question this module does not answer — a delta of 5 °C is not a
temperature of 5 °C, and nothing here distinguishes them. That is a
design decision rather than a triple; see `CHANGELOG/suggestions.txt`.

---

# SHACL validation

`representation.shacl.ttl` holds the shapes **and** the permitted-unit
table. It is loaded twice by the test runner — once as the shapes graph,
once into the data graph — because the `FILTER NOT EXISTS` in
`REP-UNIT-001` is evaluated against the data. The shapes are inert as
data; nothing targets them.

## Why OWL is not enough

OWL is open-world: an absent axiom is unknown, never false. Nothing in
`representation.ttl` says a `qk:Energy` component may not point at a
time unit, so there is no contradiction to derive — and a reasoner
derives contradictions, it does not invent rules.

Measured, not asserted. Running the invalid examples through HermiT:

| ABox | HermiT | SHACL |
|---|---|---|
| energy axis in `unit:SEC` | consistent | `REP-UNIT-001` |
| temperature signal in `unit:M` | consistent | `REP-UNIT-001` |
| component specification with no unit | consistent | `REP-UNIT-003` |
| two units on one specification | consistent | `REP-UNIT-003` |
| `qk:Energy` used where a unit belongs | consistent | `REP-UNIT-002` |

Every graph SHACL rejects, HermiT accepts. That gap is not a reasoner
defect — it is the open-world assumption doing its job, and it is why
the constraints cannot live in the TBox.

What OWL *does* catch, because it is a genuine logical axiom:
`rep:energy` used as a `qb:measure` is **inconsistent**, since `rep:Axis`
and `rep:Signal` are disjoint.

## Two layers

| | layer 1 — dimensional | layer 2 — profile |
|---|---|---|
| asks | is this unit a unit *of this kind*? | is it the unit *conventional for this type*? |
| driven by | `shp:permitsUnit` table | `sh:in` list per representation type |
| severity | `sh:Violation` | `sh:Warning` |
| effect | graph does not conform | graph still conforms |
| means | the data is **wrong** | the data is **unusual** |

**Why layer 2 has to exist.** `qk:Length` covers both the nanometre-scale
depth axis and the micrometre-scale image axes. The quantity kind cannot
separate them; the representation type can.
`examples/profile-depth-warn-micrometre-abox.ttl` is a depth profile
stepped in micrometres — a permitted length unit, exactly right on an
image axis, and three orders of magnitude off on a depth axis. Layer 1
has nothing to say about it. Layer 2 warns, and the graph still
validates.

## Error codes

| code | layer | severity | fires when |
|---|---|---|---|
| `REP-UNIT-001` | 1 | Violation | unit not permitted for the component's quantity kind |
| `REP-UNIT-002` | 1 | Violation | object of `rep:hasUnit` is a `qudt:QuantityKind` |
| `REP-UNIT-003` | 1 | Violation | a specification has zero or more than one unit |
| `REP-UNIT-010` | 2 | Warning | Scalar temperature outside K |
| `REP-UNIT-011` | 2 | Warning | Spectrum axis outside eV |
| `REP-UNIT-012` | 2 | Warning | TimeSeries axis outside s |
| `REP-UNIT-013` | 2 | Warning | DepthProfile axis outside nm |
| `REP-UNIT-014` | 2 | Warning | Image axis outside µm / nm |
| `REP-UNIT-015` | 2 | Warning | VolumeData axis outside µm / nm |
| `REP-UNIT-016` | 2 | Warning | intensity signal outside count |

`REP-UNIT-002` exists because layer 1 alone would report a swapped kind
as *"`qk:Energy` is not admissible for `qk:Energy`"* — true, and
useless. Naming the actual mistake is worth a shape of its own.

`REP-UNIT-003` is not redundant with `owl:FunctionalProperty`.
Functional means *any two values are the same individual*, so OWL
responds to two units by inferring `unit:MicroM owl:sameAs unit:NanoM`
and carrying on. That inference is silently wrong and propagates.

## Structured errors

Every shape carries `shp:code`, `shp:category`, `shp:layer` and
`shp:remedy`. A validation result points back at its shape through
`sh:sourceShape`, so a consumer joins result → shape → metadata and gets
a stable code. Nothing parses prose out of `sh:resultMessage`; the
message is for humans.

```python
owner = shapes.value(predicate=SH.property, object=source_shape) or source_shape
code  = shapes.value(owner, SHP.code)        # "REP-UNIT-013"
```

That join is `findings()` in `test/representation_test.py`, ~20 lines.

## Test coverage

14 ABoxes, each an independent graph — several contradict each other on
purpose and are never loaded together. Full output in `test/reports.md`.

| file | conforms | codes |
|---|---|---|
| `scalar-valid-kelvin` | yes | — |
| `scalar-invalid-metre` | no | `001`, `010` |
| `profile-spectrum-valid` | yes | — |
| `profile-spectrum-invalid-seconds` | no | `001`, `011` |
| `profile-spectrum-invalid-missing-unit` | no | `003` |
| `profile-spectrum-invalid-kind-as-unit` | no | `001`, `002`, `011` |
| `profile-spectrum-invalid-intensity-ev` | no | `001`, `016` |
| `profile-timeseries-valid-second` | yes | — |
| `profile-depth-valid-nanometre` | yes | — |
| `profile-depth-warn-micrometre` | **yes** | `013` |
| `image-valid-micrometre` | yes | — |
| `image-invalid-seconds` | no | `001`, `014` |
| `image-invalid-two-units` | no | `003` |
| `volume-valid-micrometre` | yes | — |

`profile-depth-warn-micrometre` conforms *and* carries a finding. A pipeline
gates on layer 1 and logs layer 2.

---

# Description logic and formal notation

The ontology in DL syntax, and the shapes in the notation that suits
them. Two different logics, deliberately — the split is the point.

## Notation

| symbol | meaning |
|---|---|
| ⊑ | subsumption (is-a) |
| ≡ | equivalence (definition) |
| ⊓ ⊔ | intersection, union |
| ∃R.C | some values from |
| ∀R.C | all values from |
| ∋ | has value (nominal) |
| ⊤ ⊥ | top, bottom |
| ⩽n R | at-most cardinality |
| ¬ | negation |

## TBox — class axioms

Everything descends from one umbrella class:

```
DataStructureDefinition  ⊑  Representation
ComponentProperty        ⊑  Representation
Observation              ⊑  Representation
Scalar ⊔ Profile ⊔ Image ⊔ VolumeData  ⊑  Representation
Spectrum ⊔ TimeSeries ⊔ DepthProfile   ⊑  Profile
```

The component roles form a **disjoint union** — this is the one axiom
in the module a reasoner can actually break an ABox on:

```
ComponentProperty  ≡  Axis ⊔ Signal ⊔ UnitAttribute
Axis ⊓ Signal  ≡  ⊥
Axis ⊓ UnitAttribute  ≡  ⊥
Signal ⊓ UnitAttribute  ≡  ⊥
```

So `rep:energy` used as a `qb:measure` is **inconsistent**, because it
would have to be both `Axis` and `Signal`.

The rank-based types are **defined**, not primitive — `≡` rather than
`⊑`, which is what lets a reasoner derive the type from the data:

```
Scalar      ≡  Representation ⊓ ∃rank.{0}
Profile     ≡  Representation ⊓ ∃rank.{1}
Image       ≡  Representation ⊓ ∃rank.{2}
VolumeData  ≡  Representation ⊓ ∃rank.{3}
```

`Spectrum`, `TimeSeries` and `DepthProfile` are primitive (`⊑ Profile`)
because rank 1 alone cannot tell them apart.

The qb bridges:

```
Axis    ⊑  qb:DimensionProperty  ⊑  rdf:Property
Signal  ⊑  qb:MeasureProperty    ⊑  rdf:Property
```

That second subsumption into `rdf:Property` is what makes the OWL 2
punning legal: `rep:energy` is an individual *and* a predicate.

## TBox — property axioms

```
⊤ ⊑ ∀hasQuantityKind.QuantityKind          range
∃hasQuantityKind.⊤ ⊑ ComponentProperty     domain
⊤ ⊑ ⩽1 hasQuantityKind                     functional

⊤ ⊑ ∀hasUnit.Unit                          range
∃hasUnit.⊤ ⊑ ComponentProperty ⊔ qb:ComponentSpecification
⊤ ⊑ ⩽1 hasUnit                             functional

has_scalar_representation     ⊑ has_representation
has_spectrum_representation   ⊑ has_representation
has_timeseries_representation ⊑ has_representation
has_depthprofile_representation ⊑ has_representation
has_image_representation      ⊑ has_representation
has_volume_representation     ⊑ has_representation

∃has_representation.⊤ ⊑ tax:MaterialProperty
⊤ ⊑ ∀has_spectrum_representation.Spectrum       (and so on per subtype)
```

The typed subproperties give two independent routes to the same
conclusion — range assertion and rank definition — and a reasoner
flags the conflict when they disagree. A dataset asserted
`has_image_representation` but carrying `rank = 1` is inconsistent:

```
Image ≡ Representation ⊓ ∃rank.{2}     and     ∃rank.{1}     ⊨  ⊥
```

The canonical individuals, as ABox assertions:

```
Axis(energy)   hasQuantityKind(energy, Energy)   hasUnit(energy, EV)
Axis(depth)    hasQuantityKind(depth, Length)    hasUnit(depth, NanoM)
Axis(x)        hasQuantityKind(x, Length)        hasUnit(x, MicroM)
Signal(temperature)  hasQuantityKind(temperature, Temperature)
                     hasUnit(temperature, K)
```

## Where DL stops

The unit rule cannot be written above. The natural-looking attempt is

```
∀c. hasUnit(c, u) ⊓ hasQuantityKind(c, k)  →  permits(k, u)
```

and it is **not expressible in OWL 2 DL**, for two separate reasons.

First, it is a *role–role* constraint: it relates the fillers of two
different roles on the same individual. DL concept constructors quantify
over one role at a time. SWRL could express it, at the cost of
decidability.

Second, even written, it would not do the job. OWL is open-world, so

```
KB ⊭ ¬permits(Energy, SEC)
```

Absence of a `permits` assertion is *unknown*, never *false*. Nothing is
violated, so nothing is derived. Measured, not argued: HermiT accepts
every one of the invalid examples in `examples/`.

The one thing OWL *does* catch here is a genuine contradiction, and it
needs the disjointness axiom to do it:

```
Axis(energy) ⊓ Signal(energy)  ⊨  ⊥
```

## SHACL — the closed-world half

SHACL is validation over a fixed graph, so the quantifier is bounded
and negation-as-failure is available. Layer 1:

```
∀ c ∈ { x : ∃u. hasUnit(x, u) } .
    ∀ k ∈ kind(c) .  hasUnit(c) ∈ permits(k)
```

where `kind(c)` resolves through whichever path applies:

```
kind(c) = { k : hasQuantityKind(c, k) }
        ∪ { k : ∃d. qb:dimension(c, d) ∧ hasQuantityKind(d, k) }
        ∪ { k : ∃m. qb:measure(c, m)   ∧ hasQuantityKind(m, k) }
```

Directly as the SPARQL the shape actually runs:

```
{(c,u,k) : hasUnit(c,u) ∧ k ∈ kind(c) ∧ (k,u) ∉ permits}  =  ∅
```

`∉` is the operative symbol. It is `FILTER NOT EXISTS`, and it is
exactly what DL cannot supply.

Layer 2 narrows by representation type rather than by kind:

```
∀ d : Image .      units(axes(d))  ⊆  {MicroM, NanoM}
∀ d : DepthProfile. units(axes(d)) ⊆  {NanoM}
```

Both sets are `qk:Length`, which is the formal statement of why one
layer is not enough:

```
permits(Length) = {NanoM, MicroM}
profile(Image)  = {MicroM, NanoM}
profile(Depth)  = {NanoM}

profile(Depth) ⊊ permits(Length)
```

A micrometre depth axis sits in `permits(Length) \ profile(Depth)` —
admissible, off-profile. Warning, not violation.

Cardinality, closing the gap `owl:FunctionalProperty` leaves open:

```
∀ c ∈ ComponentSpecification .  |{u : hasUnit(c,u)}| = 1
```

OWL's functionality says any two fillers are the *same individual*,
which under a unique-name-free semantics infers `MicroM ≡ NanoM` rather
than rejecting. SHACL counts instead of identifying.

## The division, in one line

```
OWL   ⊨  what must follow      open world,   entailment
SHACL ⊨  what must be present  closed world, validation
```

Nothing in `representation.ttl` is a constraint, and nothing in
`representation.shacl.ttl` is a definition. Each file does the job its
logic can actually do.

---

## Known limits

Not yet enforced anywhere, by design or by omission:

- **Canonical axis membership.** Nothing here stops an ABox minting
  `ex:my_axis`. A candidate shape is drafted in the enforcement note at
  the foot of `representation.ttl`; it is intended for a future
  structural shapes graph and is not present in this unit-scoped file.
- **`rep:extent` arithmetic.** That dataset extent equals the product of
  axis extents is validated in Pydantic, not in SHACL.
- **Index contiguity.**
- **`tax:Spectra ⊑ ∃has_representation.rep:Spectrum`** — the coupling
  axiom tying taxonomy classes to required representation types.

## See also

- `SPARQL_USAGE.md` — what you can ask, with real output
- `tbox-illustration/overview.md` — the diagrams
- `CHANGELOG/` — what changed, and what is only a suggestion
