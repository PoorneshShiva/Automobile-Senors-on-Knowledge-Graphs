import logging
from pathlib import Path
from typing import Dict, List

import networkx as nx
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# Define a color palette for different node types
COLOR_PALETTE = {
    "SensorModel": "#1f77b4",  # Muted Blue
    "SensorInstance": "#aec7e8",  # Light Blue
    "VehicleModel": "#ff7f0e",  # Safety Orange
    "ECU": "#ffbb78",  # Light Orange
    "SensorType": "#2ca02c",  # Cooked Asparagus Green
    "Subsystem": "#98df8a",  # Light Green
    "Protocol": "#d62728",  # Brick Red
    "Location": "#ff9896",  # Light Red
    "DTC": "#9467bd",  # Muted Purple
    "Manufacturer": "#8c564b",  # Chestnut Brown
    "Default": "#7f7f7f",  # Middle Gray
}


def plot_networkx_graph(nx_graph: nx.Graph, title: str, output_path: Path):
    """
    Creates an interactive force-directed graph visualization using Plotly.
    """
    # 1. Create the graph layout
    pos = nx.spring_layout(nx_graph, seed=42, k=0.3, iterations=50)

    # 2. Prepare node and edge traces for Plotly
    edge_x, edge_y = [], []
    for edge in nx_graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x, node_y = [], []
    node_text, node_colors, node_sizes = [], [], []
    node_types = sorted(list(set(nx.get_node_attributes(nx_graph, 'type').values())))

    for node, adjacencies in nx_graph.adjacency():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Node size based on degree
        node_sizes.append(10 + len(adjacencies) * 2)
        
        # Node color based on type
        node_type = nx_graph.nodes[node].get('type', 'Default')
        node_colors.append(COLOR_PALETTE.get(node_type, COLOR_PALETTE["Default"]))
        
        # Node hover text
        label = nx_graph.nodes[node].get('label', node)
        text = f"<b>{label}</b><br>Type: {node_type}<br>Degree: {len(adjacencies)}"
        node_text.append(text)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line_width=2))

    # 3. Create the figure and add traces
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=title,
                        title_font=dict(size=16),
                        showlegend=True,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="Interactive knowledge graph of car sensors. Hover over nodes for details.",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    # 4. Add a legend for node types
    for node_type in node_types:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], # No data points
            mode='markers',
            marker=dict(size=10, color=COLOR_PALETTE.get(node_type, COLOR_PALETTE["Default"])),
            name=node_type,
            showlegend=True
        ))

    # 5. Save to HTML
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path), auto_open=False)
    logger.info(f"Plotly graph saved to {output_path}")
