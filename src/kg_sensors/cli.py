import logging
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from kg_sensors import data_generator, neo4j_loader, nx_convert, rdf_utils, rag_demo, viz_plotly

# --- Setup ---
app = typer.Typer(
    name="kg-sensors",
    help="A CLI for generating, querying, and visualizing a car sensor knowledge graph.",
    add_completion=False,
)
console = Console()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Default File Paths ---
DEFAULT_TTL_PATH = Path("data/sensors.ttl")
DEFAULT_SPARQL_DIR = Path("queries/")
REPORTS_DIR = Path("reports/")
NEO4J_IMPORTS_DIR = Path("data/csv") # Dir for CSVs to be loaded by Neo4j
CYPHER_SCRIPT_PATH = Path("src/kg_sensors/cypher/load_from_csv.cypher")


@app.callback()
def callback():
    """
    Knowledge Graph for Car Sensors CLI
    """
    pass


@app.command()
def generate(
    size: str = typer.Option("default", help="Size of the dataset to generate: 'small' or 'default'."),
    bus_ontology: bool = typer.Option(False, "--bus", help="Generate the bus ontology (RDFS schema)."),
    sensors_with_bus: bool = typer.Option(False, "--sensors-with-bus", help="Generate the dataset with detailed bus information for each sensor."),
):
    """
    Generates the synthetic sensor dataset as a Turtle (.ttl) file.
    """
    if sensors_with_bus:
        console.print("[bold cyan]Generating dataset with sensor and bus information...[/bold cyan]")
        graph = data_generator.generate_sensors_with_bus_data()
        output_path = Path("data/sensors_with_bus.ttl")
        rdf_utils.save_graph_to_ttl(graph, output_path)
        console.print(f"[bold green]✅ Dataset with bus information generated at:[/] [default]{output_path}[/]")
    elif bus_ontology:
        console.print("[bold cyan]Generating bus ontology...[/bold cyan]")
        bus_graph = data_generator.generate_bus_ontology()
        bus_ontology_path = Path("data/bus_ontology.ttl")
        rdf_utils.save_graph_to_ttl(bus_graph, bus_ontology_path)
        console.print(f"[bold green]✅ Bus ontology generated at:[/] [default]{bus_ontology_path}[/]")
    else:
        console.print(f"[bold cyan]Generating '{size}' dataset...[/bold cyan]")
        
        if size == "default":
            graph = data_generator.generate_dataset()
            rdf_utils.save_graph_to_ttl(graph, DEFAULT_TTL_PATH)
            console.print(f"[bold green]✅ Default dataset generated at:[/] [default]{DEFAULT_TTL_PATH}[/]")
        elif size == "small":
            mini_graph = data_generator.generate_dataset(graph_size="small")
            sample_path = Path("data/samples/mini_sensors.ttl")
            rdf_utils.save_graph_to_ttl(mini_graph, sample_path)
            console.print(f"[bold green]✅ Small sample dataset generated at:[/] [default]{sample_path}[/]")
        else:
            console.print(f"[bold red]Error:[/] Invalid size '{size}'. Please use 'small' or 'default'.")
            raise typer.Exit(1)


@app.command()
def sparql(
    query_file: Path = typer.Argument(..., help="Path to the .sparql file to execute."),
    ttl_file: Path = typer.Option(DEFAULT_TTL_PATH, "--ttl", "-f", help="Path to the RDF data file."),
):
    """
    Runs one or more SPARQL queries from a file against the RDF graph.
    """
    if not query_file.exists():
        console.print(f"[bold red]Error:[/] Query file not found: {query_file}")
        raise typer.Exit(1)
    
    console.print(f"[bold cyan]Loading graph from:[/] [default]{ttl_file}[/]")
    g = rdf_utils.load_graph_from_ttl(ttl_file)

    console.print(f"[bold cyan]Executing queries from:[/] [default]{query_file}[/]")
    with open(query_file, "r") as f:
        # Split queries by a custom separator '---'
        queries = f.read().split("---")
        for i, query_string in enumerate(queries):
            query_string = query_string.strip()
            if not query_string or query_string.startswith("#"):
                continue
            
            console.print(Panel(f"[bold]Query {i+1}[/]", border_style="dim"))
            results = rdf_utils.run_sparql_query(g, query_string)
            rdf_utils.pretty_print_sparql_results(results)


