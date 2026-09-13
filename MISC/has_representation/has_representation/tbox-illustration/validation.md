# Unit validation flow

```mermaid
flowchart TB
    START["Component or specification"] --> HAS{"hasUnit present?"}
    HAS -->|no| KIND["Component has exactly one typed quantity kind"]
    HAS -->|yes| CARD["Unit is one IRI"]
    CARD --> CONTEXT["Resolve exactly one quantity kind"]
    CONTEXT --> LIST{"Pair in whitelist?"}
    LIST -->|yes| PROFILE["Optional profile warning check"]
    LIST -->|no| FAIL["REP-UNIT-001 violation"]
    KIND -->|yes| PASS["Unit validation passes"]
    KIND -->|no| KMISS["REP-UNIT-004 violation"]
    PROFILE --> PASS
```

For unit-bearing specifications, a missing or ambiguous kind also produces
`REP-UNIT-005`. A supplied unit outside the table means unsupported by the
current profile.

## Validation ownership

```mermaid
flowchart LR
    DATA["Producer data"] --> ENGINE["SHACL engine"]
    TBOX["representation.ttl"] --> ENGINE
    RULES["Shapes + trusted whitelist"] --> ENGINE
    ENGINE --> REPORT["Validation report with stable codes"]
```

The whitelist is validation configuration. Producer data must not be allowed
to widen it.
