# representation — FAIRmat taxonomy module

How material-science measurement data is shaped as OWL 2.

The FAIRmat taxonomy identifies what a material property is. This module
describes the form in which its measured data is represented: a scalar, a
one-dimensional profile, an image, or a volume. It separates the dataset, its
schema, reusable component meanings, optional unit metadata, and concrete
observations.

```text
tax:MaterialProperty
  → rep:has_*_representation
  → representation dataset
  → qb:structure
  → component specifications
  → axes and signals
  → quantity kinds and optional units
  → observations
```

The ontology uses machine-actionable subclass bridges to W3C RDF Data Cube
classes and canonical QUDT IRIs. The companion SHACL file is currently scoped
to quantity-kind and optional-unit metadata.

## Contents

```text
representation.ttl              OWL ontology
representation.shacl.ttl        unit shapes and validator-owned whitelist
README.md                       model, complete examples, and formal semantics
SPARQL_USAGE.md                 executable query capabilities and result tables
complexity.md                   graph-size and validation scaling

examples/                       18 independent ABox fixtures
  <representation>-valid-abox.ttl
  <representation>-invalid-unit-abox.ttl
  <representation>-invalid-missing-kind-abox.ttl

test/
  representation_test.py       load → validate → inspect → report
  reports.md                   generated result matrix

tbox-illustration/
  overview.md                  complete module walk-through
  class-hierarchy.md           OWL hierarchy and RDF Data Cube bridges
  scalar.md                    rank-zero example
  profile.md                   Spectrum, TimeSeries, and DepthProfile
  image.md                     rank-two example
  volume.md                    rank-three example
  validation.md                optional-unit validation flow

CHANGELOG/
  ontology.txt
  shacl.txt
  docs-and-tests.txt
  deferred.txt
```

`examples-TBOX/` is intentionally omitted.

## Quick start

```bash
python -m pip install -r requirements.txt
python test/representation_test.py
```

Expected summary:

```text
18/18 examples passed; report: test/reports.md
```

The test runner can be started from any working directory. It resolves the
package root from its own path and checks:

- Turtle parsing and SHACL meta-validation;
- expected result codes and conformance for all 18 fixtures;
- observation completeness;
- canonical QUDT ranges;
- RDF Data Cube subclass bridges;
- absence of class-level `skos:closeMatch`;
- absence of locally defined ordering semantics.

## The model

Five layers prevent scientific meaning, dataset-specific structure, and values
from being collapsed into one node.

| Layer | Main entity | Holds | Scope |
|---|---|---|---|
| taxonomy | `tax:MaterialProperty` | what is measured | scientific domain |
| dataset | `rep:Scalar` … `rep:VolumeData` | rank, extent, schema link | one representation |
| schema | `rep:DataStructureDefinition` | component specifications | one reusable structure |
| component | `rep:Axis`, `rep:Signal` | role and quantity kind | reusable vocabulary |
| observation | `rep:Observation` | coordinates and signal values | one data point |

A `qb:ComponentSpecification` sits between the schema and reusable component.
It identifies a dimension, measure, or attribute and may carry a
dataset-specific `rep:hasUnit`. Units on specifications are optional.

### End-to-end graph pattern

```turtle
ex:dataset a rep:Image ;
    rep:rank "2"^^xsd:nonNegativeInteger ;
    qb:structure ex:dsd .

ex:dsd a rep:DataStructureDefinition ;
    qb:component ex:y-spec, ex:x-spec, ex:signal-spec .

ex:y-spec a qb:ComponentSpecification ;
    qb:dimension rep:y ;
    rep:hasUnit unit:MicroM .

ex:x-spec a qb:ComponentSpecification ;
    qb:dimension rep:x .

ex:signal-spec a qb:ComponentSpecification ;
    qb:measure rep:intensity .

ex:pixel a rep:Observation ;
    qb:dataSet ex:dataset ;
    rep:y 0 ;
    rep:x 0 ;
    rep:intensity 125 .
```

The missing units on `ex:x-spec` and `ex:signal-spec` are valid. No default
value is inserted.

### RDF Data Cube alignment

The FAIRmat classes are narrower specializations of Data Cube classes:

