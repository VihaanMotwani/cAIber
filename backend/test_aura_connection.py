#!/usr/bin/env python3
"""
Test AuraDB connection with proper timeouts and retry logic
"""
import os
import time
from dotenv import load_dotenv
load_dotenv()

# Exact credentials from your instance
NEO4J_URI = "neo4j+s://786f0e42.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "JXYh2pTV5lnD6REDi2dm_lyH5Z2H9KHknegZ8_4j1Dc"

print("🚀 Testing AuraDB Professional Instance")
print(f"Instance ID: 786f0e42")
print(f"Region: Singapore (asia-southeast1)")
print(f"URI: {NEO4J_URI}")
print("=" * 60)

def test_connection_with_retries():
    from neo4j import GraphDatabase
    
    # AuraDB-optimized configuration
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        # AuraDB optimizations
        max_connection_lifetime=30 * 60,  # 30 minutes
        max_connection_pool_size=50,
        connection_acquisition_timeout=60,  # 60 seconds for AuraDB
        connection_timeout=30,  # 30 seconds for initial connection
        encrypted=True,
        trust=None  # Use system trust store for AuraDB
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}")
            
            # Test 1: Verify connectivity (recommended for AuraDB)
            print("  Testing connectivity...")
            driver.verify_connectivity()
            print("  ✅ Connectivity verified")
            
            # Test 2: Execute simple query
            print("  Testing query execution...")
            with driver.session() as session:
                result = session.run("RETURN 1 as test, datetime() as timestamp")
                record = result.single()
                print(f"  ✅ Query successful: test={record['test']}, time={record['timestamp']}")
            
            # Test 3: Check database info
            print("  Getting database info...")
            with driver.session() as session:
                result = session.run("CALL dbms.components() YIELD name, versions")
                components = list(result)
                for comp in components:
                    print(f"  📋 {comp['name']}: {comp['versions'][0]}")
            
            print("🎉 AuraDB connection successful!")
            driver.close()
            return True
            
        except Exception as e:
            print(f"  ❌ Attempt {attempt + 1} failed: {e}")
            print(f"     Error type: {type(e).__name__}")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10  # 10, 20, 30 seconds
                print(f"  ⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("❌ All attempts failed!")
                driver.close()
                return False

if __name__ == "__main__":
    try:
        success = test_connection_with_retries()
        if not success:
            print("\n🔧 Troubleshooting suggestions:")
            print("1. Instance might still be initializing - wait 2-3 minutes")
            print("2. Check if you have VPN/proxy interfering")
            print("3. Try from a different network (mobile hotspot)")
            print("4. Singapore region might have high latency from your location")
            print("5. Consider creating an instance in a closer region")
    except ImportError:
        print("❌ neo4j package not found - make sure you're in the virtual environment")
        print("Run: source venv/bin/activate && pip install neo4j")