import logging
from typing import Tuple

import networkx as nx
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS

from kg_sensors.rdf_utils import EX

logger = logging.getLogger(__name__)


def get_label(g: Graph, node: URIRef) -> str:
    """Fetches the rdfs:label for a node, falling back to its prefixed name."""
    try:
        label = g.value(subject=node, predicate=RDFS.label)
        if label:
            return str(label)
        return node.n3(g.namespace_manager)
    except Exception:
        return str(node)


def get_type_label(g: Graph, node: URIRef) -> str:
    """Fetches the label of the node's rdf:type."""
    try:
        node_type = g.value(subject=node, predicate=RDF.type)
        if node_type:
            return get_label(g, node_type)
        return "Resource"
    except Exception:
        return "Resource"


def to_networkx_entity_graph(g: Graph) -> nx.Graph:
    """
    Converts an RDF graph to a NetworkX graph where all URIs are nodes
    and predicates are edges. This is a general "entity graph".
    """
    nx_graph = nx.Graph()
    nodes = set()

    # First pass: add all nodes with attributes
    for s, p, o in g:
        if isinstance(s, URIRef):
            nodes.add(s)
        if isinstance(o, URIRef):
            nodes.add(o)

    for node in nodes:
        nx_graph.add_node(
            str(node),
            label=get_label(g, node),
            type=get_type_label(g, node),
            uri=str(node),
            kind="Entity"
        )

    # Second pass: add edges
    for s, p, o in g:
        # Only consider object properties for edges
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            nx_graph.add_edge(
                str(s),
                str(o),
                label=g.namespace_manager.qname(p),
                uri=str(p)
            )
    
    logger.info(f"Created NetworkX entity graph with {nx_graph.number_of_nodes()} nodes and {nx_graph.number_of_edges()} edges.")
    return nx_graph


def to_networkx_bipartite_graph(g: Graph) -> nx.Graph:
    """
    Converts RDF data into a bipartite graph of Sensor Models and Vehicle Models.
    An edge exists if a sensor model is compatible with a vehicle model.
    """
    nx_graph = nx.Graph()
    
    # Find all vehicle models
    vehicles = set(g.subjects(predicate=RDF.type, object=EX.VehicleModel))
    for v in vehicles:
        nx_graph.add_node(
            str(v),
            label=get_label(g, v),
            type="VehicleModel",
            bipartite=0  # Group 0 for vehicles
        )

    # Find all sensor models
    sensors = set(g.subjects(predicate=RDF.type, object=EX.SensorModel))
    for s in sensors:
        nx_graph.add_node(
            str(s),
            label=get_label(g, s),
            type="SensorModel",
            bipartite=1  # Group 1 for sensors
        )

    # Add edges based on the `compatibleWithModel` property
    for v in vehicles:
        compatible_sensors = g.objects(subject=v, predicate=EX.compatibleWithModel)
        for s in compatible_sensors:
            if str(s) in nx_graph:
                nx_graph.add_edge(str(v), str(s), label="compatibleWith")

    logger.info(f"Created NetworkX bipartite graph with {nx_graph.number_of_nodes()} nodes and {nx_graph.number_of_edges()} edges.")
    return nx_graph
