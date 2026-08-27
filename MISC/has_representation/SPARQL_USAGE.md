# FAIRmat Representation Ontology
## Technical Documentation & SPARQL Query Reference

**Namespace:** `http://fairmat-nfdi.eu/taxonomy/representation#` (prefix `rep:`)  
**Version:** TBox v4  
**Depends on:** W3C RDF Data Cube (`qb:`), QUDT (`qk:`, `unit:`), FAIRmat Taxonomy (`tax:`)

---

## 1. Architecture Overview

```
tax:Material
  └─ tax:hasMaterialProperty ──► tax:MaterialProperty
        └─ rep:has_*_representation ──► rep:Representation  (rank → subtype inferred)
              └─ qb:structure ──► rep:DataStructureDefinition
                    └─ qb:component ──► qb:ComponentSpecification
                          ├─ qb:dimension ──► rep:Axis    (+ qb:order, rep:extent, rep:hasUnit)
                          ├─ qb:measure  ──► rep:Signal  (+ rep:hasUnit)
                          └─ qb:attribute ──► rep:UnitAttribute
```

### Representation subtype → rank

| Subtype | `rep:rank` | Inferred by |
|---|---|---|
| `rep:Scalar` | 0 | `equivalentClass` on rank literal |
| `rep:Profile` | 1 | `equivalentClass` on rank literal |
| `rep:Spectrum` | 1 | primitive (asserted) |
| `rep:TimeSeries` | 1 | primitive (asserted) |
| `rep:DepthProfile` | 1 | primitive (asserted) |
| `rep:Image` | 2 | `equivalentClass` on rank literal |
| `rep:VolumeData` | 3 | `equivalentClass` on rank literal |

### Typed link properties

```turtle
rep:has_scalar_representation      rdfs:subPropertyOf rep:has_representation ; rdfs:range rep:Scalar .
rep:has_spectrum_representation    rdfs:subPropertyOf rep:has_representation ; rdfs:range rep:Spectrum .
rep:has_timeseries_representation  rdfs:subPropertyOf rep:has_representation ; rdfs:range rep:TimeSeries .
rep:has_depthprofile_representation rdfs:subPropertyOf rep:has_representation ; rdfs:range rep:DepthProfile .
rep:has_image_representation       rdfs:subPropertyOf rep:has_representation ; rdfs:range rep:Image .
rep:has_volume_representation      rdfs:subPropertyOf rep:has_representation ; rdfs:range rep:VolumeData .
```

### Canonical component vocabulary (TBox, reusable across all ABoxes)

| IRI | Role | Quantity kind |
|---|---|---|
| `rep:energy` | Axis | `qk:Energy` |
| `rep:time` | Axis | `qk:Time` |
| `rep:depth` | Axis | `qk:Length` |
| `rep:x_length` | Axis | `qk:Length` |
| `rep:y_length` | Axis | `qk:Length` |
| `rep:z_length` | Axis | `qk:Length` |
| `rep:intensity` | Signal | `tax:Intensity` |
| `rep:temperature` | Signal | `qk:Temperature` |

User-defined axis names (e.g. `alpha`, `delta`, `t_elapsed`) are stored as `rep:axis_name` on a
local `ex:` IRI. The query semantic anchor is always `rep:hasQuantityKind`, not the name string.

### Observation pattern (qb pun)

```turtle
## component IRI serves as BOTH individual (in DSD) and predicate (on observations)
ex:energy    a rep:Axis ; rep:hasQuantityKind qk:Energy .   ## individual
_:obs ex:energy "7980.0"^^xsd:double .                     ## predicate
_:obs rep:intensity "12.0"^^xsd:double .
```

### extent rules

| Subject | `rep:extent` meaning | Stored? |
|---|---|---|
| `rep:Representation` | total observations = product of all axis extents | always |
| `rep:Axis` (via DSD `qb:ComponentSpecification`) | this axis array length | always |
| `rep:Signal` | always derivable = product(axis extents) | never |

---

## 2. Sample KG Used in This Document

| Material | Property | Representation | Shape |
|---|---|---|---|
| `ex:Si` | `ex:Si_BandGap` | Scalar | () |
| `ex:Sample` | `ex:Sample_Temp` | Scalar | () |
| `ex:AuFilm` | `ex:AuFilm_XPS` | Spectrum | (200,) |
| `ex:Sample` | `ex:Sample_Spec` | Spectrum | (5,) |
| `ex:BdopedSi` | `ex:BdopedSi_SIMS` | DepthProfile | (50,) |
| `ex:SS316L` | `ex:SS316L_Passivation` | TimeSeries | (1200,) |
| `ex:GaAs` | `ex:GaAs_TRPL` | TimeSeries | (500,) |
| `ex:DP780` | `ex:DP780_EBSD` | Image | (512, 512) |
| `ex:Sample` | `ex:Sample_Img` | Image | (5, 5) |
| `ex:Detector1` | `ex:Det1_Map` | Image | (20, 20) – axes: alpha, delta |
| `ex:Detector2` | `ex:Det2_Map` | Image | (30, 30) – axes: gamma, epsilon |
| `ex:Al2O3foam` | `ex:Al2O3foam_CT` | VolumeData | (128, 256, 256) |
| `ex:Sample` | `ex:Sample_Vol` | VolumeData | (2, 2, 3) |

