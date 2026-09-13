# SPARQL usage

What you can ask this module, and what comes back.

Every query below was run against `representation.ttl` +
`representation.shacl.ttl` + the six `*-valid-*-abox.ttl` files in
`examples/`, plus `examples/profile-depth-warn-micrometre-abox.ttl`, and every
result table is the actual output — not an illustration of one. To reproduce:

```python
from pathlib import Path
from rdflib import Graph

g = Graph()
g.parse("representation.ttl", format="turtle")
g.parse("representation.shacl.ttl", format="turtle")   # brings in the unit map
for f in sorted(Path("examples").glob("*-valid-*.ttl")):
    g.parse(f, format="turtle")
g.parse("examples/profile-depth-warn-micrometre-abox.ttl", format="turtle")

for row in g.query(QUERY):
    print(row)
```

No reasoner is involved. Everything here runs on the asserted triples,
which is the point of the design: the canonical component IRIs are
shared across every dataset, so one query pattern serves the whole
knowledge graph.

Prefixes, assumed by every query below:

```sparql
PREFIX ex:   <http://example.org/data#>
PREFIX rep:  <http://fairmat-nfdi.eu/taxonomy/representation#>
PREFIX tax:  <http://fairmat-nfdi.eu/taxonomy/>
PREFIX shp:  <http://fairmat-nfdi.eu/taxonomy/shapes/units#>
PREFIX qb:   <http://purl.org/linked-data/cube#>
PREFIX qk:   <http://qudt.org/vocab/quantitykind/>
PREFIX unit: <http://qudt.org/vocab/unit/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
```

---

## Q1 — What is the canonical vocabulary?

The starting point for anyone new to the module: every axis and signal
the module defines, with what it measures and its default unit.

```sparql
SELECT ?component ?role ?kind ?unit WHERE {
  ?component rep:hasQuantityKind ?kind ;
             rep:hasUnit         ?unit ;
             a                   ?role .
  FILTER(?role IN (rep:Axis, rep:Signal))
}
ORDER BY ?role ?component
```

| component | role | kind | unit |
|---|---|---|---|
| `rep:depth` | `rep:Axis` | `qk:Length` | `unit:NanoM` |
| `rep:energy` | `rep:Axis` | `qk:Energy` | `unit:EV` |
| `rep:time` | `rep:Axis` | `qk:Time` | `unit:SEC` |
| `rep:x` | `rep:Axis` | `qk:Length` | `unit:MicroM` |
| `rep:y` | `rep:Axis` | `qk:Length` | `unit:MicroM` |
| `rep:z` | `rep:Axis` | `qk:Length` | `unit:MicroM` |
| `rep:intensity` | `rep:Signal` | `tax:Intensity` | `unit:COUNT` |
| `rep:temperature` | `rep:Signal` | `qk:Temperature` | `unit:K` |

Eight components, six axes and two signals. That is the whole
vocabulary — an ABox never mints its own.

---

## Q2 — What units may I write for this quantity kind?

Answered without a validator. The permitted-unit table is ordinary RDF
in `representation.shacl.ttl`, so it is queryable like anything else.
This is the query to run before writing a converter.

```sparql
SELECT ?unit WHERE { qk:Length shp:permitsUnit ?unit }
ORDER BY ?unit
```

| unit |
|---|
| `unit:MicroM` |
| `unit:NanoM` |

Drop the `qk:Length` binding to get the whole table:

```sparql
SELECT ?kind ?unit WHERE { ?kind shp:permitsUnit ?unit } ORDER BY ?kind ?unit
```

| kind | unit |
|---|---|
| `qk:Energy` | `unit:EV` |
| `qk:Length` | `unit:MicroM` |
| `qk:Length` | `unit:NanoM` |
| `qk:Temperature` | `unit:K` |
| `qk:Time` | `unit:SEC` |
| `tax:Intensity` | `unit:COUNT` |

Six rows. Length is the only kind with two units, because a depth axis
works in nanometres and an image axis in micrometres.

> **This table will grow, without notice.** It lists only what the
> module's six representation types use today; it is not a survey of
> QUDT. If the unit you need is missing, adding it is one triple in
> `representation.shacl.ttl` — no shape edit, no TBox change. Which is
> exactly why this is a query and not a hard-coded list: run it, don't
> memorise it.

---

## Q3 — What datasets exist, and what shape are they?

```sparql
SELECT ?dataset ?type ?rank WHERE {
  ?dataset rep:rank ?rank ; a ?type .
  FILTER(STRSTARTS(STR(?type), STR(rep:)))
}
ORDER BY ?rank ?dataset
```

