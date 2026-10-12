#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
import tempfile
import threading
from dataclasses import dataclass, field
from typing import Optional

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

#################################################################
# Namespaces
#################################################################
REP = Namespace("http://fairmat-nfdi.eu/taxonomy/representation#")
TAX = Namespace("http://fairmat-nfdi.eu/taxonomy/")
QB = Namespace("http://purl.org/linked-data/cube#")
QUDT = Namespace("http://qudt.org/schema/qudt/")
QUDT_OLD = "http://qudt.org/2.1/schema/qudt/"
UNIT = Namespace("http://qudt.org/vocab/unit/")
QK = Namespace("http://qudt.org/vocab/quantitykind/")

ROLES = ("dimension", "measure")
ROLE_PROP = {"dimension": QB.dimension, "measure": QB.measure}


#################################################################
# Data model
#################################################################
@dataclass
class Component:
    role: str                      # "dimension" | "measure"
    comp: URIRef                   # e.g. rep:energy
    unit: Optional[URIRef] = None  # e.g. unit:EV  (None = no unit on spec)


@dataclass
class Spec:
    cls: URIRef                    # taxonomy class
    prop: URIRef                   # rep:HasRepresentation
    rep_class: URIRef              # rep:Spectrum, rep:Scalar, ...
    components: list[Component] = field(default_factory=list)
    origin: str = "new"            # "file" | "new" | "edited"


