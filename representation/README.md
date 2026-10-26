# FAIRmat Representation Module

`representation.ttl` · ontology IRI `http://fairmat-nfdi.eu/taxonomy/representation`

## 1. Brief

The representation module describes **how a material property's data is shaped**. Each taxonomy property is bound to one representation type:

- **Scalar, Vector or Tensor2** for a value without axes;
- **1Dmap, Spectrum or TimeSeries** for a mapping from one axis to a signal;
- **2Dmap or 3Dmap** for a mapping from two or three axes to a signal.

A representation has **one signal** and **any number of axes**. Signal and axes carry their **physical quantity kind** from QUDT 3.5.2. Axes are identified by an **index** and a **label**. Signal, axes and the taxonomy property itself also get **`qudt:hasQuantityKind`**: signal and axes directly (sub-property), the taxonomy property from its signal and all its axes (property chain).

The module defines no units and doesn't depend on the RDF Data Cube (qb) vocabulary. The bindings of 137 taxonomy properties live in `main.ttl` (see §9).

## 2. Namespaces

| Prefix | Namespace | Role |
|---|---|---|
| `rep:` | `http://fairmat-nfdi.eu/taxonomy/representation#` | this module |
| `tax:` | `http://fairmat-nfdi.eu/taxonomy/` | FAIRmat taxonomy (`main.ttl`) |
| `qudt:` | `http://qudt.org/schema/qudt/` | QUDT schema (current, version-free) |
| `qk:` | `http://qudt.org/vocab/quantitykind/` | QUDT quantity kinds (v3.5.2) |
| `qkdv:` | `http://qudt.org/vocab/dimensionvector/` | QUDT dimension vectors (v3.5.2) |
| `fqk:` | `http://fairmat-nfdi.eu/taxonomy/quantitykind/` | local FAIRmat quantity kinds (not in QUDT) |
| `owl:`, `rdfs:`, `rdf:`, `xsd:`, `skos:` | standard W3C namespaces | — |

## 3. Entity index

### Classes

| Class | Label | Superclasses | Description |
|---|---|---|---|
| `rep:1Dmap` | 1Dmap | `rep:Representation` | Generic mapping from one axis to a signal; repeated axis values are allowed (e.g. hysteresis). |
| `rep:2Dmap` | 2Dmap | `rep:Representation` | Mapping from two axes to a signal. |
| `rep:3Dmap` | 3Dmap | `rep:Representation` | Mapping from three axes to a signal. |
| `rep:Axis` | Axis | `rep:ComponentProperty` | An independent coordinate of a representation. |
| `rep:AxisLabelTerm` | AxisLabelTerm | — | A reusable axis label (symbol). It carries no quantity kind: the meaning of an axis comes from its rep:HasComponentQuantityKind; the label only names it. |
| `rep:ComponentProperty` | ComponentProperty | `rep:Representation` | A component of a representation: either its signal or one of its axes. |
| `rep:Representation` | Representation | — | Umbrella class for the representation module. |
| `rep:Scalar` | Scalar | `rep:Representation` | Rank-0 signal: a single value without axes. |
| `rep:Signal` | Signal | `rep:ComponentProperty` | The dependent, measured component of a representation. |
| `rep:Spectrum` | Spectrum | `rep:1Dmap` | Canonical axis: Energy (may be expressed as frequency or angle). Suggested, not enforced. |
| `rep:Tensor2` | Tensor2 | `rep:Representation` | Rank-2 signal; component sizes given by rep:Shape. Indices are not axes. |
| `rep:TimeSeries` | TimeSeries | `rep:1Dmap` | 1Dmap whose axis is time (enforced). |
| `rep:Vector` | Vector | `rep:Representation` | Rank-1 signal; component count given by rep:Shape. Indices are not axes. |

### Object properties

| Property | Domain | Range | Characteristics | Description |
|---|---|---|---|---|
| `rep:AxisLabel` | `rep:Axis` | `rep:AxisLabelTerm` | functional | Case-specific label of an axis, chosen from the rep:AxisLabelTerm individuals (e.g. rep:Label_x, rep:Label_kx). New labels are added as new individuals. |
| `rep:HasAxis` | `rep:Representation` | `rep:Axis` | — | Links a representation to one of its axes (any number). |
| `rep:HasComponent` | `rep:Representation` | `rep:ComponentProperty` | — | Links a representation to any of its components: its signal or one of its axes. Super-property of rep:HasSignal and rep:HasAxis; not used directly in bindings. |
| `rep:HasComponentQuantityKind` | `rep:ComponentProperty` | `qudt:QuantityKind` | functional | Physical quantity kind of a signal or an axis (exactly one). Sub-property of qudt:hasQuantityKind, so the signal or axis also has it as its QUDT quantity kind. |
| `rep:HasRepresentation` | `tax:MaterialProperty` | `rep:Representation` | functional | Links a material property to its single representation. A taxonomy class may allow alternative representations through owl:unionOf; each instance has exactly one. |
| `rep:HasSignal` | `rep:Representation` | `rep:Signal` | functional | Links a representation to its single signal. |

### Datatype properties

| Property | Domain | Range | Characteristics | Description |
|---|---|---|---|---|
| `rep:AxisIndex` | `rep:Axis` | `xsd:positiveInteger` | functional | Position of the axis (1, 2, 3, ...). Distinct indices make distinct axes. |
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

