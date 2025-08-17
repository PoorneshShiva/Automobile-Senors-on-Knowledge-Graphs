# Data Description: Car Sensor Knowledge Graph

This document provides a human-readable overview of the synthetic dataset used in this project. It describes the types of entities (classes), their relationships (properties), and provides concrete examples.

### Prefixes Legend

To keep the data concise, we use prefixes. Here's what they mean:

| Prefix | Full URI                               | Description                                     |
| :----- | :------------------------------------- | :---------------------------------------------- |
| `ex:`    | `http://example.com/ontology/`         | Core ontology concepts (classes, properties)    |
| `sen:`   | `http://example.com/sensor/`           | Specific sensor models and instances            |
| `veh:`   | `http://example.com/vehicle/`          | Specific vehicle models and components          |
| `dtc:`   | `http://example.com/dtc/`              | Diagnostic Trouble Codes (DTCs)                 |
| `prot:`  | `http://example.com/protocol/`         | Communication protocols (e.g., CAN, LIN)        |
| `unit:`  | `http://example.com/unit/`             | Units of measurement (e.g., Celsius, Hz)        |
| `rdfs:`  | `http://www.w3.org/2000/01/rdf-schema#`  | RDF Schema vocabulary (labels, comments)        |
| `xsd:`   | `http://www.w3.org/2001/XMLSchema#`    | XML Schema datatypes (e.g., string, integer)    |

---

## Core Concepts (Classes)

The graph revolves around a few key types of entities:

*   **`ex:VehicleModel`**: Represents a specific car model, like a "Toyota Camry".
    *   *Example*: `veh:Camry`
*   **`ex:SensorModel`**: Represents a specific *type* of sensor component from a manufacturer, like Bosch's "WSS-MR-3" wheel speed sensor. It has technical specifications.
    *   *Example*: `sen:WSS-MR-3`
*   **`ex:SensorInstance`**: Represents a specific physical sensor *installed* in a specific car. It connects a `SensorModel` to a `VehicleModel`.
    *   *Example*: `sen:camry_wss_fr` (the front-right wheel speed sensor on a Camry)
*   **`ex:ECU` (Electronic Control Unit)**: The computer in a car that a sensor reports to.
    *   *Example*: `veh:CamryECU`
*   **`ex:Subsystem`**: A functional area of the car, like "Powertrain" or "Safety".
*   **`ex:Protocol`**: The communication standard a sensor uses, like "CAN Bus".
*   **`ex:DiagnosticTroubleCode` (DTC)**: A standardized code indicating a specific fault, like "P0501".

## Relationships (Properties)

Entities are connected via properties. Here are some of the most important ones:

*   `ex:manufacturedBy`: Links a component to a manufacturer (e.g., `veh:Camry` -> `ex:Toyota`).
*   `ex:installedInModel`: Links a `SensorInstance` to a `VehicleModel`.
*   `ex:isInstanceOf`: Links a `SensorInstance` to its `SensorModel`.
*   `ex:connectsToECU`: Links a `SensorInstance` to an `ECU`.
*   `ex:locatedAt`: Specifies the physical location of a `SensorInstance` (e.g., `ex:EngineBay`).
*   `ex:usesProtocol`: Links a sensor or ECU to a communication `Protocol`.
*   `ex:relatedDTC`: Links a `SensorModel` to a `DTC` that might be triggered if it fails.
*   `ex:hasSensorType`: Categorizes a `SensorModel` (e.g., as a `ex:TemperatureSensor`).
*   `rdfs:label`: Provides a human-readable name for any entity.

## Data Properties and Realistic Values

`SensorModel` entities have data properties with plausible values:

| Property            | Description                               | Example Value      | Unit      |
| :------------------ | :---------------------------------------- | :----------------- | :-------- |
| `ex:sampleRateHz`   | How many times per second it takes a reading | `100`              | `unit:Hz` |
| `ex:powerDrawW`     | Electrical power consumption              | `0.3`              | `unit:W`  |
| `ex:priceUSD`       | Approximate cost of the component         | `35.0`             | `USD`     |
| `ex:accuracyPercent`| Margin of error                           | `0.5`              | `%`       |
| `ex:rangeMin` / `Max` | The operating range of the sensor       | `0` / `250`        | `unit:KPH`|

---

## Worked Example: A Wheel Speed Sensor

Let's trace the connections for the front-left wheel speed sensor on a Toyota RAV4.

1.  **The Vehicle**: `veh:RAV4` is a `ex:VehicleModel` with the `rdfs:label` "Toyota RAV4".

2.  **The Physical Sensor**: `sen:rav4_wss_fl` is a `ex:SensorInstance`.
    *   It has an `rdfs:label` "RAV4 Wheel Speed Sensor (Front Left)".
    *   It is `ex:installedInModel` `veh:RAV4`.
    *   It is `ex:locatedAt` `ex:Wheel`.
    *   It `ex:connectsToECU` `veh:RAV4SafetyECU`.

3.  **The Sensor Model**: The instance `ex:isInstanceOf` `sen:WSS-MR-3`.
    *   `sen:WSS-MR-3` is a `ex:SensorModel` with `rdfs:label` "WSS-MR-3 Magnetoresistive Wheel Speed Sensor".
    *   It `ex:hasSensorType` `ex:SpeedSensor`.
    *   It `ex:usesProtocol` `prot:CAN`.
    *   It has a `ex:sampleRateHz` of `100`.
    *   It has a `ex:relatedDTC` of `dtc:P0501` ("Vehicle Speed Sensor Range/Performance").

This structure allows us to ask questions like:
*   "Find all sensors on the wheels of a Toyota RAV4."
*   "Which sensors use the CAN protocol and are related to safety systems?"
*   "What is the average sample rate for sensors that can trigger the DTC code P0501?"
