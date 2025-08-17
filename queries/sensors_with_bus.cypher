// Queries for the dataset with detailed bus information (sensors_with_bus.ttl)

// 1. List all sensors and their bus types
MATCH (s:ex__SensorModel)-[:ex__hasBusType]->(b:ex__Protocol)
RETURN s.rdfs__label AS sensor, b.rdfs__label AS bus
ORDER BY bus, sensor

---

// 2. List all sensors connected to the CAN bus
MATCH (s:ex__SensorModel)-[:ex__hasBusType]->(b:ex__Protocol {rdfs__label: 'CAN Bus'})
RETURN s.rdfs__label AS sensor

---

// 3. Count the number of sensors per bus type
MATCH (s:ex__SensorModel)-[:ex__hasBusType]->(b:ex__Protocol)
RETURN b.rdfs__label AS bus, count(s) AS numberOfSensors
ORDER BY numberOfSensors DESC

---

// 4. List all sensors in the "Engine & Powertrain" category and their bus types
MATCH (s:ex__SensorModel)-[:ex__partOf]->(:ex__Powertrain)
MATCH (s)-[:ex__hasBusType]->(b:ex__Protocol)
RETURN s.rdfs__label AS sensor, b.rdfs__label AS bus