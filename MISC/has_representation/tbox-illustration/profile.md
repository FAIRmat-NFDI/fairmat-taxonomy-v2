# Profile — rank 1

> Colour legend: purple = taxonomy, blue = dataset, teal = schema,
> amber = component specification, green = axis, pink = signal,
> yellow = observation/value, grey = QUDT kind and unit. See
> [overview.md](overview.md).

One axis, one signal. Three named subtypes share the rank and differ
only in which canonical axis they use:

| subtype | axis | canonical unit | quantity kind |
|---|---|---|---|
| `rep:Spectrum` | `rep:energy` | `unit:EV` | `qk:Energy` |
| `rep:TimeSeries` | `rep:time` | `unit:SEC` | `qk:Time` |
| `rep:DepthProfile` | `rep:depth` | `unit:NanoM` | `qk:Length` |

`rep:Profile` itself is a **defined** class — rank 1. The three
subtypes are **primitive**: rank alone cannot distinguish them, so the
producer asserts which one it is.

---

## Spectrum

**Example data.** An XPS survey scan.

| energy (eV) | intensity (count) |
|---|---|
| 0.0 | 120 |
| 0.5 | 134 |
| 1.0 | 129 |
| … | … |

```mermaid
flowchart LR
    MP["<b>tax:Spectra</b><br/>ex:core_level_spectrum"]
    DS["<b>rep:Spectrum + qb:DataSet</b><br/>ex:xps_survey<br/>rep:rank 1"]
    DSD["<b>rep:DataStructureDefinition<br/>+ qb:DataStructureDefinition</b><br/>ex:dsd_01"]
    CSA["<b>qb:ComponentSpecification</b><br/>ex:cs_01_energy<br/>qb:order 0<br/>rep:hasUnit unit:EV"]
    CSM["<b>qb:ComponentSpecification</b><br/>ex:cs_01_intensity<br/>rep:hasUnit unit:COUNT"]
    AX["<b>rep:Axis</b><br/>rep:energy"]
    SIG["<b>rep:Signal</b><br/>rep:intensity"]
    K1["qk:Energy"]
    U1["unit:EV"]
    K2["tax:Intensity"]
    U2["unit:COUNT"]
    OBS["<b>rep:Observation + qb:Observation</b><br/>ex:obs_01_000"]
    EVAL["0.0^^xsd:double"]
    IVAL["120^^xsd:nonNegativeInteger"]

    MP -->|rep:has_spectrum_representation| DS
    DS -->|qb:structure| DSD
    DSD -->|qb:component| CSA
    DSD -->|qb:component| CSM
    CSA -->|qb:dimension| AX
    CSM -->|qb:measure| SIG
    AX -->|rep:hasQuantityKind| K1
    AX -->|rep:hasUnit| U1
    SIG -->|rep:hasQuantityKind| K2
    SIG -->|rep:hasUnit| U2
    OBS -->|qb:dataSet| DS
    OBS -->|rep:energy| EVAL
    OBS -->|rep:intensity| IVAL

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
    class CSA,CSM spec
    class AX axis
    class SIG sig
    class K1,U1,K2,U2 qudt
    class OBS,EVAL,IVAL obs
```

---

## TimeSeries

```mermaid
flowchart LR
    MP["tax:CarrierLifetime<br/>ex:carrier_lifetime"]
    DS["rep:TimeSeries + qb:DataSet<br/>ex:decay_curve"]
    DSD["rep:DataStructureDefinition<br/>+ qb:DataStructureDefinition<br/>ex:dsd_14"]
    CSA["qb:ComponentSpecification<br/>ex:cs_14_time<br/>order 0 · unit:SEC"]
    CSM["qb:ComponentSpecification<br/>ex:cs_14_intensity<br/>unit:COUNT"]
    AX["rep:Axis<br/>rep:time"]
    SIG["rep:Signal<br/>rep:intensity"]
    K1["qk:Time"]
    U1["unit:SEC"]
    K2["tax:Intensity"]
    U2["unit:COUNT"]
    OBS["rep:Observation + qb:Observation<br/>ex:obs_14_000"]
    TV["time = 0.0"]
    IV["intensity = 4820"]

    MP -->|rep:has_timeseries_representation| DS
    DS -->|qb:structure| DSD
    DSD -->|qb:component| CSA
    DSD -->|qb:component| CSM
    CSA -->|qb:dimension| AX
    CSM -->|qb:measure| SIG
    AX -->|rep:hasQuantityKind| K1
    AX -->|rep:hasUnit| U1
    SIG -->|rep:hasQuantityKind| K2
    SIG -->|rep:hasUnit| U2
    OBS -->|qb:dataSet| DS
    OBS -->|rep:time| TV
    OBS -->|rep:intensity| IV

    classDef tax fill:#efe0ff,stroke:#7a3fa8,stroke-width:2px,color:#2d1b45
    classDef data fill:#ddeaff,stroke:#2f6fd0,stroke-width:2px,color:#10294f
    classDef dsd fill:#d6f2ee,stroke:#1d8f7e,stroke-width:2px,color:#0d3d36
    classDef spec fill:#ffeccc,stroke:#d08a1d,stroke-width:2px,color:#4f3410
    classDef axis fill:#dcf5dc,stroke:#3d9440,stroke-width:2px,color:#173d18
    classDef sig fill:#ffdfe9,stroke:#c9427a,stroke-width:2px,color:#4d162c
    classDef qudt fill:#eceff2,stroke:#7b8794,stroke-width:2px,color:#2b3138
    classDef obs fill:#fff7bf,stroke:#b89600,stroke-width:2px,color:#4b3e00
    class MP tax
    class DS data
    class DSD dsd
    class CSA,CSM spec
    class AX axis
    class SIG sig
    class K1,U1,K2,U2 qudt
    class OBS,TV,IV obs
```

