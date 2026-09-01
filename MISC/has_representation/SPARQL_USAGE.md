# FAIRmat Representation Ontology
## SPARQL Query Reference

Every query below was run against the six example ABoxes shipped with this guide,
and every result table is the actual output — not an illustration.

Load the graph:

```bash
representation.ttl        # TBox
abox_scalar.ttl           # 1 observation
abox_spectrum.ttl         # 5
abox_timeseries.ttl       # 6
abox_depthprofile.ttl     # 6
abox_image.ttl            # 25
abox_volume.ttl           # 12
                          # 822 triples after rdfs closure
```

---

## What is and is not queryable

Every component declares what it measures through a two-link chain:

```
COMPONENT  --hasQuantityKind-->  QUANTITY KIND 
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
                    LIVE                            
```

`rep:hasQuantityKind` is fully active and is the semantic anchor for every query
below — Q01, Q02, Q06 and Q16 all pivot on it. 

| question | answerable? | how |
|---|---|---|
| Which datasets measure a length? | yes | `?ax rep:hasQuantityKind qk:Length` (Q16) |
| Which axis is the slow one? | yes | `?cs qb:order 0` (Q05) |
| How many points along each axis? | yes | `?cs rep:extent ?n` (Q05, Q18) |




---

## Prefixes

All queries assume:

```sparql
PREFIX rep:  <http://fairmat-nfdi.eu/taxonomy/representation#>
PREFIX tax:  <http://fairmat-nfdi.eu/taxonomy/>
PREFIX ex:   <http://fairmat-nfdi.eu/taxonomy/abox#>
PREFIX qb:   <http://purl.org/linked-data/cube#>
PREFIX qk:   <http://qudt.org/vocab/quantitykind/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
```

Queries that traverse `rep:has_representation` need `rdfs:subPropertyOf` closure,
since the ABoxes assert the typed subproperties (`rep:has_image_representation` and
friends). Any RDFS-capable store does this automatically; with plain rdflib,
materialise first.

---

## Group 1 — Schema

### Q01 — Canonical axes

```sparql
SELECT ?axis ?quantityKind WHERE {
    ?axis a rep:Axis ;
          rep:hasQuantityKind ?quantityKind .
}
ORDER BY ?axis
```

| `?axis` | `?quantityKind` |
|---|---|
| `rep:depth` | `qk:Length` |
| `rep:energy` | `qk:Energy` |
| `rep:time` | `qk:Time` |
| `rep:x` | `qk:Length` |
| `rep:y` | `qk:Length` |
| `rep:z` | `qk:Length` |

Six axes, and four of them share `qk:Length`. Quantity kind alone cannot tell `rep:x`
from `rep:y` from `rep:z` — that is what `qb:order` is for.

---

### Q02 — Canonical signals

```sparql
SELECT ?signal ?quantityKind WHERE {
    ?signal a rep:Signal ;
            rep:hasQuantityKind ?quantityKind .
}
ORDER BY ?signal
```

| `?signal` | `?quantityKind` |
|---|---|
| `rep:intensity` | `tax:Intensity` |
| `rep:temperature` | `qk:Temperature` |

Two signals against six axes. `rep:intensity` covers every counting detector; a
measurement with a different quantity kind needs a new Signal added to the TBox, since
`rep:Axis` and `rep:Signal` are disjoint and an Axis IRI cannot stand in.

---

### Q03 — Representation classes

```sparql
SELECT ?class WHERE {
    ?class rdfs:subClassOf+ rep:Representation .
}
ORDER BY ?class
```

| `?class` |
|---|
| `rep:Axis` |
| `rep:ComponentProperty` |
| `rep:DataStructureDefinition` |
| `rep:DepthProfile` |
| `rep:Image` |
| `rep:Observation` |
| `rep:Profile` |
| `rep:Scalar` |
| `rep:Signal` |
| `rep:Spectrum` |
| `rep:TimeSeries` |
| `rep:UnitAttribute` |
| `rep:VolumeData` |