### Named individuals: quantity kinds (`qudt:QuantityKind`; QUDT v3.5.2, plus local `fqk:` kinds)

| Individual | Taxonomy name (`skos:prefLabel`) | QUDT label (`rdfs:label`) |
|---|---|---|
| `fqk:CryoscopicConstant` | CryoscopicConstant | Cryoscopic Constant |
| `qk:Angle` | Angle | Angle |
| `qk:Area` | Area | Area |
| `qk:ChemicalPotential` | ChemicalPotential | Chemical Potential |
| `qk:Compressibility` | Compressibility | Compressibility |
| `qk:Density` | Density | Density |
| `qk:Dimensionless` | Dimensionless | Dimensionless |
| `qk:DynamicViscosity` | DynamicViscosity | Dynamic Viscosity |
| `qk:ElectricCharge` | ElectricCharge | Electric Charge |
| `qk:ElectricCurrent` | ElectricCurrent | Electric Current |
| `qk:ElectricField` | ElectricField | Electric Field |
| `qk:ElectricFieldStrength` | ElectricFieldStrength | Electric Field Strength |
| `qk:ElectricPolarization` | ElectricPolarization | Electric Polarization |
| `qk:ElectricPotential` | ElectricPotential | Electric Potential |
| `qk:ElectromagneticPermeability` | ElectromagneticPermeability | Permeability |
| `qk:Energy` | Energy | Energy |
| `qk:EnergyDensity` | EnergyDensity | Energy Density |
| `qk:EnergyDensityOfStates` | EnergyDensityOfStates | Energy Density of States |
| `qk:EnergyPerTemperature` | EnergyPerTemperature | Energy per Temperature |
| `qk:ForcePerArea` | ForcePerArea | Force per Area |
| `qk:Frequency` | Frequency | Frequency |
| `qk:InverseLength` | InverseLength | Inverse Length |
| `qk:InverseTemperature` | InverseTemperature | Inverse Temperature |
| `qk:Length` | Length | Length |
| `qk:LinearVelocity` | LinearVelocity | Linear Velocity |
| `qk:MagneticFieldStrength` | MagneticFieldStrength | Magnetic Field Strength |
| `qk:Mass` | Mass | Mass |
| `qk:MolalityOfSolute` | MolalityOfSolute | Molality of Solute |
| `qk:MolarEnergy` | MolarEnergy | Molar Energy |
| `qk:NumberDensity` | NumberDensity | Number Density |
| `qk:Permittivity` | Permittivity | Permittivity |
| `qk:Pressure` | Pressure | Pressure |
| `qk:SpecificEnergy` | SpecificEnergy | Specific Energy |
| `qk:SpecificHeatCapacity` | SpecificHeatCapacity | Specific Heat Capacity |
| `qk:Stress` | Stress | Stress |
| `qk:StressIntensityFactor` | StressIntensityFactor | Stress Intensity Factor |
| `qk:Temperature` | Temperature | Temperature |
| `qk:ThermodynamicTemperature` | ThermodynamicTemperature | Thermodynamic Temperature |
| `qk:Time` | Time | Time |
| `qk:Voltage` | Voltage | Voltage |
| `qk:Volume` | Volume | Volume |
| `qk:Wavenumber` | Wavenumber | Wavenumber |

### External terms (declared, not redefined)

| Term | Type |
|---|---|
| `tax:MaterialProperty` | `owl:Class` |
| `qudt:QuantityKind` | `owl:Class` |
| `qudt:QuantityKindDimensionVector` | `owl:Class` |
| `qudt:hasDimensionVector` | `owl:ObjectProperty` |
| `qudt:hasQuantityKind` | `owl:ObjectProperty` |
| `qudt:latexDefinition` | `owl:DatatypeProperty` |
| `qudt:qkdvDenominator` | `owl:ObjectProperty` |
| `qudt:qkdvNumerator` | `owl:ObjectProperty` |
| `skos:altLabel` | `owl:AnnotationProperty` |
| `skos:definition` | `owl:AnnotationProperty` |
| `skos:note` | `owl:AnnotationProperty` |
| `skos:prefLabel` | `owl:AnnotationProperty` |
| `skos:related` | `owl:AnnotationProperty` |

## 4. Model overview

### 4.1 Core pattern

```
tax:<Property>
 │ ···► qudt:hasQuantityKind ···► qk:<signal kind>, qk:<axis kinds>      (inferred, chain)
 └─ rep:HasRepresentation ──► rep:<Type>                      (one per instance)
       ├─ rep:Shape "n" | "n,m"                               (Vector, Tensor2)
       ├─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:<kind>
       │                             ···► qudt:hasQuantityKind ···► qk:<kind>      (inferred, sub-property)
       └─ rep:HasAxis   ──► [Axis]   ─ rep:AxisIndex i
                                     ─ rep:AxisLabel ──► rep:Label_<…>
                                     ─ rep:HasComponentQuantityKind ──► qk:<kind>      × number of axes
                                     ···► qudt:hasQuantityKind ···► qk:<kind>      (inferred, sub-property)

rep:HasSignal, rep:HasAxis ⊑ rep:HasComponent        rep:HasComponentQuantityKind ⊑ qudt:hasQuantityKind
```

