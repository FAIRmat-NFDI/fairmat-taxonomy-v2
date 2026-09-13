#!/usr/bin/env python3
"""
representation_test.py -- load, check, write reports.md.

    pip install pyshacl rdflib
    python test/representation_test.py

Three steps, nothing else:

  LOAD   representation.ttl + representation.shacl.ttl form the base
         graph. Every file in examples/ is loaded on top of that base,
         one at a time, as its own independent graph. Several example
         files contradict each other on purpose, so they are never
         loaded together.

  CHECK  each graph against representation.shacl.ttl, and verify that
         every example dataset has complete, explicitly typed lifted
         observations for every component declared by its DSD.

  WRITE  test/reports.md.

The shapes file is loaded TWICE -- once as the shapes graph, once into
the data graph. That is deliberate: the shp:permitsUnit table lives in
it, and the FILTER NOT EXISTS in REP-UNIT-001 is evaluated against the
data graph. The shapes themselves are inert as data; nothing targets
them.

Each example file declares what it expects in a header comment:

    ##  expect: conforms
    ##  expect: REP-UNIT-001, REP-UNIT-011

Exit code is 0 when every file matches its declaration.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parent.parent
TBOX = ROOT / "representation.ttl"
SHAPES = ROOT / "representation.shacl.ttl"
EXAMPLES = sorted((ROOT / "examples").glob("*-abox.ttl"))
REPORT = Path(__file__).resolve().parent / "reports.md"

SH = Namespace("http://www.w3.org/ns/shacl#")
SHP = Namespace("http://fairmat-nfdi.eu/taxonomy/shapes/units#")
REP = Namespace("http://fairmat-nfdi.eu/taxonomy/representation#")
QB = Namespace("http://purl.org/linked-data/cube#")

EXPECT = re.compile(r"^##\s+expect:\s*(?P<e>.+?)\s*$", re.MULTILINE)

PREFIXES = [
    ("ex:", "http://example.org/data#"),
    ("rep:", "http://fairmat-nfdi.eu/taxonomy/representation#"),
    ("unit:", "http://qudt.org/vocab/unit/"),
    ("qk:", "http://qudt.org/vocab/quantitykind/"),
    ("tax:", "http://fairmat-nfdi.eu/taxonomy/"),
    ("qb:", "http://purl.org/linked-data/cube#"),
    ("sh:", "http://www.w3.org/ns/shacl#"),
]


def short(term) -> str:
    if term is None:
        return "-"
    s = str(term)
    for pref, ns in PREFIXES:
        if s.startswith(ns):
            return pref + s[len(ns):]
    return s


def expected_codes(path: Path) -> list[str]:
    m = EXPECT.search(path.read_text())
    raw = m.group("e") if m else "conforms"
    return [] if raw.startswith("conforms") else sorted(set(re.findall(r"REP-UNIT-\d+", raw)))


def owning_shape(shapes: Graph, node):
    """sh:sourceShape may be a blank property shape nested inside the named
    NodeShape that carries the metadata. Walk up to the shape with a code."""
    seen = set()
    cur = node
    while cur is not None and cur not in seen:
        seen.add(cur)
        if isinstance(cur, URIRef) and (cur, SHP.code, None) in shapes:
            return cur
        cur = (next(shapes.subjects(SH.property, cur), None)
               or next(shapes.subjects(SH.sparql, cur), None))
    return None


def findings(report: Graph, shapes: Graph) -> list[dict]:
    """THE JOIN: result --sh:sourceShape--> shape --shp:code--> stable code.
    Nothing here parses sh:resultMessage; the message is for humans."""
    rows = []
    for res in report.subjects(RDF.type, SH.ValidationResult):
        owner = owning_shape(shapes, next(report.objects(res, SH.sourceShape), None))

        def meta(prop, default="-"):
            if owner is None:
                return default
            v = next(shapes.objects(owner, prop), None)
            return str(v) if v is not None else default

        rows.append({
            "code": meta(SHP.code, "UNMAPPED"),
            "layer": meta(SHP.layer),
            "severity": short(next(report.objects(res, SH.resultSeverity), None)).split(":")[-1],
            "focus": short(next(report.objects(res, SH.focusNode), None)),
            "value": short(next(report.objects(res, SH.value), None)),
            "remedy": meta(SHP.remedy, ""),
        })
    rows.sort(key=lambda r: (r["layer"], r["code"], r["focus"]))
    return rows


def observation_issues(abox: Graph) -> list[str]:
    """Check the concrete RDF Data Cube rows in one standalone ABox."""
    issues = []
    datasets = set(abox.subjects(REP.rank, None))
    declared_observations = set(abox.subjects(RDF.type, REP.Observation))
    linked_observations = set(abox.subjects(QB.dataSet, None))

    for observation in sorted(declared_observations - linked_observations, key=str):
        issues.append(f"{short(observation)} has no qb:dataSet")

    for dataset in sorted(datasets, key=str):
        if (dataset, RDF.type, QB.DataSet) not in abox:
            issues.append(f"{short(dataset)} is not explicitly a qb:DataSet")

        observations = set(abox.subjects(QB.dataSet, dataset))
        if not observations:
            issues.append(f"{short(dataset)} has no lifted observations")
            continue

        components = set()
        for dsd in abox.objects(dataset, QB.structure):
            for spec in abox.objects(dsd, QB.component):
                components.update(abox.objects(spec, QB.dimension))
                components.update(abox.objects(spec, QB.measure))

        for observation in sorted(observations, key=str):
            if (observation, RDF.type, REP.Observation) not in abox:
                issues.append(f"{short(observation)} is not a rep:Observation")
            if (observation, RDF.type, QB.Observation) not in abox:
                issues.append(f"{short(observation)} is not a qb:Observation")
            for component in sorted(components, key=str):
                count = len(list(abox.objects(observation, component)))
                if count != 1:
                    issues.append(
                        f"{short(observation)} has {count} values for {short(component)}"
                    )
    return issues


def main() -> int:
    # ---- LOAD ------------------------------------------------------------
    tbox = Graph().parse(TBOX, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")

    base = Graph()
    for g in (tbox, shapes):
        for t in g:
            base.add(t)

    if not EXAMPLES:
        print(f"no *-abox.ttl files under {ROOT / 'examples'}")
        return 1

    # ---- CHECK -----------------------------------------------------------
    results = []
    for path in EXAMPLES:
        abox = Graph().parse(path, format="turtle")
        data = Graph()
        for t in base:
            data.add(t)
        for t in abox:
            data.add(t)

        conforms, report, _ = validate(
            data_graph=data,
            shacl_graph=shapes,
            advanced=True,          # sh:sparql constraints and sh:SPARQLTarget
            inference="none",
            allow_warnings=True,    # Layer 2 is advisory; it reports, it does not fail
        )
        rows = findings(report, shapes)
        got = sorted({r["code"] for r in rows})
        want = expected_codes(path)
        obs_issues = observation_issues(abox)
        results.append({
            "file": path.name, "conforms": conforms,
            "want": want, "got": got,
            "ok": got == want and not obs_issues,
            "rows": rows, "observation_issues": obs_issues,
        })
        print(f"{'PASS' if got == want and not obs_issues else 'FAIL'}  {path.name:<48}"
              f"conforms={str(conforms):<6}{', '.join(got) or '-'}  "
              f"observations={'ok' if not obs_issues else 'FAIL'}")
        for issue in obs_issues:
            print(f"      {issue}")

    # ---- WRITE -----------------------------------------------------------
    passed = sum(r["ok"] for r in results)
    out = [
        "# Validation report",
        "",
        f"`representation.ttl` + `representation.shacl.ttl` vs `examples/` "
        f"-- {passed}/{len(results)} files matched their declared SHACL expectation "
        f"and contained complete lifted observations.",
        "",
        "Layer 1 findings are `sh:Violation` and make the graph non-conforming.",
        "Layer 2 findings are `sh:Warning`: reported, but the graph still conforms.",
        "",
        "## Summary",
        "",
        "| file | conforms | observations | expected | actual | |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        out.append(
            f"| `{r['file']}` | {'yes' if r['conforms'] else 'no'} "
            f"| {'ok' if not r['observation_issues'] else 'MISSING/INCOMPLETE'} "
            f"| {', '.join(r['want']) or '-'} | {', '.join(r['got']) or '-'} "
            f"| {'ok' if r['ok'] else 'MISMATCH'} |"
        )

    out += ["", "## Findings", ""]
    for r in results:
        out.append(f"### `{r['file']}`")
        out.append("")
        if not r["rows"]:
            out += ["No findings.", ""]
            continue
        out += ["| code | severity | layer | focus node | value |",
                "|---|---|---|---|---|"]
        for row in r["rows"]:
            out.append(f"| {row['code']} | {row['severity']} | {row['layer']} "
                       f"| `{row['focus']}` | `{row['value']}` |")
        out.append("")
        seen = set()
        for row in r["rows"]:
            if row["remedy"] and row["remedy"] != "-" and row["code"] not in seen:
                seen.add(row["code"])
                out.append(f"- **{row['code']}** {row['remedy']}")
        out.append("")

    REPORT.write_text("\n".join(out) + "\n")
    print(f"\n{passed}/{len(results)} matched. Report written to {REPORT}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
