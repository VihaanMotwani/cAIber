from neo4j import GraphDatabase
from langchain_community.graphs.graph_document import GraphDocument
import os

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None, db=None):
        with self._driver.session(database=db) as session:
            result = session.run(query, parameters)
            return [record for record in result]

db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        db_connection = Neo4jConnection(uri, user, password)
    return db_connection

def close_db():
    global db_connection
    if db_connection is not None:
        db_connection.close()
        db_connection = None

def add_graph_to_db(graph_document: GraphDocument):
    """
    Writes a GraphDocument object to the Neo4j database.
    This function creates the actual nodes and relationships for the 'Organizational DNA'.
    """
    db = get_db()
    
    # Create nodes
    for node in graph_document.nodes:
        db.query(
            "MERGE (n:`%s` {id: $id}) SET n += $properties" % node.type,
            parameters={'id': node.id, 'properties': node.properties}
        )

    # Create relationships
    for rel in graph_document.relationships:
        # The fix is here: we use rel.source.id and rel.target.id
        db.query(
            """
            MATCH (a {id: $start_id}), (b {id: $end_id})
            MERGE (a)-[r:`%s`]->(b)
            SET r += $properties
            """ % rel.type,
            parameters={
                'start_id': rel.source.id, # CORRECTED from rel.start.id
                'end_id': rel.target.id,   # CORRECTED from rel.end.id
                'properties': rel.properties
            }
        )