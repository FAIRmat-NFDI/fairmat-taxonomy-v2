# Representation — FAIRmat taxonomy module

This module describes the structural representation of material-property data
as OWL 2. It covers scalar values, one-dimensional profiles, images,
three-dimensional volumes, their components, and their observations.

The model reuses the W3C RDF Data Cube vocabulary for dataset structure and
QUDT for quantity kinds and units. The companion SHACL graph currently
validates only unit-related metadata.

## Contents

```text
representation.ttl              OWL ontology
representation.shacl.ttl        unit validation profile and whitelist
examples/                       valid and invalid ABox fixtures
test/representation_test.py     executable validation checks
test/reports.md                 generated validation summary
tbox-illustration/              Mermaid explanations
SPARQL_USAGE.md                 query patterns
complexity.md                   graph-size and validation analysis
CHANGELOG/                      changes and deferred decisions
```

`examples-TBOX/` is intentionally absent. The executable examples combine
the ontology with small ABoxes and provide the required documentation.

## Quick start

Install the two Python dependencies and execute the test runner:

```bash
python -m pip install rdflib pyshacl
python test/representation_test.py
```

The runner resolves paths relative to itself, so it can be launched from any
working directory. It parses both RDF files, validates every example, checks
the ontology integration contract, checks observation completeness, and
regenerates `test/reports.md`.

The validation data graph must include three trusted inputs:

1. the producer data;
2. `representation.ttl`;
3. the `shp:permitsUnit` whitelist from `representation.shacl.ttl`.

The complete SHACL file may be loaded as the third input, as the bundled test
does. A production system should prevent producers from adding
`shp:permitsUnit` statements to their submitted data.

## The model

The representation has four layers:

| Layer | Main class | Purpose |
|---|---|---|
| representation | `rep:Scalar`, `rep:Profile`, `rep:Image`, `rep:VolumeData` | identifies the dataset shape |
| schema | `rep:DataStructureDefinition` | lists component specifications |
| component | `rep:Axis`, `rep:Signal`, `rep:UnitAttribute` | identifies coordinate and measured quantities |
| observation | `rep:Observation` | carries concrete values |

A dataset links to its schema with `qb:structure`. The schema contains
`qb:ComponentSpecification` nodes through `qb:component`. Each
specification identifies a dimension, measure, or attribute. Observations use
the component IRI itself as a predicate.

### RDF Data Cube alignment

FAIRmat classes are specialized RDF Data Cube classes:

```text
rep:DataStructureDefinition  rdfs:subClassOf  qb:DataStructureDefinition
rep:Scalar                   rdfs:subClassOf  qb:DataSet
rep:Profile                  rdfs:subClassOf  qb:DataSet
rep:Image                    rdfs:subClassOf  qb:DataSet
rep:VolumeData               rdfs:subClassOf  qb:DataSet
rep:Observation              rdfs:subClassOf  qb:Observation
rep:Axis                     rdfs:subClassOf  qb:DimensionProperty
rep:Signal                   rdfs:subClassOf  qb:MeasureProperty
rep:UnitAttribute            rdfs:subClassOf  qb:AttributeProperty
```

These bridges replace the former `skos:closeMatch` statements. Under RDFS or
OWL entailment, an instance of `rep:Image` is consequently also a
`qb:DataSet`. Applications without entailment may materialize the superclass
types during ingestion.

The ontology declares only the external entities it references. It does not
redefine Data Cube domains, ranges, disjointness, cardinalities, or ordering.
Load the official Data Cube vocabulary separately when its complete axioms or
integrity constraints are required.

### Rank determines the current representation class

The supplied rank definitions are retained:

| Representation | Rank | Intended axes |
|---|---:|---|
| `rep:Scalar` | 0 | none |
| `rep:Spectrum` | 1 | energy |
| `rep:TimeSeries` | 1 | time |
| `rep:DepthProfile` | 1 | depth |
| `rep:Image` | 2 | y, x |
| `rep:VolumeData` | 3 | z, y, x |

`Scalar`, `Profile`, `Image`, and `VolumeData` are defined classes.
For example:

```text
Image ≡ Representation ⊓ ∃rank.{2}
```

`Spectrum`, `TimeSeries`, and `DepthProfile` are asserted specializations
of `Profile`; rank alone cannot distinguish them.

The ontology does not define component ordering. Consumers must not interpret
`qb:order` or a local `rep:order` as array-storage semantics from this
module. If array order is needed later, it requires a separately named and
defined property.

### Canonical components

| Component | Role | Quantity kind | Retained unit assertion |
|---|---|---|---|
| `rep:x` | axis | `qk:Length` | `unit:MicroM` |
| `rep:y` | axis | `qk:Length` | `unit:MicroM` |
| `rep:z` | axis | `qk:Length` | `unit:MicroM` |
| `rep:depth` | axis | `qk:Length` | `unit:NanoM` |
| `rep:energy` | axis | `qk:Energy` | `unit:EV` |
| `rep:time` | axis | `qk:Time` | `unit:SEC` |
| `rep:intensity` | signal | `tax:Intensity` | `unit:COUNT` |
| `rep:temperature` | signal | `qk:Temperature` | `unit:K` |

