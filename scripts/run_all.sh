#!/bin/bash

# This script provides an end-to-end demonstration of the project's core features.
# It creates a virtual environment, installs dependencies, generates data,
# runs a query, and creates a visualization.

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting KG-Car-Sensors End-to-End Demo ---"

# --- 1. Setup Python Virtual Environment ---
if [ -d ".venv" ]; then
    echo "--> Virtual environment '.venv' already exists. Activating..."
else
    echo "--> Creating Python virtual environment in '.venv'..."
    python3.12 -m venv .venv
fi
source .venv/bin/activate
echo "--> Environment activated."

# --- 2. Install Dependencies ---
echo "--> Installing project dependencies from pyproject.toml..."
pip install -q -e .
echo "--> Installation complete."

# --- 3. Generate Data ---
echo "--> Generating the synthetic RDF dataset..."
python -m kg_sensors.cli generate
DATA_FILE="data/sensors.ttl"
echo "--> Dataset created at $DATA_FILE"

# --- 4. Run a SPARQL Query ---
echo "--> Running a basic SPARQL query..."
QUERY_FILE="queries/sensors_basics.sparql"
python -m kg_sensors.cli sparql "$QUERY_FILE"
echo "--> SPARQL query finished."

# --- 5. Create a Visualization ---
echo "--> Creating an interactive Plotly visualization..."
python -m kg_sensors.cli viz --graph entity
VIZ_FILE="reports/entity_graph.html"
echo "--> Visualization created at $VIZ_FILE"

# --- Summary ---
echo ""
echo "--- ✅ Demo Complete! ---"
echo "Summary of outputs:"
echo "  - RDF Data:       $DATA_FILE"
echo "  - SPARQL Queries: $QUERY_FILE"
echo "  - Visualization:  $VIZ_FILE"
echo ""
echo "Next step: Open '$VIZ_FILE' in your web browser to explore the graph!"
echo "Or, explore other commands: python -m kg_sensors.cli --help"
