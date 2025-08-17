import random
from pathlib import Path

from rdflib import Graph, Literal, RDF, RDFS, XSD, Namespace, BNode

from rdflib.namespace import OWL # Import OWL namespace

from kg_sensors.rdf_utils import EX, SEN, VEH, DTC, PROT, UNIT, init_graph, save_graph_to_ttl

# Seed for reproducibility
random.seed(42)

def create_ontology(g: Graph):
    """Defines the basic class hierarchy (ontology) for the graph."""
    # Core Classes
    g.add((EX.SensorType, RDFS.subClassOf, EX.Concept))
    g.add((EX.Subsystem, RDFS.subClassOf, EX.Concept))
    g.add((EX.Protocol, RDFS.subClassOf, EX.Concept))

    g.add((EX.Component, RDFS.subClassOf, RDFS.Resource))
    g.add((EX.VehicleModel, RDFS.subClassOf, EX.Component))
    g.add((EX.SensorModel, RDFS.subClassOf, EX.Component))
    g.add((EX.SensorInstance, RDFS.subClassOf, EX.Component))
    g.add((EX.ECU, RDFS.subClassOf, EX.Component))

    # Add labels to classes
    g.add((EX.SensorType, RDFS.label, Literal("Sensor Type")))
    g.add((EX.SensorModel, RDFS.label, Literal("Sensor Model")))
    g.add((EX.SensorInstance, RDFS.label, Literal("Sensor Instance")))
    g.add((EX.Protocol, RDFS.label, Literal("Protocol")))


def generate_bus_ontology() -> Graph:
    """Generates just the ontology/schema for the knowledge graph.""" 
    g = init_graph()
    create_ontology(g)
    return g