#################################################################
# Ontology logic (no GUI code here)
#################################################################
class OntologyModel:
    def __init__(self) -> None:
        self.base = Graph()          # merged files minus parsed specs
        self.specs: dict[URIRef, Spec] = {}
        self.unparsed: set[URIRef] = set()   # classes with other HasRepresentation restrictions
        self.log: list[str] = []

    # ---------------- loading ----------------
    def load(self, onto_path: str, rep_path: Optional[str] = None, align_qudt: bool = False) -> None:
        """Load main.ttl (must contain the representation module). rep_path is only
        used for an older, un-merged taxonomy file."""
        g = Graph()
        g.parse(onto_path, format="turtle")
        rep_iri = URIRef("http://fairmat-nfdi.eu/taxonomy/representation")
        if (rep_iri, RDF.type, OWL.Ontology) in g or (REP.HasRepresentation, RDF.type, OWL.ObjectProperty) in g:
            self.log = [f"Loaded {os.path.basename(onto_path)}: {len(g)} triples (representation module found)"]
        elif rep_path:
            g.parse(rep_path, format="turtle")
            self.log = [f"Loaded {os.path.basename(onto_path)} + {os.path.basename(rep_path)}: {len(g)} triples"]
        else:
            raise ValueError(f"{os.path.basename(onto_path)} does not contain the representation module "
                             "(rep:HasRepresentation not found). Load the merged main.ttl.")

        if align_qudt:
            n = 0
            fixed = Graph()
            for s, p, o in g:
                s2, p2, o2 = (self._align(t) for t in (s, p, o))
                if (s2, p2, o2) != (s, p, o):
                    n += 1
                fixed.add((s2, p2, o2))
            g = fixed
            if n:
                self.log.append(f"Aligned QUDT schema namespace ({QUDT_OLD} -> {QUDT}) in {n} triples")

        for prefix, ns in (("rep", REP), ("tax", TAX), ("qb", QB), ("qudt", QUDT),
                           ("unit", UNIT), ("qk", QK), ("owl", OWL), ("rdfs", RDFS),
                           ("skos", SKOS), ("xsd", XSD)):
            g.bind(prefix, ns, override=True, replace=True)

        self.base = g
        self.specs = {}
        self.unparsed = set()
        self._extract_existing()

    @staticmethod
    def _align(t):
        if isinstance(t, URIRef) and str(t).startswith(QUDT_OLD):
            return URIRef(QUDT + str(t)[len(QUDT_OLD):])
        return t

    # ---------------- vocabulary lookups ----------------
    def _subclasses(self, root: URIRef) -> set[URIRef]:
        out, todo = set(), [root]
        while todo:
            c = todo.pop()
            for s in self.base.subjects(RDFS.subClassOf, c):
                if isinstance(s, URIRef) and s not in out:
                    out.add(s)
                    todo.append(s)
        return out

    def _subproperties(self, root: URIRef) -> set[URIRef]:
        out, todo = set(), [root]
        while todo:
            p = todo.pop()
            for s in self.base.subjects(RDFS.subPropertyOf, p):
                if isinstance(s, URIRef) and s not in out:
                    out.add(s)
                    todo.append(s)
        return out

    def _instances_of(self, classes: set[URIRef]) -> set[URIRef]:
        return {s for c in classes for s in self.base.subjects(RDF.type, c) if isinstance(s, URIRef)}

    def label(self, t) -> str:
        if t is None:
            return "(none)"
        try:
            return self.base.namespace_manager.normalizeUri(t)
        except Exception:
            return str(t)

    def pref_label(self, t: URIRef) -> str:
        lab = self.base.value(t, SKOS.prefLabel) or self.base.value(t, RDFS.label)
        return str(lab) if lab else self.label(t).split(":")[-1]

    def rep_props(self) -> set[URIRef]:
        return {REP.HasRepresentation} | self._subproperties(REP.HasRepresentation)

    def taxonomy_classes(self) -> list[URIRef]:
        """Named classes outside the representation / external namespaces."""
        skip = (str(REP), str(QB), str(QUDT), QUDT_OLD, str(OWL), str(RDFS), str(SKOS))
        cs = {c for c in self.base.subjects(RDF.type, OWL.Class)
              if isinstance(c, URIRef) and not str(c).startswith(skip)}
        cs.discard(TAX.MaterialProperty)
        return sorted(cs, key=lambda c: self.pref_label(c).lower())

    def rank_of(self, cls: URIRef) -> Optional[int]:
        """Rank from 'equivalentClass (Representation and rank value n)', inherited via subClassOf."""
        seen, todo = set(), [cls]
        while todo:
            c = todo.pop(0)
            if c in seen:
                continue
            seen.add(c)
            for eq in self.base.objects(c, OWL.equivalentClass):
                for lst in self.base.objects(eq, OWL.intersectionOf):
                    for m in Collection(self.base, lst):
                        if self.base.value(m, OWL.onProperty) == REP.Rank:
                            v = self.base.value(m, OWL.hasValue)
                            if v is not None:
                                return int(v)
            todo.extend(o for o in self.base.objects(c, RDFS.subClassOf) if isinstance(o, URIRef))
        return None

    def representation_options(self) -> list[tuple[URIRef, URIRef]]:
        """(property, representation class) pairs offered in the dropdown."""
        data_classes = self._subclasses(QB.DataSet) & self._subclasses(REP.Representation)
        opts = [(REP.HasRepresentation, c) for c in data_classes]
        opts.sort(key=lambda pc: ((self.rank_of(pc[1]) or 0), self.pref_label(pc[1])))
        return opts

    def components_for(self, role: str) -> list[URIRef]:
        root = QB.DimensionProperty if role == "dimension" else QB.MeasureProperty
        classes = {root} | self._subclasses(root)
        return sorted(self._instances_of(classes), key=lambda c: self.pref_label(c).lower())

    def units(self) -> list[URIRef]:
        roots = {QUDT.Unit, URIRef(QUDT_OLD + "Unit")}   # current or QUDT 2.1 (merged main.ttl)
        classes = set(roots).union(*(self._subclasses(r) for r in roots))
        return sorted(self._instances_of(classes), key=lambda u: self.label(u))

    def canonical_unit(self, comp: URIRef) -> Optional[URIRef]:
        return self.base.value(comp, REP.HasUnit)

    def quantity_kind(self, comp: URIRef) -> Optional[URIRef]:
        return self.base.value(comp, REP.HasQuantityKind)

    # ---------------- class hierarchy ----------------
    def _superclasses(self, c: URIRef) -> set[URIRef]:
        out, todo = {c}, [c]
        while todo:
            for o in self.base.objects(todo.pop(), RDFS.subClassOf):
                if isinstance(o, URIRef) and o not in out:
                    out.add(o)
                    todo.append(o)
        return out

    @staticmethod
    def _restr(g: Graph, prop, kind, value) -> BNode:
        r = BNode()
        g.add((r, RDF.type, OWL.Restriction))
        g.add((r, OWL.onProperty, prop))
        g.add((r, kind, value))
        return r

    @staticmethod
    def _inter(g: Graph, members: list) -> BNode:
        c, lst = BNode(), BNode()
        g.add((c, RDF.type, OWL.Class))
        Collection(g, lst, members)
        g.add((c, OWL.intersectionOf, lst))
        return c

    def build(self, spec: Spec, g: Graph) -> BNode:
        """Add the nested restriction for one spec to graph g."""
        comp_restrs = []
        for c in spec.components:
            members = [QB.ComponentSpecification, self._restr(g, ROLE_PROP[c.role], OWL.hasValue, c.comp)]
            if c.unit is not None:
                members.append(self._restr(g, REP.HasUnit, OWL.hasValue, c.unit))
            comp_restrs.append(self._restr(g, QB.component, OWL.someValuesFrom, self._inter(g, members)))
        dsd = self._inter(g, [REP.DataStructureDefinition] + comp_restrs)
        rep = self._inter(g, [spec.rep_class, self._restr(g, QB.structure, OWL.someValuesFrom, dsd)])
        outer = self._restr(g, spec.prop, OWL.someValuesFrom, rep)
        g.add((spec.cls, RDFS.subClassOf, outer))
        return outer

    def spec_graph(self, spec: Spec) -> Graph:
        g = Graph(namespace_manager=self.base.namespace_manager)
        self.build(spec, g)
        return g

    def spec_turtle(self, spec: Spec) -> str:
        txt = self.spec_graph(spec).serialize(format="turtle")
        return "\n".join(l for l in txt.splitlines() if not l.startswith("@prefix")).strip() + "\n"

    def spec_summary(self, spec: Spec) -> str:
        lines = [f"{self.label(spec.cls)}",
                 f"  └─ {self.label(spec.prop)} some {self.label(spec.rep_class)}",
                 f"       └─ qb:structure some rep:DataStructureDefinition"]
        for i, c in enumerate(spec.components):
            branch = "└─" if i == len(spec.components) - 1 else "├─"
            unit = f"  [rep:HasUnit {self.label(c.unit)}]" if c.unit else "  [no unit]"
            lines.append(f"            {branch} qb:component → qb:{c.role} {self.label(c.comp)}{unit}")
        return "\n".join(lines)

    def kind_of(self, comp: URIRef) -> str:
        """'Axis', 'Signal', 'UnitAttribute' or 'external' (not a rep: component)."""
        for k in ("Axis", "Signal", "UnitAttribute"):
            if (comp, RDF.type, REP[k]) in self.base:
                return k
        return "external"

    def all_components(self) -> list[URIRef]:
        comps = set(self.components_for("dimension")) | set(self.components_for("measure"))
        order = {"Axis": 0, "Signal": 1}
        return sorted(comps, key=lambda c: (order.get(self.kind_of(c), 2), self.pref_label(c).lower()))

    def resolve(self, text: str) -> Optional[URIRef]:
        """Turn '<http://..>', 'http://..' or 'prefix:name' into an IRI (None if not possible)."""
        t = text.strip().split()[0] if text.strip() else ""
        if not t:
            return None
        if t.startswith("<") and t.endswith(">"):
            t = t[1:-1]
        if t.startswith(("http://", "https://", "urn:")):
            return URIRef(t)
        if ":" in t:
            prefix, local = t.split(":", 1)
            ns = dict(self.base.namespaces()).get(prefix)
            if ns is not None and local:
                return URIRef(str(ns) + local)
        return None

    def _list(self, node) -> list:
        lst = self.base.value(node, OWL.intersectionOf)
        return list(Collection(self.base, lst)) if lst is not None else []

    def _is_restr(self, n, prop=None) -> bool:
        if (n, RDF.type, OWL.Restriction) not in self.base:
            return False
        return prop is None or self.base.value(n, OWL.onProperty) == prop

    def _parse(self, cls: URIRef, r: BNode) -> Optional[Spec]:
        g = self.base
        prop = g.value(r, OWL.onProperty)
        rep_expr = g.value(r, OWL.someValuesFrom)
        if prop not in self.rep_props() or rep_expr is None:
            return None
        parts = self._list(rep_expr)
        rep_class = next((p for p in parts if isinstance(p, URIRef)), None)
        struct = next((p for p in parts if self._is_restr(p, QB.structure)), None)
        if rep_class is None or struct is None or len(parts) != 2:
            return None
        dsd_parts = self._list(g.value(struct, OWL.someValuesFrom))
        if REP.DataStructureDefinition not in dsd_parts:
            return None
        comps = []
        for cr in dsd_parts:
            if cr == REP.DataStructureDefinition:
                continue
            if not self._is_restr(cr, QB.component):
                return None
            role = comp = unit = None
            for m in self._list(g.value(cr, OWL.someValuesFrom)):
                if m == QB.ComponentSpecification:
                    continue
                p = g.value(m, OWL.onProperty)
                v = g.value(m, OWL.hasValue)
                if p == QB.dimension:
                    role, comp = "dimension", v
                elif p == QB.measure:
                    role, comp = "measure", v
                elif p == REP.HasUnit:
                    unit = v
                else:
                    return None
            if comp is None:
                return None
            comps.append(Component(role, comp, unit))
        return Spec(cls, prop, rep_class, comps, origin="file")

    def _remove_tree(self, node) -> None:
        """Remove all triples reachable from a blank node (restriction + lists)."""
        todo = [node]
        while todo:
            n = todo.pop()
            for p, o in list(self.base.predicate_objects(n)):
                self.base.remove((n, p, o))
                if isinstance(o, BNode):
                    todo.append(o)

    def _extract_existing(self) -> None:
        rep_props = self.rep_props()
        for cls, r in list(self.base.subject_objects(RDFS.subClassOf)):
            if not isinstance(r, BNode) or self.base.value(r, OWL.onProperty) not in rep_props:
                continue
            spec = self._parse(cls, r)
            if spec is None:
                self.unparsed.add(cls)
                continue
            if cls in self.specs:  # second pattern on same class: keep it in the file untouched
                self.unparsed.add(cls)
                continue
            self.specs[cls] = spec
            self.base.remove((cls, RDFS.subClassOf, r))
            self._remove_tree(r)
        if self.specs:
            self.log.append(f"Read back {len(self.specs)} existing representation restriction(s) into the model")
        if self.unparsed:
            self.log.append(f"{len(self.unparsed)} class(es) have other HasRepresentation axioms (left untouched)")

    def check_graph(self, spec: Optional[Spec]) -> Graph:
        """main.ttl + restrictions read from the file + the current form
        (which replaces a file restriction of the same class).
        The form's root node is stored in self.form_root."""
        g = Graph(namespace_manager=self.base.namespace_manager)
        for t in self.base:
            g.add(t)
        for c, sp in self.specs.items():
            if spec is None or c != spec.cls:
                self.build(sp, g)
        self.form_root = self.build(spec, g) if spec is not None else None
        return g


