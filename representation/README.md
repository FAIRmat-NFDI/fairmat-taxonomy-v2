# FAIRmat Representation Module

`representation.ttl` · ontology IRI `http://fairmat-nfdi.eu/taxonomy/representation`

## 1. Brief

The representation module describes **how a material property's data is shaped**. Each taxonomy property is bound to one representation type:

- **Scalar, Vector or Tensor2** for a value without axes;
- **1Dmap, Spectrum or TimeSeries** for a mapping from one axis to a signal;
- **2Dmap or 3Dmap** for a mapping from two or three axes to a signal.

A representation has **one signal** and **any number of axes**. Signal and axes carry their **physical quantity kind** from QUDT 3.5.2. Axes are identified by an **index** and a **label**. The quantity kind of the taxonomy property itself is **inferred from its signal**.

The module has two layers:

| Layer | Content | Required |
|---|---|---|
| **Base** (asserted) | Representation types, signal and axis bindings, quantity kinds, axis labels | yes |
| **Derived** (qb) | RDF Data Cube Data Structure Definitions (DSDs), generated from the base layer | optional: for SPARQL, validation and qb interoperability |

The module defines no units.

## 2. Namespaces

| Prefix | Namespace | Role |
|---|---|---|
| `rep:` | `http://fairmat-nfdi.eu/taxonomy/representation#` | this module |
| `tax:` | `http://fairmat-nfdi.eu/taxonomy/` | FAIRmat taxonomy (`main.ttl`) |
| `qudt:` | `http://qudt.org/schema/qudt/` | QUDT schema (current, version-free) |
| `qk:` | `http://qudt.org/vocab/quantitykind/` | QUDT quantity kinds (v3.5.2) |
| `qb:` | `http://purl.org/linked-data/cube#` | W3C RDF Data Cube |
| `dsd:` | `http://fairmat-nfdi.eu/taxonomy/dsd#` | generated DSD nodes (derived layer only) |
| `owl:`, `rdfs:`, `rdf:`, `xsd:`, `skos:` | standard W3C namespaces | — |

## 3. Entity index

### Classes

| Class | Label | Superclasses | Description |
|---|---|---|---|
| `rep:1Dmap` | 1Dmap | `rep:Representation`, `qb:DataSet` | Generic mapping from one axis to a signal; repeated axis values are allowed (e.g. hysteresis). |
| `rep:2Dmap` | 2Dmap | `rep:Representation`, `qb:DataSet` | Mapping from two axes to a signal. |
| `rep:3Dmap` | 3Dmap | `rep:Representation`, `qb:DataSet` | Mapping from three axes to a signal. |
| `rep:Axis` | Axis | `rep:ComponentProperty`, `qb:DimensionProperty` | An independent coordinate of a representation. |
| `rep:AxisLabelTerm` | AxisLabelTerm | — | A reusable axis label (symbol). It carries no quantity kind: the meaning of an axis comes from its rep:HasQuantityKind; the label only names it. |
| `rep:ComponentProperty` | ComponentProperty | `rep:Representation`, `qb:ComponentProperty` | A component of a representation: either its signal or one of its axes. |
| `rep:DataStructureDefinition` | DataStructureDefinition | `rep:Representation`, `qb:DataStructureDefinition` | RDF Data Cube structure of a representation: its measure (signal) and dimension (axis) component specifications. |
| `rep:Observation` | Observation | `rep:Representation`, `qb:Observation` | A single data point of a representation's dataset (RDF Data Cube observation). |
| `rep:Representation` | Representation | — | Umbrella class for the representation module. |
| `rep:Scalar` | Scalar | `rep:Representation`, `qb:DataSet` | Rank-0 signal: a single value without axes. |
| `rep:Signal` | Signal | `rep:ComponentProperty`, `qb:MeasureProperty` | The dependent, measured component of a representation. |
| `rep:Spectrum` | Spectrum | `rep:1Dmap` | Canonical axis: Energy (may be expressed as frequency or angle). Suggested, not enforced. |
| `rep:Tensor2` | Tensor2 | `rep:Representation`, `qb:DataSet` | Rank-2 signal; component sizes given by rep:Shape. Indices are not axes. |
| `rep:TimeSeries` | TimeSeries | `rep:1Dmap` | 1Dmap whose axis is time (enforced). |
| `rep:Vector` | Vector | `rep:Representation`, `qb:DataSet` | Rank-1 signal; component count given by rep:Shape. Indices are not axes. |

### Object properties

| Property | Domain | Range | Characteristics | Description |
|---|---|---|---|---|
| `rep:AxisLabel` | `rep:Axis` | `rep:AxisLabelTerm` | functional | Case-specific label of an axis, chosen from the rep:AxisLabelTerm individuals (e.g. rep:Label_x, rep:Label_kx). New labels are added as new individuals. |
| `rep:HasAxis` | `rep:Representation` | `rep:Axis` | — | Links a representation to one of its axes (any number). |
| `rep:HasComponent` | `rep:DataStructureDefinition` | `rep:ComponentProperty` | **deprecated** | Deprecated: use rep:HasSignal / rep:HasAxis. |
| `rep:HasDataStructureDefinition` | `tax:MaterialProperty` | `rep:DataStructureDefinition` | functional, **deprecated** | Deprecated: use rep:HasRepresentation / qb:structure. |
| `rep:HasQuantityKind` | `rep:ComponentProperty` | `qudt:QuantityKind` | functional | Physical quantity kind of a signal or an axis. |
| `rep:HasRepresentation` | `tax:MaterialProperty` | `rep:Representation` | functional | Links a material property to its single representation. A taxonomy class may allow alternative representations through owl:unionOf; each instance has exactly one. |
| `rep:HasSignal` | `rep:Representation` | `rep:Signal` | functional | Links a representation to its single signal. |

