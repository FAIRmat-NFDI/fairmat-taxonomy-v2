#!/usr/bin/env python3
"""Validate the representation ontology, its unit profile, and every example.

Install:
    python -m pip install rdflib pyshacl

Run from any directory:
    python test/representation_test.py

The SHACL graph is also loaded as trusted validation data because it owns the
shp:permitsUnit whitelist. Production validators must keep that configuration
separate from producer-controlled data.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, SKOS

ROOT = Path(__file__).resolve().parent.parent
TBOX = ROOT / "representation.ttl"
SHAPES = ROOT / "representation.shacl.ttl"
EXAMPLES = sorted((ROOT / "examples").glob("*-abox.ttl"))
REPORT = Path(__file__).resolve().parent / "reports.md"

SH = Namespace("http://www.w3.org/ns/shacl#")
SHP = Namespace("http://fairmat-nfdi.eu/taxonomy/shapes/units#")
REP = Namespace("http://fairmat-nfdi.eu/taxonomy/representation#")
QB = Namespace("http://purl.org/linked-data/cube#")
QUDT = Namespace("http://qudt.org/schema/qudt/")
LEGACY_QUDT = Namespace("http://qudt.org/2.1/schema/qudt/")

EXPECT = re.compile(r"^##\s*expect:\s*(.+?)\s*$", re.MULTILINE)


def expected_codes(path: Path) -> set[str]:
    match = EXPECT.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{path.name}: missing '## expect:' declaration")
    value = match.group(1)
    return set() if value == "conforms" else set(re.findall(r"REP-UNIT-\d+", value))


def owning_shape(shapes: Graph, source):
    """Walk from a nested property/SPARQL shape to its coded node shape."""
    current, seen = source, set()
    while current is not None and current not in seen:
        seen.add(current)
        if (current, SHP.code, None) in shapes:
            return current
        current = (
            next(shapes.subjects(SH.property, current), None)
            or next(shapes.subjects(SH.sparql, current), None)
        )
    return None


def findings(report: Graph, shapes: Graph) -> list[dict[str, str]]:
    rows = []
    for result in report.subjects(RDF.type, SH.ValidationResult):
        source = next(report.objects(result, SH.sourceShape), None)
        owner = owning_shape(shapes, source)
        code = str(next(shapes.objects(owner, SHP.code), "UNMAPPED"))
        severity = str(next(report.objects(result, SH.resultSeverity), "")).split("#")[-1]
        focus = str(next(report.objects(result, SH.focusNode), "-"))
        value = str(next(report.objects(result, SH.value), "-"))
        rows.append({"code": code, "severity": severity, "focus": focus, "value": value})
    return sorted(rows, key=lambda row: (row["code"], row["focus"], row["value"]))


def observation_issues(graph: Graph) -> list[str]:
    """Check that each example has a complete, linked observation."""
    issues: list[str] = []
    datasets = set(graph.subjects(REP.rank, None))
    for dataset in sorted(datasets, key=str):
        structures = list(graph.objects(dataset, QB.structure))
        if len(structures) != 1:
            issues.append(f"{dataset}: expected exactly one qb:structure")
            continue
        components = set()
        for spec in graph.objects(structures[0], QB.component):
            components.update(graph.objects(spec, QB.dimension))
            components.update(graph.objects(spec, QB.measure))
        observations = set(graph.subjects(QB.dataSet, dataset))
        if not observations:
            issues.append(f"{dataset}: no qb:dataSet-linked observation")
        for observation in observations:
            if (observation, RDF.type, REP.Observation) not in graph:
                issues.append(f"{observation}: missing rep:Observation type")
            for component in components:
                count = len(list(graph.objects(observation, component)))
                if count != 1:
                    issues.append(f"{observation}: {count} values for {component}")
    return issues


def ontology_contract_issues(tbox: Graph, shapes: Graph) -> list[str]:
    issues: list[str] = []
    bridges = {
        REP.DataStructureDefinition: QB.DataStructureDefinition,
        REP.Scalar: QB.DataSet,
        REP.Profile: QB.DataSet,
        REP.Image: QB.DataSet,
        REP.VolumeData: QB.DataSet,
        REP.Observation: QB.Observation,
        REP.Axis: QB.DimensionProperty,
        REP.Signal: QB.MeasureProperty,
        REP.UnitAttribute: QB.AttributeProperty,
    }
    for local, external in bridges.items():
        if (local, RDFS.subClassOf, external) not in tbox:
            issues.append(f"missing subclass bridge {local} -> {external}")
    if any(tbox.triples((None, SKOS.closeMatch, None))):
        issues.append("skos:closeMatch remains in the ontology")
    if any(tbox.triples((None, None, LEGACY_QUDT.QuantityKind))):
        issues.append("legacy versioned QUDT QuantityKind IRI remains")
    if any(tbox.triples((None, None, LEGACY_QUDT.Unit))):
        issues.append("legacy versioned QUDT Unit IRI remains")
    if (REP.hasQuantityKind, RDFS.range, QUDT.QuantityKind) not in tbox:
        issues.append("rep:hasQuantityKind does not use canonical QUDT range")
    if (REP.hasUnit, RDFS.range, QUDT.Unit) not in tbox:
        issues.append("rep:hasUnit does not use canonical QUDT range")
    if any(tbox.triples((REP.order, None, None))) or any(tbox.triples((QB.order, None, None))):
        issues.append("ordering semantics remain in the local ontology")
    if not (SHP.UnitQuantityKindContextShape, RDF.type, SH.NodeShape) in shapes:
        issues.append("unit-bearing nodes are not checked for quantity-kind context")
    return issues


def main() -> int:
    tbox = Graph().parse(TBOX, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    contract_issues = ontology_contract_issues(tbox, shapes)
    results = []

    for path in EXAMPLES:
        example = Graph().parse(path, format="turtle")
        data = tbox + shapes + example
        conforms, report, _ = validate(
            data_graph=data,
            shacl_graph=shapes,
            advanced=True,
            inference="none",
            allow_warnings=True,
            meta_shacl=True,
        )
        rows = findings(report, shapes)
        actual = {row["code"] for row in rows}
        expected = expected_codes(path)
        obs_issues = observation_issues(example)
        expected_conforms = not any(
            row["severity"] == "Violation" for row in rows
        )
        ok = actual == expected and conforms == expected_conforms and not obs_issues
        results.append((path.name, conforms, expected, actual, obs_issues, rows, ok))
        print(
            f"{'PASS' if ok else 'FAIL'}  {path.name:<48} "
            f"conforms={str(conforms):<5} codes={','.join(sorted(actual)) or '-'}"
        )

    passed = sum(row[-1] for row in results)
    lines = [
        "# Validation report",
        "",
        f"{passed}/{len(results)} examples matched their declared SHACL results "
        "and contained complete observations.",
        "",
        f"Ontology contract checks: {'passed' if not contract_issues else 'failed'}.",
        "",
        "| Example | Conforms | Expected codes | Actual codes | Observation |",
        "|---|---:|---|---|---|",
    ]
    for name, conforms, expected, actual, issues, _, ok in results:
        lines.append(
            f"| `{name}` | {'yes' if conforms else 'no'} | "
            f"{', '.join(sorted(expected)) or '—'} | "
            f"{', '.join(sorted(actual)) or '—'} | "
            f"{'complete' if not issues else '; '.join(issues)} |"
        )
    if contract_issues:
        lines += ["", "## Contract issues", ""]
        lines += [f"- {issue}" for issue in contract_issues]
    lines += [
        "",
        "Warnings are included in the code comparison but remain non-blocking.",
        "The whitelist is trusted validator configuration, not producer data.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    if not EXAMPLES:
        print("FAIL: no examples found")
        return 1
    if contract_issues:
        for issue in contract_issues:
            print(f"CONTRACT FAIL: {issue}")
    print(f"\n{passed}/{len(results)} examples passed; report: {REPORT}")
    return 0 if passed == len(results) and not contract_issues else 1


if __name__ == "__main__":
    sys.exit(main())
