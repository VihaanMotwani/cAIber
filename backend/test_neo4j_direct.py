#!/usr/bin/env python3
"""
Direct Neo4j Connection Test - Following Official Guide
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Use your exact connection details
URI = "neo4j+s://786f0e42.databases.neo4j.io"
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")  
PASSWORD = os.getenv("NEO4J_PASSWORD")

print("🔍 Testing Neo4j Connection (Direct Driver)")
print("=" * 50)
print(f"URI: {URI}")
print(f"Username: {USERNAME}")
print(f"Password: {'*' * len(PASSWORD) if PASSWORD else 'NOT SET'}")
print()

if not PASSWORD:
    print("❌ NEO4J_PASSWORD not set in .env file!")
    exit(1)

try:
    print("1. Creating driver and testing connectivity...")
    
    # Step 2 from guide: Connect to database
    with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
        print("✅ Driver created")
        
        # Verify connectivity (as recommended in guide)
        driver.verify_connectivity()
        print("✅ Connectivity verified!")
        
        print("2. Testing basic query...")
        # Step 4 from guide: Query the graph
        records, summary, keys = driver.execute_query(
            "RETURN 'Hello Neo4j' as message, datetime() as timestamp",
            database_="neo4j"
        )
        
        for record in records:
            print(f"✅ Query result: {record.data()}")
            
        print(f"✅ Query executed in {summary.result_available_after} ms")
        
        print("3. Checking database contents...")
        # Check for nodes
        records, summary, keys = driver.execute_query(
            "MATCH (n) RETURN count(n) as nodeCount",
            database_="neo4j"
        )
        
        node_count = records[0].data()['nodeCount'] if records else 0
        print(f"✅ Total nodes in database: {node_count}")
        
        if node_count == 0:
            print("⚠️  Database is empty!")
            print("💡 You may need to run Stage 1 (DNA building) to populate it.")
        else:
            # Get sample nodes
            records, summary, keys = driver.execute_query(
                "MATCH (n) RETURN labels(n) as labels, properties(n) as props LIMIT 5",
                database_="neo4j"
            )
            
            print("📋 Sample nodes:")
            for record in records:
                data = record.data()
                print(f"   • Labels: {data['labels']}, Props: {data['props']}")
        
        print("4. Checking for Entity nodes specifically...")
        records, summary, keys = driver.execute_query(
            "MATCH (n:Entity) RETURN count(n) as entityCount",
            database_="neo4j"
        )
        
        entity_count = records[0].data()['entityCount'] if records else 0
        print(f"✅ Entity nodes: {entity_count}")
        
        if entity_count > 0:
            # Get entity breakdown
            records, summary, keys = driver.execute_query(
                "MATCH (n:Entity) RETURN n.type as type, count(*) as count ORDER BY count DESC",
                database_="neo4j"
            )
            
            print("📈 Entity breakdown:")
            for record in records:
                data = record.data()
                print(f"   • {data['type']}: {data['count']}")

    print("\n🎉 Neo4j connection test PASSED!")
    print("✅ Your credentials and connection are working correctly!")

except Exception as e:
    print(f"\n❌ Neo4j connection test FAILED!")
    print(f"Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    
    # Specific error handling
    if "authentication failure" in str(e).lower():
        print("\n🔧 Authentication Error - Check your username/password!")
    elif "routing information" in str(e).lower():
        print("\n🔧 Routing Error - Your AuraDB instance might be paused or unreachable!")
        print("   • Check Neo4j Aura Console: https://console.neo4j.io/")
        print("   • Ensure your instance is running")
        print("   • Verify your IP is whitelisted")
    elif "connection refused" in str(e).lower():
        print("\n🔧 Connection Refused - Check your URI and network!")
    
    exit(1)