#################################################################
# Reasoner helpers. run_reasoner: for scripts (owlready2). run_hermit: used by the GUI
#################################################################
@dataclass
class ReasonerResult:
    status: str                       # "ok" | "unsat" | "inconsistent" | "error"
    unsat: list[str] = field(default_factory=list)   # unsatisfiable class IRIs
    exception: str = ""               # exception type + message, if any
    seconds: float = 0.0


def run_reasoner(graph: Graph) -> ReasonerResult:
    import time
    t0 = time.time()
    try:
        import owlready2
    except ImportError as e:
        return ReasonerResult("error", exception=f"{type(e).__name__}: {e}  "
                              "(pip install owlready2; Java is also required)")
    path = os.path.join(tempfile.mkdtemp(), "check.owl")
    graph.serialize(path, format="xml")
    world = owlready2.World()
    onto = world.get_ontology("file://" + path).load()
    try:
        with onto:
            owlready2.sync_reasoner_hermit(world, infer_property_values=False, debug=0)
    except owlready2.OwlReadyInconsistentOntologyError as e:
        return ReasonerResult("inconsistent", exception=f"{type(e).__name__}: {e}", seconds=time.time() - t0)
    except Exception as e:  # Java missing, parse problems, ...
        return ReasonerResult("error", exception=f"{type(e).__name__}: {e}", seconds=time.time() - t0)
    bad = sorted({str(c.iri) for c in world.inconsistent_classes()} - {str(OWL.Nothing)})
    return ReasonerResult("unsat" if bad else "ok", unsat=bad, seconds=time.time() - t0)


def check_consistency(graph: Graph) -> str:
    """Short text form of run_reasoner (kept for scripts)."""
    r = run_reasoner(graph)
    if r.status == "ok":
        return "Consistent, no unsatisfiable classes."
    if r.status == "unsat":
        return "Consistent, but unsatisfiable classes:\n  " + "\n  ".join(r.unsat)
    if r.status == "inconsistent":
        return "INCONSISTENT: " + r.exception
    return "Reasoner could not run: " + r.exception


@dataclass
class HermitRun:
    command: list[str]
    exit_code: Optional[int]
    output: str            # HermiT's stdout + stderr, verbatim (JVM option banner removed)
    seconds: float
    error: str = ""        # set when HermiT could not be started at all


def write_for_hermit(g: Graph, path: str) -> None:
    """Write g as Turtle that HermiT's (OWL API 3) parser always reads: @prefix lines for
    readable output, then every triple spelled out in N-Triples form (N-Triples is valid
    Turtle). Avoids shorthand such as 1e+01 that the old parser rejects."""
    body = g.serialize(format="nt", encoding="utf-8").decode("utf-8")
    with open(path, "w", encoding="utf-8") as f:
        for prefix, ns in sorted(g.namespaces()):
            if prefix:
                f.write(f"@prefix {prefix}: <{ns}> .\n")
        f.write("\n" + body)