The `+` matters. `rep:Spectrum`, `rep:TimeSeries` and `rep:DepthProfile` are subclasses
of `rep:Profile`, not direct subclasses of `rep:Representation`; `rep:Axis` and
`rep:Signal` sit under `rep:ComponentProperty`. A single-step `rdfs:subClassOf` returns
seven classes and silently drops the rest.

---

## Group 2 — Inventory

### Q04 — What is in the knowledge graph

```sparql
SELECT ?material ?type ?extent WHERE {
    ?material tax:hasMaterialProperty ?prop .
    ?prop     rep:has_representation  ?repr .
    ?repr     a          ?type ;
              rep:extent ?extent .
    FILTER(STRSTARTS(STR(?type), STR(rep:)))
    FILTER(?type NOT IN (rep:Representation, rep:Profile, owl:NamedIndividual))
}
ORDER BY ?material
```

| `?material` | `?type` | `?extent` |
|---|---|---|
| `ex:Al2O3foam` | `rep:VolumeData` | 12 |
| `ex:BdopedSi` | `rep:DepthProfile` | 6 |
| `ex:DP780` | `rep:Image` | 25 |
| `ex:FeFoil` | `rep:Spectrum` | 5 |
| `ex:SS316L` | `rep:TimeSeries` | 6 |
| `ex:Si` | `rep:Scalar` | 1 |

`rep:Profile` is filtered out because it is inferred for every rank-1 dataset
alongside the more specific `rep:Spectrum` / `rep:TimeSeries` / `rep:DepthProfile`.

---

### Q05 — Axis schema for every dataset

```sparql
SELECT ?material ?axis ?order ?extent WHERE {
    ?material tax:hasMaterialProperty ?prop .
    ?prop     rep:has_representation  ?repr .
    ?repr     qb:structure / qb:component ?cs .
    ?cs       qb:dimension ?axis ;
              qb:order     ?order ;
              rep:extent   ?extent .
}
ORDER BY ?material ?order
```

| `?material` | `?axis` | `?order` | `?extent` |
|---|---|---|---|
| `ex:Al2O3foam` | `rep:z` | 0 | 2 |
| `ex:Al2O3foam` | `rep:y` | 1 | 2 |
| `ex:Al2O3foam` | `rep:x` | 2 | 3 |
| `ex:BdopedSi` | `rep:depth` | 0 | 6 |
| `ex:DP780` | `rep:y` | 0 | 5 |
| `ex:DP780` | `rep:x` | 1 | 5 |
| `ex:FeFoil` | `rep:energy` | 0 | 5 |
| `ex:SS316L` | `rep:time` | 0 | 6 |

Eight rows for six datasets: the scalar contributes none, the volume contributes
three. Row count equals the sum of all ranks.

---

### Q06 — Component usage across the graph

```sparql
SELECT ?component ?role ?quantityKind (COUNT(DISTINCT ?repr) AS ?n_datasets) WHERE {
    ?repr qb:structure / qb:component ?cs .
    { ?cs qb:dimension ?component . BIND("axis"   AS ?role) }
    UNION
    { ?cs qb:measure   ?component . BIND("signal" AS ?role) }
    ?component rep:hasQuantityKind ?quantityKind .
}
GROUP BY ?component ?role ?quantityKind
ORDER BY DESC(?n_datasets) ?component
```

| `?component` | `?role` | `?quantityKind` | `?n_datasets` |
|---|---|---|---|
| `rep:intensity` | signal | `tax:Intensity` | 5 |
| `rep:x` | axis | `qk:Length` | 2 |
| `rep:y` | axis | `qk:Length` | 2 |
| `rep:depth` | axis | `qk:Length` | 1 |
| `rep:energy` | axis | `qk:Energy` | 1 |
| `rep:temperature` | signal | `qk:Temperature` | 1 |
| `rep:time` | axis | `qk:Time` | 1 |
| `rep:z` | axis | `qk:Length` | 1 |

