// Queries for visualizing the graph view of the dataset with detailed bus information (sensors_with_bus.ttl)

// 1. Visualize all sensors and their bus types
MATCH (s:ex__SensorModel)-[r:ex__hasBusType]->(b:ex__Protocol)
RETURN s, r, b

---

// 2. Visualize all sensors connected to the CAN bus
MATCH (s:ex__SensorModel)-[r:ex__hasBusType]->(b:ex__Protocol {rdfs__label: 'CAN Bus'})
RETURN s, r, b

---

// 3. Visualize all sensors in the "Engine & Powertrain" category and their bus types
MATCH (s:ex__SensorModel)-[r1:ex__partOf]->(c:ex__Powertrain)
MATCH (s)-[r2:ex__hasBusType]->(b:ex__Protocol)
RETURN s, r1, c, r2, b