```text
rep:DataStructureDefinition ⊑ qb:DataStructureDefinition
rep:Scalar                  ⊑ qb:DataSet
rep:Profile                 ⊑ qb:DataSet
rep:Image                   ⊑ qb:DataSet
rep:VolumeData              ⊑ qb:DataSet
rep:Observation             ⊑ qb:Observation
rep:Axis                    ⊑ qb:DimensionProperty
rep:Signal                  ⊑ qb:MeasureProperty
rep:UnitAttribute           ⊑ qb:AttributeProperty
```

The former class-level `skos:closeMatch` statements are removed. The current
subclass axioms support RDFS/OWL inference. From:

```turtle
ex:map a rep:Image .
```

an entailment-aware system derives:

```turtle
ex:map a qb:DataSet .
```

A basic triple-pattern engine without entailment sees only the asserted type.
It may materialize superclass types during ingestion.

The local ontology declares the external Data Cube entities it references. It
does not impose local functionality, disjointness, domains, ranges, or order on
the `qb:` vocabulary. Load the official Data Cube ontology separately when
those axioms or the complete Data Cube integrity constraints are needed.

### QUDT alignment

The canonical QUDT schema namespace is:

```turtle
@prefix qudt: <http://qudt.org/schema/qudt/> .
```

The ontology therefore uses the actual class IRIs:

```text
http://qudt.org/schema/qudt/QuantityKind
http://qudt.org/schema/qudt/Unit
```

QUDT vocabulary individuals continue to use:

```text
http://qudt.org/vocab/quantitykind/
http://qudt.org/vocab/unit/
```

### Rank determines the current representation class

`rep:Scalar`, `rep:Profile`, `rep:Image`, and `rep:VolumeData` are
defined through `owl:equivalentClass` and `rep:rank`:

| Type | Rank | Intended axes | Typical signal |
|---|---:|---|---|
| `rep:Scalar` | 0 | none | `rep:temperature` |
| `rep:Spectrum` | 1 | `rep:energy` | `rep:intensity` |
| `rep:TimeSeries` | 1 | `rep:time` | `rep:intensity` |
| `rep:DepthProfile` | 1 | `rep:depth` | `rep:intensity` |
| `rep:Image` | 2 | `rep:y`, `rep:x` | `rep:intensity` |
| `rep:VolumeData` | 3 | `rep:z`, `rep:y`, `rep:x` | `rep:intensity` |

The four defined classes are:

```text
Scalar     ≡ Representation ⊓ ∃rank.{0}
Profile    ≡ Representation ⊓ ∃rank.{1}
Image      ≡ Representation ⊓ ∃rank.{2}
VolumeData ≡ Representation ⊓ ∃rank.{3}
```

`Spectrum`, `TimeSeries`, and `DepthProfile` are primitive subclasses of
`Profile` because rank one alone does not distinguish their scientific
meaning.

The module currently documents intended axis membership but does not validate
it in the unit-only SHACL graph.

### No ordering semantics

The ontology contains neither `rep:order` nor a local `qb:order` declaration.
It makes no statement about presentation order, NumPy memory order, NeXus axis
indices, or storage layout. Queries return component membership without
claiming sequence. A future storage-order property needs its own name,
definition, domain, range, and validation rules.

### Canonical component vocabulary

| Component | Role | Quantity kind | Retained unit assertion |
|---|---|---|---|
| `rep:energy` | Axis | `qk:Energy` | `unit:EV` |
| `rep:time` | Axis | `qk:Time` | `unit:SEC` |
| `rep:depth` | Axis | `qk:Length` | `unit:NanoM` |
| `rep:x` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:y` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:z` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:intensity` | Signal | `tax:Intensity` | `unit:COUNT` |
| `rep:temperature` | Signal | `qk:Temperature` | `unit:K` |

Each canonical component IRI is both an OWL named individual and an OWL
datatype property. The individual view carries metadata; the property view is
used on observations. The predicates have the broad `rdfs:Literal` range.
Numerical datatype restrictions belong to later structural validation.

`tax:Intensity` is a local quantity kind for an uncalibrated detector signal.

The unit assertions on canonical components are retained from the supplied
ontology. This release defines no default, fallback, inheritance, precedence,
or override algorithm. If a dataset-specific specification omits
`rep:hasUnit`, the validation contract treats the unit as unspecified.

# The six representations

Each section presents the scientist-facing data, the exact complete Turtle
fixture, what OWL can infer, and what the unit profile validates.

## Scalar — rank 0

A Scalar is one measured value with no independent coordinate.

**Data.** A temperature reading:

| temperature |
|---:|
| 293.15 |

**Complete RDF** — `examples/scalar-valid-abox.ttl`

```turtle
@prefix ex:   <http://example.org/representation/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

