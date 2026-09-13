# Class hierarchy and the qb bridges

> Colour legend: purple = taxonomy, blue = dataset, teal = schema,
> amber = component specification, green = axis, pink = signal,
> grey = QUDT kind and unit. See [overview.md](overview.md).

Not a data walk — the TBox itself. Two things to see: everything
descends from `rep:Representation`, and five representation concepts
touch W3C RDF Data Cube.

---

## rep:Representation

```mermaid
flowchart TD
    R["<b>rep:Representation</b><br/>umbrella class"]

    R --> DSD["rep:DataStructureDefinition<br/><i>the schema</i>"]
    R --> CP["rep:ComponentProperty<br/><i>the slot descriptors</i>"]
    R --> OBS["rep:Observation<br/><i>one data point</i>"]
    R --> SC["rep:Scalar<br/>rank 0"]
    R --> PR["rep:Profile<br/>rank 1"]
    R --> IM["rep:Image<br/>rank 2"]
    R --> VD["rep:VolumeData<br/>rank 3"]

    CP --> AX["rep:Axis"]
    CP --> SG["rep:Signal"]
    CP --> UA["rep:UnitAttribute<br/><i>declared, unused</i>"]

    PR --> SP["rep:Spectrum"]
    PR --> TS["rep:TimeSeries"]
    PR --> DP["rep:DepthProfile"]

    classDef root fill:#ddeaff,stroke:#2f6fd0,stroke-width:3px,color:#10294f
    classDef dsd  fill:#d6f2ee,stroke:#1d8f7e,stroke-width:2px,color:#0d3d36
    classDef axis fill:#dcf5dc,stroke:#3d9440,stroke-width:2px,color:#173d18
    classDef sig  fill:#ffdfe9,stroke:#c9427a,stroke-width:2px,color:#4d162c
    classDef pale fill:#f4f5f7,stroke:#9aa4b0,stroke-width:1px,color:#4a5460,stroke-dasharray: 4 3

    class R root
    class DSD,CP,OBS,SC,PR,IM,VD,SP,TS,DP dsd
    class AX axis
    class SG sig
    class UA pale
```

`rep:ComponentProperty` is an `owl:disjointUnionOf (rep:Axis rep:Signal
rep:UnitAttribute)`. `rep:UnitAttribute` is drawn dashed because it is
declared but unused: this module attaches units directly rather than
through a qb attribute slot. It cannot simply be deleted — it is a
member of that disjoint union, and removing it would break the axiom.

That same axiom is why `rep:hasUnit` could not keep its original
`rdfs:domain rep:UnitAttribute`. A unit on `rep:energy` would have
entailed `rep:energy a rep:UnitAttribute`, colliding with `rep:Axis`.
Confirmed inconsistent under HermiT; see `CHANGELOG/representation.txt`.

---

## Where qb attaches

```mermaid
flowchart LR
    subgraph REP["representation module"]
        direction TB
        A["rep:DataStructureDefinition"]
        B["rep:Scalar / Profile / Image / VolumeData"]
        C["rep:Observation"]
        D["rep:Axis"]
        E["rep:Signal"]
    end

    subgraph QB["W3C RDF Data Cube"]
        direction TB
        QA["qb:DataStructureDefinition"]
        QB2["qb:DataSet"]
        QC["qb:Observation"]
        QD["qb:DimensionProperty"]
        QE["qb:MeasureProperty"]
    end

    A -.->|skos:closeMatch| QA
    B -.->|skos:closeMatch| QB2
    C -.->|skos:closeMatch| QC
    D ==>|rdfs:subClassOf| QD
    E ==>|rdfs:subClassOf| QE

    classDef mine fill:#ddeaff,stroke:#2f6fd0,stroke-width:2px,color:#10294f
    classDef theirs fill:#fff3d6,stroke:#c28b1b,stroke-width:2px,color:#4a3409
    class A,B,C,D,E mine
    class QA,QB2,QC,QD,QE theirs
```

The two heavy edges are real subsumption: `rep:Axis` is a subclass of
`qb:DimensionProperty`, and `rep:Signal` is a subclass of
`qb:MeasureProperty`. Canonical component IRIs are then used in two
roles in the RDF graph: as **individuals** with metadata and as
**predicates** on observations:

```turtle
rep:energy a rep:Axis ; rep:hasQuantityKind qk:Energy ; rep:hasUnit unit:EV .

ex:obs a rep:Observation , qb:Observation ;
    qb:dataSet ex:xps_survey ;
    rep:energy "7980.0"^^xsd:double ;
    rep:intensity "12"^^xsd:nonNegativeInteger .
```

The dotted edges are alignment only — `skos:closeMatch`, deliberately
not `owl:equivalentClass`, so importing qb is not a hard dependency.

**On flat per-axis predicates.** Using one shared `rdf:value` predicate
with a positional index was tried and fails: duplicate magnitudes
(Y = Z = 29.0) collapse, because RDF triples are a set. Per-axis
predicates are not stylistic — they are required for correctness.

---

## Every external vocabulary in the implementation

```mermaid
flowchart LR
    TAX["FAIRmat taxonomy<br/>tax:MaterialProperty"]
    REP["representation.ttl<br/>classes + properties"]
    QB["W3C RDF Data Cube<br/>datasets, DSDs, specs, observations"]
    QUDT["QUDT<br/>quantity kinds + units"]
    SKOS["SKOS<br/>prefLabel + closeMatch"]
    XSD["XML Schema<br/>rank, order, and value datatypes"]
    SHACL["representation.shacl.ttl<br/>closed-world unit rules"]

    TAX -->|domain of rep:has_representation| REP
    REP -->|qb:structure / component / dataSet| QB
    REP -->|rep:hasQuantityKind / hasUnit| QUDT
    REP -.->|skos:prefLabel / closeMatch| SKOS
    REP -->|xsd:nonNegativeInteger / double| XSD
    SHACL -->|validates rep + qb paths| REP
    SHACL -->|shp:permitsUnit| QUDT

    classDef mine fill:#ddeaff,stroke:#2f6fd0,stroke-width:2px,color:#10294f
    classDef ext fill:#eceff2,stroke:#7b8794,stroke-width:2px,color:#2b3138
    class REP mine
    class TAX,QB,QUDT,SKOS,XSD,SHACL ext
```

OWL/RDFS supplies class definitions, domains, ranges, functionality,
subclass/subproperty links, and the disjoint union. SKOS supplies loose
alignment where the module intentionally avoids importing an external
class as a hard dependency. SHACL supplies constraints that OWL cannot
express under open-world semantics.
