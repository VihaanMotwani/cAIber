#!/usr/bin/env python3
"""
Debug Neo4j AuraDB connection with different approaches
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("🔍 Debugging Neo4j AuraDB Connection")
print("=" * 50)

# Get credentials
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME") 
password = os.getenv("NEO4J_PASSWORD")

print(f"URI: {uri}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password) if password else 'None'}")
print()

try:
    from neo4j import GraphDatabase
    
    # Test 1: Basic connection
    print("Test 1: Basic GraphDatabase.driver connection")
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        print("✅ Driver created successfully")
        
        # Test verify_connectivity()
        print("Test 2: verify_connectivity()")
        driver.verify_connectivity()
        print("✅ Connectivity verified")
        
        # Test basic query
        print("Test 3: Basic query")
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"✅ Query result: {record['message']}")
        
        driver.close()
        print("✅ All tests passed - Neo4j is working!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Common fixes for AuraDB
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if your AuraDB instance is actually running (not just 'created')")
        print("2. Verify the URI format - should be neo4j+s://xxxxx.databases.neo4j.io")  
        print("3. Check firewall/network restrictions")
        print("4. Try regenerating the password in AuraDB console")
        print("5. Wait 2-3 minutes after resuming the instance")
        
except ImportError:
    print("❌ neo4j package not installed")
    print("Run: pip install neo4j")