### 4.2 Legend used in this document

```
──►   asserted   (written by hand, base layer)
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

Each subsection shows the **structure** and the **RDF** binding a taxonomy class carries. Examples use real taxonomy properties. Most match the bindings in `main.ttl`; ThermalConductivity, Permittivity and Morphology are illustrations of patterns whose bindings are still open, and the MeanSquaredDisplacement example shows the physically expected signal kind (see the note there and `CHANGELOG.md`). In the structures, `···►` on the class lists the kinds of the signal and of all axes; signal and axis nodes also carry `qudt:hasQuantityKind` for their own kind (not drawn).

### 5.1 Components: signal, axis, label, quantity kind

**Structure**
```
rep:ComponentProperty  ≡  rep:Signal ⊔ rep:Axis      (disjoint)
   rep:Signal   ─ rep:HasComponentQuantityKind ──► qudt:QuantityKind
   rep:Axis     ─ rep:HasComponentQuantityKind ──► qudt:QuantityKind
                ─ rep:AxisIndex                ──► xsd:positiveInteger
                ─ rep:AxisLabel                ──► rep:AxisLabelTerm
                                                   (rep:Label_x, …_kx, …_E, …)
```

- The **signal** is the dependent, measured value. There's exactly one per representation.
- An **axis** is an independent coordinate.
- `rep:HasComponentQuantityKind` (signal or axis → quantity kind, exactly one) is what bindings write. It is a sub-property of `qudt:hasQuantityKind`, so every signal and axis also has its kind as its QUDT quantity kind.
- The taxonomy property gets `qudt:hasQuantityKind` for the kinds of its signal **and** all its axes, through the property chain over `rep:HasComponent` (super-property of `rep:HasSignal` and `rep:HasAxis`, §6.1). On a taxonomy class, `qudt:hasQuantityKind` therefore means "quantity kinds of its data"; which kind belongs to the signal is stated in the binding.
- Two axes are distinct when their `rep:AxisIndex` values differ, or when their `rep:AxisLabel` individuals differ (labels are `owl:AllDifferent`).
- A label carries **no** quantity kind: `rep:Label_E` serves both electric field and energy, and the axis quantity kind disambiguates.
- A new label is added as a new `rep:AxisLabelTerm` individual and included in the `owl:AllDifferent` list.
- Quantity kinds are also `owl:AllDifferent`. OWL makes no unique-name assumption, so without this a signal or axis given two different kinds (for example `qk:Length` on a TimeSeries axis, which must be `qk:Time`) would be read as the two kinds being the same individual, not as an error.

### 5.2 Scalar: example `tax:CorrosionPotential`

**Structure**
```
tax:CorrosionPotential
 │ ···► qudt:hasQuantityKind ···► qk:ElectricPotential
 └─ rep:HasRepresentation ──► rep:Scalar   [Rank 0, no axes]
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:ElectricPotential
```

**RDF**
```turtle
tax:CorrosionPotential rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Scalar
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:ElectricPotential ] ]
    ) ] ] .
```

### 5.3 Vector: example `tax:MagneticAnisotropyField`

**Structure**
```
tax:MagneticAnisotropyField
 │ ···► qudt:hasQuantityKind ···► qk:MagneticFieldStrength
 └─ rep:HasRepresentation ──► rep:Vector   [Rank 1, Shape "3", no axes]
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:MagneticFieldStrength
```

**RDF**
```turtle
tax:MagneticAnisotropyField rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Vector
        [ a owl:Restriction ; owl:onProperty rep:Shape ; owl:hasValue "3" ]
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:MagneticFieldStrength ] ]
    ) ] ] .
```
Vector indices are not axes: all components share the one signal quantity kind.

### 5.4 Tensor2: example `tax:ThermalConductivity`

**Structure**
```
tax:ThermalConductivity
 │ ···► qudt:hasQuantityKind ···► qk:ThermalConductivity
 └─ rep:HasRepresentation ──► rep:Tensor2   [Rank 2, Shape "3,3", no axes]
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:ThermalConductivity
```

**RDF**
```turtle
tax:ThermalConductivity rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Tensor2
        [ a owl:Restriction ; owl:onProperty rep:Shape ; owl:hasValue "3,3" ]
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:ThermalConductivity ] ]
    ) ] ] .
```
`qk:ThermalConductivity` exists in QUDT 3.5.2 but isn't declared in this module. Declare it in `main.ttl` together with the binding.

### 5.5 Alternative representations (Scalar or Tensor2): example `tax:Permittivity`

Permittivity has one IRI and one label. Each instance uses exactly one of the alternatives.

**Structure**
```
tax:Permittivity   "Permittivity"
 │ ···► qudt:hasQuantityKind ···► qk:Permittivity
 └─ rep:HasRepresentation ──► one of:
       ├─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:Permittivity     (shared)
       └─ ⊔ ┬─ rep:Scalar                       (isotropic)
            └─ rep:Tensor2 [Shape "3,3"]        (anisotropic)