## expect: conforms
## case: Scalar / valid optional unit

ex:scalar-property a tax:MaterialProperty ;
    rep:has_scalar_representation ex:scalar-valid-dataset .

ex:scalar-valid-dataset a rep:Scalar ;
    rep:rank "0"^^xsd:nonNegativeInteger ;
    rep:extent "1"^^xsd:nonNegativeInteger ;
    qb:structure ex:scalar-valid-dsd .

ex:scalar-valid-dsd a rep:DataStructureDefinition ;
    qb:component
        ex:scalar-valid-signal .

ex:scalar-valid-signal a qb:ComponentSpecification ;
    qb:measure rep:temperature .

ex:scalar-valid-observation a rep:Observation ;
    qb:dataSet ex:scalar-valid-dataset ;
    rep:temperature "293.15"^^xsd:double .
```

The component specification omits `rep:hasUnit`. This conforms because units
are optional. `rep:temperature` still has exactly one quantity kind,
`qk:Temperature`. From the dataset's `rep:Scalar` type, an RDFS reasoner can
derive `qb:DataSet`. From rank zero and the equivalent-class axiom, an OWL
reasoner can also classify a suitable `rep:Representation` as `rep:Scalar`.

The invalid-unit fixture supplies `unit:EV` for the temperature measure. It
produces `REP-UNIT-001` and advisory `REP-UNIT-010`. The missing-kind fixture
uses a custom signal without `rep:hasQuantityKind` and produces
`REP-UNIT-004` and `REP-UNIT-005`.

## Spectrum — rank 1, energy axis

**Data.** Three points from an energy spectrum:

| energy (eV) | intensity |
|---:|---:|
| 10.0 | 125 |
| 10.5 | 142 |
| 11.0 | 131 |

**Complete RDF** — `examples/spectrum-valid-abox.ttl`

```turtle
@prefix ex:   <http://example.org/representation/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

## expect: conforms
## case: Spectrum / valid optional unit

ex:spectrum-property a tax:MaterialProperty ;
    rep:has_spectrum_representation ex:spectrum-valid-dataset .

ex:spectrum-valid-dataset a rep:Spectrum ;
    rep:rank "1"^^xsd:nonNegativeInteger ;
    rep:extent "3"^^xsd:nonNegativeInteger ;
    qb:structure ex:spectrum-valid-dsd .

ex:spectrum-valid-dsd a rep:DataStructureDefinition ;
    qb:component
        ex:spectrum-valid-axis-energy,
        ex:spectrum-valid-signal .

ex:spectrum-valid-axis-energy a qb:ComponentSpecification ;
    qb:dimension rep:energy ; rep:hasUnit unit:EV .

ex:spectrum-valid-signal a qb:ComponentSpecification ;
    qb:measure rep:intensity .

ex:spectrum-valid-observation a rep:Observation ;
    qb:dataSet ex:spectrum-valid-dataset ;
    rep:energy "10.0"^^xsd:double ;
    rep:intensity "125"^^xsd:nonNegativeInteger .

ex:spectrum-valid-observation-2 a rep:Observation ;
    qb:dataSet ex:spectrum-valid-dataset ;
    rep:energy "10.5"^^xsd:double ;
    rep:intensity "142"^^xsd:nonNegativeInteger .

ex:spectrum-valid-observation-3 a rep:Observation ;
    qb:dataSet ex:spectrum-valid-dataset ;
    rep:energy "11.0"^^xsd:double ;
    rep:intensity "131"^^xsd:nonNegativeInteger .
```

The energy specification supplies `unit:EV`, which is whitelisted for
`qk:Energy`. The intensity unit is omitted. Both choices conform. The component
IRIs used as observation predicates are the same resources described in the
ontology as `rep:Axis` and `rep:Signal`.

The invalid-unit fixture attaches `unit:SEC` to `rep:energy`. The pair is
outside the current whitelist, producing `REP-UNIT-001`, and outside the
Spectrum profile, producing warning `REP-UNIT-011`.

## TimeSeries — rank 1, time axis

**Data.** A decaying signal:

| time (s) | intensity |
|---:|---:|
| 0.5 | 125 |
| 1.0 | 101 |
| 1.5 | 82 |

**Complete RDF** — `examples/timeseries-valid-abox.ttl`

```turtle
@prefix ex:   <http://example.org/representation/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

