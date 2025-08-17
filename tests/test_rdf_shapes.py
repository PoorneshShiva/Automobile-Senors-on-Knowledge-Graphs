from pathlib import Path

import pytest
from rdflib import Graph, URIRef

from kg_sensors.rdf_utils import EX, DTC, PROT, load_graph_from_ttl

# Define the path to the generated data file
TTL_FILE_PATH = Path("data/sensors.ttl")

@pytest.fixture(scope="module")
def full_graph() -> Graph:
    """Fixture to load the main RDF graph once for all tests in this module."""
    if not TTL_FILE_PATH.exists():
        pytest.fail(f"Data file not found: {TTL_FILE_PATH}. Please run the data generation step first.")
    return load_graph_from_ttl(TTL_FILE_PATH)

def run_ask_query(g: Graph, query: str) -> bool:
    """Helper to run an ASK query and return a boolean result."""
    return bool(list(g.query(query))[0])

def test_graph_is_not_empty(full_graph: Graph):
    """Test that the graph contains a reasonable number of triples."""
    assert len(full_graph) > 200
    assert len(full_graph) < 1000

def test_key_classes_exist(full_graph: Graph):
    """Test that instances of core classes are present in the graph."""
    classes_to_check = [
        EX.VehicleModel,
        EX.SensorModel,
        EX.SensorInstance,
        EX.ECU,
        EX.SensorType,
    ]
    for cls in classes_to_check:
        query = f"ASK {{ ?s a <{cls}> . }}"
        assert run_ask_query(full_graph, query), f"No instances of class {cls} found."

def test_dtc_codes_are_present(full_graph: Graph):
    """Check for the presence of at least one Diagnostic Trouble Code."""
    query = f"ASK {{ ?s a <{EX.DTC}> . }}"
    # In our ontology, DTCs don't have a type, they are just linked.
    # Let's check if a known DTC URI exists as a subject or object.
    assert (DTC.P0135, None, None) in full_graph or (None, None, DTC.P0135) in full_graph

def test_protocols_are_present(full_graph: Graph):
    """Check that both CAN and LIN protocols are defined."""
    assert (PROT.CAN, None, None) in full_graph
    assert (PROT.LIN, None, None) in full_graph

def test_at_least_three_vehicle_models(full_graph: Graph):
    """Verify that there are 3 or more vehicle models defined."""
    query = "SELECT (COUNT(DISTINCT ?s) as ?count) WHERE { ?s a <http://example.com/ontology/VehicleModel> . }"
    result = list(full_graph.query(query))
    assert result[0]["count"].toPython() >= 3

def test_sensor_instance_has_all_key_relations(full_graph: Graph):
    """
    Checks if a sensor instance is properly connected to its model, vehicle, location, and ECU.
    """
    query = """
        PREFIX ex: <http://example.com/ontology/>
        ASK {
            ?instance a ex:SensorInstance ;
                ex:isInstanceOf ?model ;
                ex:installedInModel ?vehicle ;
                ex:locatedAt ?location ;
                ex:connectsToECU ?ecu .
        }
    """
    assert run_ask_query(full_graph, query), "A SensorInstance is missing one of its key relationships."
