# Setup and Installation Guide

This guide provides detailed instructions for setting up the project environment, including Python, dependencies, and the Neo4j graph database.

## 1. Prerequisites

*   **Python 3.12**: This project requires Python 3.12 or newer. You can check your version with `python3 --version`.
*   **Git**: For cloning the repository.
*   **Docker and Docker Compose**: Required for the easiest way to run a local Neo4j database.

## 2. Core Project Installation

These steps are for setting up the Python environment and installing the required packages on Linux, macOS, or Windows (using PowerShell/WSL).

```bash
# 1. Clone the repository (if you haven't already)
# git clone <repository_url>
# cd kg-car-sensors

# 2. Create a Python virtual environment
# This isolates project dependencies from your system's Python.
python3.12 -m venv .venv

# 3. Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# Your shell prompt should now be prefixed with (.venv).

# 4. Install the project and its dependencies
# The '-e' flag installs it in "editable" mode, so changes to the source
# code are immediately reflected.
pip install -e .

# 5. (Optional) Install development dependencies for running tests
pip install -e .[dev]
```

### Verification

To ensure everything is installed correctly, run the test suite:

```bash
# First, generate the data required for the tests
python -m kg_sensors.cli generate

# Now run pytest
pytest
```

You should see all tests passing.

### Environment Configuration

The project uses a `.env` file to manage environment variables for connecting to Neo4j. A sample file is provided as `.env.sample`.

1.  **Create a copy of the sample file:**
    ```bash
    cp .env.sample .env
    ```

2.  **Edit the `.env` file:**
    Open the `.env` file in a text editor and set the `NEO4J_PASSWORD` to the password you set for your Neo4j database.

    ```
    # .env
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your_neo4j_password
    NEO4J_HTTP_URI=http://localhost:7474
    ```

## 3. Neo4j Database Setup (Optional)

If you want to complete the Neo4j integration part of the tutorial, you'll need a running Neo4j instance. We provide a Docker Compose file for a quick and easy setup.

### Using Docker Compose (Recommended)

The `scripts/neo4j_docker_compose.yaml` file is configured to launch Neo4j v5 with the powerful **APOC** and **n10s (Neosemantics)** plugins, which are essential for RDF integration.

```bash
# 1. Navigate to the scripts directory
cd scripts

# 2. Start the Neo4j container in the background
docker-compose up -d

# 3. Check the container status
docker-compose ps
# You should see the 'kg-car-sensors-neo4j-1' container running.
```

The Neo4j database will be available at:
*   **Bolt Port**: `7687` (for the Python driver)
*   **HTTP Port**: `7474` (for the Neo4j Browser UI)

You can access the Neo4j Browser by navigating to `http://localhost:7474` in your web browser.

**Default Credentials:**
*   **Username**: `neo4j`
*   **Password**: `password` (You will be prompted to change this on first login. Remember the new password!)

### Enabling n10s (Neosemantics)

The n10s plugin needs to be initialized once per database.

1.  Open the Neo4j Browser at `http://localhost:7474`.
2.  Log in with the default credentials and set a new password.
3.  Run the following Cypher command in the query editor:

```cypher
CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE;
```

This creates a uniqueness constraint required by n10s to function correctly. Your database is now ready to accept RDF data.

### Loading Data into Neo4j

With the database running and n10s initialized, you can now load the RDF data.

Now, run the import command from the project's root directory:

```bash
# Method 1: Using n10s to import the TTL file directly
python -m kg_sensors.cli neo4j-import --method n10s

# Method 2: Using the CSV export and LOAD CSV Cypher script
python -m kg_sensors.cli neo4j-import --method csv
```

You can now explore the imported graph in the Neo4j Browser!

### Troubleshooting

*   **Port Conflicts**: If port `7474` or `7687` is already in use, you can change the ports in the `scripts/neo4j_docker_compose.yaml` file.
*   **Authentication Errors**: Double-check that you have set the `NEO4J_PASSWORD` in your `.env` file correctly.
*   **n10s Errors**: Ensure you have run the `CREATE CONSTRAINT` Cypher command before attempting to import data.
*   **Memory Issues**: Docker needs sufficient memory allocated to run Neo4j (4GB is a safe minimum). You can adjust this in Docker Desktop's settings.