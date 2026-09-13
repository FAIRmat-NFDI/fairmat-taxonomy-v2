# Validation report

18/18 examples matched their declared SHACL results and contained complete observations.

Ontology contract checks: passed.

| Example | Conforms | Expected codes | Actual codes | Observation |
|---|---:|---|---|---|
| `depthprofile-invalid-missing-kind-abox.ttl` | no | REP-UNIT-004, REP-UNIT-005 | REP-UNIT-004, REP-UNIT-005 | complete |
| `depthprofile-invalid-unit-abox.ttl` | no | REP-UNIT-001, REP-UNIT-013 | REP-UNIT-001, REP-UNIT-013 | complete |
| `depthprofile-valid-abox.ttl` | yes | — | — | complete |
| `image-invalid-missing-kind-abox.ttl` | no | REP-UNIT-004, REP-UNIT-005 | REP-UNIT-004, REP-UNIT-005 | complete |
| `image-invalid-unit-abox.ttl` | no | REP-UNIT-001, REP-UNIT-014 | REP-UNIT-001, REP-UNIT-014 | complete |
| `image-valid-abox.ttl` | yes | — | — | complete |
| `scalar-invalid-missing-kind-abox.ttl` | no | REP-UNIT-004, REP-UNIT-005 | REP-UNIT-004, REP-UNIT-005 | complete |
| `scalar-invalid-unit-abox.ttl` | no | REP-UNIT-001, REP-UNIT-010 | REP-UNIT-001, REP-UNIT-010 | complete |
| `scalar-valid-abox.ttl` | yes | — | — | complete |
| `spectrum-invalid-missing-kind-abox.ttl` | no | REP-UNIT-004, REP-UNIT-005 | REP-UNIT-004, REP-UNIT-005 | complete |
| `spectrum-invalid-unit-abox.ttl` | no | REP-UNIT-001, REP-UNIT-011 | REP-UNIT-001, REP-UNIT-011 | complete |
| `spectrum-valid-abox.ttl` | yes | — | — | complete |
| `timeseries-invalid-missing-kind-abox.ttl` | no | REP-UNIT-004, REP-UNIT-005 | REP-UNIT-004, REP-UNIT-005 | complete |
| `timeseries-invalid-unit-abox.ttl` | no | REP-UNIT-001, REP-UNIT-012 | REP-UNIT-001, REP-UNIT-012 | complete |
| `timeseries-valid-abox.ttl` | yes | — | — | complete |
| `volume-invalid-missing-kind-abox.ttl` | no | REP-UNIT-004, REP-UNIT-005 | REP-UNIT-004, REP-UNIT-005 | complete |
| `volume-invalid-unit-abox.ttl` | no | REP-UNIT-001, REP-UNIT-015 | REP-UNIT-001, REP-UNIT-015 | complete |
| `volume-valid-abox.ttl` | yes | — | — | complete |

Warnings are included in the code comparison but remain non-blocking.
The whitelist is trusted validator configuration, not producer data.