```

**RDF**
```turtle
tax:Permittivity rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Permittivity ] ]
        [ a owl:Class ; owl:unionOf (
            rep:Scalar
            [ a owl:Class ; owl:intersectionOf ( rep:Tensor2
                [ a owl:Restriction ; owl:onProperty rep:Shape ; owl:hasValue "3,3" ] ) ] ) ]
    ) ] ] .
```
Write the alternatives as **one** union, never as two separate `rep:HasRepresentation` restrictions. Two restrictions mean *both*, which makes the class unsatisfiable (see §6.5).

### 5.6 1Dmap: example `tax:ElectricHysteresis`

**Structure**
```
tax:ElectricHysteresis
 │ ···► qudt:hasQuantityKind ···► qk:ElectricPolarization, qk:ElectricField
 └─ rep:HasRepresentation ──► rep:1Dmap   [exactly 1 axis]
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_E, HasComponentQuantityKind ──► qk:ElectricField
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:ElectricPolarization
```

**RDF**
```turtle
tax:ElectricHysteresis rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:1Dmap
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:ElectricPolarization ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_E ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:ElectricField ] ) ] ]
    ) ] ] .
```
A 1Dmap allows repeated axis values (a hysteresis loop visits the same E twice).

### 5.7 Spectrum: example `tax:ElectronicDensityOfStates`

**Structure**
```
tax:ElectronicDensityOfStates
 │ ···► qudt:hasQuantityKind ···► qk:EnergyDensityOfStates, qk:Energy
 └─ rep:HasRepresentation ──► rep:Spectrum ⊑ rep:1Dmap
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_E, HasComponentQuantityKind ──► qk:Energy
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:EnergyDensityOfStates
```

**RDF**
```turtle
tax:ElectronicDensityOfStates rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Spectrum
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:EnergyDensityOfStates ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_E ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Energy ] ) ] ]
    ) ] ] .
```
The Energy axis of a Spectrum is a suggestion. A Spectrum with a Frequency or angle axis is still valid.

### 5.8 TimeSeries: example `tax:MeanSquaredDisplacement`

**Structure**
```
tax:MeanSquaredDisplacement
 │ ···► qudt:hasQuantityKind ···► qk:Area, qk:Time
 └─ rep:HasRepresentation ──► rep:TimeSeries ⊑ rep:1Dmap
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, HasComponentQuantityKind ──► qk:Time   (enforced)
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:Area
```

**RDF**
```turtle
tax:MeanSquaredDisplacement rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:TimeSeries
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Area ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Time ] ) ] ]
    ) ] ] .
```
- **The axis label is optional.** None is given here because no time label individual exists yet.
- **Write `qk:Time` explicitly** even though `rep:TimeSeries` implies it, so that tools reading only asserted triples (GUI, SPARQL) see it.
- `qk:Area` is declared in the module. In `main.ttl` the MeanSquaredDisplacement binding uses signal `qk:Length`, as given in the sheet and decided on 2026-10-26; physically a squared displacement has the dimension of an area (see `CHANGELOG.md`).

### 5.9 2Dmap: example `tax:Morphology` (height map)

**Structure**
```
tax:Morphology
 │ ···► qudt:hasQuantityKind ···► qk:Length
 └─ rep:HasRepresentation ──► rep:2Dmap   [exactly 2 axes]
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_x, HasComponentQuantityKind ──► qk:Length
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 2, AxisLabel rep:Label_y, HasComponentQuantityKind ──► qk:Length
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:Length
```

**RDF**
```turtle
tax:Morphology rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:2Dmap
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Length ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_x ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Length ] ) ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "2"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_y ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Length ] ) ] ]
    ) ] ] .
```
Both axes have the quantity kind Length. They stay two axes because their index and label differ. (Illustration: Morphology is not bound in `main.ttl`; the reviewer marked it unclear.)

### 5.10 3Dmap: example `tax:FermiSurface` (reciprocal space)

**Structure**
```
tax:FermiSurface
 │ ···► qudt:hasQuantityKind ···► qk:Energy, qk:Wavenumber
 └─ rep:HasRepresentation ──► rep:3Dmap   [exactly 3 axes]
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, AxisLabel rep:Label_kx, HasComponentQuantityKind ──► qk:Wavenumber
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 2, AxisLabel rep:Label_ky, HasComponentQuantityKind ──► qk:Wavenumber
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 3, AxisLabel rep:Label_kz, HasComponentQuantityKind ──► qk:Wavenumber
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:Energy
```

**RDF**
```turtle
tax:FermiSurface rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:3Dmap
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Energy ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_kx ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Wavenumber ] ) ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "2"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_ky ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Wavenumber ] ) ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "3"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:AxisLabel ; owl:hasValue rep:Label_kz ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Wavenumber ] ) ] ]
    ) ] ] .
```

### 5.11 Axis with alternative quantity kinds: example `tax:EliashbergFunction`

**Structure**
```
tax:EliashbergFunction
 │ ···► qudt:hasQuantityKind ···► qk:Dimensionless
 │ ···► qudt:hasQuantityKind ···► some of { qk:Energy, qk:Frequency }      (not a specific one)
 └─ rep:HasRepresentation ──► rep:Spectrum ⊑ rep:1Dmap
       ├─ rep:HasAxis   ──► [Axis]   ─ AxisIndex 1, HasComponentQuantityKind ──► one of { qk:Energy, qk:Frequency }
       └─ rep:HasSignal ──► [Signal] ─ rep:HasComponentQuantityKind ──► qk:Dimensionless
