# FAIRmat Representation Ontology — Usage Guide
## Writing & Loading Representations

How to write RDF for each representation type, and how to query it back out.
Every example in this guide is a real file that validates against the TBox:

| representation | file | observations |
|---|---|---|
| Scalar | `abox_scalar.ttl` | 1 |
| Spectrum | `abox_spectrum.ttl` | 5 |
| TimeSeries | `abox_timeseries.ttl` | 6 |
| DepthProfile | `abox_depthprofile.ttl` | 6 |
| Image | `abox_image.ttl` | 25 |
| VolumeData | `abox_volume.ttl` | 12 |

---

## The component chain

Every Axis and every Signal declares what it measures. The intended model is a
two-link chain:

```
COMPONENT  --hasQuantityKind-->  QUANTITY KIND  --hasUnit-->  UNIT
```

**The first link is live. The second is disabled.** `rep:hasQuantityKind` is
untouched — it is the semantic anchor for every query in this guide.
`rep:hasUnit` and every `qudt:Unit` individual are commented out in the TBox.

| representation | component | role | `rep:hasQuantityKind` | `rep:hasUnit` |
|---|---|---|---|---|
| Scalar | `rep:temperature` | signal | `qk:Temperature` | ~~`unit:K`~~ |
| Spectrum | `rep:energy` | axis | `qk:Energy` | ~~`unit:EV`~~ |
| | `rep:intensity` | signal | `tax:Intensity` | ~~`unit:COUNT`~~ |
| TimeSeries | `rep:time` | axis | `qk:Time` | ~~`unit:SEC`~~ |
| | `rep:intensity` | signal | `tax:Intensity` | ~~`unit:COUNT`~~ |
| DepthProfile | `rep:depth` | axis | `qk:Length` | ~~`unit:NanoM`~~ |
| | `rep:intensity` | signal | `tax:Intensity` | ~~`unit:COUNT`~~ |
| Image | `rep:y` (0) | axis | `qk:Length` | ~~`unit:MicroM`~~ |
| | `rep:x` (1) | axis | `qk:Length` | ~~`unit:MicroM`~~ |
| | `rep:intensity` | signal | `tax:Intensity` | ~~`unit:COUNT`~~ |
| VolumeData | `rep:z` (0) | axis | `qk:Length` | ~~`unit:MicroM`~~ |
| | `rep:y` (1) | axis | `qk:Length` | ~~`unit:MicroM`~~ |
| | `rep:x` (2) | axis | `qk:Length` | ~~`unit:MicroM`~~ |
| | `rep:intensity` | signal | `tax:Intensity` | ~~`unit:COUNT`~~ |

Struck-through cells are the removed link. They are recorded here and in the TBox
comments so the intended model stays legible, but no such triple exists in any file.

```turtle
## live -- every component declares its quantity kind
rep:energy       rep:hasQuantityKind  qk:Energy .
rep:intensity    rep:hasQuantityKind  tax:Intensity .
rep:temperature  rep:hasQuantityKind  qk:Temperature .

## disabled -- the second link and the units it points at
## rep:energy     rep:hasUnit  unit:EV .
## rep:intensity  rep:hasUnit  unit:COUNT .
```

So a query can ask *which datasets measure an energy* — that is a
`rep:hasQuantityKind` question, and Q16 in `SPARQL_USAGE.md` does exactly that. It
cannot ask *which datasets are in eV*.

Where this guide writes something like *the instrument logged kelvin*, that is
editorial context for the reader. The string is not in the graph and no query
returns it.

---

## The canonical vocabulary

All Axis and Signal IRIs come from this set. ABoxes do not mint `ex:` components.

### Axes — fixed per representation type

| representation | rank | axes (in `qb:order`) |
|---|---|---|
| `rep:Scalar` | 0 | none |
| `rep:Spectrum` | 1 | `rep:energy` |
| `rep:TimeSeries` | 1 | `rep:time` |
| `rep:DepthProfile` | 1 | `rep:depth` |
| `rep:Image` | 2 | `rep:y` (0), `rep:x` (1) |
| `rep:VolumeData` | 3 | `rep:z` (0), `rep:y` (1), `rep:x` (2) |