### Datatype properties

| Property | Domain | Range | Characteristics | Description |
|---|---|---|---|---|
| `rep:AxisIndex` | `rep:Axis` | `xsd:positiveInteger` | functional | Position of the axis (1, 2, 3, ...). Distinct indices make distinct axes. |
| `rep:Extent` | — | `xsd:nonNegativeInteger` | functional | Dataset observation count, or coordinate-array length on a dataset-specific axis ComponentSpecification. |
| `rep:Rank` | `rep:Representation` | `xsd:nonNegativeInteger` | functional | Tensor rank of the signal values (0 scalar, 1 vector, 2 matrix). Left open for maps. |
| `rep:Shape` | `rep:Representation` | `xsd:string` | functional | Component sizes of a vector or tensor signal, e.g. "3" or "3,3". |

### Named individuals: axis labels (`rep:AxisLabelTerm`)

| Individual | Label | Alt. label | Description |
|---|---|---|---|
| `rep:Label_E` | E |  | Symbol E, e.g. electric field or energy; the axis quantity kind disambiguates. |
| `rep:Label_P` | P |  | Symbol P, e.g. pressure. |
| `rep:Label_kx` | kx |  | Reciprocal-space coordinate kx (e.g. electronic band structure, Fermi surface). |
| `rep:Label_ky` | ky |  | Reciprocal-space coordinate ky. |
| `rep:Label_kz` | kz |  | Reciprocal-space coordinate kz. |
| `rep:Label_rho` | rho | ρ | Symbol rho (ρ), e.g. density. |
| `rep:Label_x` | x |  | Spatial coordinate x. |
| `rep:Label_y` | y |  | Spatial coordinate y. |
| `rep:Label_z` | z |  | Spatial coordinate z. |

### Named individuals: quantity kinds (`qudt:QuantityKind`, QUDT v3.5.2)

| Individual | Taxonomy name (`skos:prefLabel`) | QUDT label (`rdfs:label`) |
|---|---|---|
| `qk:Compressibility` | Compressibility | Compressibility |
| `qk:Density` | Density | Density |
| `qk:Dimensionless` | Dimensionless | Dimensionless |
| `qk:DynamicViscosity` | DynamicViscosity | Dynamic Viscosity |
| `qk:ElectricField` | ElectricField | Electric Field |
| `qk:ElectricFieldStrength` | ElectricFieldStrength | Electric Field Strength |
| `qk:ElectricPolarization` | ElectricPolarization | Electric Polarization |
| `qk:ElectromagneticPermeability` | ElectromagneticPermeability | Permeability |
| `qk:Energy` | Energy | Energy |
| `qk:EnergyDensity` | EnergyDensity | Energy Density |
| `qk:EnergyDensityOfStates` | EnergyDensityOfStates | Energy Density of States |
| `qk:ForcePerArea` | ForcePerArea | Force per Area |
| `qk:Frequency` | Frequency | Frequency |
| `qk:Length` | Length | Length |
| `qk:MagneticFieldStrength` | MagneticFieldStrength | Magnetic Field Strength |
| `qk:Permittivity` | Permittivity | Permittivity |
| `qk:Pressure` | Pressure | Pressure |
| `qk:Stress` | Stress | Stress |
| `qk:StressIntensityFactor` | StressIntensityFactor | Stress Intensity Factor |
| `qk:Temperature` | Temperature | Temperature |
| `qk:Time` | Time | Time |
| `qk:Voltage` | Voltage | Voltage |
| `qk:Wavenumber` | Wavenumber | Wavenumber |

### External terms (declared, not redefined)

| Term | Type |
|---|---|
| `tax:MaterialProperty` | `owl:Class` |
| `qb:ComponentProperty` | `owl:Class` |
| `qb:ComponentSpecification` | `owl:Class` |
| `qb:DataSet` | `owl:Class` |
| `qb:DataStructureDefinition` | `owl:Class` |
| `qb:DimensionProperty` | `owl:Class` |
| `qb:MeasureProperty` | `owl:Class` |
| `qb:Observation` | `owl:Class` |
| `qb:component` | `owl:ObjectProperty` |
| `qb:dataSet` | `owl:ObjectProperty` |
| `qb:dimension` | `owl:ObjectProperty` |
| `qb:measure` | `owl:ObjectProperty` |
| `qb:order` | `owl:DatatypeProperty` |
| `qb:structure` | `owl:ObjectProperty` |
| `qudt:QuantityKind` | `owl:Class` |
| `qudt:hasQuantityKind` | `owl:ObjectProperty` |
| `skos:altLabel` | `owl:AnnotationProperty` |
| `skos:definition` | `owl:AnnotationProperty` |
| `skos:note` | `owl:AnnotationProperty` |
| `skos:prefLabel` | `owl:AnnotationProperty` |


