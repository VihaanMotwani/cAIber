#!/usr/bin/env python3
"""
Neo4j Connection Test Script
Tests connection to AuraDB instance with detailed diagnostics
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

def test_neo4j_connection():
    """Test Neo4j AuraDB connection with detailed diagnostics."""
    
    print("🔍 Testing Neo4j AuraDB Connection...")
    print("=" * 50)
    
    # Get connection details from .env
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME") 
    password = os.getenv("NEO4J_PASSWORD")
    
    print(f"URI: {uri}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
    print()
    
    if not uri or not username or not password:
        print("❌ Missing Neo4j credentials in .env file!")
        return False
    
    try:
        print("1. Testing basic connection...")
        
        # Create driver
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        print("✅ Driver created successfully")
        
        # Test connection
        print("2. Testing session and query...")
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' as message, datetime() as timestamp")
            record = result.single()
            
            if record:
                print(f"✅ Query successful: {record['message']}")
                print(f"✅ Timestamp: {record['timestamp']}")
            
        print("3. Testing database info...")
        with driver.session() as session:
            # Get database info
            result = session.run("CALL db.info()")
            info = result.single()
            if info:
                print(f"✅ Database name: {info.get('name', 'N/A')}")
                print(f"✅ Database size: {info.get('storeSize', 'N/A')}")
        
        print("4. Testing node count...")
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as nodeCount")
            count = result.single()['nodeCount']
            print(f"✅ Total nodes in database: {count}")
            
            if count == 0:
                print("⚠️  Database is empty! You may need to run Stage 1 (DNA building) first.")
            
        print("5. Testing specific entity nodes...")
        with driver.session() as session:
            result = session.run("MATCH (n:Entity) RETURN count(n) as entityCount")
            count = result.single()['entityCount']
            print(f"✅ Entity nodes: {count}")
            
            if count > 0:
                # Get sample entities
                result = session.run("MATCH (n:Entity) RETURN n.name, n.type LIMIT 5")
                print("📋 Sample entities:")
                for record in result:
                    print(f"   • {record['n.name']} ({record['n.type']})")
        
        driver.close()
        print("\n🎉 Neo4j connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Neo4j connection test FAILED!")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Common troubleshooting suggestions
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if your AuraDB instance is running")
        print("2. Verify your credentials are correct")
        print("3. Check your network connection")
        print("4. Ensure you're using the correct URI format: neo4j+s://")
        print("5. Check if your IP is whitelisted in AuraDB console")
        
        return False

if __name__ == "__main__":
    test_neo4j_connection()