def hermit_parse_failed(output: str) -> bool:
    return "Could not parse ontology" in output or "UnparsableOntologyException" in output


def hermit_classpath() -> Optional[str]:
    """HermiT.jar: $HERMIT_JAR, next to this script, or the copy shipped with owlready2."""
    env = os.environ.get("HERMIT_JAR")
    if env and os.path.isfile(env):
        return env
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HermiT.jar")
    if os.path.isfile(here):
        return here
    try:
        import owlready2.reasoning as r
        return r._HERMIT_CLASSPATH
    except Exception:
        return None


def run_hermit(ttl_path: str, timeout: int = 600) -> HermitRun:
    """Run the HermiT command-line reasoner on a file and return its raw output.
    -U lists the unsatisfiable classes (classes equivalent to owl:Nothing); an
    inconsistent ontology makes HermiT exit with its own exception."""
    import subprocess
    import time
    cp = hermit_classpath()
    java = os.environ.get("JAVA_EXE", "java")
    cmd = [java, "-Xmx2000M", "-cp", cp or "HermiT.jar", "org.semanticweb.HermiT.cli.CommandLine",
           "-U", "file://" + os.path.abspath(ttl_path).replace("\\", "/")]
    if cp is None:
        return HermitRun(cmd, None, "", 0.0, "HermiT.jar not found (set HERMIT_JAR, put HermiT.jar next to "
                                              "this script, or pip install owlready2).")
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return HermitRun(cmd, None, "", 0.0, f"Java not found ('{java}'). Install Java or set JAVA_EXE.")
    except subprocess.TimeoutExpired:
        return HermitRun(cmd, None, "", time.time() - t0, f"HermiT did not finish within {timeout} s.")
    out = "\n".join(l for l in (p.stdout + p.stderr).splitlines()
                    if not l.startswith("Picked up JAVA_TOOL_OPTIONS"))
    return HermitRun(cmd, p.returncode, out, time.time() - t0)


#################################################################
# Explanation: minimal set of axioms found by re-running HermiT
# (black-box justification; no rules of its own)
#################################################################
_ANNOT = {RDFS.comment, RDFS.label, SKOS.prefLabel, SKOS.altLabel, SKOS.definition}
_DECL = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty,
         OWL.NamedIndividual, OWL.Ontology, OWL.Restriction}


def _closure(g: Graph, node, acc: set) -> None:
    for p, o in g.predicate_objects(node):
        acc.add((node, p, o))
        if isinstance(o, BNode):
            _closure(g, o, acc)


def split_axioms(g: Graph) -> tuple[set, list]:
    """(declarations, axioms). An axiom is one top-level statement with its blank-node
    structure. Annotations (labels, comments) are left out: they never cause a conflict."""
    decl, axioms = set(), []
    referenced = {o for _, _, o in g if isinstance(o, BNode)}
    roots_done = set()
    for s, p, o in g:
        if p in _ANNOT:
            continue
        if isinstance(s, URIRef):
            if p == RDF.type and o in _DECL:
                decl.add((s, p, o))
                continue
            t = {(s, p, o)}
            if isinstance(o, BNode):
                _closure(g, o, t)
            axioms.append(frozenset(t))
        elif s not in referenced and s not in roots_done:   # GCI, AllDifferent, ...
            roots_done.add(s)
            t = set()
            _closure(g, s, t)
            axioms.append(frozenset(t))
    return decl, axioms


def _entities(ax) -> set:
    return {x for t in ax for x in t if isinstance(x, URIRef) and not str(x).startswith("http://www.w3.org/")}


def relevant_axioms(axioms: list, start: URIRef) -> list:
    """Axioms syntactically reachable from the class (speeds up the search; the result is
    re-checked with HermiT before it is used)."""
    sig, chosen, changed = {start}, set(), True
    while changed:
        changed = False
        for i, ax in enumerate(axioms):
            if i in chosen:
                continue
            subj = {s for s, _, _ in ax if isinstance(s, URIRef)}
            if (subj or _entities(ax)) & sig:
                chosen.add(i)
                sig |= _entities(ax)
                changed = True
    return [axioms[i] for i in sorted(chosen)]