---

## 3. SPARQL Query Reference

All queries use these prefix declarations:

```sparql
PREFIX rep:  <http://fairmat-nfdi.eu/taxonomy/representation#>
PREFIX tax:  <http://fairmat-nfdi.eu/taxonomy/>
PREFIX qb:   <http://purl.org/linked-data/cube#>
PREFIX qk:   <http://qudt.org/vocab/quantitykind/>
PREFIX unit: <http://qudt.org/vocab/unit/>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
```

---

### Group 1 — TBox / Schema Inspection

---

#### Q01 — All representation classes

_What subclasses of `rep:Representation` are defined in the ontology?_

```sparql
SELECT ?class WHERE {
    ?class rdfs:subClassOf rep:Representation .
}
ORDER BY ?class
```

| `?class` |
|---|
| `rep:DataStructureDefinition` |
| `rep:DepthProfile` |
| `rep:Image` |
| `rep:Observation` |
| `rep:Profile` |
| `rep:Scalar` |
| `rep:Spectrum` |
| `rep:TimeSeries` |
| `rep:VolumeData` |

---

#### Q02 — All canonical component instances

_Which `rep:Axis` and `rep:Signal` individuals are defined in the TBox?_

```sparql
SELECT ?component ?role ?quantityKind WHERE {
    { ?component a rep:Axis   . BIND("axis"   AS ?role) }
    UNION
    { ?component a rep:Signal . BIND("signal" AS ?role) }
    FILTER(STRSTARTS(STR(?component), STR(rep:)))
    ?component rep:hasQuantityKind ?quantityKind .
}
ORDER BY ?role ?component
```

| `?component` | `?role` | `?quantityKind` |
|---|---|---|
| `rep:depth` | axis | `qk:Length` |
| `rep:energy` | axis | `qk:Energy` |
| `rep:time` | axis | `qk:Time` |
| `rep:x_length` | axis | `qk:Length` |
| `rep:y_length` | axis | `qk:Length` |
| `rep:z_length` | axis | `qk:Length` |
| `rep:intensity` | signal | `tax:Intensity` |
| `rep:temperature` | signal | `qk:Temperature` |

---

#### Q03 — All quantity kinds registered

_What quantity kinds appear anywhere in the KG?_

```sparql
SELECT DISTINCT ?quantityKind WHERE {
    { ?x rep:hasQuantityKind ?quantityKind }
}
ORDER BY ?quantityKind
```

| `?quantityKind` |
|---|
| `qk:ElectricCurrentDensity` |
| `qk:Energy` |
| `qk:Length` |
| `qk:NumberConcentration` |
| `qk:Temperature` |
| `qk:Time` |
| `tax:Intensity` |

---

#### Q04 — All units registered

_What units are used across all component specifications?_

```sparql
SELECT DISTINCT ?unit WHERE {
    ?cs rep:hasUnit ?unit .
}
ORDER BY ?unit
```

| `?unit` |
|---|
| `rep:Counts` |
| `unit:A-PER-M2` |
| `unit:EV` |
| `unit:K` |
| `unit:MicroM` |
| `unit:NanoM` |
| `unit:NanoSEC` |
| `unit:SEC` |

---

### Group 2 — KG Inventory

---

#### Q05 — All materials

_What materials exist in the KG?_

```sparql
SELECT ?material WHERE {
    ?material a tax:Material .
}
ORDER BY ?material
```

| `?material` |
|---|
| `ex:Al2O3foam` |
| `ex:AuFilm` |
| `ex:BdopedSi` |
| `ex:Detector1` |
| `ex:Detector2` |
| `ex:DP780` |
| `ex:GaAs` |
| `ex:Sample` |
| `ex:Si` |
| `ex:SS316L` |

---

#### Q06 — All representations grouped by type

_How many datasets of each representation type exist?_

```sparql
SELECT ?type (COUNT(DISTINCT ?repr) AS ?count) WHERE {
    ?p rep:has_representation ?repr .
    ?repr a ?type .
    FILTER(?type != rep:Representation && ?type != owl:NamedIndividual)
    FILTER(STRSTARTS(STR(?type), STR(rep:)))
}
GROUP BY ?type
ORDER BY DESC(?count)
```

| `?type` | `?count` |
|---|---|
| `rep:Image` | 4 |
| `rep:Scalar` | 2 |
| `rep:Spectrum` | 2 |
| `rep:TimeSeries` | 2 |
| `rep:VolumeData` | 2 |
| `rep:DepthProfile` | 1 |

---

#### Q07 — Full property inventory per material

_What measurement types does each material have?_

