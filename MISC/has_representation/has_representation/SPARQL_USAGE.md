# SPARQL usage

The queries below assume that `representation.ttl`,
`representation.shacl.ttl`, and the six `*-valid-abox.ttl` examples are
loaded into one graph. No ordering property is used.

## Prefixes

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

## Q1 — Which FAIRmat classes specialize RDF Data Cube classes?

```sparql
SELECT ?fairmatClass ?cubeClass WHERE {
  ?fairmatClass rdfs:subClassOf ?cubeClass .
  FILTER(STRSTARTS(STR(?cubeClass), STR(qb:)))
}
ORDER BY ?fairmatClass
```

This query exposes the machine-actionable class bridges. No
`skos:closeMatch` interpretation is required.

## Q2 — What canonical components are available?

```sparql
SELECT ?component ?role ?kind ?retainedUnit WHERE {
  VALUES ?role { rep:Axis rep:Signal }
  ?component a ?role ;
             rep:hasQuantityKind ?kind .
  OPTIONAL { ?component rep:hasUnit ?retainedUnit }
}
ORDER BY ?role ?component
```

The optional result column reflects retained ontology assertions. It does not
implement a default-selection rule.

## Q3 — Which datasets and ranks occur?

```sparql
SELECT ?dataset ?type ?rank WHERE {
  VALUES ?type {
    rep:Scalar rep:Spectrum rep:TimeSeries
    rep:DepthProfile rep:Image rep:VolumeData
  }
  ?dataset a ?type ;
           rep:rank ?rank .
}
ORDER BY ?rank ?type ?dataset
```

## Q4 — Which dimensions and measures belong to each dataset?

```sparql
SELECT ?dataset ?role ?component WHERE {
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
}
ORDER BY ?dataset ?role ?component
```

This query returns membership only. The module defines no component order.

## Q5 — Which dataset-specific units were supplied?

```sparql
SELECT ?dataset ?component ?kind ?unit WHERE {
  ?dataset qb:structure/qb:component ?spec .
  ?spec rep:hasUnit ?unit ;
        (qb:dimension|qb:measure|qb:attribute) ?component .
  ?component rep:hasQuantityKind ?kind .
}
ORDER BY ?dataset ?component
```

Components without a supplied unit are intentionally absent.

## Q6 — Which units does the validation profile permit?

```sparql
SELECT ?kind ?unit WHERE {
  ?kind shp:permitsUnit ?unit .
}
ORDER BY ?kind ?unit
```

The table is an application whitelist. Its absence of a unit is not a
scientific claim that the unit is dimensionally incompatible.

## Q7 — Read observations generically

```sparql
SELECT ?dataset ?observation ?component ?value WHERE {
  ?dataset qb:structure/qb:component/(qb:dimension|qb:measure) ?component .
  ?observation a rep:Observation ;
               qb:dataSet ?dataset ;
               ?component ?value .
}
ORDER BY ?dataset ?observation ?component
```

## Q8 — Find components with missing or ambiguous quantity kinds

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
```

SHACL additionally checks that the value is an IRI typed as
`qudt:QuantityKind`.

## Q9 — Find supplied units outside the whitelist

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
ORDER BY ?subject ?kind ?unit
```

Use SHACL for authoritative validation because it also checks missing context,
cardinality, IRI node kinds, and stable result codes.

## Queries that need entailment

Without RDFS/OWL entailment, this asserted triple:

```turtle
ex:map a rep:Image .
```

does not appear in a basic graph-pattern result for:

```sparql
SELECT ?dataset WHERE { ?dataset a qb:DataSet }
```

The result follows from `rep:Image rdfs:subClassOf qb:DataSet`. Enable RDFS
entailment or materialize superclass types at ingestion when generic Data Cube
queries must see the relationship.