All eight components in the vocabulary are used by this graph. `rep:intensity` carries
five of the six datasets; only the scalar uses `rep:temperature`.

---

## Group 3 — Reading data

### Q07 — Full spectrum

*Axis values are Enery and signal values are detector counts in the source file.*

```sparql
SELECT ?energy ?intensity WHERE {
    ?obs rep:energy    ?energy ;
         rep:intensity ?intensity .
}
ORDER BY ?energy
```

| `?energy` | `?intensity` |
|---|---|
| 7980.0 | 12.0 |
| 7980.5 | 15.0 |
| 7981.0 | 115.0 |
| 7981.5 | 850.0 |
| 7982.0 | 230.0 |

Two triple patterns, no DSD traversal. This works because `rep:energy` is the same
IRI in every spectrum in the graph.

---

### Q08 — Full time series

```sparql
SELECT ?time ?intensity WHERE {
    ?obs rep:time      ?time ;
         rep:intensity ?intensity .
}
ORDER BY ?time
```

| `?time` | `?intensity` |
|---|---|
| 0.0 | 12500.0 |
| 60.0 | 8400.0 |
| 300.0 | 5100.0 |
| 600.0 | 3800.0 |
| 1800.0 | 2200.0 |
| 3600.0 | 1520.0 |

---

### Q09 — Full depth profile

```sparql
SELECT ?depth ?intensity WHERE {
    ?obs rep:depth     ?depth ;
         rep:intensity ?intensity .
}
ORDER BY ?depth
```

| `?depth` | `?intensity` |
|---|---|
| 0.0 | 120000.0 |
| 5.0 | 85000.0 |
| 10.0 | 32000.0 |
| 20.0 | 5000.0 |
| 50.0 | 210.0 |
| 100.0 | 45.0 |

Q07, Q08 and Q09 are the same query with a different axis IRI. That is the payoff of
fixing the axis per representation type.

---

### Q10 — Scalar value

*The instrument logged some temperature data.*

```sparql
SELECT ?material ?value WHERE {
    ?material tax:hasMaterialProperty ?prop .
    ?prop     rep:has_representation  ?repr .
    ?obs      qb:dataSet       ?repr ;
              rep:temperature  ?value .
}
```

| `?material` | `?value` |
|---|---|
| `ex:Si` | 293.15 |

A rank-0 representation has no axis, so there is no coordinate to bind — the signal
predicate alone identifies the value.

---

## Group 4 — Slicing

### Q11 — Image row at fixed y

```sparql
SELECT ?x ?intensity WHERE {
    ?obs qb:dataSet     ex:r_image ;
         rep:y          "4.0"^^xsd:double ;
         rep:x          ?x ;
         rep:intensity  ?intensity .
}
ORDER BY ?x
```

| `?x` | `?intensity` |
|---|---|
| 0.0 | 11.0 |
| 2.0 | 110.0 |
| 4.0 | 850.0 |
| 6.0 | 115.0 |
| 8.0 | 12.0 |

The peak row of the 5×5 map.

---

### Q12 — Image subregion

```sparql
SELECT ?y ?x ?intensity WHERE {
    ?obs qb:dataSet     ex:r_image ;
         rep:y          ?y ;
         rep:x          ?x ;
         rep:intensity  ?intensity .
    FILTER(?y <= 2.0 && ?x <= 2.0)
}
ORDER BY ?y ?x
```

| `?y` | `?x` | `?intensity` |
|---|---|---|
| 0.0 | 0.0 | 10.0 |
| 0.0 | 2.0 | 12.0 |
| 2.0 | 0.0 | 13.0 |
| 2.0 | 2.0 | 45.0 |

The NumPy equivalent is `img[0:2, 0:2]`.

The `qb:dataSet` binding is doing real work here. Volume observations also carry
`rep:y` and `rep:x`, so without it the query returns twelve rows spanning two
datasets — and since the volume also has a `(2.0, 2.0)` cell, the result would silently
mix a 45 from the image with a 550 from the volume. Any query that constrains only a
subset of a dataset's axes needs to pin the dataset explicitly.