```sparql
SELECT ?material ?repr_type ?total_extent WHERE {
    ?material  tax:hasMaterialProperty  ?p .
    ?p         rep:has_representation   ?repr .
    ?repr      a                        ?repr_type ;
               rep:extent               ?total_extent .
    FILTER(?repr_type != rep:Representation && ?repr_type != owl:NamedIndividual)
    FILTER(STRSTARTS(STR(?repr_type), STR(rep:)))
}
ORDER BY ?material ?repr_type
```

| `?material` | `?repr_type` | `?total_extent` |
|---|---|---|
| `ex:Al2O3foam` | `rep:VolumeData` | 8388608 |
| `ex:AuFilm` | `rep:Spectrum` | 200 |
| `ex:BdopedSi` | `rep:DepthProfile` | 50 |
| `ex:Detector1` | `rep:Image` | 400 |
| `ex:Detector2` | `rep:Image` | 900 |
| `ex:DP780` | `rep:Image` | 262144 |
| `ex:GaAs` | `rep:TimeSeries` | 500 |
| `ex:Sample` | `rep:Image` | 25 |
| `ex:Sample` | `rep:Scalar` | 1 |
| `ex:Sample` | `rep:Spectrum` | 5 |
| `ex:Sample` | `rep:VolumeData` | 12 |
| `ex:Si` | `rep:Scalar` | 1 |
| `ex:SS316L` | `rep:TimeSeries` | 1200 |

---

#### Q08 — Representation count per type per material

_How many representations of each type does each material have?_

```sparql
SELECT ?material ?repr_type (COUNT(?repr) AS ?n) WHERE {
    ?material  tax:hasMaterialProperty  ?p .
    ?p         rep:has_representation   ?repr .
    ?repr      a                        ?repr_type .
    FILTER(STRSTARTS(STR(?repr_type), STR(rep:)))
    FILTER(?repr_type != rep:Representation && ?repr_type != owl:NamedIndividual)
}
GROUP BY ?material ?repr_type
ORDER BY ?material
```

| `?material` | `?repr_type` | `?n` |
|---|---|---|
| `ex:Sample` | `rep:Image` | 1 |
| `ex:Sample` | `rep:Scalar` | 1 |
| `ex:Sample` | `rep:Spectrum` | 1 |
| `ex:Sample` | `rep:VolumeData` | 1 |
| `ex:Si` | `rep:Scalar` | 1 |

---

### Group 3 — Scalar Queries

---

#### Q09 — All scalar values across KG

_Retrieve every scalar measurement: material, quantity, unit, value._

```sparql
SELECT ?material ?property ?signal_name ?value ?unit WHERE {
    ?material  tax:hasMaterialProperty        ?property .
    ?property  rep:has_scalar_representation  ?repr .
    ?repr      qb:structure / qb:component    ?cs .
    ?cs        qb:measure    ?sig_iri ;
               rep:hasUnit   ?unit .
    ?sig_iri   rep:hasQuantityKind ?qk .
    BIND(COALESCE(STRAFTER(STR(?qk),"#"),
                  STRAFTER(STR(?qk),"/")) AS ?signal_name)
    ?obs  qb:dataSet ?repr ; ?sig_iri ?value .
}
ORDER BY ?material
```

| `?material` | `?property` | `?signal_name` | `?value` | `?unit` |
|---|---|---|---|---|
| `ex:Sample` | `ex:Sample_Temp` | `Temperature` | 293.15 | `unit:K` |
| `ex:Si` | `ex:Si_BandGap` | `Energy` | 1.12 | `unit:EV` |

---

#### Q10 — All quantities and units used in scalars

_Schema-level: what quantity kinds + units appear in scalar representations?_

```sparql
SELECT DISTINCT ?quantityKind ?unit WHERE {
    ?p   rep:has_scalar_representation  ?repr .
    ?repr qb:structure / qb:component   ?cs .
    ?cs   qb:measure   ?sig_iri ;
          rep:hasUnit  ?unit .
    ?sig_iri rep:hasQuantityKind ?quantityKind .
}
ORDER BY ?quantityKind
```

| `?quantityKind` | `?unit` |
|---|---|
| `qk:Energy` | `unit:EV` |
| `qk:Temperature` | `unit:K` |

---

#### Q11 — Same quantity across all materials (compare band gaps)

_All materials that have a scalar measurement of `qk:Energy`, with values._

```sparql
SELECT ?material ?value ?unit WHERE {
    ?material  tax:hasMaterialProperty        ?p .
    ?p         rep:has_scalar_representation  ?repr .
    ?repr      qb:structure / qb:component    ?cs .
    ?cs        qb:measure   ?sig_iri ;
               rep:hasUnit  ?unit .
    ?sig_iri   rep:hasQuantityKind qk:Energy .
    ?obs       qb:dataSet ?repr ; ?sig_iri ?value .
}
ORDER BY ?value
```

| `?material` | `?value` | `?unit` |
|---|---|---|
| `ex:Si` | 1.12 | `unit:EV` |

---

#### Q12 — Scalars within a value range

_All scalar temperature measurements between 250 K and 400 K._