## 4. Model overview

### 4.1 Core pattern

```
tax:<Property>
 │ ···► qudt:hasQuantityKind ···► qk:<signal kind>          (inferred)
 └─ rep:HasRepresentation ──► rep:<Type>                      (one per instance)
       ├─ rep:Shape "n" | "n,m"                               (Vector, Tensor2)
       ├─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:<kind>
       └─ rep:HasAxis   ──► [Axis]   ─ rep:AxisIndex i
                                     ─ rep:AxisLabel ──► rep:Label_<…>
                                     ─ rep:HasQuantityKind ──► qk:<kind>      × number of axes
```

### 4.2 Legend used in this document

```
──►   asserted   (written by hand, base layer)
┄┄►   derived    (generated qb layer, optional)
···►  inferred   (computed by an OWL reasoner, never stored)
[ ]   anonymous node (class expression; no named individual)
```

### 4.3 Representation types at a glance

| Type | Parent | Rank | Axes | Signal | Axis constraint |
|---|---|---:|---:|---|---|
| `rep:Scalar` | Representation | 0 | 0 | 1 | — |
| `rep:Vector` | Representation | 1 | 0 | 1 | — (`rep:Shape` gives size) |
| `rep:Tensor2` | Representation | 2 | 0 | 1 | — (`rep:Shape` gives sizes) |
| `rep:1Dmap` | Representation | open | 1 | 1 | any |
| `rep:Spectrum` | 1Dmap | open | 1 | 1 | Energy suggested (not enforced) |
| `rep:TimeSeries` | 1Dmap | open | 1 | 1 | Time (enforced) |
| `rep:2Dmap` | Representation | open | 2 | 1 | any |
| `rep:3Dmap` | Representation | open | 3 | 1 | any |

## 5. Details

Each subsection shows the **base** structure (asserted only), the structure **with derived** qb nodes, and the **RDF** binding a taxonomy class carries. Examples use real taxonomy properties.

### 5.1 Components: signal, axis, label, quantity kind

**Structure**
```
rep:ComponentProperty  ≡  rep:Signal ⊔ rep:Axis      (disjoint)
   rep:Signal ⊑ qb:MeasureProperty      ─ rep:HasQuantityKind ──► qudt:QuantityKind
   rep:Axis   ⊑ qb:DimensionProperty    ─ rep:HasQuantityKind ──► qudt:QuantityKind
                                        ─ rep:AxisIndex       ──► xsd:positiveInteger
                                        ─ rep:AxisLabel       ──► rep:AxisLabelTerm
                                                                    (rep:Label_x, …_kx, …_E, …)
```

- The **signal** is the dependent, measured value. There's exactly one per representation.
- An **axis** is an independent coordinate.
- Two axes are distinct when their `rep:AxisIndex` values differ, or when their `rep:AxisLabel` individuals differ (labels are `owl:AllDifferent`).
- A label carries **no** quantity kind: `rep:Label_E` serves both electric field and energy, and the axis quantity kind disambiguates.
- A new label is added as a new `rep:AxisLabelTerm` individual and included in the `owl:AllDifferent` list.

### 5.2 Scalar: example `tax:CorrosionPotential`

**Base**
```
tax:CorrosionPotential
 │ ···► qudt:hasQuantityKind ···► qk:Voltage
 └─ rep:HasRepresentation ──► rep:Scalar   [Rank 0, no axes]
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:Voltage
```

**With derived**
```
tax:CorrosionPotential
 │ ···► qudt:hasQuantityKind ···► qk:Voltage
 └─ rep:HasRepresentation ──► rep:Scalar
       ├─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:Voltage
       └┄ qb:structure ┄┄► dsd:CorrosionPotential
              └┄ qb:component ┄┄► dsd:CorrosionPotential_sig
                     └┄ qb:measure ┄┄► dsd:CorrosionPotential_m ┄┄ rep:HasQuantityKind ┄┄► qk:Voltage
```

**RDF**
```turtle
tax:CorrosionPotential rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Scalar
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Voltage ] ]
    ) ] ] .
```

### 5.3 Vector: example `tax:MagneticAnisotropyField`

**Base**
```
tax:MagneticAnisotropyField
 │ ···► qudt:hasQuantityKind ···► qk:MagneticFieldStrength
 └─ rep:HasRepresentation ──► rep:Vector   [Rank 1, Shape "3", no axes]
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:MagneticFieldStrength
```

**With derived**
```
tax:MagneticAnisotropyField
 │ ···► qudt:hasQuantityKind ···► qk:MagneticFieldStrength
 └─ rep:HasRepresentation ──► rep:Vector  [Shape "3"]
       ├─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:MagneticFieldStrength
       └┄ qb:structure ┄┄► dsd:MagneticAnisotropyField
              └┄ qb:component ┄┄► _sig ┄┄ qb:measure ┄┄► _m ┄┄► qk:MagneticFieldStrength
```

**RDF**
```turtle
tax:MagneticAnisotropyField rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Vector
        [ a owl:Restriction ; owl:onProperty rep:Shape ; owl:hasValue "3" ]
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:MagneticFieldStrength ] ]
    ) ] ] .
```
Vector indices are not axes: all components share the one signal quantity kind.

