# RDF graph complexity and scaling

This analysis describes the revised representation module. It excludes the
ontology and shapes graphs themselves from per-dataset counts because those
graphs are loaded once and reused.

## Observation cost

For a dataset with rank `r`, `m` measured signals, and `n` observations:

```text
triples per observation = 2 + r + m
observation triples     = n × (2 + r + m)
```

The two base triples are `rdf:type rep:Observation` and `qb:dataSet`.
Superclass types such as `qb:Observation` can be inferred from the class
bridge instead of being repeated.

With one signal:

| Representation | Rank | Triples per observation |
|---|---:|---:|
| Scalar | 0 | 3 |
| Spectrum / TimeSeries / DepthProfile | 1 | 4 |
| Image | 2 | 5 |
| VolumeData | 3 | 6 |

The bundled valid examples make the growth concrete:

| Fixture | Observations | Values per observation | Observation triples |
|---|---:|---:|---:|
| Scalar | 1 | 1 signal | 3 |
| Spectrum | 3 | 1 coordinate + 1 signal | 12 |
| TimeSeries | 3 | 1 coordinate + 1 signal | 12 |
| DepthProfile | 3 | 1 coordinate + 1 signal | 12 |
| Image (2 × 2) | 4 | 2 coordinates + 1 signal | 20 |
| VolumeData (2 × 2 × 2) | 8 | 3 coordinates + 1 signal | 48 |

Across the six valid fixtures this is 22 observations and 63 component-value
triples. These small graphs are intended for documentation and regression
testing, not performance benchmarking.

## Dataset and schema cost

Let `c = r + m` be the number of component specifications and `u` the
number of explicitly supplied units.

For the compact pattern used in `examples/`:

```text
dataset + DSD + component specifications = 5 + 3c + u
total = 5 + 3c + u + n(2 + c)
```

The formula assumes dataset type, rank, extent, and structure; DSD type; one
`qb:component` edge, specification type, and role edge per component; and
one triple per supplied unit. Units are optional, so `0 ≤ u ≤ c`.

| Representation | Components | Fixed triples without units |
|---|---:|---:|
| Scalar | 1 | 8 |
| Rank-one profile | 2 | 11 |
| Image | 3 | 14 |
| VolumeData | 4 | 17 |

The compact formula does not include optional material-property links,
component `rep:extent` statements, labels, provenance, or named-graph
metadata. Each adds a constant number of triples per dataset or component;
they do not change the linear dependence on observation count.

## Dense arrays

RDF observation expansion is linear but large. A 512 × 512 image with one
signal needs approximately 1.31 million observation triples. A 512³ volume
needs approximately 805 million observation triples before indexes,
provenance, named-graph metadata, and storage-engine overhead.

For dense scientific arrays, keep values in HDF5, Zarr, NeXus, or another
appropriate array format. RDF should carry the semantic schema, access
location, dataset path, shape, datatype, checksum, axes, units, and provenance.

This module does not yet define that external-array reference pattern. The
recommendation is an architectural scaling boundary, not an additional
ontology commitment.

## Query complexity

| Query pattern | Primary scaling factor | Useful indexes |
|---|---|---|
| Find representations of material properties | Number of representation links | predicate, subject |
| Discover dataset components | DSD/component count | `qb:structure`, `qb:component` |
| Read one dataset's observations | Dataset observation count | `qb:dataSet` |
| Filter a profile coordinate interval | Selected observations | `qb:dataSet`, coordinate predicate/value |
| Extract an image slice | Selected observations | dataset plus coordinate predicates |
| Resolve unit/kind metadata | Component specifications | role and unit predicates |

Class and property bridges are small schema-level joins. A store with RDFS
materialization may answer generic `qb:DataSet` and `rep:has_representation`
queries directly. Without materialization, use subclass/subproperty paths;
that trades storage for query-time traversal.

Numeric range queries depend strongly on literal datatypes. The ontology uses
the broad `rdfs:Literal` range for reusable component predicates, so producers
should use consistent numeric datatypes within a dataset if efficient sorting,
filtering, or aggregation is required.

## Validation cost

The cardinality and typing checks are local to unit-bearing subjects and
components. `REP-UNIT-001` uses a SPARQL anti-join against the small trusted
whitelist. With indexes on `rep:hasUnit`, `rep:hasQuantityKind`,
`qb:dimension`, `qb:measure`, and `shp:permitsUnit`, its practical cost is
approximately linear in the number of supplied unit assertions.

The retained profile checks use SPARQL targets joining dataset, DSD,
component specification, and component. They are metadata-scale operations
and do not scan numerical observation values.

Production performance still requires measurement against the selected
triplestore and representative graph sizes. The bundled tests verify
correctness, not throughput.

## Operational recommendations

1. Load the ontology and validator-owned unit map once, then validate many
   producer graphs against them.
2. Index `qb:dataSet`, `qb:structure`, `qb:component`, component-role
   predicates, `rep:hasUnit`, and `rep:hasQuantityKind`.
3. Partition very large observation graphs by dataset or acquisition when the
   store supports named graphs.
4. Keep full-resolution arrays outside RDF once explicit observation expansion
   becomes impractical; preserve searchable semantic metadata in RDF.
5. Benchmark both asserted and entailment-enabled query plans on the intended
   triplestore before selecting runtime reasoning.