Each canonical component is explicitly both an OWL named individual and an
OWL datatype property. This is OWL 2 punning: the individual carries metadata,
while the property is used on observations. The predicates have the broad
`rdfs:Literal` range because per-component numeric datatype restrictions are
not yet part of this module.

The canonical unit assertions are retained from the supplied ontology. This
version introduces no default, inheritance, fallback, or override semantics
for them. When a dataset-specific component specification omits
`rep:hasUnit`, its unit remains unspecified by the validation contract.

## The six representations

### Scalar

A Scalar has no axis and normally has one measured component:

```turtle
ex:reading a rep:Scalar ;
    rep:rank "0"^^xsd:nonNegativeInteger ;
    qb:structure ex:scalar-dsd .

ex:scalar-dsd a rep:DataStructureDefinition ;
    qb:component ex:temperature-spec .

ex:temperature-spec a qb:ComponentSpecification ;
    qb:measure rep:temperature .

ex:observation a rep:Observation ;
    qb:dataSet ex:reading ;
    rep:temperature "293.15"^^xsd:double .
```

The omitted unit is valid.

### Spectrum

A Spectrum is a rank-one Profile with an energy axis. If a unit is supplied,
it must match the whitelist:

```turtle
ex:energy-spec a qb:ComponentSpecification ;
    qb:dimension rep:energy ;
    rep:hasUnit unit:EV .
```

### TimeSeries

A TimeSeries is a rank-one Profile with a time axis. `unit:SEC` is currently
the whitelisted time unit.

### DepthProfile

A DepthProfile is a rank-one Profile with a depth axis. `unit:NanoM` and
`unit:MicroM` are whitelisted for length, while the retained profile
convention prefers `unit:NanoM`.

### Image

An Image is currently rank two and uses y and x as intended axes. Units can be
omitted independently on its component specifications.

### VolumeData

VolumeData is currently rank three and uses z, y, and x as intended axes. Dense
volumes should normally remain in array storage; RDF should describe the
structure, semantics, provenance, and access path.

## Units

### Canonical QUDT IRIs

The schema prefix is:

```turtle
@prefix qudt: <http://qudt.org/schema/qudt/> .
```

Therefore, the range classes are the canonical resources:

```text
http://qudt.org/schema/qudt/QuantityKind
http://qudt.org/schema/qudt/Unit
```

Quantity kinds and units continue to use:

```text
http://qudt.org/vocab/quantitykind/
http://qudt.org/vocab/unit/
```

### Optional-unit contract

`rep:hasUnit` has cardinality zero or one. The following is valid:

```turtle
ex:time-spec qb:dimension rep:time .
```

If the producer supplies a unit, the unit must:

- be an IRI;
- occur at most once;
- resolve to exactly one quantity kind;
- be present in the validator-owned `shp:permitsUnit` whitelist for that
  quantity kind.

Whitelist rejection means “unsupported by the current application profile.”
It does not claim that the pair is physically dimensionally incompatible.

The current whitelist is:

| Quantity kind | Permitted units |
|---|---|
| `qk:Temperature` | `unit:K` |
| `qk:Length` | `unit:NanoM`, `unit:MicroM` |
| `qk:Time` | `unit:SEC` |
| `qk:Energy` | `unit:EV` |
| `tax:Intensity` | `unit:COUNT` |

The whitelist is intentionally a closed deployment policy. Extending it is a
curated change to `representation.shacl.ttl`.

## SHACL validation

The shapes graph is unit-scoped.

| Code | Severity | Meaning |
|---|---|---|
| `REP-UNIT-001` | Violation | supplied unit is outside the whitelist for the resolved kind |
| `REP-UNIT-002` | Violation | a quantity-kind resource was used as a unit |
| `REP-UNIT-003` | Violation | supplied unit is not one IRI or occurs more than once |
| `REP-UNIT-004` | Violation | a component lacks exactly one typed quantity kind |
| `REP-UNIT-005` | Violation | a unit-bearing node has no unique quantity-kind context |
| `REP-UNIT-010`–`016` | Warning | supplied unit differs from the retained representation profile |

Warnings are advisory. The bundled runner uses `allow_warnings=True`, so a
warning-only graph still conforms.

The following remain outside this unit-only shapes graph:

- rank against dimension count;
- canonical axis membership;
- extent arithmetic;
- observation-coordinate uniqueness;
- observation datatype restrictions;
- complete RDF Data Cube integrity constraints.

## Test coverage

`examples/` contains 18 independent ABoxes:

- six valid examples;
- six examples with a supplied non-whitelisted unit;
- six examples with missing quantity-kind metadata.

Every representation type has all three cases. The test runner also checks
that each dataset has one schema, at least one linked observation, and exactly
one observation value for every declared dimension and measure.

## Known semantic decisions

The following supplied semantics are preserved pending separate discussion:

- rank alone defines Scalar, Profile, Image, and VolumeData;
- `rep:has_representation` and its typed subproperties remain functional;
- canonical components retain their unit assertions;
- fixed axis membership is documented but not structurally validated.

## See also

- [SPARQL_USAGE.md](SPARQL_USAGE.md)
- [complexity.md](complexity.md)
- [tbox-illustration/overview.md](tbox-illustration/overview.md)
- [CHANGELOG/deferred.txt](CHANGELOG/deferred.txt)