### 5.4 Tensor2: example `tax:ThermalConductivity`

**Base**
```
tax:ThermalConductivity
 │ ···► qudt:hasQuantityKind ···► qk:ThermalConductivity
 └─ rep:HasRepresentation ──► rep:Tensor2   [Rank 2, Shape "3,3", no axes]
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:ThermalConductivity
```

**With derived**
```
tax:ThermalConductivity
 │ ···► qudt:hasQuantityKind ···► qk:ThermalConductivity
 └─ rep:HasRepresentation ──► rep:Tensor2  [Shape "3,3"]
       ├─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:ThermalConductivity
       └┄ qb:structure ┄┄► dsd:ThermalConductivity
              └┄ qb:component ┄┄► _sig ┄┄ qb:measure ┄┄► _m ┄┄► qk:ThermalConductivity
```

**RDF**
```turtle
tax:ThermalConductivity rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Tensor2
        [ a owl:Restriction ; owl:onProperty rep:Shape ; owl:hasValue "3,3" ]
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:ThermalConductivity ] ]
    ) ] ] .
```
`qk:ThermalConductivity` exists in QUDT 3.5.2 but isn't declared in this module. Declare it in `main.ttl` together with the binding.

### 5.5 Alternative representations (Scalar or Tensor2): example `tax:Permittivity`

Permittivity has one IRI and one label. Each instance uses exactly one of the alternatives.

**Base**
```
tax:Permittivity   "Permittivity"
 │ ···► qudt:hasQuantityKind ···► qk:Permittivity
 └─ rep:HasRepresentation ──► one of:
       ├─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:Permittivity     (shared)
       └─ ⊔ ┬─ rep:Scalar                       (isotropic)
            └─ rep:Tensor2 [Shape "3,3"]        (anisotropic)
```

**With derived**
```
tax:Permittivity
 └─ rep:HasRepresentation ──► one of:
       ├─ rep:Scalar
       │     └┄ qb:structure ┄┄► dsd:Permittivity_Scalar  ┄┄ _sig ┄┄ _m ┄┄► qk:Permittivity
       └─ rep:Tensor2 [Shape "3,3"]
             └┄ qb:structure ┄┄► dsd:Permittivity_Tensor2 ┄┄ _sig ┄┄ _m ┄┄► qk:Permittivity
```

**RDF**
```turtle
tax:Permittivity rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Permittivity ] ]
        [ a owl:Class ; owl:unionOf (
            rep:Scalar
            [ a owl:Class ; owl:intersectionOf ( rep:Tensor2
                [ a owl:Restriction ; owl:onProperty rep:Shape ; owl:hasValue "3,3" ] ) ] ) ]
    ) ] ] .
```
Write the alternatives as **one** union, never as two separate `rep:HasRepresentation` restrictions. Two restrictions mean *both*, which makes the class unsatisfiable (see §7.5).

### 5.6 1Dmap: example `tax:ElectricHysteresis`

**Base**
```
tax:ElectricHysteresis
 │ ···► qudt:hasQuantityKind ···► qk:ElectricPolarization
 └─ rep:HasRepresentation ──► rep:1Dmap   [exactly 1 axis]
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_E, HasQuantityKind ──► qk:ElectricField
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:ElectricPolarization
```

**With derived**
```
tax:ElectricHysteresis
 │ ···► qudt:hasQuantityKind ···► qk:ElectricPolarization
 └─ rep:HasRepresentation ──► rep:1Dmap
       ├─ rep:HasAxis   ──► [Axis] ─ 1, rep:Label_E, qk:ElectricField
       ├─ rep:HasSignal ──► [Signal] ─ qk:ElectricPolarization
       └┄ qb:structure ┄┄► dsd:ElectricHysteresis
              ├┄ qb:component ┄┄► _c1 [qb:order 1] ┄┄ qb:dimension ┄┄► _d1 (Axis, Label_E) ┄┄► qk:ElectricField
              └┄ qb:component ┄┄► _sig ┄┄ qb:measure ┄┄► _m (Signal) ┄┄► qk:ElectricPolarization
```

**RDF**
```turtle
tax:ElectricHysteresis rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:1Dmap
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:ElectricPolarization ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_E ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:ElectricField ] ) ] ]
    ) ] ] .
```
A 1Dmap allows repeated axis values (a hysteresis loop visits the same E twice).

### 5.7 Spectrum: example `tax:ElectronicDensityOfStates`

**Base**
```
tax:ElectronicDensityOfStates
 │ ···► qudt:hasQuantityKind ···► qk:EnergyDensityOfStates
 └─ rep:HasRepresentation ──► rep:Spectrum ⊑ rep:1Dmap
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_E, HasQuantityKind ──► qk:Energy
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:EnergyDensityOfStates
```

**With derived**
```
tax:ElectronicDensityOfStates
 └─ rep:HasRepresentation ──► rep:Spectrum
       ├─ rep:HasAxis   ──► [Axis] ─ 1, rep:Label_E, qk:Energy
       ├─ rep:HasSignal ──► [Signal] ─ qk:EnergyDensityOfStates
       └┄ qb:structure ┄┄► dsd:ElectronicDensityOfStates
              ├┄ qb:component ┄┄► _c1 [qb:order 1] ┄┄ qb:dimension ┄┄► _d1 ┄┄► qk:Energy
              └┄ qb:component ┄┄► _sig ┄┄ qb:measure ┄┄► _m ┄┄► qk:EnergyDensityOfStates
```