@app.command(name="to-nx")
def to_networkx(
    graph_type: str = typer.Option("entity", help="Type of NetworkX graph to create: 'entity' or 'bipartite'."),
    ttl_file: Path = typer.Option(DEFAULT_TTL_PATH, "--ttl", "-f", help="Path to the RDF data file."),
):
    """
    Converts the RDF graph to a NetworkX graph object.
    """
    console.print(f"[bold cyan]Converting RDF to NetworkX '{graph_type}' graph...[/]")
    g = rdf_utils.load_graph_from_ttl(ttl_file)

    if graph_type == "entity":
        nx_graph = nx_convert.to_networkx_entity_graph(g)
        console.print(f"[bold green]✅ Converted RDF to NetworkX entity graph with {nx_graph.number_of_nodes()} nodes and {nx_graph.number_of_edges()} edges.[/]")
    elif graph_type == "bipartite":
        nx_graph = nx_convert.to_networkx_bipartite_graph(g)
        console.print(f"[bold green]✅ Converted RDF to NetworkX bipartite graph with {nx_graph.number_of_nodes()} nodes and {nx_graph.number_of_edges()} edges.[/]")
    else:
        console.print(f"[bold red]Error:[/] Invalid graph type '{graph_type}'. Use 'entity' or 'bipartite'.")
        raise typer.Exit(1)


@app.command()
def viz(
    graph_type: str = typer.Option("entity", help="NetworkX graph to visualize: 'entity' or 'bipartite'."),
    ttl_file: Path = typer.Option(DEFAULT_TTL_PATH, "--ttl", "-f", help="Path to the RDF data file."),
):
    """
    Generates an interactive Plotly visualization of the graph.
    """
    console.print(f"[bold cyan]Generating Plotly visualization for '{graph_type}' graph...[/]")
    g = rdf_utils.load_graph_from_ttl(ttl_file)
    
    if graph_type == "entity":
        nx_graph = nx_convert.to_networkx_entity_graph(g)
        if ttl_file == Path("data/bus_ontology.ttl"):
            output_path = REPORTS_DIR / "bus_ontology_entity_graph.html"
            title = "Car Communication Buses and Sensors Ontology"
        else:
            output_path = REPORTS_DIR / "entity_graph.html"
            title = "Car Sensors Knowledge Graph - Entity View"
    elif graph_type == "bipartite":
        nx_graph = nx_convert.to_networkx_bipartite_graph(g)
        output_path = REPORTS_DIR / "bipartite_graph.html"
        title = "Sensor-Vehicle Compatibility - Bipartite View"
    else:
        console.print(f"[bold red]Error:[/] Invalid graph type '{graph_type}'. Use 'entity' or 'bipartite'.")
        raise typer.Exit(1)

    viz_plotly.plot_networkx_graph(nx_graph, title, output_path)
    console.print(f"[bold green]✅ Plotly graph saved to:[/] [default]{output_path}[/]")