def generate_dataset(graph_size: str = "default") -> Graph:
    """
    Generates the synthetic car sensor knowledge graph.
    """
    g = init_graph()
    create_ontology(g)

    # --- Define Concepts & Entities ---
    manufacturers = {
        "Bosch": EX.Bosch, "Continental": EX.Continental, "Denso": EX.Denso
    }
    for name, uri in manufacturers.items():
        g.add((uri, RDFS.label, Literal(name)))

    vehicle_mfrs = {"Toyota": EX.Toyota, "Volkswagen": EX.Volkswagen}
    for name, uri in vehicle_mfrs.items():
        g.add((uri, RDFS.label, Literal(name)))

    locations = {"EngineBay": EX.EngineBay, "Interior": EX.Interior, "Exterior": EX.Exterior, "Wheel": EX.Wheel}
    for name, uri in locations.items():
        g.add((uri, RDFS.label, Literal(name)))

    subsystems = {"Powertrain": EX.Powertrain, "Safety": EX.Safety}
    g.add((EX.Powertrain, RDFS.label, Literal("Powertrain Control")))
    g.add((EX.Safety, RDFS.label, Literal("Safety Systems")))

    protocols = {
        "CAN": (PROT.CAN, "CAN Bus", 1000),
        "LIN": (PROT.LIN, "LIN Bus", 20),
        "FlexRay": (PROT.FlexRay, "FlexRay", 10000),
    }
    for name, (uri, label, bw) in protocols.items():
        g.add((uri, RDF.type, EX.Protocol))
        g.add((uri, RDFS.label, Literal(label)))
        g.add((uri, EX.protocolBandwidthKbps, Literal(bw, datatype=XSD.integer)))
        g.add((uri, RDFS.comment, Literal({
            "CAN": "Controller Area Network, a robust vehicle bus standard designed to allow microcontrollers and devices to communicate with each other's applications without a host computer.",
            "LIN": "Local Interconnect Network, a serial network protocol used for communication between components in vehicles.",
            "FlexRay": "A high-speed, deterministic, and fault-tolerant bus system for automotive use."
        }[name])))

    units = {
        "Hz": UNIT.Hz, "W": UNIT.W, "C": UNIT.Celsius, "kPa": UNIT.kPa,
        "g": UNIT.G, "V": UNIT.V, "%": UNIT.Percent, "km/h": UNIT.KPH
    }
    for label, uri in units.items():
        g.add((uri, RDFS.label, Literal(label if label != "C" else "°C")))

    # --- Sensor Types and Measurements ---
    sensor_types = {
        "TemperatureSensor": (EX.TemperatureSensor, EX.Temperature),
        "PressureSensor": (EX.PressureSensor, EX.Pressure),
        "SpeedSensor": (EX.SpeedSensor, EX.Speed),
        "PositionSensor": (EX.PositionSensor, EX.Position),
        "OxygenSensor": (EX.OxygenSensor, EX.OxygenRatio),
        "KnockSensor": (EX.KnockSensor, EX.Vibration),
        "AirFlowSensor": (EX.AirFlowSensor, EX.AirFlow),
        "AccelerationSensor": (EX.AccelerationSensor, EX.Acceleration),
        "RadarSensor": (EX.RadarSensor, EX.Distance),
        "ImageSensor": (EX.ImageSensor, EX.Image),
        "LightSensor": (EX.LightSensor, EX.Luminance),
    }
    for name, (uri, measurement) in sensor_types.items():
        g.add((uri, RDF.type, EX.SensorType))
        g.add((uri, RDFS.label, Literal(" ".join(name.split("(?=[A-Z])"))))) # Add spaces to name
        g.add((uri, EX.measures, measurement))


    # --- Diagnostic Trouble Codes (DTCs) ---
    dtcs = {
        "P0135": (DTC.P0135, "O2 Sensor Heater Circuit Malfunction", "Indicates a malfunction in the heater circuit of the primary oxygen sensor (Bank 1, Sensor 1)."),
        "P0325": (DTC.P0325, "Knock Sensor 1 Circuit Malfunction", "Indicates that the Engine Control Module (ECM) has detected a problem with the knock sensor circuit."),
        "P0501": (DTC.P0501, "Vehicle Speed Sensor Range/Performance", "Indicates that the vehicle speed sensor is not providing a plausible signal."),
        "P0452": (DTC.P0452, "Evaporative Emission System Pressure Sensor/Switch Low", "Indicates that the fuel tank pressure sensor input is lower than the normal operating range."),
    }
    for code, (uri, label, comment) in dtcs.items():
        g.add((uri, RDFS.label, Literal(label)))
        g.add((uri, RDFS.comment, Literal(comment)))

    # --- Sensor Models ---
    sensor_models = [
        ("WSS-MR-3", "WSS-MR-3 Magnetoresistive Wheel Speed Sensor", "Bosch", "SpeedSensor", "CAN", 100, 0.3, 35.0, 0.5, 0, 250, "P0501"),
        ("CPS-HS-5", "CPS-HS-5 Hall-Effect Crankshaft Sensor", "Continental", "PositionSensor", "CAN", 1000, 0.5, 45.0, 0.1, 0, 8000, None),
        ("BOS-O2-H1", "BOS-O2-H1 Heated O2 Sensor", "Bosch", "OxygenSensor", "CAN", 50, 8.0, 55.0, 2.0, 0.1, 1.1, "P0135"),
        ("KS-PZ-2", "KS-PZ-2 Piezo Knock Sensor", "Denso", "KnockSensor", "CAN", 5000, 0.2, 30.0, 3.0, 0, 50, "P0325"),
        ("TPMS-L4", "TPMS-L4 Tire Pressure Monitor", "Continental", "PressureSensor", "LIN", 0.1, 0.05, 25.0, 1.5, 0, 450, "P0452"),
        ("AMB-T-300", "AMB-T-300 Ambient Temp Sensor", "Denso", "TemperatureSensor", "LIN", 1, 0.1, 15.0, 0.5, -40, 80, None),
        ("ACC-LR-01", "ACC-LR-01 Long-Range Radar", "Bosch", "RadarSensor", "CAN", 20, 5.5, 180.0, 1.0, 0.5, 250, "P0501"),
    ]

    model_uris = {}
    for sm in sensor_models:
        uri = SEN[sm[0]]
        model_uris[sm[0]] = uri
        g.add((uri, RDF.type, EX.SensorModel))
        g.add((uri, RDFS.label, Literal(sm[1])))
        g.add((uri, EX.manufacturedBy, manufacturers[sm[2]]))
        g.add((uri, EX.hasSensorType, sensor_types[sm[3]][0]))
        g.add((uri, EX.usesProtocol, protocols[sm[4]][0]))
        g.add((uri, EX.sampleRateHz, Literal(sm[5], datatype=XSD.decimal)))
        g.add((uri, EX.powerDrawW, Literal(sm[6], datatype=XSD.decimal)))
        g.add((uri, EX.priceUSD, Literal(sm[7], datatype=XSD.decimal)))
        g.add((uri, EX.accuracyPercent, Literal(sm[8], datatype=XSD.decimal)))
        g.add((uri, EX.rangeMin, Literal(sm[9], datatype=XSD.decimal)))
        g.add((uri, EX.rangeMax, Literal(sm[10], datatype=XSD.decimal)))
        if sm[11]:
            g.add((uri, EX.relatedDTC, dtcs[sm[11]][0]))

    # --- Vehicle Models & ECUs ---
    vehicles = {
        "Camry": (VEH.Camry, "Toyota Camry", "Toyota", VEH.CamryECU, "Powertrain"),
        "Golf": (VEH.Golf, "Volkswagen Golf", "Volkswagen", VEH.GolfECU, "Powertrain"),
        "RAV4": (VEH.RAV4, "Toyota RAV4", "Toyota", VEH.RAV4ECU, "Safety"),
    }
    vehicle_uris = {}
    for v_name, (v_uri, v_label, v_mfr, ecu_uri, subsys) in vehicles.items():
        vehicle_uris[v_name] = v_uri
        g.add((v_uri, RDF.type, EX.VehicleModel))
        g.add((v_uri, RDFS.label, Literal(v_label)))
        g.add((v_uri, EX.manufacturedBy, vehicle_mfrs[v_mfr]))
        g.add((ecu_uri, RDF.type, EX.ECU))
        g.add((ecu_uri, RDFS.label, Literal(f"{v_name} Main ECU" if subsys == "Powertrain" else f"{v_name} Safety ECU")))
        g.add((ecu_uri, EX.partOf, subsystems[subsys]))
        # All sensors are compatible with all vehicles in this simple dataset
        for sm_uri in model_uris.values():
            g.add((v_uri, EX.compatibleWithModel, sm_uri))


    # --- Sensor Instances ---
    instances = [
        ("camry_wss_fr", "Camry Wheel Speed Sensor (Front Right)", "WSS-MR-3", "Camry", "Wheel", "RAV4ECU"),
        ("rav4_wss_fl", "RAV4 Wheel Speed Sensor (Front Left)", "WSS-MR-3", "RAV4", "Wheel", "RAV4ECU"),
        ("camry_o2_1", "Camry Oxygen Sensor (Bank 1)", "BOS-O2-H1", "Camry", "EngineBay", "CamryECU"),
        ("golf_o2_1", "Golf Oxygen Sensor (Bank 1)", "BOS-O2-H1", "Golf", "EngineBay", "GolfECU"),
        ("golf_ks_1", "Golf Knock Sensor", "KS-PZ-2", "Golf", "EngineBay", "GolfECU"),
        ("rav4_cps_1", "RAV4 Crankshaft Position Sensor", "CPS-HS-5", "RAV4", "EngineBay", "CamryECU"),
        ("golf_tpms_rl", "Golf TPMS (Rear Left)", "TPMS-L4", "Golf", "Wheel", "GolfECU"),
        ("rav4_temp_cabin", "RAV4 Cabin Temp Sensor", "AMB-T-300", "RAV4", "Interior", "RAV4ECU"),
        ("camry_radar_f", "Camry Front Radar", "ACC-LR-01", "Camry", "Exterior", "RAV4ECU"),
    ]

    for inst in instances:
        uri = SEN[inst[0]]
        g.add((uri, RDF.type, EX.SensorInstance))
        g.add((uri, RDFS.label, Literal(inst[1])))
        g.add((uri, EX.isInstanceOf, model_uris[inst[2]]))
        g.add((uri, EX.installedInModel, vehicle_uris[inst[3]]))
        g.add((uri, EX.locatedAt, locations[inst[4]]))
        g.add((uri, EX.connectsToECU, vehicles[inst[3]][3] if inst[5] != "RAV4ECU" else vehicles["RAV4"][3]))


    if graph_size == "small":
        # Create a very small, targeted graph for smoke tests
        mini_g = init_graph()
        mini_g.add((EX.VehicleModel, RDFS.subClassOf, EX.Component))
        mini_g.add((EX.SensorModel, RDFS.subClassOf, EX.Component))
        mini_g.add((EX.SensorInstance, RDFS.subClassOf, EX.Component))
        mini_g.add((EX.Toyota, RDFS.label, Literal("Toyota")))
        mini_g.add((VEH.Camry, RDF.type, EX.VehicleModel))
        mini_g.add((VEH.Camry, RDFS.label, Literal("Toyota Camry")))
        mini_g.add((VEH.Camry, EX.manufacturedBy, EX.Toyota))
        mini_g.add((EX.OxygenSensor, RDF.type, EX.SensorType))
        mini_g.add((EX.OxygenSensor, RDFS.label, Literal("Oxygen Sensor")))
        mini_g.add((SEN["BOS-O2-H1"], RDF.type, EX.SensorModel))
        mini_g.add((SEN["BOS-O2-H1"], RDFS.label, Literal("BOS-O2-H1 Heated O2 Sensor")))
        mini_g.add((SEN["BOS-O2-H1"], EX.hasSensorType, EX.OxygenSensor))
        mini_g.add((SEN["BOS-O2-H1"], EX.sampleRateHz, Literal(50, datatype=XSD.integer)))
        mini_g.add((SEN.camry_o2_1, RDF.type, EX.SensorInstance))
        mini_g.add((SEN.camry_o2_1, RDFS.label, Literal("Camry Oxygen Sensor (Bank 1)")))
        mini_g.add((SEN.camry_o2_1, EX.isInstanceOf, SEN["BOS-O2-H1"]))
        mini_g.add((SEN.camry_o2_1, EX.installedInModel, VEH.Camry))
        mini_g.add((SEN.camry_o2_1, EX.locatedAt, EX.EngineBay))
        mini_g.add((VEH.CamryECU, RDF.type, EX.ECU))
        mini_g.add((VEH.CamryECU, RDFS.label, Literal("Camry Main ECU")))
        mini_g.add((VEH.CamryECU, EX.partOf, EX.Powertrain))
        mini_g.add((EX.Powertrain, RDFS.label, Literal("Powertrain Control")))
        mini_g.add((EX.EngineBay, RDFS.label, Literal("Engine Bay")))
        mini_g.add((SEN.camry_o2_1, EX.connectsToECU, VEH.CamryECU))
        return mini_g

    return g

