// Query 1: Visualize all Sensor Instances and their direct connections.
// This query helps to see how individual sensors are related to other entities
// like Vehicle Models, ECUs, and Locations.
MATCH (s:ns0__SensorInstance)-[r]-(o)
RETURN s, r, o

---

// Query 2: Visualize Sensor Instances, their Sensor Models, and the Communication Protocol (Bus) they use.
// This query helps to understand which bus a sensor communicates over.
MATCH (si:ns0__SensorInstance)-[:ns0__isInstanceOf]->(sm:ns0__SensorModel)-[:ns0__usesProtocol]->(p)
RETURN si, sm, p