@app.command(name="neo4j-import")
def neo4j_import(
    ttl_files: Optional[List[Path]] = typer.Option(None, "--ttl", "-f", help="Path to the RDF data file(s). Repeat for multiple files."),
    method: str = typer.Option("n10s", help="Import method: 'n10s' (RDF direct) or 'csv' (LOAD CSV)."),
    clear_db: bool = typer.Option(False, "--clear-db", help="Clear the database before importing."),
):
    """
    Loads the sensor data from one or more TTL files into a Neo4j database.
    """
    if not ttl_files:
        ttl_files = [DEFAULT_TTL_PATH]

    console.print(f"[bold cyan]Loading data into Neo4j using '{method}' method...[/]")
    
    if not neo4j_loader.check_neo4j_password():
        raise typer.Exit(1)

    if method == "n10s":
        success = neo4j_loader.import_with_n10s(ttl_files, clear_db=clear_db)
    elif method == "csv":
        # Note: For LOAD CSV, Neo4j expects files in a specific 'import' directory.
        # This script saves them to data/csv, and the user must copy them to
        # the Neo4j container's import volume.
        console.print(f"[yellow]Note:[/] The CSV files will be generated in [bold]'{NEO4J_IMPORTS_DIR}'[/].")
        console.print(f"You must make these files available to your Neo4j instance's 'import' directory.")
        console.print(f"If using the provided Docker Compose setup, this directory is mapped to './neo4j_import'.")
        console.print(f"Please copy '{NEO4J_IMPORTS_DIR}/*.csv' to 'scripts/neo4j_import/' before proceeding.")
        if not typer.confirm("Have you copied the files and are ready to proceed?"):
            console.print("Aborting.")
            raise typer.Exit()
        # For CSV, we'll just use the first TTL file specified.
        # A more advanced implementation could merge them first.
        success = neo4j_loader.import_with_csv(ttl_files[0], CYPHER_SCRIPT_PATH, NEO4J_IMPORTS_DIR, clear_db=clear_db)
    else:
        console.print(f"[bold red]Error:[/] Invalid method '{method}'. Use 'n10s' or 'csv'.")
        raise typer.Exit(1)

    if success:
        console.print("[bold green]✅ Neo4j import completed successfully![/]")
    else:
        console.print("[bold red]❌ Neo4j import failed. Please check the logs.[/]")
        raise typer.Exit(1)


@app.command()
def examples():
    """
    Runs a curated learning path to demonstrate key features.
    """
    console.print(Panel("[bold yellow]🎓 KGSensors Learning Path 🎓[/]", expand=False))

    console.print("\n[bold cyan]Step 1: Generating the dataset...[/]")
    generate(size="default")

    console.print("\n[bold cyan]Step 2: Running a basic SPARQL query...[/]")
    sparql(query_file=DEFAULT_SPARQL_DIR / "sensors_basics.sparql")

    console.print("\n[bold cyan]Step 3: Running an intermediate SPARQL query with aggregations...[/]")
    sparql(query_file=DEFAULT_SPARQL_DIR / "sensors_intermediate.sparql")

    console.print("\n[bold cyan]Step 4: Generating the Plotly visualization...[/]")
    viz(graph_type="entity")

    console.print("\n[bold green]✅ Example run complete![/]")
    console.print(f"Check out the visualization at [default]reports/entity_graph.html[/]")


@app.command(name="ask")
def ask_rag(
    question: str = typer.Argument(..., help="A natural language question for the KG."),
    ttl_file: Path = typer.Option(DEFAULT_TTL_PATH, "--ttl", "-f", help="Path to the RDF data file."),
):
    """
    (Demo) Asks a natural language question to the knowledge graph.
    """
    console.print(f"[bold cyan]Answering question:[/]' {question}'")
    g = rdf_utils.load_graph_from_ttl(ttl_file)
    answer = rag_demo.answer_question_with_kg(question, g)
    console.print(Panel(answer, title="[bold green]Answer from KG[/]", border_style="green"))


@app.command()
def n10s_ping():
    """Pings the n10s endpoint to check if it is available."""
    import requests
    from kg_sensors.neo4j_loader import NEO4J_HTTP_URI, NEO4J_USER, NEO4J_PASSWORD
    ping_url = NEO4J_HTTP_URI
    try:
        response = requests.get(ping_url, auth=(NEO4J_USER, NEO4J_PASSWORD))
        response.raise_for_status()
        console.print(f"[bold green]✅ Ping successful![/bold green]")
        console.print(response.headers)
        console.print(response.text)
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ Ping failed.[/bold red]")
        console.print(e)


if __name__ == "__main__":
    app()