| dataset | type | rank |
|---|---|---|
| `ex:tc_reading` | `rep:Scalar` | 0 |
| `ex:decay_curve` | `rep:TimeSeries` | 1 |
| `ex:sims_depth` | `rep:DepthProfile` | 1 |
| `ex:sims_microns` | `rep:DepthProfile` | 1 |
| `ex:xps_survey` | `rep:Spectrum` | 1 |
| `ex:sem_map` | `rep:Image` | 2 |
| `ex:tomo` | `rep:VolumeData` | 3 |

`rep:rank` is asserted by the producer. The `owl:equivalentClass`
definitions in the TBox mean a reasoner derives the type from the rank
independently — if the two disagree, HermiT flags it. Without a
reasoner, as here, both are simply read off the data.

---

## Q4 — What are the axes of each dataset, in array order?

The query you need to index into the underlying array correctly.
`qb:order` is slowest-first, matching NumPy C-order.

```sparql
SELECT ?dataset ?order ?axis ?unit WHERE {
  ?dataset qb:structure ?dsd .
  ?dsd     qb:component ?cs .
  ?cs      qb:dimension ?axis ;
           qb:order     ?order ;
           rep:hasUnit  ?unit .
}
ORDER BY ?dataset ?order
```

| dataset | order | axis | unit |
|---|---|---|---|
| `ex:decay_curve` | 0 | `rep:time` | `unit:SEC` |
| `ex:sem_map` | 0 | `rep:y` | `unit:MicroM` |
| `ex:sem_map` | 1 | `rep:x` | `unit:MicroM` |
| `ex:sims_depth` | 0 | `rep:depth` | `unit:NanoM` |
| `ex:sims_microns` | 0 | `rep:depth` | `unit:MicroM` |
| `ex:tomo` | 0 | `rep:z` | `unit:MicroM` |
| `ex:tomo` | 1 | `rep:y` | `unit:MicroM` |
| `ex:tomo` | 2 | `rep:x` | `unit:MicroM` |
| `ex:xps_survey` | 0 | `rep:energy` | `unit:EV` |

`ex:tc_reading` is absent: a Scalar is rank 0 and has no axes at all.

---

## Q5 — Which material property does this data represent?

The bridge into the FAIRmat taxonomy. The `rdfs:subPropertyOf*` path is
what makes this work without a reasoner: the data states the specific
property (`rep:has_image_representation`), and the path walks up to the
general one.

```sparql
SELECT ?property ?dataset ?type ?rank WHERE {
  ?link     rdfs:subPropertyOf* rep:has_representation .
  ?property ?link               ?dataset .
  ?dataset  a                   ?type ;
            rep:rank            ?rank .
  FILTER(STRSTARTS(STR(?type), STR(rep:)))
}
ORDER BY ?rank ?property
```

| property | dataset | type | rank |
|---|---|---|---|
| `ex:melting_point` | `ex:tc_reading` | `rep:Scalar` | 0 |
| `ex:carrier_lifetime` | `ex:decay_curve` | `rep:TimeSeries` | 1 |
| `ex:core_level_spectrum` | `ex:xps_survey` | `rep:Spectrum` | 1 |
| `ex:depth_composition` | `ex:sims_depth` | `rep:DepthProfile` | 1 |
| `ex:surface_morphology` | `ex:sem_map` | `rep:Image` | 2 |
| `ex:pore_structure` | `ex:tomo` | `rep:VolumeData` | 3 |

Going the other way — *find every dataset representing a morphology* —
is the same pattern with `?property a tax:Morphology` bound.

---

## Q6 — What values were lifted for this spectrum?

The observation layer uses the canonical component IRIs as predicates.
No join table or per-dataset column vocabulary is needed.

```sparql
SELECT ?observation ?energy ?intensity WHERE {
  ?observation a rep:Observation , qb:Observation ;
               qb:dataSet    ex:xps_survey ;
               rep:energy    ?energy ;
               rep:intensity ?intensity .
}
ORDER BY ?energy
```

| observation | energy | intensity |
|---|---:|---:|
| `ex:obs_01_000` | 0.0 | 120 |
| `ex:obs_01_001` | 0.5 | 134 |
| `ex:obs_01_002` | 1.0 | 129 |

The same pattern works for every representation: omit the dimension
predicate for a Scalar, use `rep:y` and `rep:x` for an Image, and add
`rep:z` for a VolumeData observation.

---

## Q7 — Which datasets deviate from the canonical default unit?

A data-quality sweep. Not an error: a dataset is entitled to work in
its own unit, provided it says so on its own `qb:ComponentSpecification`
and the unit is permitted for the kind. This query surfaces those
deviations so a curator can eyeball them.

```sparql
SELECT ?dataset ?component ?datasetUnit ?canonicalUnit WHERE {
  ?dataset qb:structure ?dsd .
  ?dsd     qb:component ?cs .
  { ?cs qb:dimension ?component } UNION { ?cs qb:measure ?component }
  ?cs        rep:hasUnit ?datasetUnit .
  ?component rep:hasUnit ?canonicalUnit .
  FILTER(?datasetUnit != ?canonicalUnit)
}
```

