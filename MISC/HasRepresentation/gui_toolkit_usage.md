# Tools and usage — representation module

How to model with the representation module and check the result with a
reasoner: with the GUI, by hand at class level (TBox), and with instance data
(ABox). The axioms and per-type examples are in `README.md`.

---

## 1. Setup

| Need | For | Install (Ubuntu/Debian; equivalents on other systems) |
|---|---|---|
| Python 3.9+ and `rdflib` | GUI, scripts | `pip install rdflib` |
| `tkinter` | GUI window | `sudo apt install python3-tk` (bundled on Windows/macOS) |
| Java (JRE) | HermiT reasoner | `sudo apt install default-jre` |
| `HermiT.jar` | HermiT reasoner | `pip install owlready2` (ships HermiT.jar, found automatically), or set `HERMIT_JAR=/path/HermiT.jar`, or put `HermiT.jar` next to `rep_modeller.py` |

Recommended: a virtual environment.

```bash
python3 -m venv ~/rep-env
source ~/rep-env/bin/activate
pip install rdflib owlready2
```

| File | What it is |
|---|---|
| `rep_modeller.py` | GUI modelling assistant (also importable: `write_for_hermit`, `run_hermit`, `explain_unsat`) |
| `merge_representation.py` | rebuilds `main.ttl` from the original taxonomy + `representation.ttl` (append-only) |

---

## 2. GUI — `rep_modeller.py`

```bash
source ~/rep-env/bin/activate
python rep_modeller.py main.ttl
```

The GUI is a **modelling assistant**. It contains no reasoning rules: every
verdict and every reason comes from HermiT and the axioms in the ontology. It
never writes to `main.ttl`.

### 2.1 Layout

| Area | Purpose |
|---|---|
| 1 Ontology | path to `main.ttl` (must contain the representation module), **Load** |
| 2 Class | taxonomy class; type to filter. If the class already has a representation restriction in `main.ttl`, it is loaded into the form |
| 3 Representation | Scalar, Profile, Spectrum, TimeSeries, DepthProfile, Image, VolumeData (with rank) |
| 4 Components and units | role (dimension / measure), component, unit on the spec → **Add**; **Remove component**, **Clear**, **Check consistency (HermiT)** |
| Preview (Turtle, live) | the restriction for the current form as Turtle; **Copy Turtle** |
| Reasoner | diagram of the form; after a check: HermiT's raw output, then the reason; **Copy** |

### 2.2 Workflow

| Step | Action | Result |
|---|---|---|
| 1 | Load `main.ttl` | class, type, component and unit lists are filled from the file |
| 2 | Choose class and representation type | Preview and diagram appear |
| 3 | Add components: role + component + unit | Preview updates on every add / remove / clear |
| 4 | **Check consistency (HermiT)** | `main.ttl` + the form are written to `temp.ttl` (system temp folder, `…/rep_modeller/temp.ttl`); HermiT runs on it |
| 5 | Read the Reasoner pane | temp file path, command, exit code, HermiT's output verbatim |
| 6 | If the class is unsatisfiable | **Reason**: the minimal set of axioms that together cause it (see 2.4) |
| 7 | Keep the result | **Copy Turtle** and paste into your ontology (or apply in Protégé) |

Any choice is allowed, on purpose: you can model mistakes and see how the
axioms react.

| Input | How |
|---|---|
| a listed component or unit | pick from the drop-down (kind shown as `[Axis]` / `[Signal]`) |
| an external component or unit | type `http://…`, `<http://…>` or `prefix:name` with a prefix known in `main.ttl` (e.g. `unit:M`) |
| no unit | choose `(none)` (units are optional) |

### 2.3 Reading HermiT's output

| HermiT prints | Meaning |
|---|---|
| `Classes equivalent to 'owl:Nothing':` followed only by `owl:Nothing` | everything is satisfiable: the form is accepted |
| … followed by your class (shown in red) | your class is **unsatisfiable**: the form contradicts the axioms |
| … followed by other classes | those classes are unsatisfiable too (e.g. subclasses of your class) |
| `InconsistentOntologyException` (exit code 1) | the ontology as a whole has no model (only possible with individuals, see §4 below) |
| `Could not parse ontology` | HermiT could not read `temp.ttl`; status bar says so |
| `Could not run HermiT: Java not found …` | install Java or set `JAVA_EXE` |

