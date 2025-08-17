from pathlib import Path

import pytest
from rdflib import Graph

from kg_sensors.rdf_utils import load_graph_from_ttl, run_sparql_query

# Define paths
TTL_FILE_PATH = Path("data/sensors.ttl")
QUERIES_DIR = Path("queries/")

@pytest.fixture(scope="module")
def full_graph() -> Graph:
    """Fixture to load the main RDF graph once for all tests in this module."""
    if not TTL_FILE_PATH.exists():
        pytest.fail(f"Data file not found: {TTL_FILE_PATH}. Please run the data generation step first.")
    return load_graph_from_ttl(TTL_FILE_PATH)

def get_query_from_file(file_path: Path, query_index: int = 0) -> str:
    """Reads a specific query from a SPARQL file that uses '---' as a separator."""
    if not file_path.exists():
        pytest.fail(f"Query file not found: {file_path}")
    with open(file_path, 'r') as f:
        content = f.read()
    queries = [q.strip() for q in content.split('---') if q.strip() and not q.strip().startswith('#')]
    if query_index >= len(queries):
        pytest.fail(f"Query index {query_index} out of bounds for file {file_path}")
    return queries[query_index]

def test_basic_query_all_sensor_types(full_graph: Graph):
    """
    Tests the first query in sensors_basics.sparql: "List all available sensor types".
    Asserts that the query runs and returns a non-empty result.
    """
    query_file = QUERIES_DIR / "sensors_basics.sparql"
    query_string = get_query_from_file(query_file, query_index=0)
    
    results = run_sparql_query(full_graph, query_string)
    
    assert isinstance(results, list)
    assert len(results) > 5  # Expecting at least 5 sensor types
    assert "sensor_type" in results[0]
    assert "label" in results[0]

def test_intermediate_query_count_sensors(full_graph: Graph):
    """
    Tests the first query in sensors_intermediate.sparql: "Count the number of sensor models per sensor type".
    Asserts that the query runs and returns a non-empty result with the correct columns.
    """
    query_file = QUERIES_DIR / "sensors_intermediate.sparql"
    query_string = get_query_from_file(query_file, query_index=0)
    
    results = run_sparql_query(full_graph, query_string)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert "type_label" in results[0]
    assert "count" in results[0]
    assert isinstance(results[0]["count"], int)

def test_reasoning_query_find_components(full_graph: Graph):
    """
    Tests the first query in reasoning_examples.sparql: "Find all components".
    This relies on `rdfs:subClassOf` traversal.
    """
    query_file = QUERIES_DIR / "reasoning_examples.sparql"
    query_string = get_query_from_file(query_file, query_index=0)
    
    results = run_sparql_query(full_graph, query_string)
    
    assert isinstance(results, list)
    assert len(results) > 10 # Should find many components
    assert "component" in results[0]
    assert "label" in results[0]
    assert "type" in results[0]
