# Changelog: `main.ttl`

Newest first. Entries under **History** describe earlier states and are superseded where noted.

## Current state (2026-10-26)

- `main.ttl`: taxonomy + representation module + **140 bindings** from the reviewed HasRepresentation_Adhoc sheet, all mapped fully (30 rows remain unmapped, see the discussions below).
- Representation types: Scalar, Vector, Tensor2, 1Dmap, Spectrum, TimeSeries, 2Dmap, 3Dmap, 4Dmap, **ElementList**.
- Deprecated taxonomy classes: MagneticHysteresis, Photoluminescence, Grain, Morphology, ParticleShape.
- Signal and axis carry `qudt:hasQuantityKind` (via `rep:HasComponentQuantityKind`); a taxonomy class gets the kinds of its signal and all axes (chain via `rep:HasComponent`).
- Quantity kinds: 42 in the module (41 QUDT, 1 local `fqk:CryoscopicConstant`), 45 in the distinctness list of `main.ttl`.

## Five taxonomy classes deprecated, 2026-10-26

Following the reviewer's comments in the HasRepresentation_Adhoc sheet ("REMOVE", or unclear entries to be removed), five classes are marked deprecated rather than deleted, so their IRIs keep resolving for anyone who already uses them.

### Appended to `main.ttl`

A new block `DEPRECATED TAXONOMY CLASSES` at the end of the file (after the bindings). The class blocks in the taxonomy part are not edited.

| Class | Parent | Added | Reviewer comment |
|---|---|---|---|
| `tax:MagneticHysteresis` | MagneticProperty | `owl:deprecated true`, `skos:historyNote` | "REMOVE THIS. It can mean different things." |
| `tax:Photoluminescence` | OpticalProperty | `owl:deprecated true`, `skos:historyNote` | phenomenon, not a measurable property; "REMOVE" |
| `tax:Grain` | StructuralProperty | `owl:deprecated true`, `skos:historyNote` | unclear |
| `tax:Morphology` | StructuralProperty | `owl:deprecated true`, `skos:historyNote` | unclear |
| `tax:ParticleShape` | StructuralProperty | `owl:deprecated true`, `skos:historyNote` | unclear |

Also declared: `skos:historyNote` as `owl:AnnotationProperty`.

### Effect

- `owl:deprecated` is an annotation: no logical consequence; the reasoner treats the classes as before. Tools such as Protégé show them struck through.
- None of the five has subclasses, a representation binding or a reference from another class, so nothing else is affected.
- The five rows stay "Not mapped"; their reason now says "deprecated" (also in the annotated sheet).
- The README's Morphology 2Dmap example is kept as an illustration of the 2Dmap pattern and now says the class is deprecated.

### Not deprecated (reviewer comments also suggest removal, kept for a decision)

- SpectroscopicProperty (category; "obsolete catch-all", has subclasses).
- Defect, PhaseComposition, PhaseCrystalStructure, StandardState (not a quantity or undecided).

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 610 (unchanged; taxonomy classes are not part of the module) |
| `main.ttl` | 4194 (was 4183) |

### Verification

| Check | Result |
|---|---|
| Taxonomy part of `main.ttl` unchanged; deprecations only appended | ✔ |
| 5 classes with `owl:deprecated true` | ✔ |
| HermiT: unsatisfiable classes | ✔ none |
| Bindings and derived quantity kinds | ✔ unchanged, 140/140 |
| Invalid test bindings | ✔ all still flagged |

## Element lists; ElementalComposition and Impurity bound, 2026-10-26

### Added to the representation module

| Item | Content |
|---|---|
| Prefix `table:` | `http://www.daml.org/2003/01/periodictable/PeriodicTable#` (DAML Periodic Table) |
| `table:Element` | declared as `owl:Class`; **not imported**. Chemical elements are individuals of it (e.g. `table:Fe`) |
| `rep:ElementList` | ⊑ `rep:Representation`; `rep:HasAxis` max 0; `owl:disjointWith rep:Scalar, rep:Vector, rep:Tensor2`. No signal, no axes, no quantity kind |
| `rep:HasChemicalElement` | object property; domain `rep:ElementList`; range `table:Element`. Not a sub-property of `rep:HasComponent` or `qudt:hasQuantityKind` |
| Ontology comment | lists ElementList among the representation types |

Disjointness is stated only between ElementList and Scalar, Vector, Tensor2 (`owl:disjointWith`); no axiom about the existing types among themselves was added. ElementList is disjoint from every map type automatically (maps need at least one axis).

### Bindings added

| Class | Binding | Note |
|---|---|---|
| `tax:ElementalComposition` | `rep:HasRepresentation only rep:ElementList` | range only: no specific element and no minimum number; elements are given in instance data |
| `tax:Impurity` | `rep:HasRepresentation only rep:ElementList` | restricted to elements by decision; the description also mentions chemical substances (compounds) |

The bindings use `owl:allValuesFrom` (a range statement), unlike the numeric bindings, which use `owl:someValuesFrom`.

### Unchanged

Scalar, Vector, Tensor2, all map types, TimeSeries rule, signals, axes, `rep:HasComponentQuantityKind`, the quantity-kind chain and distinctness list, the 138 existing bindings and their derived quantity kinds, and the taxonomy part of `main.ttl`. Element lists derive no `qudt:hasQuantityKind`.

### Counts

| | Before | After |
|---|---:|---:|
| Bindings | 138 | 140 |
| Not mapped | 32 | 30 |

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 610 (was 593) |
| `main.ttl` | 4183 (was 4158) |

### Verification

| Check | Result |
|---|---|
| Taxonomy part of `main.ttl` unchanged | ✔ |
| HermiT: unsatisfiable classes in `main.ttl` | ✔ none |
| Existing invalid tests (TimeSeries, Scalar with axis, axis counts, 4Dmap) | ✔ all still flagged |
| ElementalComposition also bound as Scalar | ✔ unsatisfiable |
| Instance data: an ElementalComposition listing `table:Fe`, `table:Cr` | ✔ consistent; the representation node is inferred to be a `rep:ElementList` |
| Derived `qudt:hasQuantityKind` of all 140 bound classes as expected (none for element lists) | ✔ 140/140 |
| README Turtle examples (now 14, incl. §5.14) | ✔ all parse, all satisfiable |

### Open points

- Amounts (at.%, wt.%) are not represented; a composition with fractions would be a 1Dmap over an element axis with a `qk:MoleFraction` / `qk:MassFraction` signal.
- Impurity may need a broader range than elements (e.g. ChEBI "chemical entity") if compounds should be allowed.
- The DAML Periodic Table dates from 2003; its coverage of the elements named later (113–118) should be checked before using it for data.

## 4D maps introduced; ElectronicGreensFunction bound, 2026-10-26

### Added to the representation module

| Item | Content |
|---|---|
| `rep:4Dmap` | ⊑ `rep:Representation`; at least one signal; `rep:HasAxis` exactly 4. Same pattern as 1Dmap–3Dmap |
| `rep:Label_omega` | axis label "omega" (altLabel ω), e.g. angular frequency; added to the axis-label `owl:AllDifferent` list |
| Ontology comment | lists 4Dmap among the representation types |

Disjointness needs no new axiom: 4Dmap is disjoint from 1Dmap, 2Dmap, 3Dmap (different exact axis counts) and from Scalar, Vector, Tensor2 (no axes), derived by the reasoner.

### Binding added

| Class | Bound as |
|---|---|
| `tax:ElectronicGreensFunction` | `rep:4Dmap`; signal `qk:Time`; axes 1: `rep:Label_kx`, `qk:Wavenumber`; 2: `rep:Label_ky`, `qk:Wavenumber`; 3: `rep:Label_kz`, `qk:Wavenumber`; 4: `rep:Label_omega`, `qk:Frequency` |

As suggested in the sheet ("rep:4Dmap G(kx,ky,kz,omega) → time"). The signal kind Time matches G(k, ω) having the dimension 1/frequency. The previous discussion point on new constructs is resolved for ElectronicGreensFunction.

### Counts

| | Before | After |
|---|---:|---:|
| Bindings | 137 | 138 |
| Not mapped | 33 | 32 |

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 593 (was 574) |
| `main.ttl` | 4158 (was 4035) |

### Verification

| Check | Result |
|---|---|
| Taxonomy part of `main.ttl` unchanged | ✔ |
| HermiT: unsatisfiable classes in `main.ttl` | ✔ none |
| 4Dmap ⊓ 3Dmap, 4Dmap ⊓ Scalar | ✔ unsatisfiable |
| ElectronicGreensFunction with a fifth axis | ✔ unsatisfiable |
| Earlier invalid test bindings | ✔ all 5 still flagged |
| Derived `qudt:hasQuantityKind` = signal + axis kinds (+ direct restrictions) | ✔ 138/138 |
| Signal and axis carry their own `qudt:hasQuantityKind` | ✔ 138/138 |
| README Turtle examples (now 12, incl. §5.13) | ✔ all parse, all satisfiable |