### 2.4 The Reason

When HermiT lists your class, the GUI re-runs HermiT on smaller and smaller
subsets of `temp.ttl` until only the **smallest set of axioms that still makes
the class unsatisfiable** remains (removing any one of them makes it
satisfiable). Each axiom is shown in Manchester syntax, marked `[your form]` or
`[ontology]`, with the ontology's `rdfs:comment` as context. This takes about
15–30 HermiT runs (≈ 12–25 s).

Examples (verified):

| Form | Reason HermiT finds |
|---|---|
| Scalar with a dimension | Scalar "measures only" axiom + your form |
| TimeSeries with `rep:Energy` axis | TimeSeries `dimension only {Time}` + components distinct + your form |
| DepthProfile with `rep:Depth` in `unit:K` | Length unit whitelist + units distinct + `rep:Depth HasQuantityKind Length` + your form |
| Image with X, Y, Z | Image rank limit + one dimension per spec + components distinct + your form |
| Profile with `rep:Energy` as measure | strict roles + `rep:Energy Type Axis` + Axis/Signal disjoint + your form |

What HermiT accepts although it is a modelling mistake (OWL open world):
fewer dimensions than the rank, no measure, the same component
repeated, external IRIs, Spectrum with a non-energy axis.

---

## 3. TBox usage — modelling a taxonomy class

A taxonomy class gets **one nested restriction**. Example: electronic density of
states as a spectrum, energy axis in eV, intensity in counts. This is exactly
what the GUI generates for that form.

```turtle
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

tax:ElectronicDensityOfStates rdfs:subClassOf [ a owl:Restriction ;
    owl:onProperty rep:HasRepresentation ;
    owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
        rep:Spectrum
        [ a owl:Restriction ; owl:onProperty qb:structure ;
          owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
              rep:DataStructureDefinition
              [ a owl:Restriction ; owl:onProperty qb:component ;
                owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
                    qb:ComponentSpecification
                    [ a owl:Restriction ; owl:onProperty qb:dimension ; owl:hasValue rep:Energy ]
                    [ a owl:Restriction ; owl:onProperty rep:HasUnit  ; owl:hasValue unit:EV ] ) ] ]
              [ a owl:Restriction ; owl:onProperty qb:component ;
                owl:someValuesFrom [ a owl:Class ; owl:intersectionOf (
                    qb:ComponentSpecification
                    [ a owl:Restriction ; owl:onProperty qb:measure ; owl:hasValue rep:Intensity ]
                    [ a owl:Restriction ; owl:onProperty rep:HasUnit ; owl:hasValue unit:COUNT ] ) ] ]
          ) ] ]
    ) ] ] .
```

The same in Manchester syntax (Protégé: class → *SubClass Of* → **+** → *Class expression editor*):

```text
HasRepresentation some (Spectrum
  and (structure some (DataStructureDefinition
    and (component some (ComponentSpecification and (dimension value Energy) and (HasUnit value EV)))
    and (component some (ComponentSpecification and (measure value Intensity) and (HasUnit value COUNT))))))
```

### 3.1 Pattern rules