```

**RDF**
```turtle
tax:EliashbergFunction rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Spectrum
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue qk:Dimensionless ] ]
        [ a owl:Restriction ; owl:onProperty rep:HasAxis ; owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
            [ a owl:Restriction ; owl:onProperty rep:AxisIndex ; owl:hasValue "1"^^xsd:positiveInteger ]
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ;
              owl:someValuesFrom [ a owl:Class ; owl:oneOf ( qk:Energy qk:Frequency ) ] ] ) ] ]
    ) ] ] .
```
- Each axis still has exactly one kind (functional property); it is Energy or Frequency. Any other kind makes the class unsatisfiable.
- At the class level the reasoner derives `∃ qudt:hasQuantityKind . {Energy, Frequency}`, not Energy or Frequency individually, so a query for `qudt:hasQuantityKind value qk:Energy` does not return this class.

### 5.12 Derived and local quantity kinds: `qk:StressIntensityFactor`, `fqk:CryoscopicConstant`

OWL can't compute products, powers or ratios of quantity kinds. The formula is recorded with QUDT's own properties on the kind; bindings just point to the kind.

**Structure**
```
qk:StressIntensityFactor   (QUDT 3.5.2)              = Stress × √Length
   ─ qudt:hasDimensionVector ──► qkdv:A0E0L-0dot5I0M1H0T-2D0     (M·L^-0.5·T^-2)
   ─ skos:related ──► qk:Stress, qk:Length

fqk:CryoscopicConstant     (local, not in QUDT)      = ThermodynamicTemperature / MolalityOfSolute
   ─ qudt:qkdvNumerator   ──► qkdv:A0E0L0I0M0H1T0D0            (dimension of ThermodynamicTemperature)
   ─ qudt:qkdvDenominator ──► qkdv:A1E0L0I0M-1H0T0D0           (dimension of MolalityOfSolute)
   ─ skos:related ──► qk:ThermodynamicTemperature, qk:MolalityOfSolute

tax:FractureToughness ─ HasRepresentation ─► [Scalar] ─ HasSignal ─► [Signal] ─ HasComponentQuantityKind ─► qk:StressIntensityFactor
tax:CryoscopicConstant ─ HasRepresentation ─► [Scalar] ─ HasSignal ─► [Signal] ─ HasComponentQuantityKind ─► fqk:CryoscopicConstant
```

**RDF**
```turtle
fqk:CryoscopicConstant a owl:NamedIndividual, qudt:QuantityKind ;
    skos:prefLabel "CryoscopicConstant"@en ;
    qudt:qkdvNumerator qkdv:A0E0L0I0M0H1T0D0 ;
    qudt:qkdvDenominator qkdv:A1E0L0I0M-1H0T0D0 ;
    qudt:latexDefinition "$K_f = \\Delta T_f / b$" ;
    skos:related qk:ThermodynamicTemperature, qk:MolalityOfSolute .

tax:CryoscopicConstant rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf ( rep:Scalar
        [ a owl:Restriction ; owl:onProperty rep:HasSignal ; owl:someValuesFrom
            [ a owl:Restriction ; owl:onProperty rep:HasComponentQuantityKind ; owl:hasValue fqk:CryoscopicConstant ] ]
    ) ] ] .