## expect: conforms
## case: TimeSeries / valid optional unit

ex:timeseries-property a tax:MaterialProperty ;
    rep:has_timeseries_representation ex:timeseries-valid-dataset .

ex:timeseries-valid-dataset a rep:TimeSeries ;
    rep:rank "1"^^xsd:nonNegativeInteger ;
    rep:extent "3"^^xsd:nonNegativeInteger ;
    qb:structure ex:timeseries-valid-dsd .

ex:timeseries-valid-dsd a rep:DataStructureDefinition ;
    qb:component
        ex:timeseries-valid-axis-time,
        ex:timeseries-valid-signal .

ex:timeseries-valid-axis-time a qb:ComponentSpecification ;
    qb:dimension rep:time ; rep:hasUnit unit:SEC .

ex:timeseries-valid-signal a qb:ComponentSpecification ;
    qb:measure rep:intensity .

ex:timeseries-valid-observation a rep:Observation ;
    qb:dataSet ex:timeseries-valid-dataset ;
    rep:time "0.5"^^xsd:double ;
    rep:intensity "125"^^xsd:nonNegativeInteger .

ex:timeseries-valid-observation-2 a rep:Observation ;
    qb:dataSet ex:timeseries-valid-dataset ;
    rep:time "1.0"^^xsd:double ;
    rep:intensity "101"^^xsd:nonNegativeInteger .

ex:timeseries-valid-observation-3 a rep:Observation ;
    qb:dataSet ex:timeseries-valid-dataset ;
    rep:time "1.5"^^xsd:double ;
    rep:intensity "82"^^xsd:nonNegativeInteger .
```

The time unit is omitted; the intensity specification supplies
`unit:COUNT`. Optionality is independent per specification. The supplied
intensity pair conforms to `tax:Intensity → unit:COUNT`.

The invalid-unit fixture supplies `unit:EV` for the time axis, producing
`REP-UNIT-001` and warning `REP-UNIT-012`.

## DepthProfile — rank 1, depth axis

**Data.** Three points into a surface:

| depth (nm) | intensity |
|---:|---:|
| 25.0 | 125 |
| 27.5 | 112 |
| 30.0 | 97 |

**Complete RDF** — `examples/depthprofile-valid-abox.ttl`

```turtle
@prefix ex:   <http://example.org/representation/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

## expect: conforms
## case: DepthProfile / valid optional unit

ex:depthprofile-property a tax:MaterialProperty ;
    rep:has_depthprofile_representation ex:depthprofile-valid-dataset .

ex:depthprofile-valid-dataset a rep:DepthProfile ;
    rep:rank "1"^^xsd:nonNegativeInteger ;
    rep:extent "3"^^xsd:nonNegativeInteger ;
    qb:structure ex:depthprofile-valid-dsd .

ex:depthprofile-valid-dsd a rep:DataStructureDefinition ;
    qb:component
        ex:depthprofile-valid-axis-depth,
        ex:depthprofile-valid-signal .

ex:depthprofile-valid-axis-depth a qb:ComponentSpecification ;
    qb:dimension rep:depth ; rep:hasUnit unit:NanoM .

ex:depthprofile-valid-signal a qb:ComponentSpecification ;
    qb:measure rep:intensity .

ex:depthprofile-valid-observation a rep:Observation ;
    qb:dataSet ex:depthprofile-valid-dataset ;
    rep:depth "25.0"^^xsd:double ;
    rep:intensity "125"^^xsd:nonNegativeInteger .

ex:depthprofile-valid-observation-2 a rep:Observation ;
    qb:dataSet ex:depthprofile-valid-dataset ;
    rep:depth "27.5"^^xsd:double ;
    rep:intensity "112"^^xsd:nonNegativeInteger .

ex:depthprofile-valid-observation-3 a rep:Observation ;
    qb:dataSet ex:depthprofile-valid-dataset ;
    rep:depth "30.0"^^xsd:double ;
    rep:intensity "97"^^xsd:nonNegativeInteger .