**RDF**
```turtle
tax:ElectronicDensityOfStates rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Spectrum
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:EnergyDensityOfStates ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_E ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Energy ] ) ] ]
    ) ] ] .
```
The Energy axis of a Spectrum is a suggestion. A Spectrum with a Frequency or angle axis is still valid.

### 5.8 TimeSeries: example `tax:MeanSquaredDisplacement`

**Base**
```
tax:MeanSquaredDisplacement
 │ ···► qudt:hasQuantityKind ···► qk:Area
 └─ rep:HasRepresentation ──► rep:TimeSeries ⊑ rep:1Dmap
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, HasQuantityKind ──► qk:Time   (enforced)
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:Area
```

**With derived**
```
tax:MeanSquaredDisplacement
 └─ rep:HasRepresentation ──► rep:TimeSeries
       ├─ rep:HasAxis   ──► [Axis] ─ 1, qk:Time
       ├─ rep:HasSignal ──► [Signal] ─ qk:Area
       └┄ qb:structure ┄┄► dsd:MeanSquaredDisplacement
              ├┄ qb:component ┄┄► _c1 [qb:order 1] ┄┄ qb:dimension ┄┄► _d1 ┄┄► qk:Time
              └┄ qb:component ┄┄► _sig ┄┄ qb:measure ┄┄► _m ┄┄► qk:Area
```

**RDF**
```turtle
tax:MeanSquaredDisplacement rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:TimeSeries
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Area ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Time ] ) ] ]
    ) ] ] .
```
- **The axis label is optional.** None is given here because no time label individual exists yet.
- **Write `qk:Time` explicitly** even though `rep:TimeSeries` implies it, so that the derived-layer generator (which reads only asserted triples) sees it.
- `qk:Area` exists in QUDT 3.5.2; declare it in `main.ttl` together with the binding.

### 5.9 2Dmap: example `tax:Morphology` (height map)

**Base**
```
tax:Morphology
 │ ···► qudt:hasQuantityKind ···► qk:Length
 └─ rep:HasRepresentation ──► rep:2Dmap   [exactly 2 axes]
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_x, HasQuantityKind ──► qk:Length
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 2, AxisLabel rep:Label_y, HasQuantityKind ──► qk:Length
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:Length
```

**With derived**
```
tax:Morphology
 └─ rep:HasRepresentation ──► rep:2Dmap
       ├─ rep:HasAxis   ──► [Axis] ─ 1, rep:Label_x, qk:Length
       ├─ rep:HasAxis   ──► [Axis] ─ 2, rep:Label_y, qk:Length
       ├─ rep:HasSignal ──► [Signal] ─ qk:Length
       └┄ qb:structure ┄┄► dsd:Morphology
              ├┄ qb:component ┄┄► _c1 [qb:order 1] ┄┄ qb:dimension ┄┄► _d1 (Label_x) ┄┄► qk:Length
              ├┄ qb:component ┄┄► _c2 [qb:order 2] ┄┄ qb:dimension ┄┄► _d2 (Label_y) ┄┄► qk:Length
              └┄ qb:component ┄┄► _sig ┄┄ qb:measure ┄┄► _m ┄┄► qk:Length
```

**RDF**
```turtle
tax:Morphology rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:2Dmap
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Length ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_x ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Length ] ) ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "2"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_y ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Length ] ) ] ]
    ) ] ] .
```
Both axes have the quantity kind Length. They stay two axes because their index and label differ.

### 5.10 3Dmap: example `tax:FermiSurface` (reciprocal space)

**Base**
```
tax:FermiSurface
 │ ···► qudt:hasQuantityKind ···► qk:Energy
 └─ rep:HasRepresentation ──► rep:3Dmap   [exactly 3 axes]
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_kx, HasQuantityKind ──► qk:Wavenumber
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 2, AxisLabel rep:Label_ky, HasQuantityKind ──► qk:Wavenumber
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 3, AxisLabel rep:Label_kz, HasQuantityKind ──► qk:Wavenumber
       └─ rep:HasSignal ──► [Signal] ─ rep:HasQuantityKind ──► qk:Energy
```

**With derived**
```
tax:FermiSurface
 └─ rep:HasRepresentation ──► rep:3Dmap
       ├─ rep:HasAxis × 3 ──► [Axis] ─ 1/2/3, Label_kx/ky/kz, qk:Wavenumber
       ├─ rep:HasSignal   ──► [Signal] ─ qk:Energy
       └┄ qb:structure ┄┄► dsd:FermiSurface
              ├┄ qb:component ┄┄► _c1 [order 1] ┄┄ qb:dimension ┄┄► _d1 (Label_kx) ┄┄► qk:Wavenumber
              ├┄ qb:component ┄┄► _c2 [order 2] ┄┄ qb:dimension ┄┄► _d2 (Label_ky) ┄┄► qk:Wavenumber
              ├┄ qb:component ┄┄► _c3 [order 3] ┄┄ qb:dimension ┄┄► _d3 (Label_kz) ┄┄► qk:Wavenumber
              └┄ qb:component ┄┄► _sig ┄┄ qb:measure ┄┄► _m ┄┄► qk:Energy
```