```sparql
SELECT ?material ?value ?unit WHERE {
    ?material  tax:hasMaterialProperty        ?p .
    ?p         rep:has_scalar_representation  ?repr .
    ?repr      qb:structure / qb:component    ?cs .
    ?cs        qb:measure   ?sig_iri ;
               rep:hasUnit  ?unit .
    ?sig_iri   rep:hasQuantityKind qk:Temperature .
    ?obs       qb:dataSet ?repr ; ?sig_iri ?value .
    FILTER(?value >= 250 && ?value <= 400)
}
ORDER BY ?value
```

| `?material` | `?value` | `?unit` |
|---|---|---|
| `ex:Sample` | 293.15 | `unit:K` |

---

### Group 4 — Spectrum Queries

---

#### Q13 — All spectra and axis schema

_Every spectrum in the KG with its axis quantity kind, unit, and shape._

```sparql
SELECT ?material ?ax_name ?ax_qk ?ax_unit ?ax_extent
       ?sig_qk ?sig_unit ?total WHERE {
    ?material  tax:hasMaterialProperty         ?p .
    ?p         rep:has_spectrum_representation ?repr .
    ?repr      rep:extent  ?total .
    ?repr qb:structure / qb:component ?cs_ax .
    ?cs_ax qb:dimension  ?ax_iri ;
           rep:extent     ?ax_extent ;
           rep:hasUnit    ?ax_unit .
    ?ax_iri rep:hasQuantityKind ?ax_qk .
    OPTIONAL { ?ax_iri rep:axis_name ?ax_name }
    ?repr qb:structure / qb:component ?cs_sig .
    ?cs_sig qb:measure   ?sig_iri ;
            rep:hasUnit  ?sig_unit .
    ?sig_iri rep:hasQuantityKind ?sig_qk .
}
ORDER BY ?material
```

| `?material` | `?ax_name` | `?ax_qk` | `?ax_unit` | `?ax_extent` | `?sig_qk` | `?sig_unit` | `?total` |
|---|---|---|---|---|---|---|---|
| `ex:AuFilm` | `energy` | `qk:Energy` | `unit:EV` | 200 | `tax:Intensity` | `rep:Counts` | 200 |
| `ex:Sample` | `energy` | `qk:Energy` | `unit:EV` | 5 | `tax:Intensity` | `rep:Counts` | 5 |

---

#### Q14 — Full spectrum data for one material

_All (energy, intensity) pairs for `ex:Sample`._

```sparql
SELECT ?e ?i WHERE {
    ex:Sample  tax:hasMaterialProperty         ?p .
    ?p         rep:has_spectrum_representation ?repr .
    ?repr      qb:structure / qb:component     ?cs_ax .
    ?cs_ax     qb:dimension  ?ax_iri .
    ?ax_iri    rep:hasQuantityKind qk:Energy .
    ?repr      qb:structure / qb:component     ?cs_sig .
    ?cs_sig    qb:measure    ?sig_iri .
    ?obs       qb:dataSet ?repr ; ?ax_iri ?e ; ?sig_iri ?i .
}
ORDER BY ?e
```

| `?e` | `?i` |
|---|---|
| 7980.0 | 12.0 |
| 7982.0 | 230.0 |

---

#### Q15 — Energy window slice

_All observations where energy is between 7980.0 and 7981.0 eV._

```sparql
SELECT ?material ?e ?i WHERE {
    ?material  tax:hasMaterialProperty         ?p .
    ?p         rep:has_spectrum_representation ?repr .
    ?repr      qb:structure / qb:component     ?cs_ax .
    ?cs_ax     qb:dimension  ?ax_iri .
    ?ax_iri    rep:hasQuantityKind qk:Energy .
    ?repr      qb:structure / qb:component     ?cs_sig .
    ?cs_sig    qb:measure    ?sig_iri .
    ?obs       qb:dataSet ?repr ; ?ax_iri ?e ; ?sig_iri ?i .
    FILTER(?e >= 7980.0 && ?e <= 7981.0)
}
ORDER BY ?material ?e
```

| `?material` | `?e` | `?i` |
|---|---|---|
| `ex:Sample` | 7980.0 | 12.0 |

---

#### Q16 — Peak (argmax intensity)

_The single highest-intensity observation across all spectra._

```sparql
SELECT ?material ?e ?i WHERE {
    ?material  tax:hasMaterialProperty         ?p .
    ?p         rep:has_spectrum_representation ?repr .
    ?repr      qb:structure / qb:component     ?cs_ax .
    ?cs_ax     qb:dimension  ?ax_iri .
    ?ax_iri    rep:hasQuantityKind qk:Energy .
    ?repr      qb:structure / qb:component     ?cs_sig .
    ?cs_sig    qb:measure    ?sig_iri .
    ?obs       qb:dataSet ?repr ; ?ax_iri ?e ; ?sig_iri ?i .
}
ORDER BY DESC(?i) LIMIT 1
```

| `?material` | `?e` | `?i` |
|---|---|---|
| `ex:AuFilm` | 84.0 | 18650.0 |

---

### Group 5 — Image Queries

---

#### Q17 — All images and shape

_Every image dataset with axis extents and total shape._