```

The depth specification supplies `unit:NanoM`; the signal unit is omitted.
`unit:NanoM` is whitelisted for `qk:Length` and matches the retained
DepthProfile convention.

The invalid-unit fixture supplies `unit:SEC` for the depth axis. It produces
`REP-UNIT-001` and advisory `REP-UNIT-013`. `unit:MicroM` would pass the
whitelist because it is a supported length unit, but it would produce only the
DepthProfile profile warning.

## Image — rank 2, y and x axes

**Data.** A 2 × 2 intensity image:

| y \ x | 0 | 1 |
|---:|---:|---:|
| 0 | 125 | 140 |
| 1 | 119 | 153 |

**Complete RDF** — `examples/image-valid-abox.ttl`

```turtle
@prefix ex:   <http://example.org/representation/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

## expect: conforms
## case: Image / valid optional unit

ex:image-property a tax:MaterialProperty ;
    rep:has_image_representation ex:image-valid-dataset .

ex:image-valid-dataset a rep:Image ;
    rep:rank "2"^^xsd:nonNegativeInteger ;
    rep:extent "4"^^xsd:nonNegativeInteger ;
    qb:structure ex:image-valid-dsd .

ex:image-valid-dsd a rep:DataStructureDefinition ;
    qb:component
        ex:image-valid-axis-y,
        ex:image-valid-axis-x,
        ex:image-valid-signal .

ex:image-valid-axis-y a qb:ComponentSpecification ;
    qb:dimension rep:y ; rep:hasUnit unit:MicroM .

ex:image-valid-axis-x a qb:ComponentSpecification ;
    qb:dimension rep:x .

ex:image-valid-signal a qb:ComponentSpecification ;
    qb:measure rep:intensity .

ex:image-valid-observation a rep:Observation ;
    qb:dataSet ex:image-valid-dataset ;
    rep:y "0"^^xsd:nonNegativeInteger ;
    rep:x "0"^^xsd:nonNegativeInteger ;
    rep:intensity "125"^^xsd:nonNegativeInteger .

ex:image-valid-observation-y0-x1 a rep:Observation ;
    qb:dataSet ex:image-valid-dataset ;
    rep:y "0"^^xsd:nonNegativeInteger ;
    rep:x "1"^^xsd:nonNegativeInteger ;
    rep:intensity "140"^^xsd:nonNegativeInteger .

ex:image-valid-observation-y1-x0 a rep:Observation ;
    qb:dataSet ex:image-valid-dataset ;
    rep:y "1"^^xsd:nonNegativeInteger ;
    rep:x "0"^^xsd:nonNegativeInteger ;
    rep:intensity "119"^^xsd:nonNegativeInteger .

ex:image-valid-observation-y1-x1 a rep:Observation ;
    qb:dataSet ex:image-valid-dataset ;
    rep:y "1"^^xsd:nonNegativeInteger ;
    rep:x "1"^^xsd:nonNegativeInteger ;
    rep:intensity "153"^^xsd:nonNegativeInteger .
```

Only the y specification supplies `unit:MicroM`. The x and intensity units are
omitted, proving that optionality applies to individual slots rather than to
the dataset as a whole. Every observation supplies one value for both declared
dimensions and the measure.

The invalid-unit fixture supplies `unit:SEC` for y. It produces
`REP-UNIT-001` and advisory `REP-UNIT-014`.

## VolumeData — rank 3, z, y and x axes

**Data.** A 2 × 2 × 2 volume:

| z | y | x | intensity |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 125 |
| 0 | 0 | 1 | 132 |
| 0 | 1 | 0 | 118 |
| 0 | 1 | 1 | 147 |
| 1 | 0 | 0 | 121 |
| 1 | 0 | 1 | 128 |
| 1 | 1 | 0 | 115 |
| 1 | 1 | 1 | 144 |

**Complete RDF** — `examples/volume-valid-abox.ttl`

```turtle
@prefix ex:   <http://example.org/representation/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

## expect: conforms
## case: VolumeData / valid optional unit

ex:volume-property a tax:MaterialProperty ;
    rep:has_volume_representation ex:volume-valid-dataset .

ex:volume-valid-dataset a rep:VolumeData ;
    rep:rank "3"^^xsd:nonNegativeInteger ;
    rep:extent "8"^^xsd:nonNegativeInteger ;
    qb:structure ex:volume-valid-dsd .

