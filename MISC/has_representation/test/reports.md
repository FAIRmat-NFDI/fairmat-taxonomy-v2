# Validation report

`representation.ttl` + `representation.shacl.ttl` vs `examples/` -- 14/14 files matched their declared SHACL expectation and contained complete lifted observations.

Layer 1 findings are `sh:Violation` and make the graph non-conforming.
Layer 2 findings are `sh:Warning`: reported, but the graph still conforms.

## Summary

| file | conforms | observations | expected | actual | |
|---|---|---|---|---|---|
| `image-invalid-seconds-abox.ttl` | no | ok | REP-UNIT-001, REP-UNIT-014 | REP-UNIT-001, REP-UNIT-014 | ok |
| `image-invalid-two-units-abox.ttl` | no | ok | REP-UNIT-003 | REP-UNIT-003 | ok |
| `image-valid-micrometre-abox.ttl` | yes | ok | - | - | ok |
| `profile-depth-valid-nanometre-abox.ttl` | yes | ok | - | - | ok |
| `profile-depth-warn-micrometre-abox.ttl` | yes | ok | REP-UNIT-013 | REP-UNIT-013 | ok |
| `profile-spectrum-invalid-intensity-ev-abox.ttl` | no | ok | REP-UNIT-001, REP-UNIT-016 | REP-UNIT-001, REP-UNIT-016 | ok |
| `profile-spectrum-invalid-kind-as-unit-abox.ttl` | no | ok | REP-UNIT-001, REP-UNIT-002, REP-UNIT-011 | REP-UNIT-001, REP-UNIT-002, REP-UNIT-011 | ok |
| `profile-spectrum-invalid-missing-unit-abox.ttl` | no | ok | REP-UNIT-003 | REP-UNIT-003 | ok |
| `profile-spectrum-invalid-seconds-abox.ttl` | no | ok | REP-UNIT-001, REP-UNIT-011 | REP-UNIT-001, REP-UNIT-011 | ok |
| `profile-spectrum-valid-abox.ttl` | yes | ok | - | - | ok |
| `profile-timeseries-valid-second-abox.ttl` | yes | ok | - | - | ok |
| `scalar-invalid-metre-abox.ttl` | no | ok | REP-UNIT-001, REP-UNIT-010 | REP-UNIT-001, REP-UNIT-010 | ok |
| `scalar-valid-kelvin-abox.ttl` | yes | ok | - | - | ok |
| `volume-valid-micrometre-abox.ttl` | yes | ok | - | - | ok |

## Findings

### `image-invalid-seconds-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-001 | Violation | 1 | `ex:cs_07_x` | `unit:SEC` |
| REP-UNIT-014 | Warning | 2 | `ex:cs_07_x` | `unit:SEC` |

- **REP-UNIT-001** Use a unit listed by shp:permitsUnit for this quantity kind, or correct rep:hasQuantityKind.
- **REP-UNIT-014** Image axes are reported in unit:MicroM or unit:NanoM.

### `image-invalid-two-units-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-003 | Violation | 1 | `ex:cs_12_x` | `-` |

- **REP-UNIT-003** State exactly one rep:hasUnit on every qb:ComponentSpecification.

### `image-valid-micrometre-abox.ttl`

No findings.

### `profile-depth-valid-nanometre-abox.ttl`

No findings.

### `profile-depth-warn-micrometre-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-013 | Warning | 2 | `ex:cs_09_depth` | `unit:MicroM` |

- **REP-UNIT-013** Depth axes are reported in unit:NanoM. Micrometres are a valid length unit but far off the scale of a depth profile -- check for a units-of-convenience error.

### `profile-spectrum-invalid-intensity-ev-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-001 | Violation | 1 | `ex:cs_15_intensity` | `unit:EV` |
| REP-UNIT-016 | Warning | 2 | `ex:cs_15_intensity` | `unit:EV` |

- **REP-UNIT-001** Use a unit listed by shp:permitsUnit for this quantity kind, or correct rep:hasQuantityKind.
- **REP-UNIT-016** Uncalibrated intensity is reported in unit:COUNT.

### `profile-spectrum-invalid-kind-as-unit-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-001 | Violation | 1 | `ex:cs_13_energy` | `qk:Energy` |
| REP-UNIT-002 | Violation | 1 | `qk:Energy` | `qk:Energy` |
| REP-UNIT-011 | Warning | 2 | `ex:cs_13_energy` | `qk:Energy` |

- **REP-UNIT-001** Use a unit listed by shp:permitsUnit for this quantity kind, or correct rep:hasQuantityKind.
- **REP-UNIT-002** Replace the qudt:QuantityKind with the corresponding qudt:Unit individual.
- **REP-UNIT-011** Spectrum energy axes are reported in unit:EV.

### `profile-spectrum-invalid-missing-unit-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-003 | Violation | 1 | `ex:cs_11_energy` | `-` |

- **REP-UNIT-003** State exactly one rep:hasUnit on every qb:ComponentSpecification.

### `profile-spectrum-invalid-seconds-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-001 | Violation | 1 | `ex:cs_02_energy` | `unit:SEC` |
| REP-UNIT-011 | Warning | 2 | `ex:cs_02_energy` | `unit:SEC` |

- **REP-UNIT-001** Use a unit listed by shp:permitsUnit for this quantity kind, or correct rep:hasQuantityKind.
- **REP-UNIT-011** Spectrum energy axes are reported in unit:EV.

### `profile-spectrum-valid-abox.ttl`

No findings.

### `profile-timeseries-valid-second-abox.ttl`

No findings.

### `scalar-invalid-metre-abox.ttl`

| code | severity | layer | focus node | value |
|---|---|---|---|---|
| REP-UNIT-001 | Violation | 1 | `ex:cs_05_temperature` | `unit:M` |
| REP-UNIT-010 | Warning | 2 | `ex:cs_05_temperature` | `unit:M` |

- **REP-UNIT-001** Use a unit listed by shp:permitsUnit for this quantity kind, or correct rep:hasQuantityKind.
- **REP-UNIT-010** Scalar temperature is reported in unit:K.

### `scalar-valid-kelvin-abox.ttl`

No findings.

### `volume-valid-micrometre-abox.ttl`

No findings.

