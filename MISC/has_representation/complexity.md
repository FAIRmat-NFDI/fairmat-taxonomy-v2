# RDF Data Cube: Triple Complexity and Scaling

This document outlines the structural complexity and semantic triple costs associated with representing multi-dimensional scientific measurements using the W3C RDF Data Cube (`qb`) and QUDT vocabularies. 

The architecture separates schema-level metadata from instance-level data points (observations) to optimize scaling and prevent redundant declarations.

## 1. Observation Triples (Instance Data / ABox)

Individual data points (`rep:Observation`) are optimized using OWL punning. Instead of repeating unit and quantity definitions, observations directly use canonical component IRIs (e.g., `rep:energy`, `rep:intensity`) as predicates.

**Formula for Triples per Observation:**
`Total Triples = 2 (base) + N (axes) + M (signals)`

*   **Base Triples (2):** One for the `rdf:type` (declaring it as `rep:Observation`), and one for the `qb:dataSet` (linking it to the parent dataset).
*   **Axis Triples (N):** The dimensionality (Rank) of the dataset dictates the number of coordinates (e.g., a Rank 2 Image requires `rep:x` and `rep:y`).
*   **Signal Triples (M):** The number of measured values recorded at that coordinate (e.g., `rep:intensity`).

### Triples per 1 Data Point (Assuming 1 Signal)

| Representation Type | Rank (Axes) | Base Triples | Axis Triples | Signal Triples | Total Triples |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Scalar** | Rank 0 | 2 | 0 | 1 | **3 Triples** |
| **Profile** | Rank 1 | 2 | 1 | 1 | **4 Triples** |
| **Image** | Rank 2 | 2 | 2 | 1 | **5 Triples** |
| **VolumeData** | Rank 3 | 2 | 3 | 1 | **6 Triples** |


## 2. Schema Triples (Metadata / TBox & DSD)

Unit mappings (`rep:hasQuantityKind` and `rep:hasUnit`) exist **exclusively at the dataset schema level** (`qb:DataStructureDefinition`). They are declared exactly once per dataset structure, regardless of whether the dataset contains 1 observation or 1,000,000 observations. 

This prevents redundant metadata generation. Adding a second data point to a dataset does **not** duplicate the unit or quantity kind triples.

**Schema Scaling Logic:**
*   **Base Schema Cost (15 Triples):** Every dataset requires a root connection, a DSD, one signal component specification, and the signal's `rep:UnitAttribute`.
*   **Per-Axis Cost (10 Triples):** Every additional axis (dictated by Rank) adds exactly 10 triples to link the dimension component, order, and its associated unit metadata to the DSD.


## 3. Total Graph Scaling (Schema + Observations)

The table below illustrates the total number of triples generated for a complete, SHACL-compliant dataset (assuming exactly 1 measured signal and fully defined unit metadata).

*   **triple_without_dp:** The fixed cost of the structural schema and metadata.
*   **triple_with_dp:** The total graph cost scaling linearly for `n` data points.

| Representation Type | triple_without_dp (Schema Only) | triple_with_dp (Scales for *n* Data Points) |
| :--- | :--- | :--- |
| **Scalar** (Rank 0) | 15 | 15 + (*n* × 3) |
| **Profile** (Rank 1) | 25 | 25 + (*n* × 4) |
| **Image** (Rank 2) | 35 | 35 + (*n* × 5) |
| **VolumeData** (Rank 3) | 45 | 45 + (*n* × 6) |

---
*Note: Due to the linear scaling factor (e.g., a 100x100 Image generates 50,000 observation triples), using external file linkages (like HDF5) via DCAT is highly recommended for dense arrays rather than native triplestore instantiation.*
