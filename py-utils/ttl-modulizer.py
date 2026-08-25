import sys
from pathlib import Path
from rdflib import Graph, Namespace, RDF, OWL, RDFS, BNode

TAX = Namespace("http://fairmat-nfdi.eu/taxonomy/")

def extract_blank_nodes(src_graph: Graph, target_graph: Graph, node):
    for s, p, o in src_graph.triples((node, None, None)):
        target_graph.add((s, p, o))
        if isinstance(o, BNode):
            extract_blank_nodes(src_graph, target_graph, o)

def break_rdf_to_ttl_tree(input_file_path: str, output_dir: str):
    input_path = Path(input_file_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file_path}")

    g = Graph()
    g.parse(str(input_path), format="turtle")
    base_path = Path(output_dir)

    def save_entity_ttl(entity_uri, rel_path):
        subg = Graph()
        for prefix, ns in g.namespaces():
            subg.bind(prefix, ns)
        for s, p, o in g.triples((entity_uri, None, None)):
            subg.add((s, p, o))
            if isinstance(o, BNode):
                extract_blank_nodes(g, subg, o)
        out_file = base_path / rel_path
        out_file.parent.mkdir(parents=True, exist_ok=True)
        subg.serialize(destination=str(out_file), format="turtle")

    for cls in g.subjects(RDF.type, OWL.Class):
        if not isinstance(cls, BNode) and str(cls).startswith(str(TAX)):
            name = str(cls).rsplit("/", 1)[-1]
            superclasses = [
                str(o).rsplit("/", 1)[-1]
                for o in g.objects(cls, RDFS.subClassOf)
                if not isinstance(o, BNode) and str(o).startswith(str(TAX))
            ]
            if not superclasses:
                rel_path = f"core/base_classes/{name}.ttl"
            elif "MaterialProperty" in superclasses:
                domain_folder = name.replace("Property", "").lower()
                rel_path = f"domains/{domain_folder}/classes/{name}.ttl"
            else:
                domain_folder = superclasses[0].replace("Property", "").lower()
                rel_path = f"domains/{domain_folder}/classes/{name}.ttl"
            save_entity_ttl(cls, rel_path)

    for prop in g.subjects(RDF.type, OWL.ObjectProperty):
        name = str(prop).rsplit("/", 1)[-1]
        save_entity_ttl(prop, f"properties/object_properties/{name}.ttl")

    print(f"Broken down into modules under '{output_dir}/'")

def combine_ttl_tree_to_rdf(input_dir: str, output_file_path: str):
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Directory {input_dir} not found. Skipping combination.")
        return

    combined_graph = Graph()
    ttl_files = list(input_path.rglob("*.ttl"))
    if not ttl_files:
        return

    for filepath in ttl_files:
        combined_graph.parse(str(filepath), format="turtle")

    output_path = Path(output_file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined_graph.serialize(destination=str(output_path), format="turtle")
    print(f"Successfully combined modules into '{output_file_path}'.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "combine":
            combine_ttl_tree_to_rdf(input_dir=sys.argv[2], output_file_path=sys.argv[3])
        elif mode == "break":
            break_rdf_to_ttl_tree(input_file_path=sys.argv[2], output_dir=sys.argv[3])