```sparql
SELECT ?material ?total ?ext_0 ?ext_1 WHERE {
    ?material  tax:hasMaterialProperty      ?p .
    ?p         rep:has_image_representation ?repr .
    ?repr      rep:extent  ?total .
    ?repr qb:structure / qb:component ?cs0 .
    ?cs0  qb:order "0"^^xsd:nonNegativeInteger ; rep:extent ?ext_0 .
    ?repr qb:structure / qb:component ?cs1 .
    ?cs1  qb:order "1"^^xsd:nonNegativeInteger ; rep:extent ?ext_1 .
}
ORDER BY ?material
```

| `?material` | `?total` | `?ext_0` | `?ext_1` |
|---|---|---|---|
| `ex:Detector1` | 400 | 20 | 20 |
| `ex:Detector2` | 900 | 30 | 30 |
| `ex:DP780` | 262144 | 512 | 512 |
| `ex:Sample` | 25 | 5 | 5 |

---

#### Q18 — User-defined axis names and units across all images

_All image datasets showing user-defined axis names alongside semantic metadata._

```sparql
SELECT ?material ?ax_name ?ax_order ?ax_qk ?ax_unit ?ax_extent
       ?sig_qk ?sig_unit ?total WHERE {
    ?material  tax:hasMaterialProperty      ?p .
    ?p         rep:has_image_representation ?repr .
    ?repr      rep:extent ?total .
    ?repr qb:structure / qb:component ?cs_ax .
    ?cs_ax qb:dimension  ?ax_iri ;
           qb:order      ?ax_order ;
           rep:extent    ?ax_extent ;
           rep:hasUnit   ?ax_unit .
    ?ax_iri rep:hasQuantityKind ?ax_qk .
    OPTIONAL { ?ax_iri rep:axis_name ?ax_name }
    ?repr qb:structure / qb:component ?cs_sig .
    ?cs_sig qb:measure   ?sig_iri ;
            rep:hasUnit  ?sig_unit .
    ?sig_iri rep:hasQuantityKind ?sig_qk .
}
ORDER BY ?material ?ax_order
```

| `?material` | `?ax_name` | `?ax_order` | `?ax_qk` | `?ax_unit` | `?ax_extent` | `?sig_qk` | `?sig_unit` | `?total` |
|---|---|---|---|---|---|---|---|---|
| `ex:Detector1` | `alpha` | 0 | `qk:Length` | `unit:MicroM` | 20 | `tax:Intensity` | `rep:Counts` | 400 |
| `ex:Detector1` | `delta` | 1 | `qk:Length` | `unit:MicroM` | 20 | `tax:Intensity` | `rep:Counts` | 400 |
| `ex:Detector2` | `gamma` | 0 | `qk:Length` | `unit:NanoM` | 30 | `tax:Intensity` | `rep:Counts` | 900 |
| `ex:Detector2` | `epsilon` | 1 | `qk:Length` | `unit:NanoM` | 30 | `tax:Intensity` | `rep:Counts` | 900 |
| `ex:DP780` | `y` | 0 | `qk:Length` | `unit:MicroM` | 512 | `tax:Intensity` | `rep:Counts` | 262144 |
| `ex:DP780` | `x` | 1 | `qk:Length` | `unit:MicroM` | 512 | `tax:Intensity` | `rep:Counts` | 262144 |
| `ex:Sample` | `y` | 0 | `qk:Length` | `unit:MicroM` | 5 | `tax:Intensity` | `rep:Counts` | 25 |
| `ex:Sample` | `x` | 1 | `qk:Length` | `unit:MicroM` | 5 | `tax:Intensity` | `rep:Counts` | 25 |

---

#### Q19 — Row slice (fixed axis-0 coordinate)

_All pixels where y = 4.0 µm in `ex:Sample` image._

```sparql
SELECT ?x ?i WHERE {
    ex:Sample  tax:hasMaterialProperty      ?p .
    ?p         rep:has_image_representation ?repr .
    ?repr      qb:structure / qb:component  ?cs0 .
    ?cs0       qb:dimension ?ax0 ; qb:order "0"^^xsd:nonNegativeInteger .
    ?repr      qb:structure / qb:component  ?cs1 .
    ?cs1       qb:dimension ?ax1 ; qb:order "1"^^xsd:nonNegativeInteger .
    ?repr      qb:structure / qb:component  ?css .
    ?css       qb:measure ?sig_iri .
    ?obs  qb:dataSet ?repr ; ?ax0 "4.0"^^xsd:double ; ?ax1 ?x ; ?sig_iri ?i .
}
ORDER BY ?x
```

| `?x` | `?i` |
|---|---|
| 4.0 | 850.0 |

---

#### Q20 — Spatial subregion

_All pixels where y < 4.0 µm AND x < 4.0 µm in `ex:Sample`._