ex:volume-valid-dsd a rep:DataStructureDefinition ;
    qb:component
        ex:volume-valid-axis-z,
        ex:volume-valid-axis-y,
        ex:volume-valid-axis-x,
        ex:volume-valid-signal .

ex:volume-valid-axis-z a qb:ComponentSpecification ;
    qb:dimension rep:z ; rep:hasUnit unit:MicroM .

ex:volume-valid-axis-y a qb:ComponentSpecification ;
    qb:dimension rep:y .

ex:volume-valid-axis-x a qb:ComponentSpecification ;
    qb:dimension rep:x .

ex:volume-valid-signal a qb:ComponentSpecification ;
    qb:measure rep:intensity .

ex:volume-valid-observation a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "0"^^xsd:nonNegativeInteger ;
    rep:y "0"^^xsd:nonNegativeInteger ;
    rep:x "0"^^xsd:nonNegativeInteger ;
    rep:intensity "125"^^xsd:nonNegativeInteger .

ex:volume-valid-observation-z0-y0-x1 a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "0"^^xsd:nonNegativeInteger ; rep:y "0"^^xsd:nonNegativeInteger ;
    rep:x "1"^^xsd:nonNegativeInteger ; rep:intensity "132"^^xsd:nonNegativeInteger .
ex:volume-valid-observation-z0-y1-x0 a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "0"^^xsd:nonNegativeInteger ; rep:y "1"^^xsd:nonNegativeInteger ;
    rep:x "0"^^xsd:nonNegativeInteger ; rep:intensity "118"^^xsd:nonNegativeInteger .
ex:volume-valid-observation-z0-y1-x1 a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "0"^^xsd:nonNegativeInteger ; rep:y "1"^^xsd:nonNegativeInteger ;
    rep:x "1"^^xsd:nonNegativeInteger ; rep:intensity "147"^^xsd:nonNegativeInteger .
ex:volume-valid-observation-z1-y0-x0 a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "1"^^xsd:nonNegativeInteger ; rep:y "0"^^xsd:nonNegativeInteger ;
    rep:x "0"^^xsd:nonNegativeInteger ; rep:intensity "121"^^xsd:nonNegativeInteger .
ex:volume-valid-observation-z1-y0-x1 a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "1"^^xsd:nonNegativeInteger ; rep:y "0"^^xsd:nonNegativeInteger ;
    rep:x "1"^^xsd:nonNegativeInteger ; rep:intensity "128"^^xsd:nonNegativeInteger .
ex:volume-valid-observation-z1-y1-x0 a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "1"^^xsd:nonNegativeInteger ; rep:y "1"^^xsd:nonNegativeInteger ;
    rep:x "0"^^xsd:nonNegativeInteger ; rep:intensity "115"^^xsd:nonNegativeInteger .
ex:volume-valid-observation-z1-y1-x1 a rep:Observation ;
    qb:dataSet ex:volume-valid-dataset ;
    rep:z "1"^^xsd:nonNegativeInteger ; rep:y "1"^^xsd:nonNegativeInteger ;
    rep:x "1"^^xsd:nonNegativeInteger ; rep:intensity "144"^^xsd:nonNegativeInteger .
```

Only z has an explicit dataset-specific unit. All eight observations are
complete for z, y, x, and intensity. RDF expansion is useful for small,
addressable examples; large volumes should keep their numerical arrays in
HDF5, Zarr, NeXus, or another array format and use RDF for semantics and access
metadata.

The invalid-unit fixture supplies `unit:SEC` for z. It produces
`REP-UNIT-001` and advisory `REP-UNIT-015`.

# Optional units and the whitelist

`rep:hasQuantityKind` and `rep:hasUnit` are independent edges:

```turtle
rep:energy rep:hasQuantityKind qk:Energy .
ex:energy-spec qb:dimension rep:energy ;
    rep:hasUnit unit:EV .