---

### Q13 — Volume z-slice

```sparql
SELECT ?y ?x ?intensity WHERE {
    ?obs qb:dataSet     ex:r_volume ;
         rep:z          "5.0"^^xsd:double ;
         rep:y ?y ; rep:x ?x ; rep:intensity ?intensity .
}
ORDER BY ?y ?x
```

| `?y` | `?x` | `?intensity` |
|---|---|---|
| 0.0 | 0.0 | 11.0 |
| 0.0 | 2.0 | 14.0 |
| 0.0 | 4.0 | 10.0 |
| 2.0 | 0.0 | 12.0 |
| 2.0 | 2.0 | 550.0 |
| 2.0 | 4.0 | 14.0 |

`vol[1, :, :]` — the slice containing the hotspot.

---

### Q14 — Global hotspot

```sparql
SELECT ?z ?y ?x ?intensity WHERE {
    ?obs rep:z ?z ; rep:y ?y ; rep:x ?x ; rep:intensity ?intensity .
}
ORDER BY DESC(?intensity)
LIMIT 3
```

| `?z` | `?y` | `?x` | `?intensity` |
|---|---|---|---|
| 5.0 | 2.0 | 2.0 | 550.0 |
| 0.0 | 2.0 | 2.0 | 15.0 |
| 5.0 | 2.0 | 4.0 | 14.0 |

Binding all three axis predicates restricts this to rank-3 datasets. The image
observations have no `rep:z` and drop out.

---

### Q15 — Peak per dataset

```sparql
SELECT ?repr (MAX(?intensity) AS ?peak) WHERE {
    ?obs qb:dataSet     ?repr ;
         rep:intensity  ?intensity .
}
GROUP BY ?repr
ORDER BY DESC(?peak)
```

| `?repr` | `?peak` |
|---|---|
| `ex:r_depthprofile` | 120000.0 |
| `ex:r_timeseries` | 12500.0 |
| `ex:r_spectrum` | 850.0 |
| `ex:r_image` | 850.0 |
| `ex:r_volume` | 550.0 |

Five rows, not six — the scalar has no `rep:intensity`.

**These magnitudes are not comparable.** The depth profile counts and the image
counts came off different instruments with different integration times, and the
ontology records no unit or normalisation that would let a consumer reconcile them.
Ranking by raw magnitude across datasets is meaningless unless you already know the
acquisition conditions.

---

## Group 5 — Cross-cutting

### Q16 — Datasets with a length axis

```sparql
SELECT DISTINCT ?material ?axis WHERE {
    ?material tax:hasMaterialProperty ?prop .
    ?prop     rep:has_representation  ?repr .
    ?repr     qb:structure / qb:component ?cs .
    ?cs       qb:dimension ?axis .
    ?axis     rep:hasQuantityKind qk:Length .
}
ORDER BY ?material ?axis
```

| `?material` | `?axis` |
|---|---|
| `ex:Al2O3foam` | `rep:x` |
| `ex:Al2O3foam` | `rep:y` |
| `ex:Al2O3foam` | `rep:z` |
| `ex:BdopedSi` | `rep:depth` |
| `ex:DP780` | `rep:x` |
| `ex:DP780` | `rep:y` |

Catches the depth profile alongside the spatial datasets, because `rep:depth` is also
`qk:Length`. Filter on the specific axis IRI to exclude it.

---

### Q17 — Datasets missing a measurement

```sparql
SELECT ?material WHERE {
    ?material a tax:Material .
    FILTER NOT EXISTS {
        ?material tax:hasMaterialProperty ?p .
        ?p        rep:has_scalar_representation ?r .
    }
}
ORDER BY ?material
```

| `?material` |
|---|
| `ex:Al2O3foam` |
| `ex:BdopedSi` |
| `ex:DP780` |
| `ex:FeFoil` |
| `ex:SS316L` |

