# VolumeData — rank 3

> Colour legend: purple = taxonomy, blue = dataset, teal = schema,
> amber = component specification, green = axis, pink = signal,
> yellow = observation/value, grey = QUDT kind and unit. See
> [overview.md](overview.md).

Three axes, `rep:z` then `rep:y` then `rep:x`, and one signal. Same
pattern as Image with one more dimension; slowest-first ordering again.

**Example data.** A tomography reconstruction, 2 slices of 2x3.

| z | y \ x | 0.0 | 0.5 | 1.0 |
|---|---|---|---|---|
| **0.0** | **0.0** | 120 | 118 | 131 |
| **0.0** | **0.5** | 119 | 145 | 162 |
| **1.0** | **0.0** | 122 | 117 | 129 |
| **1.0** | **0.5** | 118 | 140 | 158 |

Axis values in µm, cell values in counts. `rep:extent` on the dataset
is 12 — the product 2 x 2 x 3.

**Naming note.** The class is `rep:VolumeData`, not `rep:Volume`, and
carries `owl:disjointWith tax:Volume`. `tax:Volume` already exists in
the base taxonomy as a structural property — the amount of space a
material occupies. A 3D data cube is a different thing entirely, and
the collision is worth avoiding explicitly rather than by convention.

---

## TBox plus one ABox observation

```mermaid
flowchart LR
    MP["<b>tax:Porosity</b><br/>ex:pore_structure"]
    DS["<b>rep:VolumeData + qb:DataSet</b><br/>ex:tomo<br/>rep:rank 3"]
    DSD["<b>rep:DataStructureDefinition<br/>+ qb:DataStructureDefinition</b><br/>ex:dsd_10"]
    CSZ["<b>spec</b><br/>ex:cs_10_z<br/>qb:order 0"]
    CSY["<b>spec</b><br/>ex:cs_10_y<br/>qb:order 1"]
    CSX["<b>spec</b><br/>ex:cs_10_x<br/>qb:order 2"]
    CSM["<b>spec</b><br/>ex:cs_10_intensity"]
    AZ["<b>rep:Axis</b><br/>rep:z"]
    AY["<b>rep:Axis</b><br/>rep:y"]
    AX["<b>rep:Axis</b><br/>rep:x"]
    SIG["<b>rep:Signal</b><br/>rep:intensity"]
    KL["qk:Length"]
    UM["unit:MicroM"]
    KI["tax:Intensity"]
    UC["unit:COUNT"]
    OBS["<b>rep:Observation + qb:Observation</b><br/>ex:obs_10_z0_y0_x0"]
    ZV["z = 0.0"]
    YV["y = 0.0"]
    XV["x = 0.0"]
    IV["intensity = 120"]

    MP -->|rep:has_volume_representation| DS
    DS -->|qb:structure| DSD
    DSD -->|qb:component| CSZ
    DSD -->|qb:component| CSY
    DSD -->|qb:component| CSX
    DSD -->|qb:component| CSM
    CSZ -->|qb:dimension| AZ
    CSY -->|qb:dimension| AY
    CSX -->|qb:dimension| AX
    CSM -->|qb:measure| SIG
    AZ --> KL
    AY --> KL
    AX --> KL
    AZ --> UM
    AY --> UM
    AX --> UM
    SIG --> KI
    SIG --> UC
    OBS -->|qb:dataSet| DS
    OBS -->|rep:z| ZV
    OBS -->|rep:y| YV
    OBS -->|rep:x| XV
    OBS -->|rep:intensity| IV

    classDef tax  fill:#efe0ff,stroke:#7a3fa8,stroke-width:2px,color:#2d1b45
    classDef data fill:#ddeaff,stroke:#2f6fd0,stroke-width:2px,color:#10294f
    classDef dsd  fill:#d6f2ee,stroke:#1d8f7e,stroke-width:2px,color:#0d3d36
    classDef spec fill:#ffeccc,stroke:#d08a1d,stroke-width:2px,color:#4f3410
    classDef axis fill:#dcf5dc,stroke:#3d9440,stroke-width:2px,color:#173d18
    classDef sig  fill:#ffdfe9,stroke:#c9427a,stroke-width:2px,color:#4d162c
    classDef obs  fill:#fff7bf,stroke:#b89600,stroke-width:2px,color:#4b3e00
    classDef qudt fill:#eceff2,stroke:#7b8794,stroke-width:2px,color:#2b3138
    class MP tax
    class DS data
    class DSD dsd
    class CSZ,CSY,CSX,CSM spec
    class AZ,AY,AX axis
    class SIG sig
    class KL,UM,KI,UC qudt
    class OBS,ZV,YV,XV,IV obs
```

The unlabelled edges into the grey nodes are `rep:hasQuantityKind` and
`rep:hasUnit`; labels are dropped here only to keep the diagram
readable at three axes.

---

## Unit rule

| layer | rule | code |
|---|---|---|
| 1 | `qk:Length` permits the unit | `REP-UNIT-001` |
| 2 | VolumeData axes use `unit:MicroM` or `unit:NanoM` | `REP-UNIT-015` |

File: `examples/volume-valid-micrometre-abox.ttl`.