```
- Check QUDT first: Stress × √Length already exists as `qk:StressIntensityFactor`, so no local kind was needed for it.
- QUDT 3.5.2 has no dimension-vector individual for K·kg/mol, so the local kind gives the ratio by numerator and denominator instead of `qudt:hasDimensionVector`.
- A dimension vector doesn't identify a kind (Energy and Torque share one); the kind's IRI does.

## 6. Axioms and rules

### 6.1 Per entity

**`rep:HasRepresentation`**
- Functional: a material property has at most one representation.
- Domain `tax:MaterialProperty`; range `rep:Representation`.

**`rep:HasComponent`**
- Domain `rep:Representation`; range `rep:ComponentProperty`.
- Super-property of `rep:HasSignal` and `rep:HasAxis`; not written in bindings. It lets one property chain reach the signal and every axis.

**`rep:HasSignal`**
- Functional: at most one signal.
- Domain `rep:Representation`; range `rep:Signal`. Sub-property of `rep:HasComponent`.

**`rep:HasAxis`**
- Domain `rep:Representation`; range `rep:Axis`. No upper limit; the types set the count. Sub-property of `rep:HasComponent`.

**`rep:HasComponentQuantityKind`**
- Functional: one quantity kind per signal or axis. With the quantity kinds declared distinct, two different kinds on one component are a contradiction.
- Domain `rep:ComponentProperty`; range `qudt:QuantityKind`.
- Sub-property of `qudt:hasQuantityKind`: a signal or axis also has its kind as QUDT quantity kind. It stays a simple property (no sub-properties, not defined by a chain), so it can be functional in OWL 2 DL.

**`rep:AxisIndex`**
- Functional; domain `rep:Axis`; range `xsd:positiveInteger`. Different indices imply different axes.

**`rep:AxisLabel`**
- Functional; domain `rep:Axis`; range `rep:AxisLabelTerm`. Different labels imply different axes (through `owl:AllDifferent`).

**`rep:Rank`, `rep:Shape`**
- Both functional; domain `rep:Representation`.
- Ranges `xsd:nonNegativeInteger` and `xsd:string`.

**`qudt:hasQuantityKind`** (bridge)
- Property chain: `rep:HasRepresentation ∘ rep:HasComponent ∘ rep:HasComponentQuantityKind`. A taxonomy property has the quantity kinds of its signal and of all its axes.
- Also the super-property of `rep:HasComponentQuantityKind`, so signal and axis nodes have it too.

**`rep:ComponentProperty`, `rep:Signal`, `rep:Axis`**
- `rep:ComponentProperty` is the disjoint union of `rep:Signal` and `rep:Axis`.

**`rep:Scalar`, `rep:Vector`, `rep:Tensor2`**
- Rank 0, 1 or 2 respectively; at least one signal; no axis.

**`rep:1Dmap`, `rep:2Dmap`, `rep:3Dmap`**
- At least one signal; exactly 1, 2 or 3 axes.

**`rep:Spectrum`**
- Subclass of `rep:1Dmap`; no extra axiom (the Energy axis is a note only).

**`rep:TimeSeries`**
- Subclass of `rep:1Dmap`; every axis has quantity kind `qk:Time`.

**Axis labels**
- `rep:Label_x … rep:Label_rho` are pairwise different (`owl:AllDifferent`).

**Quantity kinds**
- The 42 quantity kinds of the module (41 `qk:` from QUDT, 1 local `fqk:`) are pairwise different (`owl:AllDifferent`). In `main.ttl` the list also covers the three further kinds the taxonomy already used (Fugacity, HeatCapacity, ThermalExpansionCoefficient), so it has 45 members.

**Derived and local quantity kinds**
- `qk:StressIntensityFactor` (QUDT) carries its QUDT dimension vector `qkdv:A0E0L-0dot5I0M1H0T-2D0` and the formula Stress × √Length (`qudt:latexDefinition`, `skos:related` Stress and Length).
- `fqk:CryoscopicConstant` (local) is ThermodynamicTemperature / MolalityOfSolute, given by `qudt:qkdvNumerator` and `qudt:qkdvDenominator`.
- These are descriptive: OWL records the relations but doesn't compute or check dimensions.

### 6.2 Summary table

| Axiom | Applies to | Effect |
|---|---|---|
| functional | `rep:HasRepresentation` | one representation per property instance |
| domain / range | `rep:HasRepresentation` | links taxonomy to module |
| functional | `rep:HasSignal` | one signal |
| domain / range | `rep:HasSignal`, `rep:HasAxis` | type signal and axis nodes |
| functional | `rep:HasComponentQuantityKind` | one quantity kind per component |
| domain / range | `rep:HasComponentQuantityKind` | quantity kinds are `qudt:QuantityKind` |
| functional | `rep:AxisIndex`, `rep:AxisLabel` | distinct index or label means distinct axis |
| `owl:AllDifferent` | axis labels | labels never merge |
| `owl:AllDifferent` | quantity kinds | quantity kinds never merge; a second, different kind on a component is an error |
| disjoint union | `rep:ComponentProperty` = Signal ⊔ Axis | a signal is never an axis |
| sub-property | `rep:HasSignal`, `rep:HasAxis` ⊑ `rep:HasComponent` | one chain covers signal and axes |
| sub-property | `rep:HasComponentQuantityKind` ⊑ `qudt:hasQuantityKind` | signal and axis carry their kind as QUDT quantity kind |
| property chain | `qudt:hasQuantityKind` | property quantity kinds = signal and axis quantity kinds |
| Rank = 0 / 1 / 2 | Scalar / Vector / Tensor2 | fixes signal rank |
| ≥1 HasSignal | all types | every representation has a signal |
| ≤0 HasAxis | Scalar, Vector, Tensor2 | no axes |
| =1 / =2 / =3 HasAxis | 1Dmap / 2Dmap / 3Dmap | exact axis count |
| ∀ HasAxis.(HasComponentQuantityKind ∋ Time) | TimeSeries | time axis enforced |
| subclass | Spectrum, TimeSeries ⊑ 1Dmap | inherit 1 axis |
| `owl:oneOf` filler (in a binding) | `rep:HasComponentQuantityKind` | a signal or axis whose kind is one of several (EliashbergFunction) |

### 6.3 Description Logic notation

**Properties**
```
⊤ ⊑ ≤1 HasRepresentation              ∃HasRepresentation.⊤ ⊑ tax:MaterialProperty      ⊤ ⊑ ∀HasRepresentation.Representation
⊤ ⊑ ≤1 HasSignal                      ∃HasSignal.⊤ ⊑ Representation                  ⊤ ⊑ ∀HasSignal.Signal
                                      ∃HasAxis.⊤ ⊑ Representation                    ⊤ ⊑ ∀HasAxis.Axis
