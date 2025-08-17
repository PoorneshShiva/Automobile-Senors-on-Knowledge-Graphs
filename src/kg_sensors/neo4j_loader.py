import logging
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
import requests
from neo4j import GraphDatabase

from kg_sensors.exporters import export_to_csv
from kg_sensors.rdf_utils import load_graph_from_ttl, load_multiple_graphs_from_ttl

load_dotenv()

logger = logging.getLogger(__name__)

# --- Environment Variable Configuration ---
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USER = os.environ.get("NEO4J_USER")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_HTTP_URI = os.environ.get("NEO4J_HTTP_URI")


def check_neo4j_password():
    """Checks if the Neo4j password is set in the environment."""
    if not NEO4J_PASSWORD:
        logger.error("NEO4J_PASSWORD environment variable not set.")
        logger.error("Please set it to your Neo4j database password before running the import.")
        logger.error('Example: export NEO4J_PASSWORD="your_password"')
        return False
    return True


def clear_neo4j_database(driver):
    """Deletes all nodes and relationships from the database."""
    logger.info("Clearing the Neo4j database...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    logger.info("Database cleared.")


def import_with_n10s(ttl_file_paths: List[Path], clear_db: bool = False) -> bool:
    """
    Imports one or more RDF TTL files into Neo4j using n10s Cypher procedures.
    The files are merged into a single graph before import.
    """
    if not check_neo4j_password():
        return False

    for p in ttl_file_paths:
        if not p.exists():
            logger.error(f"RDF file not found: {p}")
            return False

    logger.info(f"Loading and merging {len(ttl_file_paths)} TTL files...")
    merged_graph = load_multiple_graphs_from_ttl(ttl_file_paths)
    rdf_data = merged_graph.serialize(format="turtle")

    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            if clear_db:
                logger.info("Clearing the Neo4j database...")
                clear_neo4j_database(driver)

            with driver.session() as session:
                # 1) Add namespace prefixes to n10s
                from kg_sensors.rdf_utils import NS_MAP
                logger.info("Adding namespace prefixes to n10s...")
                for prefix, namespace in NS_MAP.items():
                    session.run(f"CALL n10s.nsprefixes.add('{prefix}', '{namespace}')")

                # 2) Ensure the uniqueness constraint n10s requires
                session.run("""
                    CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS
                    FOR (r:Resource) REQUIRE r.uri IS UNIQUE
                """)

                # 3) Init n10s graph config
                session.run("CALL n10s.graphconfig.init()")

                # 4) Import inline TTL (tune commitSize for large files)
                result = session.run("""
                    CALL n10s.rdf.import.inline($payload, $format, $params)
                    YIELD triplesLoaded, triplesParsed, extraInfo
                    RETURN triplesLoaded, triplesParsed, extraInfo
                """, {
                    "payload": rdf_data,
                    "format": "Turtle",
                    "params": {"commitSize": 25000}
                }).single()

                triples_loaded = result["triplesLoaded"] if result else 0

        if triples_loaded and triples_loaded > 0:
            logger.info(f"Successfully loaded {triples_loaded} triples via n10s (Bolt).")
            return True
        else:
            logger.error("n10s reported that 0 triples were loaded.")
            return False

    except Exception as e:
        logger.error(f"n10s import failed: {e}")
        logger.error("Make sure the n10s plugin is installed and the DB is reachable.")
        return False


def import_with_csv(rdf_graph_path: Path, cypher_script_path: Path, csv_dir: Path, clear_db: bool = False):
    """
    Imports data into Neo4j by first converting RDF to CSV files, then
    executing a Cypher script to load them.
    """
    if not check_neo4j_password():
        return False

    # 1. Export RDF to CSV
    logger.info("Loading RDF graph for CSV export...")
    g = load_graph_from_ttl(rdf_graph_path)
    export_to_csv(g, csv_dir)

    # 2. Load CSVs using Cypher
    if not cypher_script_path.exists():
        logger.error(f"Cypher script not found: {cypher_script_path}")
        return False
        
    with open(cypher_script_path, 'r', encoding='utf-8') as f:
        cypher_query = f.read()

    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            if clear_db:
                logger.info("Clearing the Neo4j database...")
                clear_neo4j_database(driver)
            logger.info("Executing Cypher script to load data from CSV files...")
            with driver.session() as session:
                # The Cypher script is often multiple statements separated by semicolons
                queries = [q.strip() for q in cypher_query.split(';') if q.strip()]
                for i, query in enumerate(queries):
                    logger.info(f"Running Cypher statement {i+1}/{len(queries)}")
                    session.run(query)
            logger.info("Successfully executed Cypher script.")
            return True
    except Exception as e:
        logger.error(f"An error occurred during CSV import: {e}")
        logger.error("Please ensure the Neo4j server is running and credentials are correct.")
        return False