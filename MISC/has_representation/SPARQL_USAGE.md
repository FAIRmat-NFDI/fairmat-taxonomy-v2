# SPARQL usage

This guide describes what the revised ontology supports in an asserted graph,
what changes when RDFS/OWL entailment is enabled, and what SHACL contributes
beyond querying.

The result tables were produced from the files in this package. Queries Q1–Q8
use:

- `representation.ttl`;
- `representation.shacl.ttl`, including the trusted whitelist;
- all six `*-valid-abox.ttl` examples.

Queries Q9 and Q10 intentionally use all 18 example ABoxes so that their
diagnostic rows are visible.

## Reproduce the queries

```python
from pathlib import Path
from rdflib import Graph

root = Path(".")
graph = Graph()
graph.parse(root / "representation.ttl")
graph.parse(root / "representation.shacl.ttl")

for path in sorted((root / "examples").glob("*-valid-abox.ttl")):
    graph.parse(path)

for row in graph.query(QUERY):
    print(row)
```

No reasoner is required for Q1–Q10. Q11 demonstrates the result added by RDFS
entailment.

## Prefixes

Every query below assumes:

```sparql
PREFIX ex:   <http://example.org/representation/>
PREFIX rep:  <http://fairmat-nfdi.eu/taxonomy/representation#>
PREFIX tax:  <http://fairmat-nfdi.eu/taxonomy/>
PREFIX shp:  <http://fairmat-nfdi.eu/taxonomy/shapes/units#>
PREFIX qb:   <http://purl.org/linked-data/cube#>
PREFIX qudt: <http://qudt.org/schema/qudt/>
PREFIX qk:   <http://qudt.org/vocab/quantitykind/>
PREFIX unit: <http://qudt.org/vocab/unit/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
```

# What is possible on the asserted graph

## Q1 — Inspect the RDF Data Cube class bridges

```sparql
SELECT ?localClass ?cubeClass WHERE {
  ?localClass rdfs:subClassOf ?cubeClass .
  FILTER(STRSTARTS(STR(?cubeClass), STR(qb:)))
}
ORDER BY ?localClass
```

| FAIRmat class | RDF Data Cube class |
|---|---|
| `rep:Axis` | `qb:DimensionProperty` |
| `rep:ComponentProperty` | `qb:ComponentProperty` |
| `rep:DataStructureDefinition` | `qb:DataStructureDefinition` |
| `rep:Image` | `qb:DataSet` |
| `rep:Observation` | `qb:Observation` |
| `rep:Profile` | `qb:DataSet` |
| `rep:Scalar` | `qb:DataSet` |
| `rep:Signal` | `qb:MeasureProperty` |
| `rep:UnitAttribute` | `qb:AttributeProperty` |
| `rep:VolumeData` | `qb:DataSet` |

This query exposes real class axioms. Consumers do not need to interpret SKOS
mapping properties.

## Q2 — Inspect the reusable component vocabulary

```sparql
SELECT ?component ?role ?kind ?retainedUnit WHERE {
  VALUES ?role { rep:Axis rep:Signal }
  ?component a ?role ;
             rep:hasQuantityKind ?kind .
  OPTIONAL { ?component rep:hasUnit ?retainedUnit }
}
ORDER BY ?role ?component
```

| component | role | kind | retained unit |
|---|---|---|---|
| `rep:depth` | Axis | `qk:Length` | `unit:NanoM` |
| `rep:energy` | Axis | `qk:Energy` | `unit:EV` |
| `rep:time` | Axis | `qk:Time` | `unit:SEC` |
| `rep:x` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:y` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:z` | Axis | `qk:Length` | `unit:MicroM` |
| `rep:intensity` | Signal | `tax:Intensity` | `unit:COUNT` |
| `rep:temperature` | Signal | `qk:Temperature` | `unit:K` |

The fourth column reports asserted ontology metadata. It does not calculate a
dataset unit and must not be treated as a fallback rule.

## Q3 — Follow material properties to their representations

```sparql
SELECT ?property ?link ?dataset ?type ?rank WHERE {
  ?link rdfs:subPropertyOf rep:has_representation .
  ?property ?link ?dataset .

  VALUES ?type {
    rep:Scalar rep:Spectrum rep:TimeSeries
    rep:DepthProfile rep:Image rep:VolumeData
  }
  ?dataset a ?type ;
           rep:rank ?rank .
}
ORDER BY ?rank ?type ?dataset
```