⊤ ⊑ ≤1 HasComponentQuantityKind       ∃HasComponentQuantityKind.⊤ ⊑ ComponentProperty   ⊤ ⊑ ∀HasComponentQuantityKind.qudt:QuantityKind
⊤ ⊑ ≤1 AxisIndex                      ∃AxisIndex.⊤ ⊑ Axis                            ⊤ ⊑ ∀AxisIndex.xsd:positiveInteger
⊤ ⊑ ≤1 AxisLabel                      ∃AxisLabel.⊤ ⊑ Axis                            ⊤ ⊑ ∀AxisLabel.AxisLabelTerm
⊤ ⊑ ≤1 Rank                           ∃Rank.⊤ ⊑ Representation                       ⊤ ⊑ ∀Rank.xsd:nonNegativeInteger
⊤ ⊑ ≤1 Shape                          ∃Shape.⊤ ⊑ Representation                      ⊤ ⊑ ∀Shape.xsd:string

HasSignal ⊑ HasComponent        HasAxis ⊑ HasComponent        HasComponentQuantityKind ⊑ qudt:hasQuantityKind
HasRepresentation ∘ HasComponent ∘ HasComponentQuantityKind ⊑ qudt:hasQuantityKind
```

**Components and labels**
```
ComponentProperty ⊑ Representation
ComponentProperty ≡ Signal ⊔ Axis          Signal ⊓ Axis ⊑ ⊥
Label_x ≠ Label_y ≠ Label_z ≠ Label_kx ≠ Label_ky ≠ Label_kz ≠ Label_E ≠ Label_P ≠ Label_rho   (pairwise)
qk:Time ≠ qk:Length ≠ qk:Energy ≠ …   (all quantity kinds, pairwise)
```

**Representation types**
```
Scalar     ⊑ Representation ⊓ ∃Rank.{0} ⊓ ∃HasSignal.Signal ⊓ ≤0 HasAxis
Vector     ⊑ Representation ⊓ ∃Rank.{1} ⊓ ∃HasSignal.Signal ⊓ ≤0 HasAxis
Tensor2    ⊑ Representation ⊓ ∃Rank.{2} ⊓ ∃HasSignal.Signal ⊓ ≤0 HasAxis
1Dmap      ⊑ Representation ⊓ ∃HasSignal.Signal ⊓ =1 HasAxis
Spectrum   ⊑ 1Dmap
TimeSeries ⊑ 1Dmap ⊓ ∀HasAxis.∃HasComponentQuantityKind.{qk:Time}
2Dmap      ⊑ Representation ⊓ ∃HasSignal.Signal ⊓ =2 HasAxis
3Dmap      ⊑ Representation ⊓ ∃HasSignal.Signal ⊓ =3 HasAxis
```

**Taxonomy binding pattern**
```
C ⊑ ∃HasRepresentation.( T
        ⊓ ∃Shape.{s}                                                    (Vector, Tensor2)
        ⊓ ∃HasSignal.∃HasComponentQuantityKind.{q}
        ⊓ ∃HasAxis.(∃AxisIndex.{i} ⊓ ∃AxisLabel.{ℓ} ⊓ ∃HasComponentQuantityKind.{k})   × number of axes )