def explain_unsat(g: Graph, cls: URIRef, progress=None) -> tuple[list, int]:
    """Minimal set of axioms of g that makes cls unsatisfiable (removing any one of them makes
    cls satisfiable). Every test is a HermiT run. Returns (axioms, number of HermiT runs)."""
    decl, axioms = split_axioms(g)
    path = os.path.join(tempfile.gettempdir(), "rep_modeller", "explain.nt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    runs = [0]

    def unsat(subset: list) -> bool:
        h = Graph()
        for t in decl:
            h.add(t)
        for ax in subset:
            for t in ax:
                h.add(t)
        h.serialize(path, format="nt", encoding="utf-8")
        runs[0] += 1
        if progress:
            progress(runs[0])
        r = run_hermit(path)
        return r.exit_code == 0 and any(l.strip() == f"<{cls}>" for l in r.output.splitlines())

    def minimize(background: list, cand: list) -> list:      # divide and conquer (QuickXplain style)
        if len(cand) <= 1:
            return list(cand)
        c1, c2 = cand[:len(cand) // 2], cand[len(cand) // 2:]
        if unsat(background + c1):
            return minimize(background, c1)
        if unsat(background + c2):
            return minimize(background, c2)
        m1 = minimize(background + c2, c1)
        return m1 + minimize(background + m1, c2)

    cand = relevant_axioms(axioms, cls)
    if not unsat(cand):          # reachability filter too narrow: use everything
        cand = axioms
        if not unsat(cand):
            return [], runs[0]
    return minimize([], cand), runs[0]


def render_axiom(g: Graph, ax) -> str:
    """Manchester-syntax style rendering of one axiom (structure only, no interpretation)."""
    h = Graph()
    for t in ax:
        h.add(t)
    nm = g.namespace_manager

    def name(x):
        if isinstance(x, Literal):
            return str(x)
        try:
            return nm.normalizeUri(x)
        except Exception:
            return f"<{x}>"

    def lst(node):
        return list(Collection(h, node)) if node is not None else []

    def ce(x, top=False):
        if not isinstance(x, BNode):
            return name(x)
        v = lambda p: h.value(x, p)
        if v(OWL.onProperty) is not None:
            p = name(v(OWL.onProperty))
            if v(OWL.someValuesFrom) is not None:
                r = f"{p} some {ce(v(OWL.someValuesFrom))}"
            elif v(OWL.allValuesFrom) is not None:
                r = f"{p} only {ce(v(OWL.allValuesFrom))}"
            elif v(OWL.hasValue) is not None:
                r = f"{p} value {name(v(OWL.hasValue))}"
            elif v(OWL.hasSelf) is not None:
                r = f"{p} Self"
            else:
                r = None
                for key, word in ((OWL.maxQualifiedCardinality, "max"), (OWL.minQualifiedCardinality, "min"),
                                  (OWL.qualifiedCardinality, "exactly"), (OWL.maxCardinality, "max"),
                                  (OWL.minCardinality, "min"), (OWL.cardinality, "exactly")):
                    if v(key) is not None:
                        on = v(OWL.onClass)
                        r = f"{p} {word} {v(key)}" + (f" {ce(on)}" if on is not None else "")
                        break
                r = r or p
            return r if top else f"({r})"
        if v(OWL.intersectionOf) is not None:
            r = " and ".join(ce(m) for m in lst(v(OWL.intersectionOf)))
        elif v(OWL.unionOf) is not None:
            r = " or ".join(ce(m) for m in lst(v(OWL.unionOf)))
        elif v(OWL.complementOf) is not None:
            return f"not {ce(v(OWL.complementOf))}"
        elif v(OWL.oneOf) is not None:
            return "{" + ", ".join(name(m) for m in lst(v(OWL.oneOf))) + "}"
        else:
            return "[…]"
        return r if top else f"({r})"

    referenced = {o for _, _, o in h if isinstance(o, BNode)}
    roots = [s for s in h.subjects() if s not in referenced]
    if not roots:
        return "(empty)"
    s = roots[0]
    if isinstance(s, BNode):
        if (s, RDF.type, OWL.AllDifferent) in h:
            return "DifferentIndividuals: " + ", ".join(name(m) for m in lst(h.value(s, OWL.distinctMembers)))
        sup = h.value(s, RDFS.subClassOf)
        if sup is not None:
            return f"{ce(s, True)}\n    SubClassOf  {ce(sup, True)}"
        return ce(s, True)
    p, o = next(iter((p, o) for p, o in h.predicate_objects(s)))
    words = {RDFS.subClassOf: "SubClassOf", OWL.equivalentClass: "EquivalentTo", OWL.disjointWith: "DisjointWith",
             RDFS.domain: "Domain", RDFS.range: "Range", RDFS.subPropertyOf: "SubPropertyOf", RDF.type: "Type"}
    if p == OWL.disjointUnionOf:
        return f"{name(s)}  DisjointUnionOf  " + ", ".join(name(m) for m in lst(o))
    if p == RDF.type and o == OWL.FunctionalProperty:
        return f"{name(s)}  Characteristics: Functional"
    return f"{name(s)}  {words.get(p, name(p))}  {ce(o, True)}"


#################################################################
# GUI
#################################################################
def run_gui(onto_path: str = "") -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText

    model = OntologyModel()
    check = {"sig": None, "result": None, "path": "", "explain": None, "graph": None, "form_root": None}

    class FilterCombo(ttk.Combobox):
        """Editable combobox; the list narrows to entries containing the typed text."""
        def __init__(self, master, **kw):
            super().__init__(master, **kw)
            self._all: list[str] = []
            self.bind("<KeyRelease>", self._on_key)

        def set_items(self, items: list[str]) -> None:
            self._all = items
            self["values"] = items

        def _on_key(self, event) -> None:
            if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
                return
            txt = self.get().lower()
            self["values"] = [i for i in self._all if txt in i.lower()] or self._all

    root = tk.Tk()
    root.title("Representation Restriction Modeller")
    root.geometry("1320x860")
    root.minsize(1040, 680)
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("Head.TLabel", font=("TkDefaultFont", 10, "bold"))
    style.configure("Hint.TLabel", foreground="#555555")

    onto_var = tk.StringVar(value=onto_path)
    status_var = tk.StringVar(value="Load main.ttl to start.")
    class_info = tk.StringVar(value="")
    rep_info = tk.StringVar(value="")
    comp_info = tk.StringVar(value="")

    class_map: dict[str, URIRef] = {}
    rep_map: dict[str, tuple[URIRef, URIRef]] = {}
    comp_map: dict[str, URIRef] = {}
    unit_map: dict[str, Optional[URIRef]] = {}
    current: list[Component] = []
    load_log: list[str] = []

    # ---------------- layout: file ----------------
    files = ttk.LabelFrame(root, text="1  Ontology (main.ttl with the representation module)", padding=8)
    files.pack(fill="x", padx=10, pady=(10, 4))

    def browse():
        p = filedialog.askopenfilename(filetypes=[("Turtle", "*.ttl"), ("All files", "*.*")])
        if p:
            onto_var.set(p)

    ttk.Label(files, text="main.ttl", width=10).grid(row=0, column=0, sticky="w")
    ttk.Entry(files, textvariable=onto_var).grid(row=0, column=1, sticky="ew", padx=4)
    ttk.Button(files, text="Browse…", command=browse).grid(row=0, column=2)
    ttk.Button(files, text="Load", command=lambda: do_load()).grid(row=0, column=3, padx=(4, 0))
    files.columnconfigure(1, weight=1)

    body = ttk.PanedWindow(root, orient="horizontal")
    body.pack(fill="both", expand=True, padx=10, pady=4)

    # ---------------- layout: left (form) ----------------
    left = ttk.Frame(body, padding=(0, 0, 6, 0))
    body.add(left, weight=1)

    f2 = ttk.LabelFrame(left, text="2  Class", padding=8)
    f2.pack(fill="x")
    class_cb = FilterCombo(f2)
    class_cb.pack(fill="x")
    ttk.Label(f2, textvariable=class_info, style="Hint.TLabel", wraplength=540,
              justify="left").pack(anchor="w", pady=(4, 0))

    f3 = ttk.LabelFrame(left, text="3  Representation", padding=8)
    f3.pack(fill="x", pady=6)
    rep_cb = ttk.Combobox(f3, state="readonly")
    rep_cb.pack(fill="x")
    ttk.Label(f3, textvariable=rep_info, style="Hint.TLabel", wraplength=540,
              justify="left").pack(anchor="w", pady=(4, 0))

    f4 = ttk.LabelFrame(left, text="4  Components and units",
                        padding=8)
    f4.pack(fill="both", expand=True)
    row = ttk.Frame(f4)
    row.pack(fill="x")
    ttk.Label(row, text="Role").grid(row=0, column=0, sticky="w")
    ttk.Label(row, text="Component").grid(row=0, column=1, sticky="w")
    ttk.Label(row, text="Unit on spec").grid(row=0, column=2, sticky="w")
    role_cb = ttk.Combobox(row, values=ROLES, state="readonly", width=11)
    role_cb.grid(row=1, column=0, padx=(0, 4))
    role_cb.set("dimension")
    comp_cb = FilterCombo(row, width=24)
    comp_cb.grid(row=1, column=1, padx=(0, 4))
    unit_cb = FilterCombo(row, width=18)
    unit_cb.grid(row=1, column=2, padx=(0, 4))
    ttk.Button(row, text="Add", command=lambda: add_component()).grid(row=1, column=3)
    ttk.Label(f4, textvariable=comp_info, style="Hint.TLabel", wraplength=540,
              justify="left").pack(anchor="w", pady=(4, 2))

    comp_tv = ttk.Treeview(f4, columns=("role", "comp", "kind", "qk", "unit", "canon"), show="headings", height=8)
    for col, txt, w in (("role", "Role", 75), ("comp", "Component", 120), ("kind", "Kind", 70),
                        ("qk", "Quantity kind", 105), ("unit", "Unit on spec", 95), ("canon", "Canonical", 85)):
        comp_tv.heading(col, text=txt)
        comp_tv.column(col, width=w, anchor="w")
    comp_tv.pack(fill="both", expand=True)
    btns = ttk.Frame(f4)
    btns.pack(fill="x", pady=(4, 0))
    ttk.Button(btns, text="Remove component", command=lambda: remove_component()).pack(side="left")
    ttk.Button(btns, text="Clear", command=lambda: (current.clear(), refresh_components())).pack(side="left", padx=4)
    check_btn = ttk.Button(btns, text="Check consistency (HermiT)", command=lambda: do_check())
    check_btn.pack(side="right")

    # ---------------- layout: right (preview + reasoner) ----------------
    right = ttk.PanedWindow(body, orient="vertical")
    body.add(right, weight=1)

    def text_pane(title: str, copy_label: str, copy_cmd, height: int):
        frame = ttk.Frame(right, padding=(6, 0, 0, 4))
        head = ttk.Frame(frame)
        head.pack(fill="x")
        ttk.Label(head, text=title, style="Head.TLabel").pack(side="left")
        ttk.Button(head, text=copy_label, command=copy_cmd).pack(side="right")
        txt = ScrolledText(frame, height=height, wrap="none", font=("Courier", 10))
        xb = ttk.Scrollbar(frame, orient="horizontal", command=txt.xview)
        txt.configure(xscrollcommand=xb.set)
        txt.pack(fill="both", expand=True)
        xb.pack(fill="x")
        txt.tag_configure("fail", foreground="#b00020")
        txt.tag_configure("ok", foreground="#1b7f3b")
        txt.tag_configure("note", foreground="#8a6d00")
        txt.tag_configure("head", font=("Courier", 10, "bold"))
        txt.tag_configure("code", foreground="#1f3a93")
        txt.tag_configure("dim", foreground="#777777")
        # read-only, but text can be selected and copied
        txt.bind("<Key>", lambda e: None if (e.state & 0x4 and e.keysym.lower() in ("c", "a"))
                 or e.keysym in ("Left", "Right", "Up", "Down", "Prior", "Next", "Home", "End") else "break")
        right.add(frame, weight=1)
        return txt

    prev = text_pane("Preview  (Turtle, live)", "Copy Turtle", lambda: copy_text(prev), 14)
    out = text_pane("Reasoner", "Copy", lambda: copy_text(out), 14)

    ttk.Label(root, textvariable=status_var, relief="sunken", anchor="w", padding=(6, 2)).pack(fill="x", side="bottom")

    # ---------------- helpers ----------------
    def write(widget, parts) -> None:
        widget.delete("1.0", "end")
        if isinstance(parts, str):
            parts = [(parts, None)]
        for text, tag in parts:
            widget.insert("end", text, tag) if tag else widget.insert("end", text)

    def copy_text(widget) -> None:
        txt = widget.get("1.0", "end-1c")
        if not txt.strip():
            status_var.set("Nothing to copy.")
            return
        root.clipboard_clear()
        root.clipboard_append(txt)
        status_var.set("Copied to clipboard.")

    def class_display(c: URIRef) -> str:
        return f"{model.pref_label(c)}   ({model.label(c)})"

    def comp_display(c: URIRef) -> str:
        return f"{model.label(c)}   [{model.kind_of(c)}]"

    def unit_display(u: Optional[URIRef]) -> str:
        if u is None:
            return "(none)"
        return next((k for k, v in unit_map.items() if v == u), model.label(u))

    def loaded() -> bool:
        if not class_map:
            messagebox.showinfo("Not loaded", "Load main.ttl first.")
            return False
        return True

    def form_spec() -> Optional[Spec]:
        c = class_map.get(class_cb.get())
        sel = rep_map.get(rep_cb.get())
        if c is None or sel is None:
            return None
        return Spec(c, sel[0], sel[1], list(current))

    def signature(spec: Optional[Spec]):
        if spec is None:
            return None
        return (spec.cls, spec.rep_class, tuple((x.role, x.comp, x.unit) for x in spec.components))

    # ---------------- live panes ----------------
    def refresh_panes(_=None) -> None:
        """Preview = Turtle of the current form. Reasoner = diagram of the form, plus the
        HermiT output of the last check while the form is unchanged."""
        if not class_map:
            return
        spec = form_spec()
        if spec is None:
            c_ok, r_ok = class_map.get(class_cb.get()) is not None, rep_map.get(rep_cb.get()) is not None
            missing = " and ".join(x for x, ok in (("a class", c_ok), ("a representation type", r_ok)) if not ok)
            write(prev, [(f"# Choose {missing} to see the Turtle snippet.\n", "dim")])
            write(out, [(f"Choose {missing}.\n\n", "note")] + [(l + "\n", "dim") for l in load_log])
            return
        write(prev, [(model.spec_turtle(spec), "code")])
        parts = [("Diagram\n", "head"), (model.spec_summary(spec) + "\n", None)]
        run = check["result"]
        if run is None or check["sig"] != signature(spec):
            parts.append(("\nPress 'Check consistency (HermiT)': main.ttl + this form are written to "
                          "temp.ttl and HermiT is run on it.\n", "dim"))
        else:
            parts += hermit_parts(spec, run)
        write(out, parts)

    def hermit_parts(spec: Spec, run: "HermitRun") -> list:
        """Show HermiT's own output; lines naming the current class are highlighted."""
        parts = [("\nHermiT\n", "head"),
                 (f"temp file : {check['path']}\n", "dim"),
                 (f"command   : {' '.join(run.command)}\n", "dim")]
        if run.error:
            return parts + [(f"\nCould not run HermiT: {run.error}\n", "fail")]
        parts.append((f"exit code : {run.exit_code}   ({run.seconds:.1f} s)\n\n", "dim"))
        names = class_tokens(spec.cls)
        for line in run.output.splitlines():
            hit = line.strip() in names
            bad = run.exit_code != 0 or hermit_parse_failed(run.output) or "Exception" in line \
                or line.startswith("\tat ")
            parts.append((line + "\n", "fail" if hit or bad else None))
        if not run.output.strip():
            parts.append(("(no output)\n", "dim"))
        parts += reason_parts(spec)
        return parts

    def class_tokens(cls: URIRef) -> set:
        """How HermiT may print the class: prefixed name or <IRI>."""
        return {model.label(cls), f"<{cls}>", str(cls)}

    def hermit_says_unsat(run: "HermitRun", cls: URIRef) -> bool:
        return run.exit_code == 0 and any(l.strip() in class_tokens(cls) for l in run.output.splitlines())

    def reason_parts(spec: Spec) -> list:
        """Explanation below HermiT's output: the minimal set of axioms HermiT needs to
        derive the result (found by re-running HermiT on subsets)."""
        ex = check.get("explain")
        if ex is None:
            return []
        parts = [("\nReason\n", "head")]
        if ex["state"] == "running":
            return parts + [(f"Searching for the axioms that cause it … (HermiT run {ex['runs']})\n", "dim")]
        if ex["state"] == "error":
            return parts + [(f"Could not compute an explanation: {ex['error']}\n", "note")]
        axioms = ex["axioms"]
        if not axioms:
            return parts + [("HermiT could not reproduce the result on a subset; no explanation found.\n", "note")]
        g = check["graph"]
        parts.append((f"{model.label(spec.cls)} is unsatisfiable because of these {len(axioms)} axioms together "
                      f"(found with {ex['runs']} HermiT runs, {ex['seconds']:.0f} s). Removing any one of them "
                      f"makes the class satisfiable:\n", None))
        for i, ax in enumerate(axioms, 1):
            mine = any(o == check.get("form_root") for _, _, o in ax)
            src = "in given TTL" if mine else "ontology"
            parts.append((f"\n{i}. [{src}]\n", "head"))
            parts.append(("   " + render_axiom(g, ax).replace("\n", "\n   ") + "\n", "fail" if mine else "code"))
            subj = next((t[0] for t in ax if isinstance(t[0], URIRef)), None)
            note = g.value(subj, RDFS.comment) if subj is not None and not mine else None
            if note:
                parts.append((f"   comment on {model.label(subj)}: {note}\n", "dim"))
        return parts

    # ---------------- actions ----------------
    def do_load() -> None:
        if not os.path.isfile(onto_var.get()):
            messagebox.showerror("File", "Choose main.ttl.")
            return
        try:
            model.load(onto_var.get())
        except Exception as e:
            messagebox.showerror("Load failed", f"{type(e).__name__}: {e}")
            return
        check.update(sig=None, result=None)
        class_map.clear()
        class_map.update({class_display(c): c for c in model.taxonomy_classes()})
        class_cb.set_items(list(class_map))
        class_cb.set("")
        rep_map.clear()
        for p, c in model.representation_options():
            r = model.rank_of(c)
            rep_map[f"{model.pref_label(c)}   ({model.label(c)}" + (f", rank {r})" if r is not None else ")")] = (p, c)
        rep_cb["values"] = list(rep_map)
        rep_cb.set("")
        comp_map.clear()
        comp_map.update({comp_display(c): c for c in model.all_components()})
        comp_cb.set_items(list(comp_map))
        comp_cb.set("")
        unit_map.clear()
        unit_map["(none)"] = None
        unit_map.update({f"{model.label(u)}   ({model.pref_label(u)})": u for u in model.units()})
        unit_cb.set_items(list(unit_map))
        unit_cb.set("")
        current.clear()
        load_log.clear()
        load_log.extend(model.log)
        load_log.append(f"{len(class_map)} classes, {len(rep_map)} representation types, "
                        f"{len(comp_map)} components, {len(unit_map) - 1} units.")
        refresh_components()
        status_var.set(f"Loaded {os.path.basename(onto_var.get())}.")

    def on_class(_=None) -> None:
        c = class_map.get(class_cb.get())
        if c is None:
            class_info.set("")
            refresh_panes()
            return
        parents = [model.label(p) for p in model.base.objects(c, RDFS.subClassOf) if isinstance(p, URIRef)]
        comment = model.base.value(c, RDFS.comment)
        txt = f"Parent: {', '.join(parents) or '—'}"
        if comment:
            txt += f"\n{comment}"
        if c in model.specs:
            txt += "\n● Has a representation restriction in main.ttl — loaded into the form."
            s = model.specs[c]
            rep_cb.set(next((k for k, v in rep_map.items() if v == (s.prop, s.rep_class)), ""))
            on_rep(refresh=False)
            current.clear()
            current.extend(Component(x.role, x.comp, x.unit) for x in s.components)
            refresh_components()
        if c in model.unparsed:
            txt += "\n⚠ Has another HasRepresentation axiom in the file (left untouched)."
        class_info.set(txt)
        refresh_panes()

    def on_rep(_=None, refresh: bool = True) -> None:
        sel = rep_map.get(rep_cb.get())
        if not sel:
            rep_info.set("")
        else:
            p, c = sel
            r = model.rank_of(c)
            txt = f"{model.label(c)} via {model.label(p)}; rank {r if r is not None else '?'}"
            rep_info.set(txt)
        if refresh:
            refresh_panes()

    def on_comp(_=None) -> None:
        c = comp_map.get(comp_cb.get()) or model.resolve(comp_cb.get())
        if c is None:
            comp_info.set("")
            return
        if model.kind_of(c) == "external":
            comp_info.set(f"{model.label(c)}: external IRI (no quantity kind or canonical unit in the ontology).")
            return
        cu = model.canonical_unit(c)
        unit_cb.set(unit_display(cu))
        comp_info.set(f"{model.label(c)} [{model.kind_of(c)}]: quantity kind {model.label(model.quantity_kind(c))}, "
                      f"canonical unit {model.label(cu)}")

    def refresh_components() -> None:
        comp_tv.delete(*comp_tv.get_children())
        for i, c in enumerate(current):
            ext = model.kind_of(c.comp) == "external"
            comp_tv.insert("", "end", iid=str(i), values=(
                c.role, model.label(c.comp), model.kind_of(c.comp),
                "—" if ext else model.label(model.quantity_kind(c.comp)),
                model.label(c.unit), "—" if ext else model.label(model.canonical_unit(c.comp))))
        refresh_panes()

    def add_component() -> None:
        if not loaded():
            return
        ctext = comp_cb.get().strip()
        c = comp_map.get(ctext) or model.resolve(ctext)
        if c is None:
            messagebox.showinfo("Component", "Choose a component, or type an IRI "
                                "(http://…, <http://…> or prefix:name with a known prefix).")
            return
        utext = unit_cb.get().strip()
        if utext in ("", "(none)"):
            u = None
        else:
            u = unit_map.get(utext) or model.resolve(utext)
            if u is None:
                messagebox.showinfo("Unit", "Choose a unit, '(none)', or type an IRI "
                                    "(http://…, <http://…> or prefix:name with a known prefix).")
                return
        current.append(Component(role_cb.get(), c, u))
        refresh_components()

    def remove_component() -> None:
        for iid in sorted((int(i) for i in comp_tv.selection()), reverse=True):
            del current[iid]
        refresh_components()

    def do_check() -> None:
        if not loaded():
            return
        spec = form_spec()
        if spec is None:
            messagebox.showinfo("Check", "Choose a class and a representation type first.")
            return
        path = os.path.join(tempfile.gettempdir(), "rep_modeller", "temp.ttl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            g = model.check_graph(spec)
            write_for_hermit(g, path)
        except Exception as e:
            messagebox.showerror("temp.ttl", f"{type(e).__name__}: {e}")
            return
        sig = signature(spec)
        status_var.set(f"Running HermiT on {path} …")
        check_btn.state(["disabled"])

        check.update(explain=None, graph=g, form_root=model.form_root)

        def work():
            res = run_hermit(path)
            root.after(0, lambda: finish(sig, path, spec, res))
        threading.Thread(target=work, daemon=True).start()

    def finish(sig, path: str, spec: Spec, res: "HermitRun") -> None:
        check.update(sig=sig, result=res, path=path)
        if res.error or not hermit_says_unsat(res, spec.cls):
            check_btn.state(["!disabled"])
            refresh_panes()
            if res.error:
                status_var.set("HermiT could not run.")
            elif hermit_parse_failed(res.output):
                status_var.set("HermiT could not parse temp.ttl — see the Reasoner pane.")
            else:
                status_var.set(f"HermiT finished with exit code {res.exit_code} ({res.seconds:.1f} s). "
                               "Output in the Reasoner pane.")
            return
        # unsatisfiable: find the reason with further HermiT runs, in the background
        import time
        ex = {"state": "running", "runs": 0}
        check["explain"] = ex
        refresh_panes()
        status_var.set(f"HermiT: {model.label(spec.cls)} is unsatisfiable. Searching for the reason …")
        t0 = time.time()

        def progress(n):
            ex["runs"] = n
            root.after(0, lambda: refresh_panes() if check.get("explain") is ex and check["sig"] == sig else None)

        def work():
            try:
                axioms, runs = explain_unsat(check["graph"], spec.cls, progress)
                ex.update(state="done", axioms=axioms, runs=runs, seconds=time.time() - t0)
            except Exception as e:
                ex.update(state="error", error=f"{type(e).__name__}: {e}")
            root.after(0, done)

        def done():
            check_btn.state(["!disabled"])
            if check.get("explain") is ex:
                refresh_panes()
                status_var.set(f"HermiT: {model.label(spec.cls)} is unsatisfiable; reason found "
                               f"({ex.get('runs', 0)} HermiT runs)." if ex["state"] == "done" else "Explanation failed.")
        threading.Thread(target=work, daemon=True).start()

    class_cb.bind("<<ComboboxSelected>>", on_class)
    class_cb.bind("<Return>", on_class)
    rep_cb.bind("<<ComboboxSelected>>", on_rep)
    comp_cb.bind("<<ComboboxSelected>>", on_comp)
    comp_cb.bind("<Return>", on_comp)
    comp_cb.bind("<FocusOut>", on_comp)

    if onto_path:
        root.after(100, do_load)
    root.mainloop()


if __name__ == "__main__":
    run_gui(sys.argv[1] if len(sys.argv) > 1 else "")