```sparql
SELECT ?y ?x ?i WHERE {
    ex:Sample  tax:hasMaterialProperty      ?p .
    ?p         rep:has_image_representation ?repr .
    ?repr      qb:structure / qb:component  ?cs0 .
    ?cs0       qb:dimension ?ax0 ; qb:order "0"^^xsd:nonNegativeInteger .
    ?repr      qb:structure / qb:component  ?cs1 .
    ?cs1       qb:dimension ?ax1 ; qb:order "1"^^xsd:nonNegativeInteger .
    ?repr      qb:structure / qb:component  ?css .
    ?css       qb:measure   ?sig_iri .
    ?obs  qb:dataSet ?repr ; ?ax0 ?y ; ?ax1 ?x ; ?sig_iri ?i .
    FILTER(?y < 4.0 && ?x < 4.0)
}
ORDER BY ?y ?x
```

| `?y` | `?x` | `?i` |
|---|---|---|
| 0.0 | 0.0 | 10.0 |

---

#### Q21 — Peak pixel and coordinates

_The highest intensity pixel across all images._

```sparql
SELECT ?material ?y ?x ?i WHERE {
    ?material  tax:hasMaterialProperty      ?p .
    ?p         rep:has_image_representation ?repr .
    ?repr      qb:structure / qb:component  ?cs0 .
    ?cs0       qb:dimension ?ax0 ; qb:order "0"^^xsd:nonNegativeInteger .
    ?repr      qb:structure / qb:component  ?cs1 .
    ?cs1       qb:dimension ?ax1 ; qb:order "1"^^xsd:nonNegativeInteger .
    ?repr      qb:structure / qb:component  ?css .
    ?css       qb:measure   ?sig_iri .
    ?obs  qb:dataSet ?repr ; ?ax0 ?y ; ?ax1 ?x ; ?sig_iri ?i .
}
ORDER BY DESC(?i) LIMIT 1
```

| `?material` | `?y` | `?x` | `?i` |
|---|---|---|---|
| `ex:Sample` | 4.0 | 4.0 | 850.0 |

---

### Group 6 — Volume Queries

---

#### Q22 — All volumes and shape

_Every volume dataset with axis extents and total voxel count._

```sparql
SELECT ?material ?total ?ext_0 ?ext_1 ?ext_2 WHERE {
    ?material  tax:hasMaterialProperty       ?p .
    ?p         rep:has_volume_representation ?repr .
    ?repr      rep:extent ?total .
    ?repr qb:structure / qb:component ?cs0 .
    ?cs0  qb:order "0"^^xsd:nonNegativeInteger ; rep:extent ?ext_0 .
    ?repr qb:structure / qb:component ?cs1 .
    ?cs1  qb:order "1"^^xsd:nonNegativeInteger ; rep:extent ?ext_1 .
    ?repr qb:structure / qb:component ?cs2 .
    ?cs2  qb:order "2"^^xsd:nonNegativeInteger ; rep:extent ?ext_2 .
}
ORDER BY ?material
```

| `?material` | `?total` | `?ext_0` (z) | `?ext_1` (y) | `?ext_2` (x) |
|---|---|---|---|---|
| `ex:Al2O3foam` | 8388608 | 128 | 256 | 256 |
| `ex:Sample` | 12 | 2 | 2 | 3 |

---

#### Q23 — Single z-slice at fixed coordinate

_All voxels where z = 5.0 µm in `ex:Sample` volume._

```sparql
SELECT ?y ?x ?i WHERE {
    ex:Sample  tax:hasMaterialProperty       ?p .
    ?p         rep:has_volume_representation ?repr .
    ?repr qb:structure / qb:component ?cs0 .
    ?cs0  qb:dimension ?ax0 ; qb:order "0"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?cs1 .
    ?cs1  qb:dimension ?ax1 ; qb:order "1"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?cs2 .
    ?cs2  qb:dimension ?ax2 ; qb:order "2"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?css .
    ?css  qb:measure  ?sig_iri .
    ?obs  qb:dataSet ?repr ;
          ?ax0 "5.0"^^xsd:double ;
          ?ax1 ?y ; ?ax2 ?x ; ?sig_iri ?i .
}
ORDER BY ?y ?x
```

| `?y` | `?x` | `?i` |
|---|---|---|
| 2.0 | 2.0 | 550.0 |

---

#### Q24 — Subvolume bounding box

_All voxels where z ≤ 5.0 AND y ≤ 2.0 AND x ≤ 2.0._

```sparql
SELECT ?z ?y ?x ?i WHERE {
    ex:Sample  tax:hasMaterialProperty       ?p .
    ?p         rep:has_volume_representation ?repr .
    ?repr qb:structure / qb:component ?cs0 .
    ?cs0  qb:dimension ?ax0 ; qb:order "0"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?cs1 .
    ?cs1  qb:dimension ?ax1 ; qb:order "1"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?cs2 .
    ?cs2  qb:dimension ?ax2 ; qb:order "2"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?css .
    ?css  qb:measure ?sig_iri .
    ?obs  qb:dataSet ?repr ;
          ?ax0 ?z ; ?ax1 ?y ; ?ax2 ?x ; ?sig_iri ?i .
    FILTER(?z <= 5.0 && ?y <= 2.0 && ?x <= 2.0)
}
ORDER BY ?z ?y ?x
```