**RDF**
```turtle
tax:FermiSurface rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:3Dmap
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Energy ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_kx ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Wavenumber ] ) ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "2"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_ky ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Wavenumber ] ) ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "3"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_kz ]
            [ a owl:Restriction ; owl:onProperty rep:HasQuantityKind ; owl:hasValue qk:Wavenumber ] ) ] ]
    ) ] ] .
```

## 6. Derived layer (optional)

The derived layer translates each base binding into an RDF Data Cube DSD with named nodes. It adds no new information, but it gives flat triples for SPARQL, qb-style validation, and a structure that future datasets can reference with `qb:structure`. All its nodes live in `dsd:`. They're never edited by hand; change the base binding and regenerate instead.

### 6.1 Naming convention

| Node | IRI | Type |
|---|---|---|
| DSD | `dsd:<Property>` | `rep:DataStructureDefinition` |
| Signal component specification | `dsd:<Property>_sig` | `qb:ComponentSpecification` |
| Measure property | `dsd:<Property>_m` | `rep:Signal` |
| Axis component specification *i* | `dsd:<Property>_c<i>` | `qb:ComponentSpecification` (`qb:order i`) |
| Dimension property *i* | `dsd:<Property>_d<i>` | `rep:Axis` |
| Alternative (union) | `dsd:<Property>_<Type>` | one DSD per alternative |

### 6.2 RDF example (derived, `tax:Morphology`)
```turtle
tax:Morphology rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Restriction ; owl:onProperty qb:structure ; owl:hasValue dsd:Morphology ] ] .

dsd:Morphology a owl:NamedIndividual, rep:DataStructureDefinition ;
    qb:component dsd:Morphology_c1, dsd:Morphology_c2, dsd:Morphology_sig .
dsd:Morphology_c1 a owl:NamedIndividual, qb:ComponentSpecification ; qb:order 1 ; qb:dimension dsd:Morphology_d1 .
dsd:Morphology_c2 a owl:NamedIndividual, qb:ComponentSpecification ; qb:order 2 ; qb:dimension dsd:Morphology_d2 .
dsd:Morphology_d1 a owl:NamedIndividual, owl:DatatypeProperty, rep:Axis ;
    rep:AxisIndex "1"^^xsd:positiveInteger ; rep:AxisLabel rep:Label_x ; rep:HasQuantityKind qk:Length .
dsd:Morphology_d2 a owl:NamedIndividual, owl:DatatypeProperty, rep:Axis ;
    rep:AxisIndex "2"^^xsd:positiveInteger ; rep:AxisLabel rep:Label_y ; rep:HasQuantityKind qk:Length .
dsd:Morphology_sig a owl:NamedIndividual, qb:ComponentSpecification ; qb:measure dsd:Morphology_m .
dsd:Morphology_m a owl:NamedIndividual, owl:DatatypeProperty, rep:Signal ; rep:HasQuantityKind qk:Length .
[ a owl:AllDifferent ; owl:distinctMembers ( dsd:Morphology_c1 dsd:Morphology_c2 dsd:Morphology_sig ) ] .
```
Because `rep:HasRepresentation` is functional, the derived `qb:structure` axiom and the base binding describe the same representation.

### 6.3 Generation

The derived layer is produced by two SPARQL CONSTRUCT queries over the base layer: Gen-1 for the signal and DSD, and Gen-2 for each axis. They can run as a script (Apache Jena `arq`, rdflib) or as SHACL-AF `sh:SPARQLRule`s. The `owl:AllDifferent` list for the component specifications has a variable length, so it needs a small post-processing step.

## 7. Axioms and rules

### 7.1 Per entity

**`rep:HasRepresentation`**
- Functional: a material property has at most one representation.
- Domain `tax:MaterialProperty`; range `rep:Representation`.

**`rep:HasSignal`**
- Functional: at most one signal.
- Domain `rep:Representation`; range `rep:Signal`.

**`rep:HasAxis`**
- Domain `rep:Representation`; range `rep:Axis`. No upper limit; the types set the count.

**`rep:HasQuantityKind`**
- Functional: one quantity kind per signal or axis.
- Domain `rep:ComponentProperty`; range `qudt:QuantityKind`.

**`rep:AxisIndex`**
- Functional; domain `rep:Axis`; range `xsd:positiveInteger`. Different indices imply different axes.

**`rep:AxisLabel`**
- Functional; domain `rep:Axis`; range `rep:AxisLabelTerm`. Different labels imply different axes (through `owl:AllDifferent`).

**`rep:Rank`, `rep:Shape`**
- Both functional; domain `rep:Representation`.
- Ranges `xsd:nonNegativeInteger` and `xsd:string`.

**`qudt:hasQuantityKind`** (bridge)
- Property chain: `rep:HasRepresentation ∘ rep:HasSignal ∘ rep:HasQuantityKind`. The property's quantity kind is its signal's quantity kind.

**`rep:ComponentProperty`, `rep:Signal`, `rep:Axis`**
- `rep:ComponentProperty` is the disjoint union of `rep:Signal` and `rep:Axis`.
- `rep:Signal ⊑ qb:MeasureProperty`; `rep:Axis ⊑ qb:DimensionProperty`.

