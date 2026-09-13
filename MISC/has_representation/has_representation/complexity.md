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

## Dense arrays

RDF observation expansion is linear but large. A 512 × 512 image with one
signal needs approximately 1.31 million observation triples. A 512³ volume
needs approximately 805 million observation triples before indexes,
provenance, named-graph metadata, and storage-engine overhead.

For dense scientific arrays, keep values in HDF5, Zarr, NeXus, or another
appropriate array format. RDF should carry the semantic schema, access
location, dataset path, shape, datatype, checksum, axes, units, and provenance.

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