## DepthProfile

```mermaid
flowchart LR
    MP["tax:ElementalComposition<br/>ex:depth_composition"]
    DS["rep:DepthProfile + qb:DataSet<br/>ex:sims_depth"]
    DSD["rep:DataStructureDefinition<br/>+ qb:DataStructureDefinition<br/>ex:dsd_08"]
    CSA["qb:ComponentSpecification<br/>ex:cs_08_depth<br/>order 0 · unit:NanoM"]
    CSM["qb:ComponentSpecification<br/>ex:cs_08_intensity<br/>unit:COUNT"]
    AX["rep:Axis<br/>rep:depth"]
    SIG["rep:Signal<br/>rep:intensity"]
    K1["qk:Length"]
    U1["unit:NanoM"]
    K2["tax:Intensity"]
    U2["unit:COUNT"]
    OBS["rep:Observation + qb:Observation<br/>ex:obs_08_000"]
    DV["depth = 0.0"]
    IV["intensity = 9120"]

    MP -->|rep:has_depthprofile_representation| DS
    DS -->|qb:structure| DSD
    DSD -->|qb:component| CSA
    DSD -->|qb:component| CSM
    CSA -->|qb:dimension| AX
    CSM -->|qb:measure| SIG
    AX -->|rep:hasQuantityKind| K1
    AX -->|rep:hasUnit| U1
    SIG -->|rep:hasQuantityKind| K2
    SIG -->|rep:hasUnit| U2
    OBS -->|qb:dataSet| DS
    OBS -->|rep:depth| DV
    OBS -->|rep:intensity| IV

    classDef tax fill:#efe0ff,stroke:#7a3fa8,stroke-width:2px,color:#2d1b45
    classDef data fill:#ddeaff,stroke:#2f6fd0,stroke-width:2px,color:#10294f
    classDef dsd fill:#d6f2ee,stroke:#1d8f7e,stroke-width:2px,color:#0d3d36
    classDef spec fill:#ffeccc,stroke:#d08a1d,stroke-width:2px,color:#4f3410
    classDef axis fill:#dcf5dc,stroke:#3d9440,stroke-width:2px,color:#173d18
    classDef sig fill:#ffdfe9,stroke:#c9427a,stroke-width:2px,color:#4d162c
    classDef qudt fill:#eceff2,stroke:#7b8794,stroke-width:2px,color:#2b3138
    classDef obs fill:#fff7bf,stroke:#b89600,stroke-width:2px,color:#4b3e00
    class MP tax
    class DS data
    class DSD dsd
    class CSA,CSM spec
    class AX axis
    class SIG sig
    class K1,U1,K2,U2 qudt
    class OBS,DV,IV obs
```

The two implementations have the same RDF Data Cube topology; only
the green canonical axis and its QUDT kind/unit change. Both datasets
state their unit on their own component specification;
`SPARQL_USAGE.md` Q7 surfaces deviations from the module default.

---

## Unit rules

| subtype | permitted at Layer 2 | code |
|---|---|---|
| Spectrum axis | `unit:EV` | `REP-UNIT-011` |
| TimeSeries axis | `unit:SEC` | `REP-UNIT-012` |
| DepthProfile axis | `unit:NanoM` | `REP-UNIT-013` |
| any intensity signal | `unit:COUNT` | `REP-UNIT-016` |

**Why Layer 2 exists, in one line:** `qk:Length` covers both the
nanometre-scale depth axis and the micrometre-scale image axes, so the
quantity kind alone cannot separate them — only the representation type
can. `examples/profile-depth-warn-micrometre-abox.ttl` is a depth axis in
micrometres: a permitted length unit, exactly right on an image axis,
three orders of magnitude off here. Warning, not violation.