**`rep:Scalar`, `rep:Vector`, `rep:Tensor2`**
- Rank 0, 1 or 2 respectively; at least one signal; no axis.
- In the derived layer, their DSD has measure components only.

**`rep:1Dmap`, `rep:2Dmap`, `rep:3Dmap`**
- At least one signal; exactly 1, 2 or 3 axes.
- In the derived layer, their DSD has at most 1, 2 or 3 dimension components.

**`rep:Spectrum`**
- Subclass of `rep:1Dmap`; no extra axiom (the Energy axis is a note only).

**`rep:TimeSeries`**
- Subclass of `rep:1Dmap`; every axis has quantity kind `qk:Time`.
- In the derived layer, every DSD dimension has quantity kind `qk:Time`.

**`rep:DataStructureDefinition`**
- Every `qb:dimension` of its components is a `rep:Axis`, and every `qb:measure` is a `rep:Signal`.
- Each component specification has at most one dimension.

**Axis labels**
- `rep:Label_x … rep:Label_rho` are pairwise different (`owl:AllDifferent`).

### 7.2 Summary table

| Axiom | Applies to | Effect | Layer |
|---|---|---|---|
| functional | `rep:HasRepresentation` | one representation per property instance | base |
| domain / range | `rep:HasRepresentation` | links taxonomy to module | base |
| functional | `rep:HasSignal` | one signal | base |
| domain / range | `rep:HasSignal`, `rep:HasAxis` | type signal and axis nodes | base |
| functional | `rep:HasQuantityKind` | one quantity kind per component | base |
| domain / range | `rep:HasQuantityKind` | quantity kinds are `qudt:QuantityKind` | base |
| functional | `rep:AxisIndex`, `rep:AxisLabel` | distinct index or label means distinct axis | base |
| `owl:AllDifferent` | axis labels | labels never merge | base |
| disjoint union | `rep:ComponentProperty` = Signal ⊔ Axis | a signal is never an axis | base |
| property chain | `qudt:hasQuantityKind` | property quantity kind = signal quantity kind | base |
| Rank = 0 / 1 / 2 | Scalar / Vector / Tensor2 | fixes signal rank | base |
| ≥1 HasSignal | all types | every representation has a signal | base |
| ≤0 HasAxis | Scalar, Vector, Tensor2 | no axes | base |
| =1 / =2 / =3 HasAxis | 1Dmap / 2Dmap / 3Dmap | exact axis count | base |
| ∀ HasAxis.(HasQuantityKind ∋ Time) | TimeSeries | time axis enforced | base |
| subclass | Spectrum, TimeSeries ⊑ 1Dmap | inherit 1 axis | base |
| ∀ component.(∀ dimension.Axis ⊓ ∀ measure.Signal) | DSD | strict qb roles | derived |
| ∀ component.≤1 dimension | DSD | one dimension per specification | derived |
| measure only, no dimension | Scalar, Vector, Tensor2 | axis-free DSD | derived |
| ≤1 / ≤2 / ≤3 dimension components | 1Dmap / 2Dmap / 3Dmap | DSD axis limit | derived |
| every dimension is Time | TimeSeries | time axis in DSD | derived |

### 7.3 Description Logic notation

**Properties**
```
⊤ ⊑ ≤1 HasRepresentation              ∃HasRepresentation.⊤ ⊑ tax:MaterialProperty      ⊤ ⊑ ∀HasRepresentation.Representation
⊤ ⊑ ≤1 HasSignal                      ∃HasSignal.⊤ ⊑ Representation                  ⊤ ⊑ ∀HasSignal.Signal
                                      ∃HasAxis.⊤ ⊑ Representation                    ⊤ ⊑ ∀HasAxis.Axis
⊤ ⊑ ≤1 HasQuantityKind                ∃HasQuantityKind.⊤ ⊑ ComponentProperty         ⊤ ⊑ ∀HasQuantityKind.qudt:QuantityKind
⊤ ⊑ ≤1 AxisIndex                      ∃AxisIndex.⊤ ⊑ Axis                            ⊤ ⊑ ∀AxisIndex.xsd:positiveInteger
⊤ ⊑ ≤1 AxisLabel                      ∃AxisLabel.⊤ ⊑ Axis                            ⊤ ⊑ ∀AxisLabel.AxisLabelTerm
⊤ ⊑ ≤1 Rank                           ∃Rank.⊤ ⊑ Representation                       ⊤ ⊑ ∀Rank.xsd:nonNegativeInteger
⊤ ⊑ ≤1 Shape                          ∃Shape.⊤ ⊑ Representation                      ⊤ ⊑ ∀Shape.xsd:string

HasRepresentation ∘ HasSignal ∘ HasQuantityKind ⊑ qudt:hasQuantityKind
```

**Components and labels**
```
ComponentProperty ⊑ Representation ⊓ qb:ComponentProperty
ComponentProperty ≡ Signal ⊔ Axis          Signal ⊓ Axis ⊑ ⊥
Signal ⊑ qb:MeasureProperty                Axis ⊑ qb:DimensionProperty
Label_x ≠ Label_y ≠ Label_z ≠ Label_kx ≠ Label_ky ≠ Label_kz ≠ Label_E ≠ Label_P ≠ Label_rho   (pairwise)
```