`rank` equals the number of axes, and the axis IRIs are determined by the type. A
rank-2 dataset uses `rep:y` and `rep:x` — no other pair is valid.

| Axis IRI | quantity kind |
|---|---|
| `rep:x` | `qk:Length` |
| `rep:y` | `qk:Length` |
| `rep:z` | `qk:Length` |
| `rep:depth` | `qk:Length` |
| `rep:energy` | `qk:Energy` |
| `rep:time` | `qk:Time` |

### Signals

| Signal IRI | quantity kind | use |
|---|---|---|
| `rep:intensity` | `tax:Intensity` | raw detector counts — the default |
| `rep:temperature` | `qk:Temperature` | temperature as a measured value |

### Axis and Signal are disjoint

`rep:Axis` and `rep:Signal` are `owl:disjointWith`, so an IRI declared as one cannot
be used as the other. `rep:energy` is an Axis; putting it in a `qb:measure` slot makes
the graph inconsistent under HermiT.

```turtle
## INCONSISTENT — rep:energy is an Axis, not a Signal
qb:component [ qb:measure rep:energy ] .
```

A measurement whose quantity kind has no matching Signal in the vocabulary needs one
added to the TBox — see *Extending the vocabulary* below. Do not reach for the Axis
IRI that happens to share the quantity kind.

---

## Prefix block

```turtle
@prefix ex:   <http://fairmat-nfdi.eu/taxonomy/abox#> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
```

`ex:` is for instance IRIs only — materials, properties, representations. Components
always come from `rep:`.

---

## 1. Scalar — `abox_scalar.ttl`

**Shape** `()` · **rank** 0 · **inferred** `rep:Scalar` · **axes** none

Silicon sample, recorded specimen temperature. *The instrument logged kelvin.*

| value |
|---|
| 293.15 |

```turtle
ex:Si     a tax:Material , owl:NamedIndividual ;
    skos:prefLabel "Silicon"@en ;
    tax:hasMaterialProperty ex:Si_Temp .

ex:Si_Temp  a tax:MaterialProperty , owl:NamedIndividual ;
    skos:prefLabel "Specimen temperature"@en ;
    rep:has_scalar_representation ex:r_scalar ;
    rep:has_dsd                   _:dsd .

ex:r_scalar a rep:Representation , rep:Scalar , owl:NamedIndividual ;
    rep:rank   "0"^^xsd:nonNegativeInteger ;   ## triggers rep:Scalar
    rep:extent "1"^^xsd:nonNegativeInteger ;
    qb:structure _:dsd .

## no dimension component — rank 0 has no independent variable
_:dsd a rep:DataStructureDefinition ;
    rep:hasComponent rep:temperature ;
    qb:component [ qb:measure rep:temperature ] .

_:o0 a rep:Observation ; qb:dataSet ex:r_scalar ;
    rep:temperature "293.15"^^xsd:double .
```

`rep:temperature` carries `rep:hasQuantityKind qk:Temperature`, so a query can find
this dataset by quantity kind without knowing the material or the property name.

---

## 2. Spectrum — `abox_spectrum.ttl`

**Shape** `(5,)` · **rank** 1 · **inferred** `rep:Profile` · **asserted** `rep:Spectrum`
· **axis** `rep:energy`

Fe K-edge absorption scan. *Axis values are eV and signal values are detector counts
in the source file; neither unit is in the graph.*

| index | energy | intensity |
|---|---|---|
| 0 | 7980.0 | 12 |
| 1 | 7980.5 | 15 |
| 2 | 7981.0 | 115 |
| 3 | 7981.5 | 850 |
| 4 | 7982.0 | 230 |