| Part | How |
|---|---|
| representation type | `rep:HasRepresentation some (rep:<Type> and …)` — the type class carries rank and rules |
| one component spec per component | a separate `qb:component some (qb:ComponentSpecification and …)` for each dimension and each measure |
| axis | `qb:dimension value rep:<Axis>` |
| signal | `qb:measure value rep:<Signal>` |
| unit (optional) | `rep:HasUnit value unit:<U>` **on the spec**, never on the component (the component's canonical unit stays as it is) |
| several classes | write one restriction per class; a restriction on a parent class is inherited by all its subclasses |
| different units per class | allowed, because each class has its own spec (e.g. Depth in µm for one class, nm for another) |

### 3.2 Do / don't

| Do | Don't |
|---|---|
| put the restriction on leaf classes, or on a parent only if *all* children share it | give a parent and a child representations of different rank (`HasRepresentation` is functional) |
| one component per spec | repeat a component to "fill" the rank (OWL counts it once) |
| keep units on specs | add `rep:HasUnit` to `rep:Depth` etc. (they already have a canonical unit; a second one is a contradiction) |
| check with HermiT after editing | rely on the GUI preview alone |

### 3.3 Checking a TBox file without the GUI

```python
from rdflib import Graph
from rep_modeller import write_for_hermit, run_hermit

g = Graph().parse("main.ttl")
g.parse("my_classes.ttl")              # your restrictions
write_for_hermit(g, "temp.ttl")        # Turtle that HermiT's parser always reads
print(run_hermit("temp.ttl").output)   # 'Classes equivalent to owl:Nothing: …'
```

Or directly: `java -cp HermiT.jar org.semanticweb.HermiT.cli.CommandLine -U file:///path/temp.ttl`.

Note: HermiT's Turtle parser is old and rejects some shorthand (e.g. `1e+01`).
`write_for_hermit` avoids that; with other tools, give HermiT N-Triples or RDF/XML.

---

## 4. ABox usage — instance data

At instance level the same axioms apply to named individuals: the material
property sample, its dataset, the DSD, the component specifications and the
observations. A violation makes the whole ontology **inconsistent**
(HermiT: `InconsistentOntologyException`).

### 4.1 Valid example — spectrum with three points

```turtle
@prefix ex:   <http://example.org/data/> .
@prefix rep:  <http://fairmat-nfdi.eu/taxonomy/representation#> .
@prefix tax:  <http://fairmat-nfdi.eu/taxonomy/> .
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

ex:dos-sample-42 a tax:ElectronicDensityOfStates ;
    rep:HasRepresentation ex:dos-spectrum .

ex:dos-spectrum a rep:Spectrum ;
    rep:Rank "1"^^xsd:nonNegativeInteger ;
    rep:Extent "3"^^xsd:nonNegativeInteger ;
    qb:structure ex:dos-dsd .

ex:dos-dsd a rep:DataStructureDefinition ;
    qb:component ex:dos-energy-spec , ex:dos-intensity-spec .

ex:dos-energy-spec a qb:ComponentSpecification ;
    qb:dimension rep:Energy ;
    rep:HasUnit unit:EV .

ex:dos-intensity-spec a qb:ComponentSpecification ;
    qb:measure rep:Intensity ;
    rep:HasUnit unit:COUNT .

ex:obs-1 a rep:Observation ; qb:dataSet ex:dos-spectrum ;
    rep:Energy "10.0"^^xsd:double ; rep:Intensity "125"^^xsd:nonNegativeInteger .
ex:obs-2 a rep:Observation ; qb:dataSet ex:dos-spectrum ;
    rep:Energy "10.5"^^xsd:double ; rep:Intensity "142"^^xsd:nonNegativeInteger .
ex:obs-3 a rep:Observation ; qb:dataSet ex:dos-spectrum ;
    rep:Energy "11.0"^^xsd:double ; rep:Intensity "131"^^xsd:nonNegativeInteger .
```

| Element | Role |
|---|---|
| `ex:dos-sample-42` | instance of a taxonomy class; one representation (`HasRepresentation` is functional) |
| `ex:dos-spectrum` | the dataset; its type gives the rank (stating `rep:Rank` is optional but must agree) |
| `ex:dos-dsd` | the schema; one spec per component |
| `ex:dos-energy-spec`, `ex:dos-intensity-spec` | dimension and measure, each with an optional unit |
| `ex:obs-*` | observations; the component IRIs (`rep:Energy`, `rep:Intensity`) are used as data properties |

A Scalar works the same way, with one measure spec and no dimension spec
(e.g. `qb:measure rep:Temperature ; rep:HasUnit unit:K`, one observation with `rep:Temperature 293.15`).

### 4.2 Invalid variants (verified with HermiT against `main.ttl`)

| Change to the valid example | HermiT | Rule (README §1) |
|---|---|---|
| none | consistent | — |
| energy spec unit `unit:K` instead of `unit:EV` | **inconsistent** | unit table (Units) |
| energy spec `qb:measure rep:Energy` instead of `qb:dimension` | **inconsistent** | dimension = Axis, measure = Signal (Structure) |
| an extra spec `qb:dimension rep:X` (Spectrum with 2 axes) | **inconsistent** | at most 1 dimension (Profile / Spectrum) |
| energy spec with two units `unit:EV , unit:K` | **inconsistent** | at most one unit + units are different (Units) |
| dataset typed `rep:TimeSeries` (axis is Energy) | **inconsistent** | axis is `Time` only (TimeSeries) |
| sample with a second representation typed `rep:Scalar` | **inconsistent** | one representation + one rank (Taxonomy link) |
| Scalar dataset with an extra `qb:dimension rep:X` spec | **inconsistent** | measures only (Scalar) |
| Scalar dataset with `rep:Rank "1"` | **inconsistent** | rank 0 (Scalar) |

### 4.3 Checking instance data

```python
from rdflib import Graph
from rep_modeller import write_for_hermit, run_hermit

g = Graph().parse("main.ttl")
g.parse("my_data.ttl")
write_for_hermit(g, "temp.ttl")
r = run_hermit("temp.ttl")
print("exit code", r.exit_code)
print(r.output)        # InconsistentOntologyException → data violates an axiom
```

The GUI's Reason search (`explain_unsat`) works on unsatisfiable classes; for an
inconsistent ABox, remove statements step by step (or use Protégé's
*Explain inconsistency*) to find the cause.

### 4.4 Limits at instance level

| Not detected by OWL | Status |
|---|---|
| missing observation values, missing measure, missing quantity kind | not checked by the reasoner |
| fewer dimensions than the rank | not checked by the reasoner |
| observation values outside the declared dimensions, wrong numeric datatypes | not checked by the reasoner |
| two spec IRIs that might be the same spec (no unique-name assumption) | state `owl:differentFrom` / `owl:AllDifferent` for specs if counts matter |

Large numerical arrays belong in HDF5, NeXus or Zarr; RDF holds the semantics
and small, addressable examples.

---

## 5. Rebuilding `main.ttl` — `merge_representation.py`

```bash
python merge_representation.py main_original.ttl representation.ttl main.ttl --fix-qudt
```

| Behaviour | Detail |
|---|---|
| append-only | the original text is copied byte-for-byte; the module is appended with its own prefixes |
| `--fix-qudt` | the only edit to the original: QUDT prefix `http://qudt.org/2.1/schema/qudt/` → `http://qudt.org/schema/qudt/` |
| one ontology header | the module's `owl:Ontology` header is not repeated |
| built-in checks | original is an exact prefix, all original triples present, block = module, no extra header |

---

## 6. Extending the module

| Task | Edit in `representation.ttl` | Don't forget |
|---|---|---|
| new component | `rep:NewAxis a owl:NamedIndividual, owl:DatatypeProperty, rep:Axis ; rep:HasQuantityKind qk:… ; rep:HasUnit unit:…` | add it to the components `owl:AllDifferent` list, otherwise rank limits and TimeSeries can be bypassed |
| new unit | `unit:… a owl:NamedIndividual, qudt:Unit` | add it to the units `owl:AllDifferent` list and to the permitted-unit axiom of its quantity kind |
| new quantity kind | declare it; add one permitted-unit axiom (copy an existing one) | — |
| make a type's axis strict | copy the TimeSeries axiom: `rep:<Type> SubClassOf structure only (component only (dimension only {Axis1, Axis2}))` | same pattern for measures: `measure only {…}` |
| afterwards | rebuild `main.ttl` (§5), run HermiT on it, try valid and invalid forms in the GUI | record the change in `CHANGELOG.md` |