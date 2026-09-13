# Overview — the complete module

This page explains the ontology from the material property to concrete values.
It also shows which statements belong to OWL, RDF Data Cube, QUDT, and SHACL.

## Top-level architecture

```mermaid
flowchart TB
    MP["Material property"] -->|representation property| DS["Representation dataset"]
    DS -->|qb:structure| DSD["Data structure definition"]
    DSD -->|qb:component| SPEC["Component specification"]
    SPEC -->|dimension or measure| COMP["Axis or signal"]
    COMP -->|hasQuantityKind| KIND["QUDT quantity kind"]
    SPEC -->|optional hasUnit| UNIT["QUDT unit"]
    KIND -.->|validator whitelist| UNIT
    OBS["Observation"] -->|qb:dataSet| DS
    OBS -->|component predicates| COMP
```

The dataset states rank and links to one structure. The DSD lists
dataset-specific specification nodes. A specification selects a reusable
component and may state a unit. An observation uses the component IRI as a
predicate whose object is the measured value.

## Vocabulary ownership

| Namespace | Responsibility in this module |
|---|---|
| `tax:` | material-property domain and local uncalibrated Intensity kind |
| `rep:` | representation classes, components, rank, extent, and links |
| `qb:` | dataset, DSD, component-specification, and observation pattern |
| `qudt:` | canonical QuantityKind and Unit classes |
| `qk:` | quantity-kind individuals |
| `unit:` | unit individuals |
| `shp:` | validator-owned whitelist and stable result metadata |
| `sh:` | SHACL shapes, targets, paths, severities, and reports |

The QUDT schema prefix is `http://qudt.org/schema/qudt/`. FAIRmat classes use
`rdfs:subClassOf` to specialize RDF Data Cube classes.

## One complete Image path

```mermaid
flowchart TB
    PROP["ex:image-property"] -->|has_image_representation| IMG["ex:image-valid-dataset"]
    IMG -->|qb:structure| DSD["ex:image-valid-dsd"]
    DSD --> YS["y specification"]
    DSD --> XS["x specification"]
    DSD --> IS["intensity specification"]
    YS -->|qb:dimension| Y["rep:y"]
    XS -->|qb:dimension| X["rep:x"]
    IS -->|qb:measure| INT["rep:intensity"]
    Y -->|hasQuantityKind| LEN["qk:Length"]
    X -->|hasQuantityKind| LEN
    INT -->|hasQuantityKind| IK["tax:Intensity"]
    YS -->|hasUnit| UM["unit:MicroM"]
```

Only the y specification supplies a unit. The x and intensity specifications
remain valid because `rep:hasUnit` is optional.

A pixel is a separate node:

```turtle
ex:image-valid-observation-y1-x1 a rep:Observation ;
    qb:dataSet ex:image-valid-dataset ;
    rep:y "1"^^xsd:nonNegativeInteger ;
    rep:x "1"^^xsd:nonNegativeInteger ;
    rep:intensity "153"^^xsd:nonNegativeInteger .
```

The observation can be queried without traversing a positional list. The DSD
tells a generic client which predicates constitute the coordinates and
measures.

## Schema reuse and dataset-specific metadata

```mermaid
flowchart TB
    D1["Dataset A"] -->|qb:structure| DSD["Shared DSD"]
    D2["Dataset B"] -->|qb:structure| DSD
    DSD --> SPEC["Component specifications"]
    SPEC --> COMP["Canonical components"]
    SPEC --> UNIT["Optional dataset unit"]
```

The model allows a DSD to be reused. In the supplied examples, each fixture
uses its own named DSD so validation cases remain independent.

The component carries its stable meaning:

```turtle
rep:energy a owl:NamedIndividual, owl:DatatypeProperty, rep:Axis ;
    rdfs:range rdfs:Literal ;
    rep:hasQuantityKind qk:Energy ;
    rep:hasUnit unit:EV .
```

A specification carries dataset context:

```turtle
ex:spectrum-valid-axis-energy a qb:ComponentSpecification ;
    qb:dimension rep:energy ;
    rep:hasUnit unit:EV .
```

The canonical unit assertion is retained ontology metadata. The model defines
no algorithm that copies it to a specification or treats it as a fallback.

## OWL and SHACL responsibilities

```mermaid
flowchart LR
    OWL["OWL and RDFS"] --> E["Entailments"]
    DATA["Explicit ABox"] --> SHACL["SHACL validation"]
    RULES["Trusted shapes and whitelist"] --> SHACL
    SHACL --> REPORT["Validation report"]
```

OWL/RDFS handles:

- class and subproperty relationships;
- rank-based class definitions;
- domains, ranges, and functional properties;
- the disjoint union of Axis, Signal, and UnitAttribute;
- Data Cube superclass inference.

SHACL handles:

- required quantity-kind metadata;
- optional-unit explicit cardinality;
- unit IRI checks;
- whitelist membership when a unit is present;
- advisory representation profiles;
- stable error codes and remedies.

## Rank and scientific specialization

```mermaid
flowchart TB
    R["rep:Representation"] --> S["rep:Scalar, rank 0"]
    R --> P["rep:Profile, rank 1"]
    R --> I["rep:Image, rank 2"]
    R --> V["rep:VolumeData, rank 3"]
    P --> SP["rep:Spectrum"]
    P --> TS["rep:TimeSeries"]
    P --> DP["rep:DepthProfile"]
```

The four rank classes are defined classes. The three profile types are
primitive scientific specializations asserted by the producer.

## Query path

A generic consumer can discover and read values in four steps:

```mermaid
flowchart LR
    FIND["Find dataset"] --> STRUCT["Read DSD"]
    STRUCT --> SLOTS["Resolve components"]
    SLOTS --> VALUES["Query observations"]
    VALUES --> VALIDATE["Inspect SHACL status"]
```

The ontology provides no component ordering. Consumers query membership and
apply a separately agreed serialization rule when they need array order.

## Continue reading

- [class-hierarchy.md](class-hierarchy.md) gives every class bridge and key
  property axiom.
- [scalar.md](scalar.md) explains the rank-zero case.
- [profile.md](profile.md) compares Spectrum, TimeSeries, and DepthProfile.
- [image.md](image.md) walks through the 2 × 2 image.
- [volume.md](volume.md) walks through the 2 × 2 × 2 volume.
- [validation.md](validation.md) maps each SHACL code to the graph path it
  checks.