| dataset | component | dataset unit | canonical unit |
|---|---|---|---|
| `ex:sims_microns` | `rep:depth` | `unit:MicroM` | `unit:NanoM` |

One hit: a depth profile stepped in micrometres while `rep:depth`
defaults to nanometres. Permitted for `qk:Length`, so Layer 1 has
nothing to say — but three orders of magnitude off the usual scale, and
worth a curator's eye. This is the same dataset that Layer 2 flags as
`REP-UNIT-013`.

---

## Q8 — Give me every slot with its kind and unit

The general-purpose introspection query. One row per component
specification across the whole graph.

```sparql
SELECT ?dataset ?slot ?component ?kind ?unit WHERE {
  ?dataset qb:structure ?dsd .
  ?dsd     qb:component ?cs .
  { ?cs qb:dimension ?component  BIND("dimension" AS ?slot) }
  UNION
  { ?cs qb:measure   ?component  BIND("measure"   AS ?slot) }
  ?cs        rep:hasUnit         ?unit .
  ?component rep:hasQuantityKind ?kind .
}
ORDER BY ?dataset ?slot
```

| dataset | slot | component | kind | unit |
|---|---|---|---|---|
| `ex:decay_curve` | dimension | `rep:time` | `qk:Time` | `unit:SEC` |
| `ex:decay_curve` | measure | `rep:intensity` | `tax:Intensity` | `unit:COUNT` |
| `ex:sem_map` | dimension | `rep:y` | `qk:Length` | `unit:MicroM` |
| `ex:sem_map` | dimension | `rep:x` | `qk:Length` | `unit:MicroM` |
| `ex:sem_map` | measure | `rep:intensity` | `tax:Intensity` | `unit:COUNT` |
| `ex:sims_depth` | dimension | `rep:depth` | `qk:Length` | `unit:NanoM` |
| `ex:sims_depth` | measure | `rep:intensity` | `tax:Intensity` | `unit:COUNT` |
| `ex:sims_microns` | dimension | `rep:depth` | `qk:Length` | `unit:MicroM` |
| `ex:sims_microns` | measure | `rep:intensity` | `tax:Intensity` | `unit:COUNT` |
| `ex:tc_reading` | measure | `rep:temperature` | `qk:Temperature` | `unit:K` |
| `ex:tomo` | dimension | `rep:z` | `qk:Length` | `unit:MicroM` |
| `ex:tomo` | dimension | `rep:y` | `qk:Length` | `unit:MicroM` |
| `ex:tomo` | dimension | `rep:x` | `qk:Length` | `unit:MicroM` |
| `ex:tomo` | measure | `rep:intensity` | `tax:Intensity` | `unit:COUNT` |
| `ex:xps_survey` | dimension | `rep:energy` | `qk:Energy` | `unit:EV` |
| `ex:xps_survey` | measure | `rep:intensity` | `tax:Intensity` | `unit:COUNT` |

---

## Q9 — Find unit errors with SPARQL alone

You can express the dimensional check as a plain query. It is worth
seeing, because it shows exactly what SHACL adds and what it does not.

```sparql
SELECT ?cs ?kind ?unit WHERE {
  { ?cs qb:dimension ?component } UNION { ?cs qb:measure ?component }
  ?cs        rep:hasUnit         ?unit .
  ?component rep:hasQuantityKind ?kind .
  FILTER NOT EXISTS { ?kind shp:permitsUnit ?unit }
}
```

Run against the valid examples this returns nothing. Run against
`examples/profile-spectrum-invalid-seconds-abox.ttl`:

| cs | kind | unit |
|---|---|---|
| `ex:cs_02_energy` | `qk:Energy` | `unit:SEC` |

So SPARQL *can* find the problem. What it cannot do is tell you this is
an error rather than a result, attach a severity, attach a stable code,
or run as part of a gate — that is what the shapes graph is for. The
`FILTER NOT EXISTS` line above is literally the body of `REP-UNIT-001`;
the shape wraps it in a target, a message, a severity and a code. See
[README.md](README.md#shacl-validation) and `test/reports.md`.

---

## Queries that need a reasoner

Everything above is asserted-triple SPARQL. Two things genuinely need
HermiT, and no query will substitute:

- **Type from rank.** `rep:Spectrum` and friends are defined by
  `owl:equivalentClass` on the `rep:rank` value. Asking "what type is
  this dataset, given only its rank" is a classification, not a lookup.
- **Contradiction between asserted type and rank.** A dataset typed
  `rep:Image` with `rep:rank 1` is inconsistent. No SPARQL query
  reports that; a reasoner does.

Both are exercised in the workbench notebook rather than here.