```turtle
ex:FeFoil      a tax:Material , owl:NamedIndividual ;
    skos:prefLabel "Iron foil"@en .

ex:FeFoil_XAS  a tax:MaterialProperty , owl:NamedIndividual ;
    skos:prefLabel "Fe K-edge absorption"@en ;
    rep:has_spectrum_representation ex:r_spectrum ;
    rep:has_dsd                     _:dsd .

ex:r_spectrum a rep:Representation , rep:Spectrum , owl:NamedIndividual ;
    rep:rank   "1"^^xsd:nonNegativeInteger ;
    rep:extent "5"^^xsd:nonNegativeInteger ;
    qb:structure _:dsd .

_:dsd a rep:DataStructureDefinition ;
    rep:hasComponent rep:energy , rep:intensity ;
    qb:component
        [ qb:dimension rep:energy ;
          qb:order     "0"^^xsd:nonNegativeInteger ;
          rep:extent   "5"^^xsd:nonNegativeInteger ] ,
        [ qb:measure   rep:intensity ] .

## component IRIs act as predicates on the observation
_:o3 a rep:Observation ; qb:dataSet ex:r_spectrum ;
    rep:index "3"^^xsd:nonNegativeInteger ;
    rep:energy "7981.5"^^xsd:double ; rep:intensity "850.0"^^xsd:double .
```

---

## 3. TimeSeries — `abox_timeseries.ttl`

**Shape** `(6,)` · **rank** 1 · **inferred** `rep:Profile` · **asserted** `rep:TimeSeries`
· **axis** `rep:time`

316L stainless steel, passivation current decay. *Times were logged in seconds.*

| index | time | intensity |
|---|---|---|
| 0 | 0 | 12500 |
| 1 | 60 | 8400 |
| 2 | 300 | 5100 |
| 3 | 600 | 3800 |
| 4 | 1800 | 2200 |
| 5 | 3600 | 1520 |

```turtle
ex:SS316L         a tax:Material , owl:NamedIndividual ;
    skos:prefLabel "316L stainless steel"@en .

ex:SS316L_Passiv  a tax:MaterialProperty , owl:NamedIndividual ;
    skos:prefLabel "Passivation current decay"@en ;
    rep:has_timeseries_representation ex:r_timeseries ;
    rep:has_dsd                       _:dsd .

ex:r_timeseries a rep:Representation , rep:TimeSeries , owl:NamedIndividual ;
    rep:rank   "1"^^xsd:nonNegativeInteger ;
    rep:extent "6"^^xsd:nonNegativeInteger ;
    qb:structure _:dsd .

_:dsd a rep:DataStructureDefinition ;
    rep:hasComponent rep:time , rep:intensity ;
    qb:component
        [ qb:dimension rep:time ;
          qb:order     "0"^^xsd:nonNegativeInteger ;
          rep:extent   "6"^^xsd:nonNegativeInteger ] ,
        [ qb:measure   rep:intensity ] .

_:t5 a rep:Observation ; qb:dataSet ex:r_timeseries ;
    rep:index "5"^^xsd:nonNegativeInteger ;
    rep:time "3600.0"^^xsd:double ; rep:intensity "1520.0"^^xsd:double .
```

The only structural difference from a Spectrum is the axis IRI. Swapping
`rep:energy` for `rep:time` and asserting `rep:TimeSeries` instead of `rep:Spectrum`
is the whole change.

---

## 4. DepthProfile — `abox_depthprofile.ttl`

**Shape** `(6,)` · **rank** 1 · **inferred** `rep:Profile` · **asserted** `rep:DepthProfile`
· **axis** `rep:depth`

Boron-implanted silicon, SIMS sputter profile. *Depths were recorded in nm.*

| index | depth | intensity |
|---|---|---|
| 0 | 0 | 120000 |
| 1 | 5 | 85000 |
| 2 | 10 | 32000 |
| 3 | 20 | 5000 |
| 4 | 50 | 210 |
| 5 | 100 | 45 |

```turtle
ex:BdopedSi       a tax:Material , owl:NamedIndividual ;
    skos:prefLabel "Boron-implanted silicon"@en .

ex:BdopedSi_SIMS  a tax:MaterialProperty , owl:NamedIndividual ;
    skos:prefLabel "SIMS boron depth profile"@en ;
    rep:has_depthprofile_representation ex:r_depthprofile ;
    rep:has_dsd                         _:dsd .

ex:r_depthprofile a rep:Representation , rep:DepthProfile , owl:NamedIndividual ;
    rep:rank   "1"^^xsd:nonNegativeInteger ;
    rep:extent "6"^^xsd:nonNegativeInteger ;
    qb:structure _:dsd .

_:dsd a rep:DataStructureDefinition ;
    rep:hasComponent rep:depth , rep:intensity ;
    qb:component
        [ qb:dimension rep:depth ;
          qb:order     "0"^^xsd:nonNegativeInteger ;
          rep:extent   "6"^^xsd:nonNegativeInteger ] ,
        [ qb:measure   rep:intensity ] .

_:d5 a rep:Observation ; qb:dataSet ex:r_depthprofile ;
    rep:index "5"^^xsd:nonNegativeInteger ;
    rep:depth "100.0"^^xsd:double ; rep:intensity "45.0"^^xsd:double .
```

