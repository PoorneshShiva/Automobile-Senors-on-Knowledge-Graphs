# Ontology Design for the Car Sensor Knowledge Graph

This document outlines the design choices, structure, and rationale for the ontology used in this project. The ontology defines the "vocabulary" or "schema" of our knowledge graph.

## 1. Design Principles

*   **Clarity and Simplicity**: The ontology is intentionally small and focused. It's designed for teaching, not for industrial-scale production.
*   **Realism**: The concepts and relationships are based on real-world automotive engineering principles.
*   **Extensibility**: The structure allows for new types of sensors, vehicles, and properties to be added easily.
*   **Distinction between Type and Instance**: A key concept is the separation of a `SensorModel` (the blueprint, e.g., a Bosch XYZ sensor) from a `SensorInstance` (the physical thing in a specific car). This is a common and powerful modeling pattern.

## 2. Prefixes

We use standard prefixes to shorten URIs.

| Prefix | Full URI                               | Description                                  |
| :----- | :------------------------------------- | :------------------------------------------- |
| `ex:`    | `http://example.com/ontology/`         | Core ontology classes and properties         |
| `sen:`   | `http://example.com/sensor/`           | URIs for specific sensors (models/instances) |
| `veh:`   | `http://example.com/vehicle/`          | URIs for specific vehicles and components    |
| `rdfs:`  | `http://www.w3.org/2000/01/rdf-schema#`  | RDF Schema for labels, comments, subclasses  |
| `xsd:`   | `http://www.w3.org/2001/XMLSchema#`    | Standard data types (string, decimal, etc.)  |

## 3. Class Hierarchy

We use `rdfs:subClassOf` to create a simple hierarchy. This helps in writing more general queries.

```
rdfs:Resource
└── ex:Concept
|   ├── ex:SensorType
|   ├── ex:Subsystem
|   ├── ex:Protocol
|   └── ...
└── ex:Component
    ├── ex:VehicleModel
    ├── ex:SensorModel
    ├── ex:SensorInstance
    └── ex:ECU
```

*   **`ex:Concept`**: An abstract idea or classification (e.g., Temperature, Powertrain).
*   **`ex:Component`**: A physical or logical component part (e.g., a specific car, a sensor model).

## 4. Ontology Diagram (ASCII)

This diagram shows the main classes and their relationships. `(Class A) --[property]--> (Class B)` means a resource of type `Class A` is linked to a resource of type `Class B` via the `property` predicate.

```
                               +------------------+
                               | ex:VehicleModel  |
                               +------------------+
                                     ^      |
                                     |      | ex:manufacturedBy
      ex:installedInModel /          |      |
                         /           |      v
  +-------------------+ <------------+   +------------------------+
  | ex:SensorInstance |              |   | ex:VehicleManufacturer |
  +-------------------+------------> +   +------------------------+
      |           |     ex:connectsToECU
      |           |
      | ex:isInstanceOf
      |           |
      v           v
+---------------+   +---------+
| ex:SensorModel|   | ex:ECU  |
+---------------+   +---------+
  |    |    |           ^
  |    |    |           | ex:partOf
  |    |    +--------------------> +------------+
  |    | ex:usesProtocol           | ex:Subsystem |
  |    |                           +------------+
  |    v
  |  +------------+
  |  | ex:Protocol|
  |  +------------+
  |
  | ex:hasSensorType
  v
+-------------+
| ex:SensorType |
+-------------+
```

## 5. Properties: Domain and Range

This table defines the intended subject (`Domain`) and object (`Range`) for our key properties.

| Property                | Domain              | Range               | Description                                    |
| :---------------------- | :------------------ | :------------------ | :--------------------------------------------- |
| **Object Properties**   |                     |                     |                                                |
| `ex:manufacturedBy`     | `ex:Component`      | `ex:Manufacturer`   | Who made the component.                        |
| `ex:installedInModel`   | `ex:SensorInstance` | `ex:VehicleModel`   | Puts a specific sensor in a specific car model.|
| `ex:isInstanceOf`       | `ex:SensorInstance` | `ex:SensorModel`    | Links a physical sensor to its blueprint.      |
| `ex:connectsToECU`      | `ex:SensorInstance` | `ex:ECU`            | Defines the data path from sensor to ECU.      |
| `ex:partOf`             | `ex:ECU`            | `ex:Subsystem`      | Assigns an ECU to a car subsystem.             |
| `ex:locatedAt`          | `ex:SensorInstance` | `ex:Location`       | Physical placement of the sensor.              |
| `ex:usesProtocol`       | `ex:SensorModel`    | `ex:Protocol`       | Communication standard used.                   |
| `ex:hasSensorType`      | `ex:SensorModel`    | `ex:SensorType`     | The general category of the sensor.            |
| `ex:relatedDTC`         | `ex:SensorModel`    | `ex:DTC`            | A fault code associated with this sensor model.|
| **Data Properties**     |                     |                     |                                                |
| `ex:sampleRateHz`       | `ex:SensorModel`    | `xsd:decimal`       | Readings per second.                           |
| `ex:powerDrawW`         | `ex:SensorModel`    | `xsd:decimal`       | Power consumption in watts.                    |
| `ex:priceUSD`           | `ex:SensorModel`    | `xsd:decimal`       | Approximate cost.                              |
| `ex:protocolBandwidthKbps` | `ex:Protocol`    | `xsd:integer`       | Data rate of the protocol.                     |

## 6. Rationale for Modeling Choices

*   **`SensorModel` vs. `SensorInstance`**: This is the most important distinction.
    *   **`SensorModel`** holds all the reusable technical specifications (sample rate, accuracy, protocol). It is `compatibleWith` a `VehicleModel`.
    *   **`SensorInstance`** represents the single, unique sensor in a car. It has a specific `location` and is `installedIn` a specific `VehicleModel`. This prevents data duplication and makes the graph more precise. For example, you can say "the front-right wheel sensor" is an *instance* of the "Bosch WSS-MR-3" *model*.

*   **`ex:hasSensorType` vs. `rdfs:subClassOf`**: We use `ex:hasSensorType` to link a `SensorModel` to a category like `ex:TemperatureSensor`. We *could* have made each sensor model a subclass of `ex:TemperatureSensor`, but this is less flexible. Using a property link allows a sensor to have multiple types if needed and keeps the class hierarchy cleaner.

## 7. Mapping RDF to a Labeled Property Graph (Neo4j)

When we load this RDF data into Neo4j, the mapping will look like this:

*   **Nodes**: Each unique URI (like `sen:WSS-MR-3` or `veh:Camry`) becomes a node in Neo4j.
*   **Node Labels**: The `rdf:type` of a resource becomes its label in Neo4j. For example, `sen:WSS-MR-3` has `rdf:type ex:SensorModel`, so it will become a node with the label `:SensorModel`.
*   **Node Properties**: RDF properties with literal values (like numbers or strings) become node properties in Neo4j. For example, the triple `sen:WSS-MR-3 ex:sampleRateHz "100"^^xsd:decimal` results in the `SensorModel` node having a property `sampleRateHz: 100`. The `rdfs:label` also becomes a `name` or `label` property on the node.
*   **Relationships**: RDF properties that link two URIs become relationships in Neo4j. The triple `sen:camry_wss_fr ex:connectsToECU veh:RAV4SafetyECU` becomes a relationship `(:SensorInstance)-[:CONNECTS_TO_ECU]->(:ECU)`. The relationship type is derived from the predicate's local name.