```

The unit can occur directly on a reusable component or on the
dataset-specific component specification. It is optional in both locations.

## What is required

Every `rep:ComponentProperty` must identify exactly one IRI typed as
`qudt:QuantityKind`. This requirement remains even when no unit is supplied,
because the quantity kind is the semantic anchor for the component.

If `rep:hasUnit` is present, validation requires:

1. zero or one unit value overall;
2. an IRI value;
3. exactly one resolvable quantity kind;
4. a quantity-kind/unit pair in the validator-owned whitelist.

## Current whitelist

| Quantity kind | Permitted unit |
|---|---|
| `qk:Temperature` | `unit:K` |
| `qk:Length` | `unit:NanoM`, `unit:MicroM` |
| `qk:Time` | `unit:SEC` |
| `qk:Energy` | `unit:EV` |
| `tax:Intensity` | `unit:COUNT` |

The table expresses application support. A unit absent from the table is
unsupported by this profile. It is not automatically scientifically
incompatible. Metres are physically valid for length but are currently
outside this profile.

The whitelist is trusted validation configuration. Producers must not be able
to make submitted data conform by adding their own `shp:permitsUnit` triples.

# SHACL validation

The shapes graph is unit-scoped and provides stable, machine-readable codes.

| Code | Severity | Meaning |
|---|---|---|
| `REP-UNIT-001` | Violation | supplied pair is outside the whitelist |
| `REP-UNIT-002` | Violation | a quantity kind is used as a unit |
| `REP-UNIT-003` | Violation | unit value is non-IRI or occurs more than once |
| `REP-UNIT-004` | Violation | component lacks one typed quantity kind |
| `REP-UNIT-005` | Violation | unit-bearing node lacks one resolvable kind |
| `REP-UNIT-010` | Warning | Scalar temperature outside K profile |
| `REP-UNIT-011` | Warning | Spectrum axis outside eV profile |
| `REP-UNIT-012` | Warning | TimeSeries axis outside seconds profile |
| `REP-UNIT-013` | Warning | DepthProfile axis outside nanometre profile |
| `REP-UNIT-014` | Warning | Image axis outside micrometre/nanometre profile |
| `REP-UNIT-015` | Warning | Volume axis outside micrometre/nanometre profile |
| `REP-UNIT-016` | Warning | intensity outside count profile |

## Optionality versus completeness

These statements conform:

```turtle
ex:time-spec qb:dimension rep:time .
ex:intensity-spec qb:measure rep:intensity .
```

The unit is absent, while `rep:time` and `rep:intensity` already carry their
quantity kinds.

This statement fails:

```turtle
ex:custom-signal a rep:Signal .
```

It lacks `rep:hasQuantityKind` and produces `REP-UNIT-004`.

This unit-bearing specification also fails:

```turtle
ex:custom-spec qb:measure ex:custom-signal ;
    rep:hasUnit unit:COUNT .
```

The specification cannot resolve a kind, so it produces `REP-UNIT-005` as well.

## Why SHACL is used

OWL's open-world semantics does not treat a missing whitelist triple as false.
The profile needs closed-world validation over a controlled graph:

```text
for each supplied hasUnit(subject, unit):
    resolve exactly one kind
    require permitsUnit(kind, unit)
```

The whitelist check is an anti-join:

```sparql
FILTER NOT EXISTS { ?kind shp:permitsUnit ?unit }
```

OWL still supplies useful entailments: subclass classification, domains,
ranges, functional properties, disjoint component roles, and rank-based
classes. SHACL checks explicit data completeness and application policy.

## Structured results

Each named shape carries:

```turtle
shp:code
shp:category
shp:layer
shp:remedy
```

A validation result points to a source shape. The test runner walks from a
nested property or SPARQL shape to its named owner and reads the stable code.
Consumers should use the code; the result message is written for the human
reader.

## Test matrix

There are three fixtures for every representation:

| Representation | Valid | Wrong supplied unit | Missing quantity kind |
|---|---|---|---|
| Scalar | conforms | `001`, `010` | `004`, `005` |
| Spectrum | conforms | `001`, `011` | `004`, `005` |
| TimeSeries | conforms | `001`, `012` | `004`, `005` |
| DepthProfile | conforms | `001`, `013` | `004`, `005` |
| Image | conforms | `001`, `014` | `004`, `005` |
| VolumeData | conforms | `001`, `015` | `004`, `005` |

Warnings are reported but remain non-blocking when `allow_warnings=True`.

# Description logic and formal notation

## Core class axioms

```text
DataStructureDefinition ⊑ Representation ⊓ qb:DataStructureDefinition
ComponentProperty       ⊑ Representation ⊓ qb:ComponentProperty
Observation             ⊑ Representation ⊓ qb:Observation