def generate_sensors_with_bus_data() -> Graph:
    """Generates the synthetic car sensor knowledge graph with detailed bus information."""
    g = init_graph()
    create_ontology(g)

    # --- Define Concepts & Entities (same as generate_dataset) ---
    manufacturers = {
        "Bosch": EX.Bosch, "Continental": EX.Continental, "Denso": EX.Denso
    }
    for name, uri in manufacturers.items():
        g.add((uri, RDFS.label, Literal(name)))

    vehicle_mfrs = {"Toyota": EX.Toyota, "Volkswagen": EX.Volkswagen}
    for name, uri in vehicle_mfrs.items():
        g.add((uri, RDFS.label, Literal(name)))

    locations = {"EngineBay": EX.EngineBay, "Interior": EX.Interior, "Exterior": EX.Exterior, "Wheel": EX.Wheel}
    for name, uri in locations.items():
        g.add((uri, RDFS.label, Literal(name)))

    subsystems = {"Powertrain": EX.Powertrain, "Safety": EX.Safety, "Comfort": EX.Comfort, "VehicleDynamics": EX.VehicleDynamics, "Exhaust": EX.Exhaust}
    g.add((EX.Powertrain, RDFS.label, Literal("Powertrain Control")))
    g.add((EX.Safety, RDFS.label, Literal("Safety Systems")))
    g.add((EX.Comfort, RDFS.label, Literal("Comfort Systems")))
    g.add((EX.VehicleDynamics, RDFS.label, Literal("Vehicle Dynamics")))
    g.add((EX.Exhaust, RDFS.label, Literal("Exhaust Systems")))

    protocols = {
        "CAN": (PROT.CAN, "CAN Bus", 1000),
        "LIN": (PROT.LIN, "LIN Bus", 20),
        "FlexRay": (PROT.FlexRay, "FlexRay", 10000),
        "Automotive Ethernet": (PROT.Ethernet, "Automotive Ethernet", 100000),
    }
    for name, (uri, label, bw) in protocols.items():
        g.add((uri, RDF.type, EX.Protocol))
        g.add((uri, RDFS.label, Literal(label)))
        g.add((uri, EX.protocolBandwidthKbps, Literal(bw, datatype=XSD.integer)))
        g.add((uri, RDFS.comment, Literal({
            "CAN": "Controller Area Network, a robust vehicle bus standard designed to allow microcontrollers and devices to communicate with each other's applications without a host computer.",
            "LIN": "Local Interconnect Network, a serial network protocol used for communication between components in vehicles.",
            "FlexRay": "A high-speed, deterministic, and fault-tolerant bus system for automotive use.",
            "Automotive Ethernet": "High-bandwidth network for advanced applications."
        }.get(name, ""))))

    # --- Sensor Data with Bus Info ---
    sensors_with_bus_data = [
        # Engine & Powertrain Sensors
        {"name": "Oxygen Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "MAF Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "MAP Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Throttle Position Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Crankshaft Position Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Camshaft Position Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Knock Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Coolant Temp Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Oil Pressure Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Fuel Pressure Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Transmission Speed Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        {"name": "Clutch/Brake Pedal Position Sensor", "category": "Engine & Powertrain", "bus": "CAN", "ecu": "Powertrain"},
        # Environmental & Comfort Sensors
        {"name": "Ambient Temperature Sensor", "category": "Environmental & Comfort", "bus": "LIN", "ecu": "Comfort"},
        {"name": "Cabin Temperature Sensor", "category": "Environmental & Comfort", "bus": "LIN", "ecu": "Comfort"},
        {"name": "Sunlight Sensor", "category": "Environmental & Comfort", "bus": "LIN", "ecu": "Comfort"},
        {"name": "Rain Sensor", "category": "Environmental & Comfort", "bus": "LIN", "ecu": "Comfort"},
        {"name": "Humidity Sensor", "category": "Environmental & Comfort", "bus": "LIN", "ecu": "Comfort"},
        {"name": "Air Quality Sensor", "category": "Environmental & Comfort", "bus": "LIN", "ecu": "Comfort"},
        # Vehicle Dynamics Sensors
        {"name": "Wheel Speed Sensor", "category": "Vehicle Dynamics", "bus": "CAN", "ecu": "VehicleDynamics"},
        {"name": "Steering Angle Sensor", "category": "Vehicle Dynamics", "bus": "CAN", "ecu": "VehicleDynamics"},
        {"name": "Yaw Rate Sensor", "category": "Vehicle Dynamics", "bus": "CAN", "ecu": "VehicleDynamics"},
        {"name": "Lateral Acceleration Sensor", "category": "Vehicle Dynamics", "bus": "CAN", "ecu": "VehicleDynamics"},
        {"name": "Brake Pressure Sensor", "category": "Vehicle Dynamics", "bus": "CAN", "ecu": "VehicleDynamics"},
        {"name": "Suspension Height Sensor", "category": "Vehicle Dynamics", "bus": "CAN", "ecu": "VehicleDynamics"},
        {"name": "TPMS", "category": "Vehicle Dynamics", "bus": "CAN", "ecu": "VehicleDynamics"},
        # Safety & ADAS Sensors
        {"name": "Radar Sensor", "category": "Safety & ADAS", "bus": "CAN", "ecu": "Safety"},
        {"name": "LiDAR Sensor", "category": "Safety & ADAS", "bus": "Automotive Ethernet", "ecu": "Safety"},
        {"name": "Ultrasonic Sensor", "category": "Safety & ADAS", "bus": "LIN", "ecu": "Safety"},
        {"name": "Camera Sensor", "category": "Safety & ADAS", "bus": "Automotive Ethernet", "ecu": "Safety"},
        {"name": "Seat Occupant Sensor", "category": "Safety & ADAS", "bus": "LIN", "ecu": "Safety"},
        {"name": "Airbag Crash Sensor", "category": "Safety & ADAS", "bus": "CAN", "ecu": "Safety"},
        # Exhaust & Emission Sensors
        {"name": "NOx Sensor", "category": "Exhaust & Emission", "bus": "CAN", "ecu": "Exhaust"},
        {"name": "EGT Sensor", "category": "Exhaust & Emission", "bus": "CAN", "ecu": "Exhaust"},
        {"name": "DPF Pressure Sensor", "category": "Exhaust & Emission", "bus": "CAN", "ecu": "Exhaust"},
    ]

    for sensor_data in sensors_with_bus_data:
        sensor_name = sensor_data["name"]
        sensor_uri_name = "".join(sensor_name.title().split())
        sensor_uri = SEN[sensor_uri_name]
        g.add((sensor_uri, RDF.type, EX.SensorModel))
        g.add((sensor_uri, RDFS.label, Literal(sensor_name)))
        g.add((sensor_uri, EX.hasBusType, protocols[sensor_data["bus"]][0]))
        g.add((sensor_uri, EX.partOf, subsystems[sensor_data["ecu"]]))

    return g


def main():
    """Main function to generate and save the datasets."""
    # Generate and save the default dataset
    full_graph = generate_dataset()
    save_path = Path("data/sensors.ttl")
    save_graph_to_ttl(full_graph, save_path)
    print(f"Full dataset saved to {save_path}")

    # Generate and save the mini dataset for smoke tests
    mini_graph = generate_dataset(graph_size="small")
    mini_save_path = Path("data/samples/mini_sensors.ttl")
    save_graph_to_ttl(mini_graph, mini_save_path)
    print(f"Mini sample dataset saved to {mini_save_path}")

    # Generate and save the sensors with bus data
    sensors_with_bus_graph = generate_sensors_with_bus_data()
    sensors_with_bus_save_path = Path("data/sensors_with_bus.ttl")
    save_graph_to_ttl(sensors_with_bus_graph, sensors_with_bus_save_path)
    print(f"Sensors with bus data saved to {sensors_with_bus_save_path}")


if __name__ == "__main__":
    main()