Alternatives:   C ⊑ ∃HasRepresentation.( ∃HasSignal.∃HasComponentQuantityKind.{q} ⊓ (T₁ ⊔ T₂ ⊔ …) )
Alternative kinds:   ∃HasAxis.(∃AxisIndex.{i} ⊓ ∃HasComponentQuantityKind.{k₁, k₂})
```

### 6.4 Consequences the reasoner derives

| Consequence | Reason |
|---|---|
| Scalar, Vector and Tensor2 are pairwise disjoint | functional `rep:Rank` with different values |
| Scalar, Vector and Tensor2 are disjoint from every map type | ≤0 axes vs ≥1 axis |
| 1Dmap, 2Dmap and 3Dmap are pairwise disjoint | different exact axis counts |
| `tax:C qudt:hasQuantityKind q` for the signal kind and every axis kind of a bound property | property chain on `qudt:hasQuantityKind` through `rep:HasComponent` |
| `[signal or axis] qudt:hasQuantityKind q` for its own kind | `rep:HasComponentQuantityKind ⊑ qudt:hasQuantityKind` |
| Two axes with different index or label are distinct | functional `AxisIndex` / `AxisLabel` + `AllDifferent` |

### 6.5 Rules and conventions

**Modelling errors that the reasoner catches** (the class becomes unsatisfiable):

| Error | Violated axiom |
|---|---|
| TimeSeries with a non-time axis | TimeSeries axis must have quantity kind `qk:Time`; `rep:HasComponentQuantityKind` is functional and quantity kinds are distinct |
| Signal or axis with two different quantity kinds | `rep:HasComponentQuantityKind` is functional and quantity kinds are distinct |
| Scalar, Vector or Tensor2 with an axis | Scalar, Vector and Tensor2 allow no axis |
| 1Dmap, 2Dmap or 3Dmap with the wrong number of axes | exact axis count per map type, with axes kept distinct by index or label |
| Two separate `HasRepresentation` restrictions with different types | `rep:HasRepresentation` is functional and the representation types are disjoint (§6.4) |
| A node used as both signal and axis | Signal and Axis are disjoint |

**Authoring conventions** (not enforced by OWL):
1. **Bind leaf classes only.** Restrictions inherit, so a binding on a parent class forces every subclass.
2. **Give every axis an `rep:AxisIndex`** (1, 2, 3, …). The label is optional.
3. **Write implied quantity kinds explicitly** (for example `qk:Time` on a TimeSeries axis), so tools that read asserted triples see them.
4. **Write alternatives as one `owl:unionOf`,** never as two separate restrictions.
5. **New labels:** add a `rep:AxisLabelTerm` individual and include it in the `owl:AllDifferent` list.
6. **New quantity kinds:** use the version-free QUDT IRI (`qk:<Name>`), check that it exists in QUDT 3.5.2, declare it as `owl:NamedIndividual, qudt:QuantityKind`, and add it to the quantity-kind `owl:AllDifferent` list (in `representation.ttl` and `main.ttl`). Check QUDT before defining a local kind: StressIntensityFactor and HallCoefficient, for example, exist there.
7. **`qudt:hasQuantityKind` must not get cardinality or functional axioms.** The property chain makes it non-simple in OWL 2 DL.
8. **Kinds missing from QUDT:** define them as `fqk:<Name>` (`owl:NamedIndividual, qudt:QuantityKind`) with `qudt:hasDimensionVector` when QUDT has the vector, otherwise `qudt:qkdvNumerator` / `qudt:qkdvDenominator` for a ratio, plus `qudt:latexDefinition`, `skos:definition` and `skos:related` to the constituent kinds; add them to the distinctness list.
9. **Alternative kinds for one signal or axis:** `rep:HasComponentQuantityKind some [ owl:oneOf ( qk:A qk:B ) ]` instead of `hasValue` (§5.11).
10. **Vector-valued map signal:** `rep:Shape` may also be given on a map (e.g. Trajectory: TimeSeries with `rep:Shape "3"`, three position components per time step).

## 7. Verification

The module was checked with the HermiT reasoner, together with test bindings. The test bindings add no distinctness axioms of their own; the checks rely only on the module.

| Test | Expected | Result |
|---|---|---|
| Test classes: Scalar, 2Dmap, TimeSeries, Scalar ⊔ Tensor2 union | satisfiable | ✔ |
| TimeSeries with a Length axis | unsatisfiable | ✔ |
| Scalar with an axis | unsatisfiable | ✔ |
| 2Dmap with three axes | unsatisfiable | ✔ |
| 1Dmap with two axes of different labels | unsatisfiable | ✔ |
| Scalar and Tensor2 as two separate restrictions | unsatisfiable | ✔ |
| Instance of a Scalar test class with signal Voltage | infers `qudt:hasQuantityKind qk:Voltage` | ✔ |
| Merged `main.ttl` (taxonomy + module + 137 bindings) | no unsatisfiable class | ✔ |
| Each of the 137 bound classes | inferred `qudt:hasQuantityKind` = signal kind + axis kinds from the sheet (+ any direct restriction) | ✔ 137/137 |
| Each of the 137 bound classes | its signal and axes carry `qudt:hasQuantityKind` for their own kind | ✔ 137/137 |
| EliashbergFunction (axis `oneOf {Energy, Frequency}`) | class ⊑ `∃ qudt:hasQuantityKind.{Energy, Frequency}`; a Length axis is unsatisfiable | ✔ |

## 8. Merging into `main.ttl`

- **Use the current QUDT schema namespace** in `main.ttl`: `@prefix qudt: <http://qudt.org/schema/qudt/>`. With the old `…/2.1/schema/qudt/`, `qudt:hasQuantityKind` would split into two unrelated properties.
- **Replace any older appended representation module; don't append next to it.** The old `Profile ≡ Rank 1` axiom would otherwise classify Vector and TimeSeries as Profile, and the old disjoint union with `UnitAttribute` would conflict.
- **Existing direct `qudt:hasQuantityKind` restrictions** on taxonomy classes stay valid. When such a class gets a binding, remove the direct restriction or make sure it matches the signal quantity kind (seven of the eleven currently differ; see `CHANGELOG.md`); the property isn't functional, so a mismatch isn't flagged.
- **Declare in `main.ttl` any quantity kind used in a binding** that isn't declared in this module, and include it in the quantity-kind `owl:AllDifferent` list.

## 9. Taxonomy bindings in `main.ttl`

`main.ttl` contains the representation module together with one `rep:HasRepresentation` binding per mapped taxonomy class, mapped from the HasRepresentation_Adhoc sheet (reviewed version received 2026-10-26). The bindings sit below the banner `REPRESENTATION BINDINGS (mapped from HasRepresentation_Adhoc)` at the end of the file and use only entities defined in this module.

| | Count |
|---|---:|
| Bound classes | 137 (137 fully, 0 in part) |
| Not mapped | 33 |

| Representation type | Bound classes |
|---|---:|
| `rep:Scalar` | 122 |
| `rep:1Dmap` | 4 |
| `rep:3Dmap` | 3 |
| `rep:Spectrum` | 3 |
| `rep:Vector` | 3 |
| `rep:TimeSeries` | 2 |

| Not mapped, by reason | Rows |
|---|---:|
| Scalar or tensor (open modelling choice) | 13 |
| Reviewer: remove / unclear / not a quantity | 11 |
| No QUDT quantity kind / rank-3 tensor | 4 |
| No matching representation type | 3 |
| Parent class | 1 |
| Contradicts class description | 1 |

The full list, the mapping rules, the unmapped rows and the open points are in `CHANGELOG.md`.