| property | link | dataset | type | rank |
|---|---|---|---|---:|
| `ex:scalar-property` | `rep:has_scalar_representation` | `ex:scalar-valid-dataset` | Scalar | 0 |
| `ex:depthprofile-property` | `rep:has_depthprofile_representation` | `ex:depthprofile-valid-dataset` | DepthProfile | 1 |
| `ex:spectrum-property` | `rep:has_spectrum_representation` | `ex:spectrum-valid-dataset` | Spectrum | 1 |
| `ex:timeseries-property` | `rep:has_timeseries_representation` | `ex:timeseries-valid-dataset` | TimeSeries | 1 |
| `ex:image-property` | `rep:has_image_representation` | `ex:image-valid-dataset` | Image | 2 |
| `ex:volume-property` | `rep:has_volume_representation` | `ex:volume-valid-dataset` | VolumeData | 3 |

The query expands the typed subproperty vocabulary explicitly, so it works
without RDFS subproperty entailment.

## Q4 — Discover every dataset slot, kind, and supplied unit

```sparql
SELECT ?dataset ?role ?component ?kind ?unit WHERE {
  ?dataset qb:structure/qb:component ?spec .

  {
    ?spec qb:dimension ?component .
    BIND("dimension" AS ?role)
  }
  UNION
  {
    ?spec qb:measure ?component .
    BIND("measure" AS ?role)
  }

  ?component rep:hasQuantityKind ?kind .
  OPTIONAL { ?spec rep:hasUnit ?unit }
}
ORDER BY ?dataset ?role ?component
```

Representative rows:

| dataset | role | component | kind | supplied unit |
|---|---|---|---|---|
| depthprofile-valid-dataset | dimension | `rep:depth` | `qk:Length` | `unit:NanoM` |
| depthprofile-valid-dataset | measure | `rep:intensity` | `tax:Intensity` | — |
| image-valid-dataset | dimension | `rep:x` | `qk:Length` | — |
| image-valid-dataset | dimension | `rep:y` | `qk:Length` | `unit:MicroM` |
| scalar-valid-dataset | measure | `rep:temperature` | `qk:Temperature` | — |
| spectrum-valid-dataset | dimension | `rep:energy` | `qk:Energy` | `unit:EV` |
| timeseries-valid-dataset | dimension | `rep:time` | `qk:Time` | `unit:SEC` |
| volume-valid-dataset | dimension | `rep:z` | `qk:Length` | `unit:MicroM` |

The complete result has 14 rows. An empty unit cell means the specification
does not assert a unit. It does not mean that the query should read the
canonical component assertion as a default.

The module exposes membership only. It has no component-order semantics.

## Q5 — List the trusted unit whitelist

```sparql
SELECT ?kind ?unit WHERE {
  ?kind shp:permitsUnit ?unit .
}
ORDER BY ?kind ?unit
```

| quantity kind | permitted unit |
|---|---|
| `tax:Intensity` | `unit:COUNT` |
| `qk:Energy` | `unit:EV` |
| `qk:Length` | `unit:MicroM` |
| `qk:Length` | `unit:NanoM` |
| `qk:Temperature` | `unit:K` |
| `qk:Time` | `unit:SEC` |

This is a query over validator configuration. The result answers “which units
does this application profile accept?” It does not enumerate every
scientifically compatible QUDT unit.

## Q6 — Read a specific spectrum

```sparql
SELECT ?observation ?energy ?intensity WHERE {
  ?observation a rep:Observation ;
               qb:dataSet ex:spectrum-valid-dataset ;
               rep:energy ?energy ;
               rep:intensity ?intensity .
}
ORDER BY ?energy
```

| observation | energy | intensity |
|---|---:|---:|
| `ex:spectrum-valid-observation` | 10.0 | 125 |
| `ex:spectrum-valid-observation-2` | 10.5 | 142 |
| `ex:spectrum-valid-observation-3` | 11.0 | 131 |

The component predicates make the query short and independent of blank-node
positions.

## Q7 — Read observations from any representation

```sparql
SELECT ?dataset ?observation ?component ?value WHERE {
  ?dataset qb:structure/qb:component/
           (qb:dimension|qb:measure) ?component .

  ?observation a rep:Observation ;
               qb:dataSet ?dataset ;
               ?component ?value .
}
ORDER BY ?dataset ?observation ?component
```

This query works for all six types without hard-coding `rep:x`,
`rep:energy`, or `rep:intensity`. On the six valid fixtures it returns 63
component values across 22 observations.

A client can pivot these rows into a table or array after reading the dataset
type and DSD. The ontology provides no array ordering rule, so any ordered
serialization requires an application-level contract.

## Q8 — Count observations and compare with stated extent

```sparql
SELECT ?dataset ?statedExtent (COUNT(?observation) AS ?actualCount) WHERE {
  ?dataset rep:extent ?statedExtent .
  ?observation qb:dataSet ?dataset .
}
GROUP BY ?dataset ?statedExtent
ORDER BY ?dataset
```

| dataset | stated extent | actual count |
|---|---:|---:|
| depthprofile-valid-dataset | 3 | 3 |
| image-valid-dataset | 4 | 4 |
| scalar-valid-dataset | 1 | 1 |
| spectrum-valid-dataset | 3 | 3 |
| timeseries-valid-dataset | 3 | 3 |
| volume-valid-dataset | 8 | 8 |