---

## 5. Image — `abox_image.ttl`

**Shape** `(5, 5)` · **rank** 2 · **inferred** `rep:Image` · **axes** `rep:y` (0), `rep:x` (1)

DP780 dual-phase steel, EBSD orientation map. *Step size was 2 µm.*

| y \ x | 0 | 2 | 4 | 6 | 8 |
|---|---|---|---|---|---|
| **0** | 10 | 12 | 11 | 14 | 10 |
| **2** | 13 | 45 | 120 | 50 | 15 |
| **4** | 11 | 110 | **850** | 115 | 12 |
| **6** | 14 | 55 | 118 | 48 | 11 |
| **8** | 10 | 12 | 14 | 11 | 9 |

Flat index: `idx = j × Nx + i`

```turtle
ex:DP780       a tax:Material , owl:NamedIndividual ;
    skos:prefLabel "DP780 dual-phase steel"@en .

ex:DP780_EBSD  a tax:MaterialProperty , owl:NamedIndividual ;
    skos:prefLabel "EBSD orientation map"@en ;
    rep:has_image_representation ex:r_image ;
    rep:has_dsd                  _:dsd .

ex:r_image a rep:Representation , rep:Image , owl:NamedIndividual ;
    rep:rank        "2"^^xsd:nonNegativeInteger ;
    rep:extent      "25"^^xsd:nonNegativeInteger ;   ## 5 × 5
    rep:is_separable true ;
    qb:structure    _:dsd .

_:dsd a rep:DataStructureDefinition ;
    rep:hasComponent rep:y , rep:x , rep:intensity ;
    qb:component
        [ qb:dimension rep:y ;                       ## slow axis
          qb:order     "0"^^xsd:nonNegativeInteger ;
          rep:extent   "5"^^xsd:nonNegativeInteger ] ,
        [ qb:dimension rep:x ;                       ## fast axis
          qb:order     "1"^^xsd:nonNegativeInteger ;
          rep:extent   "5"^^xsd:nonNegativeInteger ] ,
        [ qb:measure   rep:intensity ] .

_:p22 a rep:Observation ; qb:dataSet ex:r_image ;
    rep:index "12"^^xsd:nonNegativeInteger ;         ## j=2, i=2 → 2×5+2
    rep:y "4.0"^^xsd:double ; rep:x "4.0"^^xsd:double ;
    rep:intensity "850.0"^^xsd:double .
```

Both axes carry `qk:Length`. `qb:order` is the only thing that tells `rep:y` from
`rep:x` — a query that filters on quantity kind alone gets them in arbitrary order.

---

## 6. VolumeData — `abox_volume.ttl`

**Shape** `(2, 2, 3)` · **rank** 3 · **inferred** `rep:VolumeData` · **axes** `rep:z` (0),
`rep:y` (1), `rep:x` (2)

Porous alumina foam, microCT reconstruction. *Voxel pitch was 2 µm.*

**z = 0**

| y \ x | 0 | 2 | 4 |
|---|---|---|---|
| **0** | 10 | 12 | 11 |
| **2** | 13 | 15 | 12 |

**z = 5**

| y \ x | 0 | 2 | 4 |
|---|---|---|---|
| **0** | 11 | 14 | 10 |
| **2** | 12 | **550** | 14 |

Flat index: `idx = k × Ny × Nx + j × Nx + i`

