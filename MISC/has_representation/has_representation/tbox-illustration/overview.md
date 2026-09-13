# Ontology overview

The solid arrows below are OWL/RDFS relations. The dotted arrow is the
validator-owned whitelist lookup.

```mermaid
flowchart TB
    MP["tax:MaterialProperty"] -->|has representation| DS["Representation dataset"]
    DS -->|qb:structure| DSD["Data structure definition"]
    DSD -->|qb:component| CS["Component specification"]
    CS -->|dimension / measure| CP["Axis or signal"]
    CP -->|quantity kind| QK["QUDT quantity kind"]
    CS -->|optional unit| U["QUDT unit"]
    QK -.->|whitelist permits| U
```

The dataset-specific `rep:hasUnit` edge may be absent. If it exists, SHACL
resolves the component's quantity kind and checks the pair against the
whitelist.

## Class hierarchy and external bridges

```mermaid
flowchart TB
    R["rep:Representation"] --> DSD["rep:DataStructureDefinition"]
    R --> CP["rep:ComponentProperty"]
    R --> OBS["rep:Observation"]
    R --> DATA["Scalar / Profile / Image / VolumeData"]
    DSD -->|subclass| QDSD["qb:DataStructureDefinition"]
    OBS -->|subclass| QOBS["qb:Observation"]
    DATA -->|subclass| QDATA["qb:DataSet"]
    CP --> AX["rep:Axis"]
    CP --> SG["rep:Signal"]
    AX -->|subclass| QDIM["qb:DimensionProperty"]
    SG -->|subclass| QMEAS["qb:MeasureProperty"]
```

`skos:closeMatch` is not used for these class relationships. Each FAIRmat
class is narrower than its RDF Data Cube parent.

## One Image example

```mermaid
flowchart TB
    IMG["Image dataset, rank 2"] -->|qb:structure| DSD["Image DSD"]
    DSD --> YS["y spec, MicroM"]
    DSD --> XS["x spec, unit omitted"]
    DSD --> IS["intensity spec, unit omitted"]
    YS -->|qb:dimension| Y["rep:y, Length"]
    XS -->|qb:dimension| X["rep:x, Length"]
    IS -->|qb:measure| I["rep:intensity"]
```

The omitted x and intensity units are valid. The graph does not inherit or
copy the retained canonical unit assertions.
