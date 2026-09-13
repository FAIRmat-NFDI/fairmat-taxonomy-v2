# Image — rank 2

> Colour legend: purple = taxonomy, blue = dataset, teal = schema,
> amber = component specification, green = axis, pink = signal,
> yellow = observation/value, grey = QUDT kind and unit. See
> [overview.md](overview.md).

Two axes, `rep:y` then `rep:x`, and one signal. Ordering is
slowest-first, matching NumPy C-order and the NeXus `<axis>_indices`
convention. A rank-2 dataset uses that pair and no other.

**Example data.** An SEM intensity map, 3x4 pixels.

| y \ x | 0.0 | 0.5 | 1.0 | 1.5 |
|---|---|---|---|---|
| **0.0** | 120 | 118 | 131 | 127 |
| **0.5** | 119 | 145 | 162 | 130 |
| **1.0** | 121 | 133 | 128 | 125 |

Axis values in µm, cell values in counts. `rep:extent` on the dataset
is 12; on `rep:y` it is 3 and on `rep:x` it is 4. The signal never
carries an extent — it is always the product of the axis extents.

---

## TBox plus one ABox observation

```mermaid
flowchart LR
    MP["<b>tax:Morphology</b><br/>ex:surface_morphology"]
    DS["<b>rep:Image + qb:DataSet</b><br/>ex:sem_map<br/>rep:rank 2"]
    DSD["<b>rep:DataStructureDefinition<br/>+ qb:DataStructureDefinition</b><br/>ex:dsd_06"]
    CSY["<b>spec</b><br/>ex:cs_06_y<br/>qb:order 0<br/>rep:hasUnit unit:MicroM"]
    CSX["<b>spec</b><br/>ex:cs_06_x<br/>qb:order 1<br/>rep:hasUnit unit:MicroM"]
    CSM["<b>spec</b><br/>ex:cs_06_intensity<br/>rep:hasUnit unit:COUNT"]
    AY["<b>rep:Axis</b><br/>rep:y"]
    AX["<b>rep:Axis</b><br/>rep:x"]
    SIG["<b>rep:Signal</b><br/>rep:intensity"]
    KL["qk:Length"]
    UM["unit:MicroM"]
    KI["tax:Intensity"]
    UC["unit:COUNT"]
    OBS["<b>rep:Observation + qb:Observation</b><br/>ex:obs_06_y0_x0"]
    YV["y = 0.0"]
    XV["x = 0.0"]
    IV["intensity = 120"]

    MP -->|rep:has_image_representation| DS
    DS -->|qb:structure| DSD
    DSD -->|qb:component| CSY
    DSD -->|qb:component| CSX
    DSD -->|qb:component| CSM
    CSY -->|qb:dimension| AY
    CSX -->|qb:dimension| AX
    CSM -->|qb:measure| SIG
    AY -->|rep:hasQuantityKind| KL
    AX -->|rep:hasQuantityKind| KL
    AY -->|rep:hasUnit| UM
    AX -->|rep:hasUnit| UM
    SIG -->|rep:hasQuantityKind| KI
    SIG -->|rep:hasUnit| UC
    OBS -->|qb:dataSet| DS
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
    class CSY,CSX,CSM spec
    class AY,AX axis
    class SIG sig
    class KL,UM,KI,UC qudt
    class OBS,YV,XV,IV obs
```

Both axes converge on one `qk:Length` node and one `unit:MicroM` node.
That is not a drawing shortcut — they really are the same two IRIs.
`qb:order` on the amber specs is the only thing distinguishing y from x
positionally.

---

## Unit rule

| layer | rule | code |
|---|---|---|
| 1 | `qk:Length` permits the unit | `REP-UNIT-001` |
| 2 | Image axes use `unit:MicroM` or `unit:NanoM` | `REP-UNIT-014` |

Files: `examples/image-valid-micrometre-abox.ttl`,
`examples/image-invalid-seconds-abox.ttl` — the latter puts a time unit
on `rep:x` while `rep:y` stays correct, and the report names only the
offending specification.