## Remaining rows resolved by decision, 2026-10-26

The 11 rows that were bound only in part are now bound fully, following decisions taken on 2026-10-26. All 137 bindings are complete; the 33 unmapped rows are unchanged.

### Bindings changed

| Class | Now bound as | Note |
|---|---|---|
| `tax:CorrosionRate` | `rep:Scalar`, signal `qk:LinearVelocity` | as given in the sheet |
| `tax:EliashbergFunction` | `rep:Spectrum`, signal `qk:Dimensionless`, axis 1: one of {`qk:Energy`, `qk:Frequency`} | axis kind as `owl:oneOf`; each axis still has exactly one kind |
| `tax:FatigueCrackGrowthThreshold` | `rep:Scalar`, signal `qk:StressIntensityFactor` | Stress × √Length; existing QUDT kind, dimension vector A0E0L-0dot5I0M1H0T-2D0 |
| `tax:FractureToughness` | `rep:Scalar`, signal `qk:StressIntensityFactor` | as above |
| `tax:StressIntensityFactor` | `rep:Scalar`, signal `qk:StressIntensityFactor` | as above |
| `tax:AbsorptionCoefficient` | `rep:Scalar`, signal `qk:InverseLength` | as given in the sheet |
| `tax:2DDefectInterfacialEnergy` | `rep:Scalar`, signal `qk:Energy` | as given in the sheet |
| `tax:CryoscopicConstant` | `rep:Scalar`, signal `fqk:CryoscopicConstant` | local kind ThermodynamicTemperature / MolalityOfSolute (not in QUDT 3.5.2) |
| `tax:HeatOfFusion` | `rep:Scalar`, signal `qk:MolarEnergy` | as given in the sheet |
| `tax:MeanSquaredDisplacement` | `rep:TimeSeries`, signal `qk:Length`, axis 1: `qk:Time` | as given in the sheet |
| `tax:Trajectory` | `rep:TimeSeries`, `rep:Shape "3"`, signal `qk:Length`, axis 1: `qk:Time` | three position components per time step |

Previously open for CorrosionRate, HeatOfFusion, AbsorptionCoefficient, 2DDefectInterfacialEnergy and MeanSquaredDisplacement: the sheet's quantity kind seemed to contradict the class description. The sheet's kinds are now used as given; the descriptions are unchanged, so the wording of those descriptions may still need a review.

### Added to the representation module

| Item | Content |
|---|---|
| Prefixes | `qkdv:` (QUDT dimension vectors), `fqk:` (`http://fairmat-nfdi.eu/taxonomy/quantitykind/`, local kinds) |
| External declarations | `qudt:QuantityKindDimensionVector` (class); `qudt:hasDimensionVector`, `qudt:qkdvNumerator`, `qudt:qkdvDenominator` (object properties); `qudt:latexDefinition` (datatype property); `skos:related` (annotation) |
| QUDT quantity kinds | `qk:LinearVelocity`, `qk:InverseLength`, `qk:MolalityOfSolute` (all exist, not deprecated, in QUDT 3.5.2) |
| Math on `qk:StressIntensityFactor` | `qudt:hasDimensionVector qkdv:A0E0L-0dot5I0M1H0T-2D0` (as in QUDT), `qudt:latexDefinition "$K = \sigma\sqrt{L}$"`, `skos:related qk:Stress, qk:Length`, note "Stress × √Length" |
| Local kind `fqk:CryoscopicConstant` | `qudt:QuantityKind`; `qudt:qkdvNumerator qkdv:A0E0L0I0M0H1T0D0` (ThermodynamicTemperature), `qudt:qkdvDenominator qkdv:A1E0L0I0M-1H0T0D0` (MolalityOfSolute), `qudt:latexDefinition`, `skos:related` to both kinds. QUDT 3.5.2 has no dimension-vector individual for its dimension (A-1·M1·H1), so no `qudt:hasDimensionVector` |
| Dimension vectors declared | the three `qkdv:` individuals above, typed `qudt:QuantityKindDimensionVector` (all exist in QUDT 3.5.2) |
| Distinctness list | now 42 kinds in the module, 45 in `main.ttl` |

OWL records these relations but doesn't compute them: nothing checks that the dimension vector equals Stress × √Length. Such a check would need SPARQL or code over the dimension exponents.

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 574 (was 518) |
| `main.ttl` | 4035 (was 3847) |

### Verification

| Check | Result |
|---|---|
| Taxonomy part of `main.ttl` unchanged | ✔ |
| HermiT: unsatisfiable classes in `main.ttl` | ✔ none |
| Invalid test bindings flagged | ✔ all 5 |
| Derived `qudt:hasQuantityKind` = signal + axis kinds (+ direct restrictions) for all bindings | ✔ 137/137 |
| Signal and axis carry their own `qudt:hasQuantityKind` | ✔ 137/137 |
| EliashbergFunction ⊑ `∃ qudt:hasQuantityKind.{Energy, Frequency}`; a Length axis would make it unsatisfiable | ✔ / ✔ |
| README Turtle examples (now 11, incl. §5.11 and §5.12) | ✔ all parse, all satisfiable |

### Discussion points resolved

From the discussion of the previous entry: point 4 (stress intensity factor) and point 7 (EliashbergFunction axis) are resolved; point 5 is resolved for CryoscopicConstant (local kind), and HallCoefficient turns out to exist in QUDT 3.5.2 as `qk:HallCoefficient` (dimension A0E-1L3I0M0H0T-1D0, i.e. Volume / Charge), so only its rank-3 representation is open. Point 2 is resolved for the five rows listed above by using the sheet's kinds; MagneticAnisotropyConstant and MagneticSusceptibility stay unmapped. Point 6 is resolved for Trajectory (`rep:Shape "3"`).

## Representation bindings remapped from the reviewed HasRepresentation_Adhoc sheet, 2026-10-26