Everything except `ex:Si`, the only scalar in the graph.

---

### Q18 — Shape of every dataset

```sparql
SELECT ?material ?rank ?total
       (GROUP_CONCAT(?ext ; separator=" x ") AS ?shape) WHERE {
    ?material tax:hasMaterialProperty ?prop .
    ?prop     rep:has_representation  ?repr .
    ?repr     rep:rank   ?rank ;
              rep:extent ?total .
    OPTIONAL {
        ?repr qb:structure / qb:component ?cs .
        ?cs   qb:order ?ord ; rep:extent ?ext .
    }
}
GROUP BY ?material ?rank ?total
ORDER BY ?rank ?material
```

| `?material` | `?rank` | `?total` | `?shape` |
|---|---|---|---|
| `ex:Si` | 0 | 1 | |
| `ex:BdopedSi` | 1 | 6 | 6 |
| `ex:FeFoil` | 1 | 5 | 5 |
| `ex:SS316L` | 1 | 6 | 6 |
| `ex:DP780` | 2 | 25 | 5 x 5 |
| `ex:Al2O3foam` | 3 | 12 | 2 x 2 x 3 |

`?total` always equals the product of the per-axis extents. Nothing enforces that —
it is a SHACL concern, not an OWL one.

---

## Query patterns

Three shapes cover nearly everything.

**A — direct predicate match.** The component is known ahead of time, so name it.
No DSD traversal, fastest, and the right default (Q07–Q09, Q11–Q15).

```sparql
SELECT ?e ?i WHERE { ?obs rep:energy ?e ; rep:intensity ?i }
```

**B — schema traversal.** The question is about structure rather than values (Q05, Q18).

```sparql
?repr qb:structure / qb:component ?cs .
?cs   qb:dimension ?axis ; qb:order ?order ; rep:extent ?extent .
```

**C — variable as predicate.** The component is discovered from the schema and then
used to read values. This is what the OWL 2 pun buys: one IRI is an individual in the
DSD and a property on the observation.

```sparql
SELECT ?axis ?value ?signal ?measurement WHERE {
    ?repr   qb:structure / qb:component ?cs_ax .
    ?cs_ax  qb:dimension ?axis .
    ?repr   qb:structure / qb:component ?cs_sig .
    ?cs_sig qb:measure ?signal .
    ?obs    qb:dataSet ?repr ;
            ?axis   ?value ;          ## variable in predicate position
            ?signal ?measurement .
}
```

Use C when a query must work across representation types without knowing the axis
names in advance.

---

## Common mistakes

**Using an Axis IRI as a measure.** `rep:Axis` and `rep:Signal` are
`owl:disjointWith`, so `rep:energy` cannot fill a `qb:measure` slot even though its
quantity kind is right.

```turtle
qb:component [ qb:measure rep:energy ] .   ## INCONSISTENT — rep:energy is an Axis
```

If no Signal in the vocabulary matches your quantity kind, add one to the TBox.

**Comparing magnitudes across datasets.** No unit is stored, so `850` in the spectrum
and `850` in the image are not the same physical quantity and cannot be ranked
against each other (see Q15).

**Telling axes apart by quantity kind.** Four canonical axes share `qk:Length`. Filter
on `qb:order`, or name the axis IRI directly.

**Forgetting subproperty closure.** ABoxes assert `rep:has_image_representation`, not
`rep:has_representation`. Queries on the parent property need RDFS closure, which most
stores do automatically and plain rdflib does not.

**Putting `rep:extent` on the Signal.** It is always the product of the axis extents.
Storing it invites the two to disagree.

**Slicing without pinning the dataset.** `rep:y` and `rep:x` appear in both images and
volumes. A filter on those two alone silently spans every rank-2 and rank-3 dataset in
the graph. Bind `qb:dataSet` whenever you constrain fewer axes than the dataset has
(see Q12).
