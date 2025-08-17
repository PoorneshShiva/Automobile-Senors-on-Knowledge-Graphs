import logging
from pathlib import Path

import pandas as pd
from rdflib import Graph, Literal, URIRef

from kg_sensors.rdf_utils import get_node_label, get_type_label

logger = logging.getLogger(__name__)


def export_to_csv(g: Graph, output_dir: Path):
    """
    Exports an RDF graph into two CSV files: nodes.csv and edges.csv,
    suitable for Neo4j's `LOAD CSV` command.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    nodes_path = output_dir / "nodes.csv"
    edges_path = output_dir / "edges.csv"

    nodes_data = []
    edges_data = []
    processed_nodes = set()

    # Extract all unique subjects and objects that are URIs
    all_uris = set()
    for s, p, o in g:
        if isinstance(s, URIRef):
            all_uris.add(s)
        if isinstance(o, URIRef):
            all_uris.add(o)

    # Create node records
    for uri in all_uris:
        if uri not in processed_nodes:
            node_type = get_type_label(g, uri)
            # Use a generic 'Resource' label for nodes that are only objects
            if node_type == "Resource" and (uri, None, None) not in g:
                 node_type = "Concept" # Fallback for things like locations, units

            nodes_data.append({
                "uri": str(uri),
                "label": get_node_label(g, uri),
                "type": node_type,
            })
            processed_nodes.add(uri)

    # Create edge records
    for s, p, o in g:
        # We only create relationships for object properties (URI to URI)
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            edges_data.append({
                "start_uri": str(s),
                "end_uri": str(o),
                "type": g.namespace_manager.qname(p).replace(":", "_").upper(),
                "uri": str(p),
            })

    # Create pandas DataFrames and save to CSV
    nodes_df = pd.DataFrame(nodes_data)
    edges_df = pd.DataFrame(edges_data)

    nodes_df.to_csv(nodes_path, index=False)
    edges_df.to_csv(edges_path, index=False)

    logger.info(f"Exported {len(nodes_df)} nodes to {nodes_path}")
    logger.info(f"Exported {len(edges_df)} edges to {edges_path}")