| `?z` | `?y` | `?x` | `?i` |
|---|---|---|---|
| 0.0 | 0.0 | 0.0 | 10.0 |
| 5.0 | 2.0 | 2.0 | 550.0 |

---

#### Q25 — Global hotspot (argmax across all volumes)

_The single highest-intensity voxel across all volume datasets._

```sparql
SELECT ?material ?z ?y ?x ?i WHERE {
    ?material  tax:hasMaterialProperty       ?p .
    ?p         rep:has_volume_representation ?repr .
    ?repr qb:structure / qb:component ?cs0 .
    ?cs0  qb:dimension ?ax0 ; qb:order "0"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?cs1 .
    ?cs1  qb:dimension ?ax1 ; qb:order "1"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?cs2 .
    ?cs2  qb:dimension ?ax2 ; qb:order "2"^^xsd:nonNegativeInteger .
    ?repr qb:structure / qb:component ?css .
    ?css  qb:measure ?sig_iri .
    ?obs  qb:dataSet ?repr ;
          ?ax0 ?z ; ?ax1 ?y ; ?ax2 ?x ; ?sig_iri ?i .
}
ORDER BY DESC(?i) LIMIT 1
```

| `?material` | `?z` | `?y` | `?x` | `?i` |
|---|---|---|---|---|
| `ex:Sample` | 5.0 | 2.0 | 2.0 | 550.0 |

---

### Group 7 — TimeSeries Queries

---

#### Q26 — All time series: axis and signal schema

_Every time series with user-defined axis name, time unit, signal kind, signal unit._

```sparql
SELECT ?material ?ax_name ?ax_unit ?ax_extent
       ?sig_qk ?sig_unit ?total WHERE {
    ?material  tax:hasMaterialProperty           ?p .
    ?p         rep:has_timeseries_representation ?repr .
    ?repr      rep:extent ?total .
    ?repr qb:structure / qb:component ?cs_ax .
    ?cs_ax qb:dimension  ?ax_iri ;
           rep:extent     ?ax_extent ;
           rep:hasUnit    ?ax_unit .
    ?ax_iri rep:hasQuantityKind qk:Time .
    OPTIONAL { ?ax_iri rep:axis_name ?ax_name }
    ?repr qb:structure / qb:component ?cs_sig .
    ?cs_sig qb:measure   ?sig_iri ;
            rep:hasUnit  ?sig_unit .
    ?sig_iri rep:hasQuantityKind ?sig_qk .
}
ORDER BY ?material
```

| `?material` | `?ax_name` | `?ax_unit` | `?ax_extent` | `?sig_qk` | `?sig_unit` | `?total` |
|---|---|---|---|---|---|---|
| `ex:GaAs` | `time_stamp` | `unit:NanoSEC` | 500 | `tax:Intensity` | `rep:Counts` | 500 |
| `ex:SS316L` | `t_elapsed` | `unit:SEC` | 1200 | `qk:ElectricCurrentDensity` | `unit:A-PER-M2` | 1200 |

---

#### Q27 — Full decay curve for one material

_All (time, signal) pairs for `ex:GaAs` ordered by time._

```sparql
SELECT ?t ?i WHERE {
    ex:GaAs  tax:hasMaterialProperty           ?p .
    ?p       rep:has_timeseries_representation ?repr .
    ?repr    qb:structure / qb:component       ?cs_ax .
    ?cs_ax   qb:dimension ?ax_iri .
    ?ax_iri  rep:hasQuantityKind qk:Time .
    ?repr    qb:structure / qb:component       ?cs_sig .
    ?cs_sig  qb:measure ?sig_iri .
    ?obs     qb:dataSet ?repr ; ?ax_iri ?t ; ?sig_iri ?i .
}
ORDER BY ?t
```

| `?t` | `?i` |
|---|---|
| 0.0 | 10000.0 |
| 2.0 | 1353.0 |

---

#### Q28 — Time-windowed fetch

_All observations where time ≥ 0.5 ns AND time ≤ 3.0 ns for GaAs._

```sparql
SELECT ?t ?i WHERE {
    ex:GaAs  tax:hasMaterialProperty           ?p .
    ?p       rep:has_timeseries_representation ?repr .
    ?repr    qb:structure / qb:component       ?cs_ax .
    ?cs_ax   qb:dimension ?ax_iri .
    ?ax_iri  rep:hasQuantityKind qk:Time .
    ?repr    qb:structure / qb:component       ?cs_sig .
    ?cs_sig  qb:measure ?sig_iri .
    ?obs     qb:dataSet ?repr ; ?ax_iri ?t ; ?sig_iri ?i .
    FILTER(?t >= 0.5 && ?t <= 3.0)
}
ORDER BY ?t
```

| `?t` | `?i` |
|---|---|
| 2.0 | 1353.0 |

---

### Group 8 — Cross-Cutting Queries

---

#### Q29 — All datasets with a `qk:Energy` axis

_Which representations use energy as a dimension — regardless of representation type._