Axis          ⊑ ComponentProperty ⊓ qb:DimensionProperty
Signal        ⊑ ComponentProperty ⊓ qb:MeasureProperty
UnitAttribute ⊑ ComponentProperty ⊓ qb:AttributeProperty

ComponentProperty ≡ Axis ⊔ Signal ⊔ UnitAttribute
Axis ⊓ Signal ≡ ⊥
Axis ⊓ UnitAttribute ≡ ⊥
Signal ⊓ UnitAttribute ≡ ⊥
```

The `owl:disjointUnionOf` axiom partitions component roles. If one resource is
both an Axis and Signal, an OWL reasoner can detect an inconsistency.

## Rank definitions

```text
Scalar     ≡ Representation ⊓ ∃rank.{0}
Profile    ≡ Representation ⊓ ∃rank.{1}
Image      ≡ Representation ⊓ ∃rank.{2}
VolumeData ≡ Representation ⊓ ∃rank.{3}

Spectrum     ⊑ Profile
TimeSeries   ⊑ Profile
DepthProfile ⊑ Profile
```

## Property axioms

```text
domain(hasQuantityKind) = ComponentProperty
range(hasQuantityKind)  = qudt:QuantityKind
Functional(hasQuantityKind)

domain(hasUnit) = ComponentProperty ⊔ qb:ComponentSpecification
range(hasUnit)  = qudt:Unit
Functional(hasUnit)

has_scalar_representation       ⊑ has_representation
has_spectrum_representation     ⊑ has_representation
has_timeseries_representation   ⊑ has_representation
has_depthprofile_representation ⊑ has_representation
has_image_representation        ⊑ has_representation
has_volume_representation       ⊑ has_representation
```

`Functional(hasUnit)` means at most one filler under OWL semantics. It does not
require a filler. SHACL `sh:maxCount 1` checks the explicit graph and does not
infer `owl:sameAs` between two supplied units.

## Validation predicates

Let `kind(s)` be the union of the direct and component-mediated paths:

```text
kind(s) =
  { k | hasQuantityKind(s,k) }
  ∪ { k | dimension(s,c) ∧ hasQuantityKind(c,k) }
  ∪ { k | measure(s,c) ∧ hasQuantityKind(c,k) }
  ∪ { k | attribute(s,c) ∧ hasQuantityKind(c,k) }
```

For every unit-bearing subject `s`, the required condition is:

```text
|kind(s)| = 1
and
(hasUnit(s,u) → permitsUnit(kind(s),u))
```

For every representation component `c`:

```text
|hasQuantityKind(c)| = 1
```

The last condition does not make units mandatory.

# What can be queried and inferred

Without entailment, SPARQL can retrieve:

- representation instances with explicitly stated types and ranks;
- dataset-to-DSD and DSD-to-component paths;
- dimensions, measures, quantity kinds, supplied units, and observations;
- the complete whitelist;
- missing quantity kinds and non-whitelisted supplied units.

With RDFS/OWL entailment, applications can additionally retrieve:

- every FAIRmat dataset as `qb:DataSet`;
- every FAIRmat observation as `qb:Observation`;
- rank-derived structural classes;
- domain/range-derived types;
- consequences of functionality and component-role disjointness.

SHACL adds:

- zero-or-one explicit unit enforcement;
- quantity-kind completeness;
- whitelist membership;
- per-representation advisory profiles;
- stable validation codes and remedies.

See `SPARQL_USAGE.md` for executable queries and their actual results.

# Known limits

The current unit shapes do not validate:

- rank against the number of dimensions;
- intended axis membership;
- extent multiplication;
- observation uniqueness;
- numeric datatypes;
- coordinate reference systems;
- calibration and uncertainty;
- external dense-array locations;
- all RDF Data Cube integrity constraints.

The following ontology decisions remain pending separate review:

- rank alone defines the structural representation class;
- representation properties remain functional;
- canonical components retain unit assertions without default semantics.

# See also

- `SPARQL_USAGE.md`
- `complexity.md`
- `tbox-illustration/overview.md`
- `tbox-illustration/class-hierarchy.md`
- `tbox-illustration/validation.md`
- `CHANGELOG/deferred.txt`
