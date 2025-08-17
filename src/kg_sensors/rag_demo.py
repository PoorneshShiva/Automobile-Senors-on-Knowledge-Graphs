from typing import Dict, List

from rdflib import Graph

from kg_sensors.rdf_utils import run_sparql_query

# A simple mapping from intents to SPARQL queries
INTENT_TO_SPARQL = {
    "find_temp_sensors": """
        PREFIX ex: <http://example.com/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?sensor_model ?label WHERE {
          ?temp_type ex:measures ex:Temperature .
          ?sensor_model ex:hasSensorType ?temp_type ;
                        rdfs:label ?label .
        }
    """,
    "what_is_can_bus": """
        PREFIX prot: <http://example.com/protocol/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?comment WHERE {
          prot:CAN rdfs:label ?label ;
                   rdfs:comment ?comment .
        }
    """,
    "sensors_on_wheels": """
        PREFIX ex: <http://example.com/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?instance_label ?model_label ?vehicle_label WHERE {
          ?location rdfs:label "Wheel" .
          ?instance ex:locatedAt ?location ;
                    rdfs:label ?instance_label ;
                    ex:installedInModel ?vehicle ;
                    ex:isInstanceOf ?model .
          ?vehicle rdfs:label ?vehicle_label .
          ?model rdfs:label ?model_label .
        }
    """,
}


def answer_question_with_kg(question: str, g: Graph) -> str:
    """
    A very simple RAG-like demo. It maps a question to a pre-defined
    SPARQL query, executes it, and formats a natural language answer.
    """
    # Simple intent detection
    intent = None
    if "temperature" in question.lower() or "temp" in question.lower():
        intent = "find_temp_sensors"
    elif "can bus" in question.lower():
        intent = "what_is_can_bus"
    elif "wheel" in question.lower() or "wheels" in question.lower():
        intent = "sensors_on_wheels"

    if not intent:
        return "I'm sorry, I can only answer questions about temperature sensors, CAN bus, or sensors on wheels."

    # Get and run the corresponding query
    query = INTENT_TO_SPARQL[intent]
    results = run_sparql_query(g, query)

    # Format the answer
    if not results:
        return "I found no information related to your question in the knowledge graph."

    answer = f"Based on the knowledge graph, here's what I found about '{question}':\n\n"
    
    if intent == "find_temp_sensors":
        answer += "The following sensor models measure temperature:\n"
        for res in results:
            answer += f"- {res.get('label', 'N/A')} ({res.get('sensor_model', '')})\n"
    
    elif intent == "what_is_can_bus":
        res = results[0]
        answer += f"**{res.get('label', 'CAN Bus')}**: {res.get('comment', 'No description available.')}"
    
    elif intent == "sensors_on_wheels":
        answer += "I found these sensors located at the wheels:\n"
        for res in results:
            answer += f"- The '{res.get('instance_label')}' (model: {res.get('model_label')}) is installed on the {res.get('vehicle_label')}.\n"

    answer += "\n\nSource: KG query results."
    return answer