```turtle
ex:Al2O3foam     a tax:Material , owl:NamedIndividual ;
    skos:prefLabel "Porous alumina foam"@en .

ex:Al2O3foam_CT  a tax:MaterialProperty , owl:NamedIndividual ;
    skos:prefLabel "MicroCT reconstruction"@en ;
    rep:has_volume_representation ex:r_volume ;
    rep:has_dsd                   _:dsd .

ex:r_volume a rep:Representation , rep:VolumeData , owl:NamedIndividual ;
    rep:rank        "3"^^xsd:nonNegativeInteger ;
    rep:extent      "12"^^xsd:nonNegativeInteger ;   ## 2 × 2 × 3
    rep:is_separable true ;
    qb:structure    _:dsd .

_:dsd a rep:DataStructureDefinition ;
    rep:hasComponent rep:z , rep:y , rep:x , rep:intensity ;
    qb:component
        [ qb:dimension rep:z ;                       ## slowest
          qb:order     "0"^^xsd:nonNegativeInteger ;
          rep:extent   "2"^^xsd:nonNegativeInteger ] ,
        [ qb:dimension rep:y ;
          qb:order     "1"^^xsd:nonNegativeInteger ;
          rep:extent   "2"^^xsd:nonNegativeInteger ] ,
        [ qb:dimension rep:x ;                       ## fastest
          qb:order     "2"^^xsd:nonNegativeInteger ;
          rep:extent   "3"^^xsd:nonNegativeInteger ] ,
        [ qb:measure   rep:intensity ] .

_:v111 a rep:Observation ; qb:dataSet ex:r_volume ;
    rep:index "10"^^xsd:nonNegativeInteger ;         ## k=1,j=1,i=1 → 1×6+1×3+1
    rep:z "5.0"^^xsd:double ; rep:y "2.0"^^xsd:double ;
    rep:x "2.0"^^xsd:double ; rep:intensity "550.0"^^xsd:double .
```

---

## Authoring checklist

```
1. Pick the representation type and set rep:rank to match
       rank 0 -> Scalar          rank 2 -> Image
       rank 1 -> Profile         rank 3 -> VolumeData
       Spectrum / TimeSeries / DepthProfile also asserted at rank 1

2. Use the axis IRIs fixed for that type
       Scalar        none
       Spectrum      rep:energy
       TimeSeries    rep:time
       DepthProfile  rep:depth
       Image         rep:y , rep:x
       VolumeData    rep:z , rep:y , rep:x

3. Pick the signal
       counts       -> rep:intensity     (the usual case)
       temperature  -> rep:temperature
       anything else -> add a Signal to the TBox first;
                        never reuse an Axis IRI as a measure

4. Assign qb:order   0 = slowest ... n-1 = fastest

5. rep:extent goes on
       the Representation             total observations
       each axis ComponentSpec        that axis's length
       never on the Signal            it is product(axis extents)

6. Use the component IRIs as predicates on each observation

7. Do not write a unit anywhere
```

---

## Extent rules

| subject | meaning | stored? |
|---|---|---|
| `rep:Representation` | total observations = product of axis extents | always |
| `qb:ComponentSpecification` (axis) | that axis's array length | always |
| `rep:Signal` | always equals product(axis extents) | never — derivable |

---

## Flat index convention

`rep:index` is optional. Include it when the dataset must point back to a position in
the source array.

| rank | formula | worked example |
|---|---|---|
| 1 | `i` | index 3 → element 3 |
| 2 | `j × Nx + i` | (2,2) with Nx=5 → 12 |
| 3 | `k × Ny × Nx + j × Nx + i` | (1,1,1) with Ny=2, Nx=3 → 10 |

When all coordinates are materialised in RDF the coordinate tuple is the natural key,
and the index adds nothing.

---

## Extending the vocabulary

If the quantity you need has no canonical component, add the individual to the
canonical vocabulary block in the TBox:

```turtle
rep:pressure  a owl:NamedIndividual , rep:Signal ;
    rep:hasQuantityKind qk:Pressure ;
    rdfs:comment "Pressure signal."@en ;
    skos:prefLabel "pressure"@en .
```

Declare the quantity kind if it is not already present:

```turtle
qk:Pressure a owl:NamedIndividual , qudt:QuantityKind ;
    skos:prefLabel "Pressure"@en .
```

The new component is then available across the whole knowledge graph. The one
judgement call is Axis versus Signal: an Axis is an independent variable you scan
over, a Signal is what the detector reports.
