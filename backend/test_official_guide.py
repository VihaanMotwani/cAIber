#!/usr/bin/env python3
"""
Test Neo4j connection following the EXACT official guide steps
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# Step 2 from guide: Connect to the database
URI = "neo4j+s://786f0e42.databases.neo4j.io"
AUTH = (os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD"))

print("🔍 Testing Neo4j Connection (Official Guide Pattern)")
print("=" * 60)
print(f"URI: {URI}")
print(f"Username: {AUTH[0]}")
print(f"Password: {'*' * len(AUTH[1]) if AUTH[1] else 'NOT SET'}")
print()

if not AUTH[1]:
    print("❌ NEO4J_PASSWORD not set!")
    exit(1)

try:
    print("Step 1: Creating driver and verifying connectivity...")
    
    # EXACT pattern from guide
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("✅ Connectivity verified!")
        
        print("\nStep 2: Testing basic query with execute_query...")
        
        # Step 4 pattern from guide - using execute_query
        records, summary, keys = driver.execute_query("""
            RETURN 'Hello from cAIber' as message, datetime() as timestamp
            """,
            database_="neo4j",
        )
        
        # Loop through results (guide pattern)
        for record in records:
            print(f"✅ Result: {record.data()}")
            
        # Summary information (guide pattern)
        print("✅ Query `{query}` returned {records_count} records in {time} ms.".format(
            query=summary.query, 
            records_count=len(records),
            time=summary.result_available_after
        ))
        
        print("\nStep 3: Checking database contents...")
        
        # Check total nodes
        records, summary, keys = driver.execute_query("""
            MATCH (n) RETURN count(n) as nodeCount
            """,
            database_="neo4j",
        )
        
        node_count = records[0].data()['nodeCount'] if records else 0
        print(f"✅ Total nodes in database: {node_count}")
        
        if node_count == 0:
            print("⚠️  Database is empty!")
            
            # Let's create some test data following the guide
            print("\nStep 4: Creating test nodes (following guide example)...")
            summary = driver.execute_query("""
                CREATE (a:Person {name: $name})
                CREATE (b:Person {name: $friendName})
                CREATE (a)-[:KNOWS]->(b)
                """,
                name="Alice", friendName="David",
                database_="neo4j",
            ).summary
            
            print("Created {nodes_created} nodes in {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                time=summary.result_available_after
            ))
            
            # Query the test data
            records, summary, keys = driver.execute_query("""
                MATCH (p:Person)-[:KNOWS]->(:Person)
                RETURN p.name AS name
                """,
                database_="neo4j",
            )
            
            print("\nQuerying test data:")
            for record in records:
                print(f"✅ Found person: {record.data()}")
                
        else:
            print("\nStep 4: Checking existing data...")
            
            # Get sample of existing nodes
            records, summary, keys = driver.execute_query("""
                MATCH (n) 
                RETURN labels(n) as labels, properties(n) as props 
                LIMIT 5
                """,
                database_="neo4j",
            )
            
            print("📋 Sample existing nodes:")
            for record in records:
                data = record.data()
                print(f"   • Labels: {data['labels']}")
                print(f"     Props: {data['props']}")
                
            # Check for Entity nodes specifically (what our app uses)
            records, summary, keys = driver.execute_query("""
                MATCH (n:Entity) 
                RETURN count(n) as entityCount
                """,
                database_="neo4j",
            )
            
            entity_count = records[0].data()['entityCount'] if records else 0
            print(f"\n📊 Entity nodes (used by cAIber): {entity_count}")
            
            if entity_count > 0:
                # Get Entity breakdown
                records, summary, keys = driver.execute_query("""
                    MATCH (n:Entity) 
                    RETURN n.type as type, count(*) as count 
                    ORDER BY count DESC
                    """,
                    database_="neo4j",
                )
                
                print("📈 Entity breakdown:")
                for record in records:
                    data = record.data()
                    print(f"   • {data['type']}: {data['count']}")

    print("\n🎉 Neo4j connection test PASSED!")
    print("✅ Your AuraDB instance is working correctly!")
    
    if node_count == 0:
        print("\n💡 Next steps:")
        print("   1. Your database is empty - run Stage 1 (DNA building) to populate it")
        print("   2. Or the PIR generator should work with mock data")
    else:
        print(f"\n💡 Found {node_count} nodes in your database - PIR generator should work!")

except Exception as e:
    print(f"\n❌ Neo4j connection FAILED!")
    print(f"Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    
    # Specific troubleshooting
    if "authentication failure" in str(e).lower() or "unauthorized" in str(e).lower():
        print("\n🔧 AUTHENTICATION ERROR:")
        print("   • Double-check your username and password in Neo4j Aura Console")
        print("   • Make sure .env file has correct NEO4J_USERNAME and NEO4J_PASSWORD")
        
    elif "routing information" in str(e).lower():
        print("\n🔧 ROUTING ERROR:")
        print("   • Your AuraDB instance might be paused or stopped")
        print("   • Go to https://console.neo4j.io/ and check your instance status")
        print("   • Make sure your IP address is whitelisted")
        print("   • Wait a few minutes if you just started the instance")
        
    elif "connection refused" in str(e).lower() or "name resolution" in str(e).lower():
        print("\n🔧 CONNECTION ERROR:")
        print("   • Check your internet connection")
        print("   • Verify the URI is correct: neo4j+s://786f0e42.databases.neo4j.io")
        print("   • Make sure no firewall is blocking the connection")
        
    else:
        print(f"\n🔧 UNKNOWN ERROR:")
        print(f"   • Full error: {repr(e)}")
        
    print(f"\n📋 Will use mock data for now")
    
print("\n" + "=" * 60)