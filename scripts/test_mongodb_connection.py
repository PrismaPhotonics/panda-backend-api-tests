#!/usr/bin/env python3
"""Test MongoDB connection with different configurations."""

import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
import time

def test_mongodb_connection():
    """Test MongoDB connection with various configurations."""
    print("=" * 80)
    print("Testing MongoDB Connection")
    print("=" * 80)
    
    # Connection configurations to test
    configs = [
        {
            "name": "Direct connection with auth source",
            "uri": "mongodb://prisma:prisma@10.10.100.108:27017/?authSource=prisma"
        },
        {
            "name": "Connection with database specified",
            "uri": "mongodb://prisma:prisma@10.10.100.108:27017/prisma?authSource=prisma"
        },
        {
            "name": "Connection without auth source",
            "uri": "mongodb://prisma:prisma@10.10.100.108:27017/"
        }
    ]
    
    for config in configs:
        print(f"\n[TEST] {config['name']}")
        print(f"URI: {config['uri']}")
        
        try:
            # Create client with timeout
            client = pymongo.MongoClient(
                config['uri'],
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            start_time = time.time()
            client.admin.command('ping')
            ping_time = (time.time() - start_time) * 1000
            
            print(f"[OK] Connection successful! Ping time: {ping_time:.2f}ms")
            
            # Get server info
            server_info = client.server_info()
            print(f"MongoDB version: {server_info.get('version', 'Unknown')}")
            
            # List databases
            db_list = client.list_database_names()
            print(f"Available databases: {db_list}")
            
            # Check if prisma database exists
            if 'prisma' in db_list:
                db = client['prisma']
                collections = db.list_collection_names()
                print(f"Collections in 'prisma' database: {collections[:5]}..." if len(collections) > 5 else collections)
            
            # Close connection
            client.close()
            
        except ConnectionFailure as e:
            print(f"[ERROR] Connection failed: {e}")
        except ServerSelectionTimeoutError as e:
            print(f"[ERROR] Server selection timeout: {e}")
        except OperationFailure as e:
            print(f"[ERROR] Operation failed (auth issue?): {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
    
    print("\n" + "=" * 80)
    print("Testing network connectivity to MongoDB host")
    print("=" * 80)
    
    import socket
    
    host = "10.10.100.108"
    port = 27017
    
    print(f"Testing TCP connection to {host}:{port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"[OK] Port {port} is open on {host}")
        else:
            print(f"[ERROR] Cannot connect to {host}:{port} - Error code: {result}")
    except socket.gaierror as e:
        print(f"[ERROR] Hostname could not be resolved: {e}")
    except socket.error as e:
        print(f"[ERROR] Socket error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    test_mongodb_connection()
