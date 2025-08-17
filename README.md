# Knowledge Graph for Car Sensors (kg-car-sensors)

This repository provides a complete, runnable project to learn about Knowledge Graphs (KGs) using a synthetic-but-realistic dataset of automobile sensors. You will explore the entire pipeline: from data generation and ontology design to querying, visualization, and integration with different graph databases and tools.

This project is designed for beginners and uses Python 3.12, RDF/SPARQL, Neo4j, NetworkX, and Plotly.

![Plotly Entity Graph Screenshot](https://github.com/PoorneshShiva/Automobile-Senors-on-Knowledge-Graphs/main/public/images/graph.png)
*(An example of the interactive entity graph you will generate.)*

## What You'll Learn

*   **Ontology Design**: How to model a domain (car sensors) with classes and properties.
*   **Data Generation**: Create a synthetic, interconnected RDF dataset in Turtle format.
*   **RDF & SPARQL**: Use `rdflib` to work with RDF data and run SPARQL queries to ask complex questions.
*   **Graph Algorithms**: Convert RDF data into `networkx` graphs to analyze connectivity.
*   **Graph Visualization**: Create beautiful, interactive visualizations with `plotly`.
*   **Graph Database Integration**: Load your KG into a production-grade Neo4j database using two different methods (n10s RDF import and CSV import).
*   **Lightweight RAG**: See a tiny example of how a KG can power a Retrieval-Augmented Generation-like system.

## Quickstart (5-10 Minutes)

Get up and running in a few simple commands. This will generate the data, run some queries, and create an interactive visualization.

```bash
# 1. Clone the repository (not shown)

# 2. Create a virtual environment and activate it
python3.12 -m venv .venv
source .venv/bin/activate
# On Windows: .venv\Scripts\activate

# 3. Install the project in editable mode
pip install -e .

# 4. Generate the synthetic sensor dataset
python -m kg_sensors.cli generate
# Output: ✅ Dataset generated at data/sensors.ttl

# To generate the bus ontology (RDFS schema for car communication buses and sensors)
python -m kg_sensors.cli generate --bus
# Output: ✅ Bus ontology generated at data/bus_ontology.ttl

# To generate a dataset with detailed bus information for each sensor
python -m kg_sensors.cli generate --sensors-with-bus
# Output: ✅ Dataset with bus information generated at data/sensors_with_bus.ttl

# 5. Run some basic SPARQL queries
python -m kg_sensors.cli sparql queries/sensors_basics.sparql

# To query the bus ontology
python -m kg_sensors.cli sparql queries/bus_ontology_basics.sparql --ttl data/bus_ontology.ttl

# 6. Convert the RDF graph to a NetworkX graph
python -m kg_sensors.cli to-nx --graph-type entity
# Output: ✅ Converted RDF to NetworkX entity graph with X nodes and Y edges.

# To convert the bus ontology to a NetworkX graph
python -m kg_sensors.cli to-nx --graph-type entity --ttl data/bus_ontology.ttl
# Output: ✅ Converted RDF to NetworkX entity graph with X nodes and Y edges.

# 7. Create an interactive Plotly visualization
python -m kg_sensors.cli viz --graph-type entity
# Output: ✅ Plotly graph saved to reports/entity_graph.html

# To create an interactive Plotly visualization for the bus ontology
python -m kg_sensors.cli viz --graph-type entity --ttl data/bus_ontology.ttl
# Output: ✅ Plotly graph saved to reports/bus_ontology_entity_graph.html
```

Now you can open `reports/entity_graph.html` in your browser to explore the graph!

## Generated Sensors

The data generation process creates the following sensor models:

*   WSS-MR-3 Magnetoresistive Wheel Speed Sensor
*   CPS-HS-5 Hall-Effect Crankshaft Sensor
*   BOS-O2-H1 Heated O2 Sensor
*   KS-PZ-2 Piezo Knock Sensor
*   TPMS-L4 Tire Pressure Monitor
*   AMB-T-300 Ambient Temp Sensor
*   ACC-LR-01 Long-Range Radar

## Bus Systems and Sensor Connections

Different buses are used depending on criticality, speed, and cost:

*   **CAN (Controller Area Network):** High-reliability, medium/high speed, widely used in engine/powertrain.
*   **LIN (Local Interconnect Network):** Low-cost, low-speed bus for simple actuators/sensors (mirrors, windows, climate).
*   **FlexRay:** High-speed, time-deterministic, safety-critical (steer-by-wire, brake-by-wire).
*   **Ethernet Automotive:** High-bandwidth, ADAS cameras, radar, infotainment.
*   **MOST (Media Oriented Systems Transport):** Multimedia/audio/video.
*   **K-line / legacy:** Diagnostics (older cars).

### Sensors + Typical Bus Connections

#### 1. Engine & Powertrain Sensors (usually CAN / sometimes LIN)

*   Oxygen Sensor (O2) → CAN (powertrain ECU)
*   MAF (Mass Air Flow) Sensor → CAN
*   MAP (Manifold Pressure) Sensor → CAN
*   Throttle Position Sensor → CAN
*   Crankshaft Position Sensor → CAN (high-priority, timing critical)
*   Camshaft Position Sensor → CAN
*   Knock Sensor → CAN
*   Coolant Temp Sensor → CAN (sometimes LIN for non-critical)
*   Oil Pressure Sensor → CAN
*   Fuel Pressure Sensor → CAN
*   Transmission Speed Sensor → CAN
*   Clutch/Brake Pedal Position Sensor → CAN

#### 2. Environmental & Comfort Sensors (mostly LIN)

*   Ambient Temperature Sensor → LIN
*   Cabin Temperature Sensor → LIN
*   Sunlight Sensor → LIN (climate control)
*   Rain Sensor → LIN
*   Humidity Sensor → LIN
*   Air Quality Sensor → LIN

#### 3. Vehicle Dynamics Sensors (usually CAN / FlexRay)

*   Wheel Speed Sensors → CAN (ABS/ESP ECU)
*   Steering Angle Sensor → CAN (sometimes FlexRay in safety-critical)
*   Yaw Rate Sensor → CAN / FlexRay
*   Lateral Acceleration Sensor → CAN / FlexRay
*   Brake Pressure Sensor → CAN
*   Suspension Height Sensor → CAN / LIN
*   TPMS (Tire Pressure Monitoring) → RF wireless to ECU, then CAN

#### 4. Safety & ADAS Sensors

*   Radar Sensors → CAN / Automotive Ethernet
*   LiDAR Sensors → Automotive Ethernet
*   Ultrasonic Sensors → LIN (clusters) or CAN
*   Camera Sensors → Automotive Ethernet (high bandwidth)
*   Seat Occupant / Weight Sensors → LIN
*   Airbag Crash Sensors → CAN (safety ECU)

#### 5. Exhaust & Emission Sensors

*   NOx Sensor → CAN (engine ECU)
*   Exhaust Gas Temp Sensor (EGT) → CAN
*   DPF Pressure Sensor → CAN

### Big Picture Mapping

*   Powertrain & dynamics sensors → CAN (sometimes FlexRay)
*   Comfort/climate sensors → LIN
*   High-bandwidth ADAS sensors → Automotive Ethernet
*   Legacy or simple setups → K-line / RF → CAN.

## Learning Roadmap

This project is structured to guide you from basic concepts to more advanced applications.

1.  **Understand the Data Model**:
    *   Start with `docs/ontology.md` to see the structure of the knowledge graph.
    *   Read `docs/data_description.md` for a human-readable overview of the sensor data.

2.  **Querying the Knowledge Graph**:
    *   **SPARQL**:
        *   `queries/sensors_basics.sparql`: Learn the fundamentals of `SELECT`, `WHERE`, and `FILTER`.
        *   `queries/sensors_intermediate.sparql`: Explore `GROUP BY`, aggregations, and property paths.
        *   `queries/reasoning_examples.sparql`: See how `rdfs:subClassOf` can make your queries more powerful.
    *   **Cypher (for Neo4j)**:
        *   `queries/sensors_with_bus.cypher`: Contains example Cypher queries to run against the `sensors_with_bus.ttl` dataset in Neo4j.
        *   `queries/graph_view.cypher`: Contains example Cypher queries for visualizing the graph in Neo4j Browser.

3.  **Visualize and Analyze**:
    *   Run the `to-nx` and `viz` CLI commands to see the graph's structure.
    *   Explore the code in `src/kg_sensors/nx_convert.py` and `src/kg_sensors/viz_plotly.py`.

4.  **Integrate with Neo4j**:
    *   Follow the `setup.md` guide to launch a Neo4j instance using the provided `docker-compose` file.
    *   Try both loading methods:
        *   **n10s (Neosemantics)**: Directly import the RDF data. To import both the sensors and the bus ontology, run:
          ```bash
          python -m kg_sensors.cli neo4j-import --method n10s --ttl data/sensors.ttl --ttl data/bus_ontology.ttl
          ```
        *   To import the new dataset with bus information:
          ```bash
          python -m kg_sensors.cli neo4j-import --method n10s --ttl data/sensors_with_bus.ttl
          ```
        *   **CSV + Cypher**: Export to CSV and use `LOAD CSV` for fine-grained control.
          ```bash
          python -m kg_sensors.cli neo4j-import --method csv
          ```
    *   **Updating Data**: By default, the `neo4j-import` command will add data to the existing graph. If you want to clear the database before importing, use the `--clear-db` flag:
        ```bash
        python -m kg_sensors.cli neo4j-import --method n10s --ttl data/sensors.ttl --clear-db
        ```

## Project Structure

A brief overview of the key files and directories:

*   `README.md`: This file.
*   `setup.md`: Detailed installation and configuration guide.
*   `pyproject.toml`: Project dependencies and metadata.
*   `data/`: Contains the generated RDF data (`sensors.ttl`).
*   `docs/`: In-depth documentation on the ontology and data.
*   `queries/`: SPARQL query files for learning.
*   `src/kg_sensors/`: The core Python source code.
    *   `cli.py`: The Typer/Rich command-line interface.
    *   `data_generator.py`: The script that creates the dataset.
    *   `rdf_utils.py`: Helpers for working with `rdflib`.
    *   `nx_convert.py` & `viz_plotly.py`: NetworkX/Plotly logic.
    *   `neo4j_loader.py`: Logic for loading data into Neo4j.
*   `scripts/`: Helper scripts, including `run_all.sh` and `neo4j_docker_compose.yaml`.
*   `tests/`: Project tests to ensure correctness.