```sparql
SELECT DISTINCT ?material ?repr_type WHERE {
    ?material  tax:hasMaterialProperty  ?p .
    ?p         rep:has_representation   ?repr .
    ?repr      a                        ?repr_type .
    ?repr      qb:structure / qb:component ?cs .
    ?cs        qb:dimension ?ax .
    ?ax        rep:hasQuantityKind qk:Energy .
    FILTER(STRSTARTS(STR(?repr_type), STR(rep:)))
    FILTER(?repr_type != rep:Representation && ?repr_type != owl:NamedIndividual)
}
ORDER BY ?material
```

| `?material` | `?repr_type` |
|---|---|
| `ex:AuFilm` | `rep:Spectrum` |
| `ex:Sample` | `rep:Spectrum` |
| `ex:Si` | `rep:Scalar` |

---

#### Q30 — All datasets with signal in `rep:Counts`

_Every representation whose signal is measured in detector counts._

```sparql
SELECT DISTINCT ?material ?repr_type WHERE {
    ?material  tax:hasMaterialProperty  ?p .
    ?p         rep:has_representation   ?repr .
    ?repr      a                        ?repr_type .
    ?repr      qb:structure / qb:component ?cs .
    ?cs        qb:measure   ?sig ;
               rep:hasUnit  rep:Counts .
    FILTER(STRSTARTS(STR(?repr_type), STR(rep:)))
    FILTER(?repr_type != rep:Representation && ?repr_type != owl:NamedIndividual)
}
ORDER BY ?material ?repr_type
```

| `?material` | `?repr_type` |
|---|---|
| `ex:AuFilm` | `rep:Spectrum` |
| `ex:Detector1` | `rep:Image` |
| `ex:Detector2` | `rep:Image` |
| `ex:DP780` | `rep:Image` |
| `ex:GaAs` | `rep:TimeSeries` |
| `ex:Sample` | `rep:Image` |
| `ex:Sample` | `rep:Spectrum` |
| `ex:Sample` | `rep:VolumeData` |

---

#### Q31 — Materials missing a specific measurement

_All materials that have NO scalar temperature measurement._

```sparql
SELECT ?material WHERE {
    ?material  a tax:Material .
    FILTER NOT EXISTS {
        ?material  tax:hasMaterialProperty        ?p .
        ?p         rep:has_scalar_representation  ?repr .
        ?repr      qb:structure / qb:component    ?cs .
        ?cs        qb:measure   ?sig .
        ?sig       rep:hasQuantityKind qk:Temperature .
    }
}
ORDER BY ?material
```

| `?material` |
|---|
| `ex:Al2O3foam` |
| `ex:AuFilm` |
| `ex:BdopedSi` |
| `ex:Detector1` |
| `ex:Detector2` |
| `ex:DP780` |
| `ex:GaAs` |
| `ex:Si` |
| `ex:SS316L` |

---

#### Q32 — Full unit inventory across KG

_Every unit used anywhere in any dataset, with count of datasets using it._

```sparql
SELECT ?unit (COUNT(DISTINCT ?repr) AS ?n_datasets) WHERE {
    ?repr  qb:structure / qb:component  ?cs .
    ?cs    rep:hasUnit  ?unit .
}
GROUP BY ?unit
ORDER BY DESC(?n_datasets)
```

| `?unit` | `?n_datasets` |
|---|---|
| `rep:Counts` | 8 |
| `unit:MicroM` | 6 |
| `unit:EV` | 3 |
| `unit:SEC` | 2 |
| `unit:K` | 1 |
| `unit:NanoM` | 1 |
| `unit:NanoSEC` | 1 |
| `unit:A-PER-M2` | 1 |

---

## 4. Design Decisions Record

| Decision | Choice | Rationale |
|---|---|---|
| Representation subtype | Derived from `rep:rank` via `owl:equivalentClass` | Single triple triggers inference; no redundant type assertion needed |
| Typed `has_*_representation` | Subproperties with specific `rdfs:range` | Subtype visible in raw ABox without running reasoner; two independent inference paths |
| Component IRI as predicate | OWL 2 pun: IRI is both individual and property | Enables `?obs ?ax_iri ?value` in SPARQL; no extra reification hop |
| `rep:extent` placement | On `rep:Representation` (total) and on `qb:ComponentSpecification` (per axis) | Signal extent always derivable = product(axis extents); never stored |
| `rep:hasUnit` placement | On `qb:ComponentSpecification` blank node | Unit is dataset-specific; co-located with order and extent on same blank node |
| Canonical component vocabulary | `rep:energy`, `rep:intensity` etc. in TBox | Cross-dataset SPARQL without per-file IRI minting |
| User-defined axis names | `rep:axis_name` string + local `ex:` IRI | Semantic anchor is `rep:hasQuantityKind`; name is display-only |
| Blank nodes for DSD internals | Allowed — DSD and ComponentSpec are structural | Named IRI only needed when IRI is used as predicate |
| `rep:axis_name` vs `rdfs:label` | `rep:axis_name` kept | Domain-specific; clearer than general-purpose label in this context |
| Index (`rep:index`) | Optional HDF5 back-reference | Coordinate values now stored directly on observations; index only needed for non-sorted data |