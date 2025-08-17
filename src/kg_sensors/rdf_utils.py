import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.term import BNode, Literal, URIRef
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- Namespace Definitions ---
EX = Namespace("http://example.com/ontology/")
SEN = Namespace("http://example.com/sensor/")
VEH = Namespace("http://example.com/vehicle/")
DTC = Namespace("http://example.com/dtc/")
PROT = Namespace("http://example.com/protocol/")
UNIT = Namespace("http://example.com/unit/")

# --- Namespace Bindings for Serialization ---
NS_MAP = {
    "ex": EX,
    "sen": SEN,
    "veh": VEH,
    "dtc": DTC,
    "prot": PROT,
    "unit": UNIT,
    "rdfs": RDFS,
    "rdf": RDF,
    "xsd": XSD,
}


def init_graph() -> Graph:
    """Initializes an rdflib.Graph with all project namespaces bound."""
    g = Graph()
    for prefix, ns_uri in NS_MAP.items():
        g.bind(prefix, ns_uri)
    return g


def load_graph_from_ttl(file_path: Path) -> Graph:
    """Loads an RDF graph from a Turtle file."""
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Could not find the RDF file at {file_path}")
    g = init_graph()
    g.parse(file_path, format="turtle")
    logger.info(f"Loaded graph from {file_path} with {len(g)} triples.")
    return g


def load_multiple_graphs_from_ttl(file_paths: List[Path]) -> Graph:
    """Loads and merges multiple RDF graphs from a list of Turtle files."""
    g = init_graph()
    for file_path in file_paths:
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            continue
        g.parse(file_path, format="turtle")
        logger.info(f"Loaded and merged graph from {file_path}")
    
    logger.info(f"Finished merging {len(file_paths)} files. Total triples: {len(g)}")
    return g


def save_graph_to_ttl(g: Graph, file_path: Path):
    """Saves an RDF graph to a Turtle file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(file_path), format="turtle")
    logger.info(f"Saved graph with {len(g)} triples to {file_path}")


def run_sparql_query(
    g: Graph, query_string: str
) -> List[Dict[str, Any]]:
    """
    Runs a SPARQL query against a graph and returns results as a list of dicts.
    """
    results = g.query(query_string)
    
    # Convert results to a more Python-friendly format
    output = []
    for row in results:
        row_dict = {}
        for var in results.vars:
            val = row[var]
            if isinstance(val, URIRef):
                try:
                    # Try to pretty-print the URI using its prefix
                    row_dict[str(var)] = val.n3(g.namespace_manager)
                except Exception:
                    row_dict[str(var)] = str(val)
            elif isinstance(val, Literal):
                row_dict[str(var)] = val.toPython()
            elif isinstance(val, BNode):
                 row_dict[str(var)] = str(val)
            else:
                 row_dict[str(var)] = val
        output.append(row_dict)
        
    return output


def pretty_print_sparql_results(results: List[Dict[str, Any]]):
    """
    Prints SPARQL query results in a nice table using rich.
    """
    if not results:
        print("Query returned no results.")
        return

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")

    # Define columns based on the keys of the first result dictionary
    headers = results[0].keys()
    for header in headers:
        table.add_column(header)

    # Add rows
    for row in results:
        table.add_row(*(str(row.get(header, "")) for header in headers))

    console.print(table)


def get_node_label(g: Graph, node: URIRef) -> str:
    """
    Retrieves the best available label for a given URI node (rdfs:label, qname, or last part of URI).
    """
    if not isinstance(node, URIRef):
        return str(node)
    
    # 1. Try to get rdfs:label
    label = g.value(subject=node, predicate=RDFS.label)
    if label:
        return str(label)
    
    # 2. If no label, try to get a qname (e.g., "ex:MyClass")
    try:
        qname = node.n3(g.namespace_manager)
        if not qname.startswith("<"): # n3 returns "<uri>" if no prefix is found
            return qname
    except Exception:
        pass # Fallback to URI part

    # 3. Fallback to the last part of the URI
    return node.split("/")[-1]


def get_type_label(g: Graph, node: URIRef) -> str:
    """
    Finds the rdf:type of a node and returns its label.
    Defaults to 'Resource' if no specific type is found.
    """
    node_type = g.value(subject=node, predicate=RDF.type)
    if node_type and isinstance(node_type, URIRef):
        return get_node_label(g, node_type)
    return "Resource" # Default for nodes without a specific type