All bindings were regenerated from the reviewed sheet (Luca's completed review). As before, this is a mapping operation: representation types, axis labels and properties are the existing ones; rows that are contradictory, undecided or need a new modelling construct are reported here and not mapped. The taxonomy classes themselves are unchanged; the previous bindings section is replaced by the new one.

### Summary

| | Count |
|---|---:|
| Sheet rows (properties) | 191 |
| Rows with a representation, axis or signal entry (unique classes) | 170 |
| Mapped fully | 126 |
| Mapped in part | 11 |
| Not mapped (see Discussion) | 33 |
| Bindings in `main.ttl` | 137 (previously 78) |
| Binding triples | 2442 |

| Representation type | Bound classes |
|---|---:|
| `rep:Scalar` | 122 |
| `rep:1Dmap` | 4 |
| `rep:3Dmap` | 3 |
| `rep:Spectrum` | 3 |
| `rep:Vector` | 3 |
| `rep:TimeSeries` | 2 |

Compared with the previous bindings: 60 classes are newly bound, 34 bindings changed (mostly a signal quantity kind added, or Voltage → ElectricPotential and Temperature → ThermodynamicTemperature as given in the reviewed sheet), and ElectronicGreensFunction is no longer bound (the reviewer now suggests a 4D map; see Discussion).

### Quantity kinds added to the module

15 QUDT quantity kinds used by the reviewed sheet were not declared yet. Each exists and is not deprecated in QUDT 3.5.2; they are declared in section 4b of `representation.ttl` (`owl:NamedIndividual, qudt:QuantityKind`, `skos:prefLabel`, English `rdfs:label` from QUDT, `rdfs:isDefinedBy` QUDT 3.5.2) and added to the quantity-kind `owl:AllDifferent` list.

`qk:Angle`, `qk:Area`, `qk:ChemicalPotential`, `qk:ElectricCharge`, `qk:ElectricCurrent`, `qk:ElectricPotential`, `qk:EnergyPerTemperature`, `qk:InverseTemperature`, `qk:Mass`, `qk:MolarEnergy`, `qk:NumberDensity`, `qk:SpecificEnergy`, `qk:SpecificHeatCapacity`, `qk:ThermodynamicTemperature`, `qk:Volume`

`qk:ChemicalPotential` and `qk:Volume` were typed in `main.ttl` only (used by the taxonomy); they now live in the module. The module has 38 quantity kinds; the distinctness list in `main.ttl` has 41 (plus Fugacity, HeatCapacity, ThermalExpansionCoefficient, used only by the taxonomy's own restrictions).

Seven module kinds are no longer used by any binding and are kept: ElectricFieldStrength, Frequency, Permittivity, Stress, StressIntensityFactor, Temperature, Voltage (Temperature and Voltage are still used by the taxonomy's own restrictions).

### Mapping rules applied

| Sheet entry | Mapped to |
|---|---|
| Representation `Scalar` / `Spectrum` / `TimeSeries` | `rep:Scalar` / `rep:Spectrum` / `rep:TimeSeries` |
| Representation `VolumeData` | `rep:3Dmap` |
| `Not sure` + comment "vector of dimension 3" | `rep:Vector` with `rep:Shape "3"` |
| `Not sure` + comment "rep:1Dmap …" | `rep:1Dmap` |
| `Not sure` for ElectricHysteresis (comment: a map P(E)) | `rep:1Dmap` |
| `Not sure` for Trajectory (comment: "It is a time series … signal dimension is qudt:Length") | `rep:TimeSeries`, signal `qk:Length` from the comment |
| `qudt:<Name>` in Signal / Axis | `qk:<Name>`; must exist and not be deprecated in QUDT 3.5.2 |
| `qudtDimensionless` (missing colon; 5 rows) | `qk:Dimensionless` |
| Signal containing "not in qudt" | no signal quantity kind (type only) |
| Axis label `kx`, `ky`, `kz`, `E` | existing individuals `rep:Label_kx`, `rep:Label_ky`, `rep:Label_kz`, `rep:Label_E` |
| Order of axes in the cell | `rep:AxisIndex` 1, 2, 3 |
| Rows without representation, axis and signal (categories, tree duplicates, comment only) | skipped |

### Mapped

| Class | Type | Shape | Signal | Axes (index: label, quantity kind) |
|---|---|---|---|---|
| `tax:AnodicPartialCurrent` | `rep:Scalar` | — | `qk:ElectricCurrent` | — |
| `tax:CathodicPartialCurrent` | `rep:Scalar` | — | `qk:ElectricCurrent` | — |
| `tax:AnodicPartialCurrentCorrosion` | `rep:Scalar` | — | `qk:ElectricCurrent` | — |
| `tax:CorrosionPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:FreeCorrosionCurrent` | `rep:Scalar` | — | `qk:ElectricCurrent` | — |
| `tax:FreeCorrosionPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:PassivationCurrent` | `rep:Scalar` | — | `qk:ElectricCurrent` | — |
| `tax:PassivationPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:PittingInitiationPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:PoralizedPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:ReactivationPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:TranspassivationPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:RedoxPotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:StandardElectrodePotential` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:BandGapElectronicBowingCoefficient` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:BindingEnergyExciton` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:CarrierDensity` | `rep:Scalar` | — | `qk:NumberDensity` | — |
| `tax:CoulombInteractions` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:DielectricStrength` | `rep:Scalar` | — | `qk:ElectricField` | — |
| `tax:EffectiveElectronMass` | `rep:Scalar` | — | `qk:Mass` | — |
| `tax:EffectiveHoleMass` | `rep:Scalar` | — | `qk:Mass` | — |
| `tax:ElectronicBandGap` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:ElectronicBandStructure` | `rep:3Dmap` | — | `qk:Energy` | 1: `rep:Label_kx`, `qk:Wavenumber`; 2: `rep:Label_ky`, `qk:Wavenumber`; 3: `rep:Label_kz`, `qk:Wavenumber` |
| `tax:ElectronicCompressibility` | `rep:Scalar` | — | `qk:Compressibility` | — |
| `tax:ElectronicDensityOfStates` | `rep:Spectrum` | — | `qk:EnergyDensityOfStates` | 1: `qk:Energy` |
| `tax:ElectronicSusceptibility` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:FermiLevel` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:FermiSurface` | `rep:3Dmap` | — | `qk:Energy` | 1: `rep:Label_kx`, `qk:Wavenumber`; 2: `rep:Label_ky`, `qk:Wavenumber`; 3: `rep:Label_kz`, `qk:Wavenumber` |
| `tax:ElectricCoercitivity` | `rep:Scalar` | — | `qk:ElectricField` | — |
| `tax:ElectricCurieTemperature` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:ElectricHysteresis` | `rep:1Dmap` | — | `qk:ElectricPolarization` | 1: `rep:Label_E`, `qk:ElectricField` |
| `tax:RemanentPolarization` | `rep:Scalar` | — | `qk:ElectricPolarization` | — |
| `tax:SaturationPolarization` | `rep:Scalar` | — | `qk:ElectricPolarization` | — |
| `tax:ElectromechanicalCouplingFactor` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:MechanicalQualityFactor` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:SpinOrbitCouplingConstant` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:SuperconductingCoherenceLength` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:SuperconductingCriticalTemperature` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:SuperconductingGap` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:MagneticAnisotropyField` | `rep:Vector` | 3 | `qk:MagneticFieldStrength` | — |
| `tax:MagneticCoercitivity` | `rep:Scalar` | — | `qk:MagneticFieldStrength` | — |
| `tax:MagneticCurieTemperature` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:MagneticSquareness` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:MaximumEnergyProduct` | `rep:Scalar` | — | `qk:EnergyDensity` | — |
| `tax:Permeability` | `rep:Scalar` | — | `qk:ElectromagneticPermeability` | — |
| `tax:RemanentMagnetization` | `rep:Vector` | 3 | `qk:MagneticFieldStrength` | — |
| `tax:SaturationMagentization` | `rep:Vector` | 3 | `qk:MagneticFieldStrength` | — |
| `tax:SpinExchangeInteractions` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:BulkModulus` | `rep:Scalar` | — | `qk:Pressure` | — |
| `tax:Compressibility` | `rep:Scalar` | — | `qk:Compressibility` | — |
| `tax:CriticalResolvedShearStress` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:FatigueCrackGrowthRate` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:FatigueLife` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:FatigueLimit` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:CharpyImpactEnergy` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:CrackTipOpeningDisplacement` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:DuctileToBrittleTransitionTemperature` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:ReductionArea` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:Hardness` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:ImpactToughness` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:ModulusOfResilience` | `rep:Scalar` | — | `qk:EnergyDensity` | — |
| `tax:PoissonRatio` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:ShearModulus` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:StrainHardeningExponent` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:StressStrainCurve` | `rep:1Dmap` | — | `qk:ForcePerArea` | 1: `qk:Dimensionless` |
| `tax:TensileStrength` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:TotalElongation` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:Toughness` | `rep:Scalar` | — | `qk:EnergyDensity` | — |
| `tax:UniformElongation` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:Viscosity` | `rep:Scalar` | — | `qk:DynamicViscosity` | — |
| `tax:YieldStrength` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:YoungModulus` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:OpticalBandGap` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:OpticalReflectance` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:OpticalTransmittance` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:0DDefectDensity` | `rep:Scalar` | — | `qk:NumberDensity` | — |
| `tax:0DDefectElectricCharge` | `rep:Scalar` | — | `qk:ElectricCharge` | — |
| `tax:0DDefectFormationEnergy` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:1DDefectDensity` | `rep:Scalar` | — | `qk:NumberDensity` | — |
| `tax:2DDefectMisorientation` | `rep:Scalar` | — | `qk:Angle` | — |
| `tax:2DDefectStackingFaultEnergy` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:Area` | `rep:Scalar` | — | `qk:Area` | — |
| `tax:BETSurfaceArea` | `rep:Scalar` | — | `qk:Area` | — |
| `tax:Density` | `rep:Scalar` | — | `qk:Density` | — |
| `tax:ElectrochemicallyActiveSurfaceArea` | `rep:Scalar` | — | `qk:Area` | — |
| `tax:GrainAspectRatio` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:GrainSize` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:LangmuirSurfaceArea` | `rep:Scalar` | — | `qk:Area` | — |
| `tax:LayerThickness` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:ParticleDiameter` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:ParticleFacet` | `rep:Scalar` | — | `qk:Angle` | — |
| `tax:ParticleHeight` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:ParticleLength` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:ParticleSize` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:ParticleWidth` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:PoreDiameter` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:PoreLimitingDiameter` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:PoreTotalVolume` | `rep:Scalar` | — | `qk:Volume` | — |
| `tax:Porosity` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:RadialDistributionFunction` | `rep:1Dmap` | — | `qk:Dimensionless` | 1: `qk:Length` |
| `tax:RadiusOfGyration` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:SurfaceArea` | `rep:Scalar` | — | `qk:Area` | — |
| `tax:Volume` | `rep:Scalar` | — | `qk:Volume` | — |
| `tax:BoilingTemperature` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:ChemicalPotential` | `rep:Scalar` | — | `qk:ChemicalPotential` | — |
| `tax:EnergyVolumeCurve` | `rep:1Dmap` | — | `qk:Energy` | 1: `qk:Volume` |
| `tax:Fugacity` | `rep:Scalar` | — | `qk:Pressure` | — |
| `tax:GibbsEnergy` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:HeatCapacity` | `rep:Scalar` | — | `qk:EnergyPerTemperature` | — |
| `tax:HeatOfFormation` | `rep:Scalar` | — | `qk:MolarEnergy` | — |
| `tax:HelmholtzEnergy` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:LatentHeatOfFusion` | `rep:Scalar` | — | `qk:SpecificEnergy` | — |
| `tax:MeltingRange` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:MeltingTemperature` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:SpecificHeatCapacity` | `rep:Scalar` | — | `qk:SpecificHeatCapacity` | — |
| `tax:ThermalExpansionCoefficient` | `rep:Scalar` | — | `qk:InverseTemperature` | — |
| `tax:ThermodynamicActivity` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:CarrierDiffusionLength` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:CarrierLifetime` | `rep:Scalar` | — | `qk:Time` | — |
| `tax:HallVoltage` | `rep:Scalar` | — | `qk:ElectricPotential` | — |
| `tax:SpinHallAngle` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:TemperatureCoefficientOfResistance` | `rep:Scalar` | — | `qk:InverseTemperature` | — |
| `tax:DebyeTemperature` | `rep:Scalar` | — | `qk:ThermodynamicTemperature` | — |
| `tax:PhononicBandStructure` | `rep:3Dmap` | — | `qk:Energy` | 1: `rep:Label_kx`, `qk:Wavenumber`; 2: `rep:Label_ky`, `qk:Wavenumber`; 3: `rep:Label_kz`, `qk:Wavenumber` |
| `tax:PhononicDensityOfStates` | `rep:Spectrum` | — | `qk:EnergyDensityOfStates` | 1: `qk:Energy` |
| `tax:PhononicSpecificHeatCapacity` | `rep:Scalar` | — | `qk:SpecificHeatCapacity` | — |

### Mapped in part

> All 11 rows below were resolved later the same day; see "Remaining rows resolved by decision, 2026-10-26".

| Class | Bound as | Left open, and why |
|---|---|---|
| `tax:CorrosionRate` | `rep:Scalar` | Given quantity kind LinearVelocity contradicts the class description ('mass loss per unit area over a specified time'); type mapped, signal left unspecified. |
| `tax:EliashbergFunction` | `rep:Spectrum`, signal `qk:Dimensionless` | Axis quantity kind given as 'Energy or Frequency' (open choice); type and signal mapped, axis left unspecified. |
| `tax:FatigueCrackGrowthThreshold` | `rep:Scalar` | Signal marked 'not in qudt'; type mapped, signal quantity kind left unspecified. |
| `tax:FractureToughness` | `rep:Scalar` | Signal marked 'not in qudt'; type mapped, signal quantity kind left unspecified. |
| `tax:StressIntensityFactor` | `rep:Scalar` | Signal marked 'not in qudt'; type mapped, signal quantity kind left unspecified. |
| `tax:AbsorptionCoefficient` | `rep:Scalar` | Given quantity kind InverseLength fits the name but contradicts the class description ('distance that light ... can travel', a length); type mapped, signal left unspecified. |
| `tax:2DDefectInterfacialEnergy` | `rep:Scalar` | Given quantity kind Energy contradicts the class description ('energy required to form a unit area', i.e. energy per area); type mapped, signal left unspecified. |
| `tax:CryoscopicConstant` | `rep:Scalar` | Signal marked 'not in qudt' (temperature per molality); type mapped, signal quantity kind left unspecified. |
| `tax:HeatOfFusion` | `rep:Scalar` | Given quantity kind MolarEnergy contradicts the class description ('enthalpy change by unit mass', i.e. SpecificEnergy); type mapped, signal left unspecified. |
| `tax:MeanSquaredDisplacement` | `rep:TimeSeries`, axis 1: `qk:Time` | Signal given as Length, but a mean squared displacement has dimension length squared (Area); type and Time axis mapped, signal left unspecified. |
| `tax:Trajectory` | `rep:TimeSeries`, signal `qk:Length`, axis 1: `qk:Time` | TimeSeries with Time axis and signal kind Length taken from the reviewer comment; the n×3 array shape of the signal is not expressible in the module. |

### Not mapped

| Class | Sheet (representation / signal) | Reason |
|---|---|---|
| `tax:CorrosionProperty` | Scalar / — | Parent class (9 subclasses). A binding on it would be inherited by every subclass; only leaf classes are bound. |
| `tax:ElectronicGreensFunction` | Not sure / qudt:Time | Suggested rep:4Dmap (kx, ky, kz, omega); the module has maps up to 3D only (nD maps are planned, not defined). |
| `tax:Permittivity` | Not sure / qudt:Permittivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:PiezoelectricChargeCoefficient` | Not sure / Not in qudt. It is effectively inverse (1 over) qudt:ElectricFieldStrength. | No QUDT quantity kind exists; scalar or tensor open; physically a rank-3 tensor (3x3x3 or 3x6 Voigt). |
| `tax:PiezoelectricStrainCoefficient` | Not sure / Not in qudt. It is effectively inverse (1 over) qudt:ElectricFieldStrength. | Marked as the same quantity as PiezoelectricChargeCoefficient; no representation given. Merge or deprecation is a taxonomy decision. |
| `tax:PiezoelectricVoltageCoefficient` | Not sure / Not in qudt. It is effectively qudt:ElectricFieldStrength/qudt:Stress | No QUDT quantity kind exists; scalar or tensor open; physically a rank-3 tensor. |
| `tax:RelativePermittivity` | Not sure / qudt:Dimensionless | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:MagneticAnisotropyConstant` | Scalar / qudt:MagneticFieldStrength | Given quantity kind MagneticFieldStrength contradicts the class description ('energy density difference'). |
| `tax:MagneticHysteresis` | Not sure / — | Reviewer: 'REMOVE THIS'. Removing a class is not a mapping operation. |
| `tax:MagneticSusceptibility` | Not sure / qudt:MagneticFieldStrength | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. The given quantity kind (MagneticFieldStrength) also conflicts with susceptibility being dimensionless. |
| `tax:Color` | Not sure / — | Signal is a 3-component array (hue, saturation, brightness) that is not a vector; no matching representation type (reviewer: exception). |
| `tax:Photoluminescence` | Not sure / — | Reviewer: phenomenon, not a measurable property; 'REMOVE'. Removing a class is not a mapping operation. |
| `tax:RefractiveIndex` | Not sure / qudtDimensionless | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:1DDefectBurgersVector` | Not sure / — | Lattice-direction notation or scalar magnitude; representation open, no quantity kind given. |
| `tax:Defect` | Not sure / — | Reviewer: multi-value classification; not a quantity. |
| `tax:ElementalComposition` | Not sure / — | Reviewer: list of chemical symbols; not a quantity. |
| `tax:Grain` | Not sure / — | Reviewer: unclear. |
| `tax:Impurity` | Not sure / — | Reviewer: list of chemical symbols (probably); not a quantity. |
| `tax:Morphology` | Not sure / — | Reviewer: unclear. |
| `tax:ParticleShape` | Not sure / — | Reviewer: unclear. |
| `tax:PhaseComposition` | Not sure / — | Reviewer: list of numbers that needs a list of phases; no matching representation type. |
| `tax:PhaseCrystalStructure` | Not sure / — | Reviewer: 'probably an integer (scalar)', i.e. space or point group; undecided. |
| `tax:StandardState` | Not sure / — | Reviewer: defined reference condition, not a measurable quantity. |
| `tax:ElectricalConductivity` | Not sure / qudt:ElectricConductivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:ElectricalResistivity` | Not sure / qudt:Resistivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:ElectronMobility` | Not sure / qudt:Mobility | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:HallCoefficient` | Not sure / not in qudt. It would be qudt:Volume/qudt:Charge | Scalar or rank-3 tensor (no rank-3 type in the module); signal quantity kind not in QUDT. |
| `tax:HoleMobility` | Not sure / qudt:Mobility | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:IonicConductivity` | Not sure / qudt:ElectricConductivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:IonicMobility` | Not sure / qudt:Mobility | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:ThermalConductivity` | Not sure / qudt:ThermalConductivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:ThermalDiffusivity` | Not sure / qudt:ThermalDiffusivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:PhononicThermalConductivity` | Not sure / qudt:ThermalConductivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 518 (was 405) |
| `main.ttl` (taxonomy + module + bindings) | 3847 (was 2358) |

### Verification

| Check | Result |
|---|---|
| Taxonomy part of `main.ttl` (above the module banner) unchanged against the previous `main.ttl` | ✔ identical |
| Every quantity kind used exists and is not deprecated in QUDT 3.5.2; every axis label exists in the module | ✔ |
| HermiT: unsatisfiable classes in `main.ttl` | ✔ none |
| Invalid test bindings flagged (TimeSeries with a Length axis, Scalar with an axis, two axes with the same index, 2Dmap with three axes, Scalar and Tensor2 together) | ✔ all 5 |
| Derived `qudt:hasQuantityKind` of each bound class = signal kind + axis kinds from the sheet (+ any direct restriction of the original taxonomy) | ✔ 137/137 |
| Signal and axis of each bound class carry `qudt:hasQuantityKind` for their own kind | ✔ 137/137 |
| README Turtle examples | ✔ 9 parse, all satisfiable |

A side check confirmed the functional quantity-kind property works as intended: an old test binding that gave CorrosionPotential the signal kind Voltage, loaded next to the new binding (ElectricPotential), made the ontology inconsistent. The test classes now use their own IRIs.

### Discussion: not mapped, open points and suggestions

1. **Scalar or tensor (13 rows): one decision maps them all.** Permittivity, RelativePermittivity, RefractiveIndex, MagneticSusceptibility, ElectricalConductivity, ElectricalResistivity, ElectronMobility, HoleMobility, IonicConductivity, IonicMobility, ThermalConductivity, ThermalDiffusivity, PhononicThermalConductivity. Both options from the earlier discussion are valid OWL and need no module change: one IRI with `rep:Scalar ⊔ (rep:Tensor2 ⊓ Shape "3,3")` (README §5.5), or two IRIs with the same label. Once chosen, these rows map directly; their quantity kinds exist in QUDT 3.5.2 (ElectricConductivity, Resistivity, Mobility, ThermalConductivity, ThermalDiffusivity, Permittivity, Dimensionless) except MagneticSusceptibility (see next point).
2. **Quantity kind contradicts the class description (not mapped, or signal left open).** MagneticAnisotropyConstant (MagneticFieldStrength vs "energy density difference"), MagneticSusceptibility (MagneticFieldStrength vs dimensionless susceptibility), CorrosionRate (LinearVelocity vs "mass loss per unit area over time"), HeatOfFusion (MolarEnergy vs "by unit mass" → SpecificEnergy), AbsorptionCoefficient (InverseLength fits the name, the description defines a length), 2DDefectInterfacialEnergy (Energy vs "per unit area"), MeanSquaredDisplacement (Length vs squared displacement → Area). Either the quantity kind or the description needs adjusting; then the signal can be added.
3. **Direct `qudt:hasQuantityKind` restrictions of the original taxonomy differ from the reviewed sheet (7 of 11).** BoilingTemperature, DebyeTemperature, MeltingTemperature (Temperature vs ThermodynamicTemperature), HallVoltage (Voltage vs ElectricPotential), Fugacity (Fugacity vs Pressure), HeatCapacity (HeatCapacity vs EnergyPerTemperature), ThermalExpansionCoefficient (ThermalExpansionCoefficient vs InverseTemperature). Each of these classes now has both kinds as `qudt:hasQuantityKind` (no contradiction, since that property isn't functional). Suggestion: remove the 11 direct restrictions and let the bindings be the single source, or align the sheet to the more specific QUDT kinds. Not changed here (original taxonomy part untouched).
4. **"Not in qudt" for the stress intensity factor.** FatigueCrackGrowthThreshold, FractureToughness and StressIntensityFactor are marked "not in qudt", but `qk:StressIntensityFactor` exists in QUDT 3.5.2 (dimension A0E0L-0.5I0M1H0T-2D0, matching the reviewer's own vector) and is already declared in the module. Suggestion: use it for all three.
5. **No QUDT quantity kind.** CryoscopicConstant (bound as Scalar, signal open), HallCoefficient, PiezoelectricChargeCoefficient, PiezoelectricVoltageCoefficient. A custom quantity kind would be needed; HallCoefficient and the piezoelectric coefficients additionally need a rank-3 tensor type.
6. **New representation constructs requested by the sheet.** ElectronicGreensFunction: 4D map (kx, ky, kz, ω); the module stops at 3D, nD → mD maps are planned. Color: a signal with three components that is not a vector (hue, saturation, brightness). Trajectory: a TimeSeries whose signal is an n×3 array (bound without the array shape). HallCoefficient, piezoelectric coefficients: rank-3 tensor. 1DDefectBurgersVector: lattice-direction notation or scalar magnitude.
7. **EliashbergFunction axis.** Energy or Frequency; bound as Spectrum with signal Dimensionless and the axis left open. Choosing one (Energy matches the Spectrum convention) completes the binding.
8. **Removal requests (taxonomy decisions, not applied).** Marked for removal by the reviewer: MagneticHysteresis, Photoluminescence, SpectroscopicProperty ("obsolete catch-all"). Unclear or not a quantity, which the reviewer asks to remove: Grain, Morphology, ParticleShape, Defect, ElementalComposition, Impurity, PhaseComposition, PhaseCrystalStructure, StandardState. Deleting classes is outside a mapping operation.
9. **PiezoelectricStrainCoefficient** is marked as the same quantity as PiezoelectricChargeCoefficient: merge or deprecate in the taxonomy.
10. **CorrosionProperty** (parent of 9 classes) is marked Scalar in the sheet; only its leaf classes are bound, so the parent stays unbound.
11. **Sheet typos read as intended:** `qudtDimensionless` (5 rows: OpticalReflectance, OpticalTransmittance, GrainAspectRatio, Porosity, RadialDistributionFunction) read as `qudt:Dimensionless`.
12. **Taxonomy label and IRI observations (not changed):** IRI `…/FracturesProperty` for FractureProperty, IRI `…/Viscosity` for DynamicViscosity, labels SaturationMagentization, PoralizedPotential, ElectricCoercitivity, MagneticCoercitivity.

## Quantity kinds on signal, axis and taxonomy class, 2026-10-26

Supersedes the signal-only property chain described in "Representation module merge" and "`rep:HasQuantityKind` renamed …".

Signal and axis carry their quantity kind as QUDT `qudt:hasQuantityKind`, and the taxonomy class gets the quantity kinds of its signal and of all its axes.

### Changed in the representation module (`representation.ttl` and the module section of `main.ttl`)

| Item | Before | After |
|---|---|---|
| New property `rep:HasComponent` | — | domain `rep:Representation`, range `rep:ComponentProperty`; super-property of `rep:HasSignal` and `rep:HasAxis`; not used in bindings |
| `rep:HasSignal`, `rep:HasAxis` | — | `rdfs:subPropertyOf rep:HasComponent` |
| `rep:HasComponentQuantityKind` | functional, domain `rep:ComponentProperty` | unchanged, plus `rdfs:subPropertyOf qudt:hasQuantityKind` |
| Property chain on `qudt:hasQuantityKind` | `HasRepresentation ∘ HasSignal ∘ HasComponentQuantityKind` | `HasRepresentation ∘ HasComponent ∘ HasComponentQuantityKind` |

### Effect

```
[signal] ─HasComponentQuantityKind─▶ qk:A    ┄qudt:hasQuantityKind┄▶ qk:A      (sub-property)
[axis]   ─HasComponentQuantityKind─▶ qk:B    ┄qudt:hasQuantityKind┄▶ qk:B      (sub-property)
tax:C    ┄qudt:hasQuantityKind┄▶ qk:A, qk:B                                   (chain)
```

- Bindings are written exactly as before (`rep:HasSignal` / `rep:HasAxis` → `rep:HasComponentQuantityKind`).
- `rep:HasComponentQuantityKind` stays a simple property, so it remains functional in OWL 2 DL; together with the quantity-kind distinctness axiom the reasoner still rejects two kinds on one signal or axis and a non-Time TimeSeries axis.
- On a taxonomy class, `qudt:hasQuantityKind` now means "quantity kinds of its data" (signal and axes), not only the signal kind. Which kind belongs to the signal is still stated in the binding. A query such as `?c qudt:hasQuantityKind qk:Energy` also returns classes that have Energy only on an axis.
- `qudt:hasQuantityKind` itself gets no new axioms (no domain, not functional), so QUDT's own use of it is unaffected.

---

# History

## `rep:HasQuantityKind` renamed to `rep:HasComponentQuantityKind`, 2026-10-25

The module's quantity-kind property for signals and axes was renamed so it can no longer be confused with QUDT's `qudt:hasQuantityKind`. The two names differed only in prefix and capitalisation, which made them hard to tell apart in viewers, queries and hand-written bindings.

| | `qudt:hasQuantityKind` | `rep:HasComponentQuantityKind` |
|---|---|---|
| Owner | QUDT | representation module |
| Used on | taxonomy property classes | signal and axis nodes |
| Characteristics | not functional, no domain | functional, domain `rep:ComponentProperty` |
| Link | derived from the signal's kind through the property chain | — |

The name keeps the module's UpperCamelCase convention (`rep:HasSignal`, `rep:HasAxis`).

### Changed

| File | Occurrences renamed |
|---|---:|
| `representation.ttl` (declaration, label, ontology comment, label-term definition, property chain, TimeSeries axiom, distinctness comment) | 7 |
| `main.ttl` (module section and the 78 bindings) | 60 |
| README (tables, diagrams, RDF examples, DL) | 53 |

The original taxonomy part of `main.ttl` never used this property and is unchanged. Meaning is unchanged: same characteristics, same axioms, same bindings.

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 405 (unchanged) |
| `main.ttl` | 2358 (unchanged) |

### Verification

| Check | Result |
|---|---|
| `rep:HasQuantityKind` left in `representation.ttl` / `main.ttl` / README | ✔ 0 / 0 / 0 |
| `main.ttl` diff against the previous version | ✔ only the rename (plus banner re-wrap) |
| HermiT: unsatisfiable classes in `main.ttl` | ✔ none |
| Invalid test bindings flagged (without the tests' own distinctness axiom) | ✔ all 5 |
| README Turtle examples | ✔ 9 parse, all satisfiable |
| Inferred `qudt:hasQuantityKind` of the 78 bound classes equals the sheet | ✔ 78/78 |

## Distinctness of quantity kinds, 2026-10-25

One axiom added: the quantity kinds are declared pairwise different (`owl:AllDifferent`).

### Reason

OWL makes no unique-name assumption: `qk:Length` and `qk:Time` may denote the same individual unless stated otherwise. Without this axiom, the functional `rep:HasQuantityKind` and the TimeSeries rule (`∀ HasAxis . (HasQuantityKind value qk:Time)`) only add facts and never detect an error. A TimeSeries axis given `qk:Length` was read as `qk:Length = qk:Time`, not flagged.

The earlier verification ("wrong TimeSeries axis flagged") passed only because the test file declared its own `owl:AllDifferent` over the test quantity kinds. The tests now run without it.

### Added

| File | Where | Content |
|---|---|---|
| `representation.ttl` | end of section 4b (quantity kinds) | `owl:AllDifferent` over the 23 module quantity kinds |
| `main.ttl` | the same position in the appended module section | the same axiom, also listing the five kinds the taxonomy already used (ChemicalPotential, Fugacity, HeatCapacity, ThermalExpansionCoefficient, Volume): 28 members |

Unchanged: the original taxonomy part of `main.ttl`, `qudt:hasQuantityKind`, the 11 direct restrictions, all properties, types and the 78 bindings. The original taxonomy has no functional property over quantity kinds, so the axiom has no effect there.

Upkeep: a quantity kind added later must also be added to this list.

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 405 (was 357) |
| `main.ttl` | 2358 (was 2300) |

### Verification

| Check | Result |
|---|---|
| `main.ttl` diff against the previous version | ✔ only the new axiom (16 lines) |
| List members = all declared `qudt:QuantityKind` individuals; covers every kind used in a restriction | ✔ 28 / ✔ |
| HermiT: unsatisfiable classes in `main.ttl` | ✔ none |
| Test bindings **without** their own distinctness axiom: TimeSeries with a Length axis | ✔ unsatisfiable (was satisfiable before this change) |
| Other invalid test bindings (Scalar with axis, Scalar and Tensor2, two axes same index, 2Dmap with three axes) | ✔ unsatisfiable |
| README Turtle examples | ✔ 9 parse, all satisfiable |
| Inferred `qudt:hasQuantityKind` of the 78 bound classes equals the sheet | ✔ 78/78 |

## RDF Data Cube (qb) layer removed, 2026-10-25

The optional qb layer was removed from the representation module, and therefore from `main.ttl`. The taxonomy bindings didn't use qb, so they are unchanged.

### Removed

| Item | Count |
|---|---|
| `qb:` prefix and declarations of qb classes and properties | 13 declarations |
| Subclass links to qb: representation types ⊑ `qb:DataSet`; `rep:ComponentProperty` ⊑ `qb:ComponentProperty`; `rep:Signal` ⊑ `qb:MeasureProperty`; `rep:Axis` ⊑ `qb:DimensionProperty` | 9 links |
| DSD-layer axioms: strict roles, one dimension per specification, measure-only DSD (Scalar, Vector, Tensor2), maximum dimensions (1D/2D/3D map), TimeSeries dimensions | 9 axioms |
| `rep:DataStructureDefinition`, `rep:Observation`, `rep:Extent` | 3 entities |
| Deprecated `rep:HasDataStructureDefinition`, `rep:HasComponent` (referenced the DSD only) | 2 properties |

Unchanged: `rep:Signal`, `rep:Axis`, all representation types, their axioms, the axis labels, the quantity kinds, the property chain and the 78 bindings.

### Files

| File | Triples |
|---|---:|
| `representation.ttl` | 357 |
| `main.ttl` (taxonomy + module + bindings) | 2300 |

### Verification

| Check | Result |
|---|---|
| qb IRIs left in `representation.ttl` / `main.ttl` | ✔ 0 / 0 |
| Original taxonomy triples missing in `main.ttl` | ✔ none |
| HermiT: unsatisfiable classes in `main.ttl` | ✔ none |
| Invalid test bindings still flagged (wrong TimeSeries axis, Scalar with axis, wrong axis count, two labelled axes on a 1Dmap, Scalar and Tensor2 together) | ✔ |
| Inferred `qudt:hasQuantityKind` of the 78 bound classes equals the sheet | ✔ 78/78 |

### Consequences

- No Data Cube structures for flat SPARQL or qb-style validation of future datasets. If needed later, a separate alignment file can add the qb subclass links and DSD axioms again without changing any binding.
- The README no longer describes a derived layer; its sections were renumbered.

## Representation bindings from HasRepresentation_Adhoc, 2026-10-25

> **Superseded** by "Representation bindings remapped from the reviewed HasRepresentation_Adhoc sheet, 2026-10-26" at the top of this file. The tables below describe the first, partly reviewed sheet and are kept as history.

Rows of the HasRepresentation_Adhoc sheet mapped onto `main.ttl` as `rep:HasRepresentation` bindings. This is a mapping operation only: no class, property, individual or axiom was added to the representation module, and the taxonomy classes themselves are unchanged.

### Summary

| | Count |
|---|---:|
| Sheet rows with an entry | 88 |
| Mapped fully | 74 |
| Mapped in part | 4 |
| Not mapped (see Discussion) | 9 |
| Comment only, nothing to map (PiezoelectricProperty, tree duplicate) | 1 |
| Rows not yet reviewed in the sheet | 92 |
| Triples added | 1055 |

### Appended to `main.ttl`

One `rdfs:subClassOf` restriction per mapped class, written as a separate statement below the banner `REPRESENTATION BINDINGS (mapped from HasRepresentation_Adhoc)` at the end of the file. The existing class blocks aren't edited.

### Mapping rules applied

| Sheet entry | Mapped to |
|---|---|
| Representation `Scalar` / `Spectrum` | `rep:Scalar` / `rep:Spectrum` |
| Representation `VolumeData` | `rep:3Dmap` (VolumeData is renamed 3Dmap in the representation module) |
| `Not sure` + comment "vector of dimension 3" | `rep:Vector` with `rep:Shape "3"` |
| `Not sure` + comment "rep:1Dmap Stress(Strain)" | `rep:1Dmap` |
| `Not sure` for ElectricHysteresis (comment: a map P(E)) | `rep:1Dmap`, the generic 1D map introduced for exactly this case in the 21/10 thread |
| `qudt:<Name>` in Signal / Axis | `qk:<Name>` (QUDT quantity-kind namespace); every kind used is already declared in `main.ttl` |
| Axis label `kx`, `ky`, `kz`, `E` | existing individuals `rep:Label_kx`, `rep:Label_ky`, `rep:Label_kz`, `rep:Label_E` |
| Axis without a label | axis bound by index and quantity kind only |
| Order of axes in the cell | `rep:AxisIndex` 1, 2, 3 |
| Representation without a signal quantity kind | type only: `rep:HasRepresentation some rep:<Type>` |

### Mapped

| Class | Type | Shape | Signal | Axes (index: label, quantity kind) |
|---|---|---|---|---|
| `tax:AnodicPartialCurrent` | `rep:Scalar` | — | — | — |
| `tax:CathodicPartialCurrent` | `rep:Scalar` | — | — | — |
| `tax:AnodicPartialCurrentCorrosion` | `rep:Scalar` | — | — | — |
| `tax:CorrosionPotential` | `rep:Scalar` | — | `qk:Voltage` | — |
| `tax:CorrosionRate` | `rep:Scalar` | — | — | — |
| `tax:FreeCorrosionCurrent` | `rep:Scalar` | — | — | — |
| `tax:FreeCorrosionPotential` | `rep:Scalar` | — | — | — |
| `tax:PassivationCurrent` | `rep:Scalar` | — | — | — |
| `tax:PassivationPotential` | `rep:Scalar` | — | `qk:Voltage` | — |
| `tax:PittingInitiationPotential` | `rep:Scalar` | — | `qk:Voltage` | — |
| `tax:PoralizedPotential` | `rep:Scalar` | — | — | — |
| `tax:ReactivationPotential` | `rep:Scalar` | — | — | — |
| `tax:TranspassivationPotential` | `rep:Scalar` | — | — | — |
| `tax:RedoxPotential` | `rep:Scalar` | — | — | — |
| `tax:StandardElectrodePotential` | `rep:Scalar` | — | — | — |
| `tax:BandGapElectronicBowingCoefficient` | `rep:Scalar` | — | — | — |
| `tax:BindingEnergyExciton` | `rep:Scalar` | — | — | — |
| `tax:CarrierDensity` | `rep:Scalar` | — | — | — |
| `tax:CoulombInteractions` | `rep:Scalar` | — | — | — |
| `tax:DielectricStrength` | `rep:Scalar` | — | — | — |
| `tax:EffectiveElectronMass` | `rep:Scalar` | — | — | — |
| `tax:EffectiveHoleMass` | `rep:Scalar` | — | — | — |
| `tax:ElectronicBandGap` | `rep:Scalar` | — | — | — |
| `tax:ElectronicBandStructure` | `rep:3Dmap` | — | `qk:Energy` | 1: `rep:Label_kx`, `qk:Wavenumber`; 2: `rep:Label_ky`, `qk:Wavenumber`; 3: `rep:Label_kz`, `qk:Wavenumber` |
| `tax:ElectronicCompressibility` | `rep:Scalar` | — | — | — |
| `tax:ElectronicDensityOfStates` | `rep:Spectrum` | — | `qk:EnergyDensityOfStates` | 1: `qk:Energy` |
| `tax:ElectronicGreensFunction` | `rep:Scalar` | — | — | — |
| `tax:ElectronicSusceptibility` | `rep:Scalar` | — | — | — |
| `tax:FermiLevel` | `rep:Scalar` | — | — | — |
| `tax:FermiSurface` | `rep:3Dmap` | — | `qk:Energy` | 1: `rep:Label_kx`, `qk:Wavenumber`; 2: `rep:Label_ky`, `qk:Wavenumber`; 3: `rep:Label_kz`, `qk:Wavenumber` |
| `tax:ElectricCoercitivity` | `rep:Scalar` | — | — | — |
| `tax:ElectricCurieTemperature` | `rep:Scalar` | — | — | — |
| `tax:ElectricHysteresis` | `rep:1Dmap` | — | `qk:ElectricPolarization` | 1: `rep:Label_E`, `qk:ElectricField` |
| `tax:RemanentPolarization` | `rep:Scalar` | — | — | — |
| `tax:SaturationPolarization` | `rep:Scalar` | — | — | — |
| `tax:ElectromechanicalCouplingFactor` | `rep:Scalar` | — | — | — |
| `tax:MechanicalQualityFactor` | `rep:Scalar` | — | — | — |
| `tax:SpinOrbitCouplingConstant` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:SuperconductingCoherenceLength` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:SuperconductingCriticalTemperature` | `rep:Scalar` | — | `qk:Temperature` | — |
| `tax:SuperconductingGap` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:MagneticAnisotropyField` | `rep:Vector` | 3 | `qk:MagneticFieldStrength` | — |
| `tax:MagneticCoercitivity` | `rep:Scalar` | — | `qk:MagneticFieldStrength` | — |
| `tax:MagneticCurieTemperature` | `rep:Scalar` | — | `qk:Temperature` | — |
| `tax:MagneticSquareness` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:MaximumEnergyProduct` | `rep:Scalar` | — | `qk:EnergyDensity` | — |
| `tax:Permeability` | `rep:Scalar` | — | `qk:ElectromagneticPermeability` | — |
| `tax:RemanentMagnetization` | `rep:Vector` | 3 | `qk:MagneticFieldStrength` | — |
| `tax:SaturationMagentization` | `rep:Vector` | 3 | `qk:MagneticFieldStrength` | — |
| `tax:SpinExchangeInteractions` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:BulkModulus` | `rep:Scalar` | — | `qk:Pressure` | — |
| `tax:Compressibility` | `rep:Scalar` | — | `qk:Compressibility` | — |
| `tax:CriticalResolvedShearStress` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:FatigueCrackGrowthRate` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:FatigueLife` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:FatigueLimit` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:CharpyImpactEnergy` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:CrackTipOpeningDisplacement` | `rep:Scalar` | — | `qk:Length` | — |
| `tax:DuctileToBrittleTransitionTemperature` | `rep:Scalar` | — | `qk:Temperature` | — |
| `tax:ReductionArea` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:Hardness` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:ImpactToughness` | `rep:Scalar` | — | `qk:Energy` | — |
| `tax:ModulusOfResilience` | `rep:Scalar` | — | `qk:EnergyDensity` | — |
| `tax:PoissonRatio` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:ShearModulus` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:StrainHardeningExponent` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:StressStrainCurve` | `rep:1Dmap` | — | `qk:ForcePerArea` | 1: `qk:Dimensionless` |
| `tax:TensileStrength` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:TotalElongation` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:Toughness` | `rep:Scalar` | — | `qk:EnergyDensity` | — |
| `tax:UniformElongation` | `rep:Scalar` | — | `qk:Dimensionless` | — |
| `tax:Viscosity` | `rep:Scalar` | — | `qk:DynamicViscosity` | — |
| `tax:YieldStrength` | `rep:Scalar` | — | `qk:ForcePerArea` | — |
| `tax:YoungModulus` | `rep:Scalar` | — | `qk:ForcePerArea` | — |

### Mapped in part

| Class | Mapped | Left out |
|---|---|---|
| `tax:EliashbergFunction` | `rep:Spectrum`, signal `qk:Dimensionless` | Axis quantity kind given as 'Energy or Frequency' (open choice); type and signal mapped, axis left unspecified. |
| `tax:FatigueCrackGrowthThreshold` | `rep:Scalar` | Signal marked 'not in qudt'; type mapped, signal quantity kind left unspecified. |
| `tax:FractureToughness` | `rep:Scalar` | Signal marked 'not in qudt'; type mapped, signal quantity kind left unspecified. |
| `tax:StressIntensityFactor` | `rep:Scalar` | Signal marked 'not in qudt'; type mapped, signal quantity kind left unspecified. |

### Not mapped

| Class | Sheet entry | Reason |
|---|---|---|
| `tax:CorrosionProperty` | Scalar | Parent class (9 subclasses). A binding on it would be inherited by every subclass; only leaf classes are bound. |
| `tax:Permittivity` | Not sure; signal: qudt:Permittivity | Scalar or rank-2 (3x3) tensor. The modelling choice (one IRI with Scalar ⊔ Tensor2, or two IRIs with the same label) is still open. |
| `tax:PiezoelectricChargeCoefficient` | Not sure; signal: Not in qudt. It is effectively inverse ( | No QUDT quantity kind exists; scalar-or-tensor open; physically a rank-3 tensor (3x3x3 or 3x6 Voigt), not 3x3. |
| `tax:PiezoelectricStrainCoefficient` | Not sure | Marked as the same quantity as PiezoelectricChargeCoefficient; no representation given. Merge or deprecation is a taxonomy decision. |
| `tax:PiezoelectricVoltageCoefficient` | Not sure; signal: Not in qudt. It is effectively qudt:Elec | No QUDT quantity kind exists; scalar-or-tensor open; physically a rank-3 tensor. |
| `tax:RelativePermittivity` | Not sure; signal: qudt:Dimensionless | Scalar or 3x3 tensor, like Permittivity; same open modelling choice. |
| `tax:MagneticAnisotropyConstant` | Scalar; signal: qudt:MagneticFieldStrength | Given quantity kind MagneticFieldStrength contradicts the class description ('energy density difference'). |
| `tax:MagneticHysteresis` | Not sure | Marked 'REMOVE THIS'. Removing a class is not a mapping operation. |
| `tax:MagneticSusceptibility` | Not sure; signal: qudt:MagneticFieldStrength | Scalar or 3x3 tensor; same open modelling choice. The given quantity kind (MagneticFieldStrength) also conflicts with susceptibility being dimensionless. |

### Verification

| Check | Result |
|---|---|
| Every IRI used in the bindings was already defined in `main.ttl` | ✔ no new entity |
| No new named individual, class or property | ✔ |
| Mapped classes with a pre-existing direct `qudt:hasQuantityKind` restriction | ✔ none (no conflict) |
| HermiT: unsatisfiable classes | ✔ none |
| Inferred `qudt:hasQuantityKind` of each mapped class equals the sheet's signal quantity kind | ✔ 78/78 |
| OWL 2 syntax: no intersection with fewer than two operands | ✔ |

### Discussion: not mapped, open points and suggestions

**Open modelling decisions**
1. **Scalar-or-tensor quantities** (Permittivity, RelativePermittivity, MagneticSusceptibility). The choice is between one IRI with `Scalar ⊔ Tensor2`, or two IRIs with the same label. Either can be written with the existing module once decided. Permeability is mapped as Scalar only; it may belong to the same group.
2. **CorrosionProperty** is a parent class. If all its subclasses are scalars, the 9 leaf bindings already cover it; a binding on the parent would be inherited by every subclass.
3. **Piezoelectric coefficients**
   - PiezoelectricChargeCoefficient and PiezoelectricVoltageCoefficient have no QUDT 3.5.2 quantity kind and need local FAIRmat kinds, which would be new individuals.
   - They are physically rank-3 tensors (3×3×3, or 3×6 in Voigt notation) rather than 3×3.
   - PiezoelectricStrainCoefficient is marked as the same quantity as PiezoelectricChargeCoefficient; merge or deprecate.
4. **MagneticHysteresis** is marked for removal. Deprecation (`owl:deprecated true`) or deletion is a taxonomy change, not a mapping.

**Quantity kinds to review**
5. **MagneticAnisotropyConstant:** the sheet gives MagneticFieldStrength, but the description says energy density. `qk:EnergyDensity` would match the description.
6. **MagneticSusceptibility:** the sheet gives MagneticFieldStrength, but susceptibility is dimensionless.
7. **FatigueCrackGrowthThreshold, FractureToughness, StressIntensityFactor** are marked "not in qudt", but `qk:StressIntensityFactor` exists in QUDT 3.5.2 (already declared in `main.ttl`) with exactly the given dimension vector A0E0L-0.5I0M1H0T-2D0. If confirmed, the three signal quantity kinds can be mapped without adding anything.
8. **RemanentMagnetization, SaturationMagentization** are mapped as MagneticFieldStrength, as given. `qk:Magnetization` has the same dimension and is the more specific kind (it would need to be declared).
9. **StressStrainCurve** axis is mapped as Dimensionless, as given. `qk:Strain` is the more specific kind (it would need to be declared).
10. **ElectricHysteresis** axis uses `qk:ElectricField`; the piezoelectric comments use `qk:ElectricFieldStrength`. Both exist in QUDT with the same dimension; one should be chosen for consistency.

**Representation details to review**
11. **EliashbergFunction** axis: "Energy or Frequency". The axis was left unspecified; choosing one (Energy is the Spectrum default) completes the mapping.
12. **ElectronicBandStructure** is mapped as a 3Dmap k → Energy, as given. A band structure has several bands (E_n(k)), so the signal may need to be a vector over the band index. It currently has the same binding as FermiSurface.
13. **Axis labels.** ElectronicDensityOfStates and StressStrainCurve axes have no label in the sheet. Labels such as "t" or "ε" don't exist yet as `rep:AxisLabelTerm` individuals.
14. **30 Scalars have no signal quantity kind** yet (mostly ChemicalProperty and ElectronicProperty); their type is mapped and the quantity kind can be added later.

**Sheet edits not applied (outside the mapping scope)**
15. Label change Viscosity → DynamicViscosity (IRI stays `/Viscosity`); the binding is on `tax:Viscosity`.
16. Description addition for MagneticAnisotropyConstant (note on the first anisotropy constant).
17. "Also listed under …" text on PiezoelectricProperty and SuperconductingProperty: these come from the sheet's tree layout and shouldn't go into `rdfs:comment`.
18. The sheet's "Representation types" tab still lists Profile, DepthProfile, Image and VolumeData and a units table; it should be updated to the current types.
19. 92 rows (OpticalProperty, SpectroscopicProperty, StructuralProperty, ThermodynamicProperty, TransportProperty, VibrationalProperty) aren't reviewed in the sheet yet.

## Representation module merge, 2026-10-25

`representation.ttl` merged into `main.ttl`. No content from the HasRepresentation_Adhoc sheet is included in this change; taxonomy bindings follow in the next stage.

### Changed in place (minor fixes)

| Change | Where | Detail |
|---|---|---|
| QUDT schema namespace updated | line 3 (`@prefix qudt:`) | `http://qudt.org/2.1/schema/qudt/` → `http://qudt.org/schema/qudt/` (current, version-free). This moves all `qudt:` terms to the namespace used by the representation module, so `qudt:hasQuantityKind` and `qudt:QuantityKind` are one property and one class. No 2.1 IRIs remain. |
| Duplicate restrictions collapsed | 11 classes | Each `qudt:hasQuantityKind` restriction appeared five times with the same value; four copies removed per class. The restriction set itself is unchanged (11 class / quantity-kind pairs before and after). |

Classes with collapsed restrictions: BoilingTemperature, ChemicalPotential, DebyeTemperature, Fugacity, GibbsEnergy, HallVoltage, HeatCapacity, HelmholtzEnergy, MeltingTemperature, ThermalExpansionCoefficient, Volume.

### Appended at the end of the file

All new content sits below the banner `REPRESENTATION MODULE (merged from representation.ttl)`.

| Addition | Content |
|---|---|
| Prefix declarations | `rep:`, `tax:`, `qb:`, `qudt:`, `qk:`, `owl:`, `rdf:`, `rdfs:`, `xsd:`, `skos:` (Turtle allows prefixes mid-file) |
| Representation module | the full content of `representation.ttl`: classes, properties, representation types, axis labels, QUDT 3.5.2 quantity kinds, optional Data Cube (DSD) layer and deprecated properties |
| Quantity-kind typing | `qk:ChemicalPotential`, `qk:Fugacity`, `qk:HeatCapacity`, `qk:ThermalExpansionCoefficient`, `qk:Volume`, already used by the taxonomy, typed as `qudt:QuantityKind` with `rdfs:isDefinedBy` QUDT 3.5.2. All five exist and are not deprecated in QUDT 3.5.2. |

The module's own `owl:Ontology` header (`http://fairmat-nfdi.eu/taxonomy/representation`) was not copied, so `main.ttl` keeps a single ontology header, `http://fairmat-nfdi.eu/taxonomy`. Its description is kept as a comment in the banner.

### Unchanged

- All taxonomy classes, labels, alternative labels, comments and the class hierarchy. No named triple of the original file is missing in the merged file.
- The existing `qudt:hasQuantityKind` restrictions on the 11 classes above (values unchanged; only the duplicates were removed).
- Existing quantity-kind individuals and their `rdfs:label` values.

### Verification

| Check | Result |
|---|---|
| Merged file parses (rdflib) | ✔ 1387 triples |
| Original named triples present in merged file | ✔ none missing |
| Remaining `qudt.org/2.1` IRIs | ✔ 0 |
| `owl:Ontology` headers | ✔ 1 |
| HermiT: unsatisfiable classes in merged file | ✔ none |
| HermiT with test bindings: valid bindings satisfiable, invalid ones unsatisfiable | ✔ |
| Inference through the property chain (CorrosionPotential instance → `qk:Voltage`) | ✔ |

### Next stage (not in this change)

- Taxonomy bindings (`rep:HasRepresentation`) from the HasRepresentation_Adhoc sheet.
- Label and description edits from the sheet (Viscosity → DynamicViscosity, MagneticAnisotropyConstant note).
- Local FAIRmat quantity kinds for PiezoelectricChargeCoefficient and PiezoelectricVoltageCoefficient (no QUDT 3.5.2 kind exists).
- For classes that get a binding: remove or align their direct `qudt:hasQuantityKind` restriction with the signal quantity kind.
