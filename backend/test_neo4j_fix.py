#!/usr/bin/env python3
"""
Test Neo4j connection with exact environment variables
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment
load_dotenv()

# Get credentials
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME") 
password = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password) if password else 'None'}")

try:
    # Test connection
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful!' AS message")
        record = result.single()
        print(f"✅ SUCCESS: {record['message']}")
        
        # Check if any data exists
        result = session.run("MATCH (n) RETURN count(n) AS node_count")
        count = result.single()['node_count']
        print(f"📊 Current nodes in database: {count}")
        
    driver.close()
    print("🔒 Connection closed")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    print(f"   Error type: {type(e).__name__}")