This is an analytical query, not an ontology constraint. The current
unit-only SHACL graph does not enforce extent equality.

# Pre-validation diagnostics

## Q9 — Find missing or ambiguous quantity kinds

Load all 18 examples for this diagnostic query:

```sparql
SELECT ?component (COUNT(DISTINCT ?kind) AS ?kindCount) WHERE {
  {
    ?component a rep:ComponentProperty .
  }
  UNION
  {
    ?spec (qb:dimension|qb:measure) ?component .
  }
  OPTIONAL { ?component rep:hasQuantityKind ?kind }
}
GROUP BY ?component
HAVING (COUNT(DISTINCT ?kind) != 1)
ORDER BY ?component
```

| component | kind count |
|---|---:|
| `ex:depthprofile-untyped-signal` | 0 |
| `ex:image-untyped-signal` | 0 |
| `ex:scalar-untyped-signal` | 0 |
| `ex:spectrum-untyped-signal` | 0 |
| `ex:timeseries-untyped-signal` | 0 |
| `ex:volume-untyped-signal` | 0 |

SHACL adds node-kind and `qudt:QuantityKind` class checks and reports
`REP-UNIT-004` or `REP-UNIT-005` with stable remedies.

## Q10 — Find supplied units outside the whitelist

Load all 18 examples:

```sparql
SELECT ?subject ?component ?kind ?unit WHERE {
  ?subject rep:hasUnit ?unit .

  {
    BIND(?subject AS ?component)
    ?subject rep:hasQuantityKind ?kind .
  }
  UNION
  {
    ?subject (qb:dimension|qb:measure|qb:attribute) ?component .
    ?component rep:hasQuantityKind ?kind .
  }

  FILTER NOT EXISTS { ?kind shp:permitsUnit ?unit }
}
ORDER BY ?subject
```

| subject | component | kind | supplied unit |
|---|---|---|---|
| `ex:depthprofile-bad-axis-depth` | `rep:depth` | `qk:Length` | `unit:SEC` |
| `ex:image-bad-axis-y` | `rep:y` | `qk:Length` | `unit:SEC` |
| `ex:scalar-bad-signal` | `rep:temperature` | `qk:Temperature` | `unit:EV` |
| `ex:spectrum-bad-axis-energy` | `rep:energy` | `qk:Energy` | `unit:SEC` |
| `ex:timeseries-bad-axis-time` | `rep:time` | `qk:Time` | `unit:EV` |
| `ex:volume-bad-axis-z` | `rep:z` | `qk:Length` | `unit:SEC` |

The query mirrors `REP-UNIT-001` but does not replace SHACL cardinality,
typing, target selection, profile warnings, or structured result metadata.

# What entailment adds

## Q11 — Query every FAIRmat representation as a Data Cube dataset

```sparql
SELECT ?dataset WHERE {
  ?dataset a qb:DataSet .
}
ORDER BY ?dataset
```

Against asserted triples only, the query returns zero rows because examples
state their most specific FAIRmat type.

After RDFS entailment over `rdfs:subClassOf`, it returns:

| dataset |
|---|
| `ex:depthprofile-valid-dataset` |
| `ex:image-valid-dataset` |
| `ex:scalar-valid-dataset` |
| `ex:spectrum-valid-dataset` |
| `ex:timeseries-valid-dataset` |
| `ex:volume-valid-dataset` |

Using RDFLib and OWL-RL:

```python
from owlrl import DeductiveClosure, RDFS_Semantics

DeductiveClosure(RDFS_Semantics).expand(graph)
rows = graph.query(QUERY)
```

An OWL reasoner can additionally use the rank equivalent-class axioms. For
example, a `rep:Representation` with rank two can be classified as
`rep:Image` under the current model.

# Capability boundary

| Capability | Plain SPARQL | RDFS/OWL | SHACL |
|---|---:|---:|---:|
| retrieve explicit datasets, DSDs, components, and observations | yes | yes | — |
| query whitelist configuration | yes | yes | — |
| find obvious missing kinds with aggregation | yes | yes | yes |
| infer `qb:DataSet` from `rep:Image` | no | yes | — |
| infer rank-defined representation class | no | OWL | — |
| enforce optional unit cardinality | diagnostic only | identity semantics | yes |
| require quantity-kind completeness | diagnostic only | open world | yes |
| reject a supplied pair outside the whitelist | diagnostic only | open world | yes |
| return stable error codes and remedies | no | no | yes |
| validate rank, axis membership, and extents | query only | partial | future shapes |

SPARQL answers questions over the graph provided to it. RDFS/OWL adds logical
consequences. SHACL evaluates the explicit data against closed validation
rules. Production services can expose all three as separate operations:
query, entail, and validate.