**Representation types (base)**
```
Scalar     ⊑ Representation ⊓ qb:DataSet ⊓ ∃Rank.{0} ⊓ ∃HasSignal.Signal ⊓ ≤0 HasAxis
Vector     ⊑ Representation ⊓ qb:DataSet ⊓ ∃Rank.{1} ⊓ ∃HasSignal.Signal ⊓ ≤0 HasAxis
Tensor2    ⊑ Representation ⊓ qb:DataSet ⊓ ∃Rank.{2} ⊓ ∃HasSignal.Signal ⊓ ≤0 HasAxis
1Dmap      ⊑ Representation ⊓ qb:DataSet ⊓ ∃HasSignal.Signal ⊓ =1 HasAxis
Spectrum   ⊑ 1Dmap
TimeSeries ⊑ 1Dmap ⊓ ∀HasAxis.∃HasQuantityKind.{qk:Time}
2Dmap      ⊑ Representation ⊓ qb:DataSet ⊓ ∃HasSignal.Signal ⊓ =2 HasAxis
3Dmap      ⊑ Representation ⊓ qb:DataSet ⊓ ∃HasSignal.Signal ⊓ =3 HasAxis
```

**Derived layer (DSD)**
```
DataStructureDefinition ⊑ Representation ⊓ qb:DataStructureDefinition
DataStructureDefinition ⊑ ∀qb:component.(∀qb:dimension.Axis ⊓ ∀qb:measure.Signal)
DataStructureDefinition ⊑ ∀qb:component.≤1 qb:dimension
Observation ⊑ Representation ⊓ qb:Observation
Scalar ⊔ Vector ⊔ Tensor2 ⊑ ∀qb:structure.∀qb:component.(∃qb:measure.⊤ ⊓ ¬∃qb:dimension.⊤)
1Dmap ⊑ ∀qb:structure.≤1 qb:component.(∃qb:dimension.⊤)
2Dmap ⊑ ∀qb:structure.≤2 qb:component.(∃qb:dimension.⊤)
3Dmap ⊑ ∀qb:structure.≤3 qb:component.(∃qb:dimension.⊤)
TimeSeries ⊑ ∀qb:structure.∀qb:component.∀qb:dimension.∃HasQuantityKind.{qk:Time}
```

**Taxonomy binding pattern**
```
C ⊑ ∃HasRepresentation.( T
        ⊓ ∃Shape.{s}                                                    (Vector, Tensor2)
        ⊓ ∃HasSignal.∃HasQuantityKind.{q}
        ⊓ ∃HasAxis.(∃AxisIndex.{i} ⊓ ∃AxisLabel.{ℓ} ⊓ ∃HasQuantityKind.{k})   × number of axes )

Alternatives:   C ⊑ ∃HasRepresentation.( ∃HasSignal.∃HasQuantityKind.{q} ⊓ (T₁ ⊔ T₂ ⊔ …) )
```

### 7.4 Consequences the reasoner derives

| Consequence | Reason |
|---|---|
| Scalar, Vector and Tensor2 are pairwise disjoint | functional `rep:Rank` with different values |
| Scalar, Vector and Tensor2 are disjoint from every map type | ≤0 axes vs ≥1 axis |
| 1Dmap, 2Dmap and 3Dmap are pairwise disjoint | different exact axis counts |
| `tax:C qudt:hasQuantityKind q` for every bound property | property chain on `qudt:hasQuantityKind` |
| Two axes with different index or label are distinct | functional `AxisIndex` / `AxisLabel` + `AllDifferent` |

### 7.5 Rules and conventions

**Modelling errors that the reasoner catches** (the class becomes unsatisfiable):

| Error | Violated axiom |
|---|---|
| TimeSeries with a non-time axis | TimeSeries axis must have quantity kind `qk:Time` |
| Scalar, Vector or Tensor2 with an axis | Scalar, Vector and Tensor2 allow no axis |
| 1Dmap, 2Dmap or 3Dmap with the wrong number of axes | exact axis count per map type, with axes kept distinct by index or label |
| Two separate `HasRepresentation` restrictions with different types | `rep:HasRepresentation` is functional and the representation types are disjoint (§7.4) |
| An axis used as a signal, or a signal as an axis (derived layer) | Signal and Axis are disjoint; DSD dimensions must be axes and measures must be signals |

**Authoring conventions** (not enforced by OWL):
1. **Bind leaf classes only.** Restrictions inherit, so a binding on a parent class forces every subclass.
2. **Give every axis an `rep:AxisIndex`** (1, 2, 3, …). The label is optional.
3. **Write implied quantity kinds explicitly** (for example `qk:Time` on a TimeSeries axis), so tools that read asserted triples see them.
4. **Write alternatives as one `owl:unionOf`,** never as two separate restrictions.
5. **New labels:** add a `rep:AxisLabelTerm` individual and include it in the `owl:AllDifferent` list.
6. **New quantity kinds:** use the version-free QUDT IRI (`qk:<Name>`), check that it exists in QUDT 3.5.2, and declare it as `owl:NamedIndividual, qudt:QuantityKind`.
7. **Derived layer:** never edit `dsd:` nodes by hand; regenerate them from the base layer.
8. **`qudt:hasQuantityKind` must not get cardinality or functional axioms.** The property chain makes it non-simple in OWL 2 DL.

