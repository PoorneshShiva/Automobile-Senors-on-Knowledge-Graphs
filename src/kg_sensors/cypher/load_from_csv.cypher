// This script loads the knowledge graph from CSV files into Neo4j.
// It assumes the CSV files (nodes.csv, edges.csv) are in the 'import'
// directory of your Neo4j database instance.
// The CLI command handles placing the files there.

// Note: The `periodic commit` helps with large datasets by committing transactions periodically.
// For our small dataset, it's not strictly necessary but is good practice.

// Step 1: Load all nodes and set their labels and properties.
// We use apoc.create.node to dynamically set the label from the 'type' column.
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CALL apoc.create.node([row.type], {uri: row.uri, name: row.label}) YIELD node
RETURN count(*);

// Step 2: Create indexes for faster lookups when creating relationships.
// This is crucial for performance on large graphs.
CREATE INDEX node_uri_index IF NOT EXISTS FOR (n:Resource) ON (n.uri);

// Step 3: Load all edges and create the corresponding relationships.
// We match the start and end nodes by their URI and create the relationship.
// We use apoc.create.relationship to dynamically set the relationship type.
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (start_node {uri: row.start_uri})
MATCH (end_node {uri: row.end_uri})
CALL apoc.create.relationship(start_node, row.type, {uri: row.uri}, end_node) YIELD rel
RETURN count(*);
