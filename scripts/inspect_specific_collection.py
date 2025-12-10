
import sys
import os
import pymongo
import time
import logging
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config_manager import ConfigManager
from src.infrastructure.ssh_manager import SSHManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_collection(env_name, collection_name):
    logger.info(f"Inspecting collection '{collection_name}' in environment '{env_name}'")
    
    config_manager = ConfigManager(env_name)
    
    # Setup SSH Tunnel manually
    ssh_manager = SSHManager(config_manager)
    ssh_manager.connect()
    client = ssh_manager.ssh_client
    
    # Port forward
    local_port = 27017
    mongo_config = config_manager.get_database_config()
    remote_port = mongo_config.get("port", 27017)
    namespace = config_manager.get_kubernetes_config().get("namespace", "panda")
    service_name = mongo_config.get("service_name", "mongodb")
    
    # Check if we need to port-forward (if we are not inside the network)
    # Assuming we are running externally
    
    pf_cmd = f"kubectl port-forward --address 0.0.0.0 -n {namespace} svc/{service_name} {local_port}:{remote_port}"
    logger.info(f"Starting port forward: {pf_cmd}")
    
    stdin, stdout, stderr = client.exec_command(pf_cmd)
    
    # Wait for PF to start
    time.sleep(5)
    
    mongo_client = None
    try:
        # Connect to MongoDB via localhost (tunnel)
        # Note: The tunnel is running on the SSH TARGET host, binding to 0.0.0.0
        # So we need to connect to the SSH TARGET HOST IP, not localhost of the runner
        # UNLESS we are using a local SSH tunnel which forwards local port to remote.
        # SSHManager.connect() establishes a connection. 
        # But kubectl port-forward runs on the remote machine.
        # We need to tunnel FROM our machine TO the remote machine's port 27017.
        
        # Wait, the SSHManager in this project seems to just establish SSH connection.
        # It doesn't automatically set up a local tunnel to the remote port forward.
        # The `MongoDBTunnelManager` in recording_fixtures.py handles this by connecting to `manager.get_connection_host()`
        # which returns `k8s_host` (the jump/target host).
        
        # Let's try connecting to the target host IP
        ssh_config = config_manager.get_ssh_config()
        target_host = ssh_config.get("target_host", {}).get("host") or ssh_config.get("host")
        
        logger.info(f"Connecting to MongoDB at {target_host}:{local_port}")
        
        mongo_client = pymongo.MongoClient(
            host=target_host,
            port=local_port,
            username=mongo_config["username"],
            password=mongo_config["password"],
            authSource=mongo_config.get("auth_source", "prisma"),
            serverSelectionTimeoutMS=5000
        )
        
        db_name = mongo_config.get("database", "prisma")
        db = mongo_client[db_name]
        
        # List collections
        collections = db.list_collection_names()
        if collection_name not in collections:
            logger.error(f"Collection {collection_name} not found in database {db_name}")
            logger.info(f"Available collections: {collections}")
            return
            
        collection = db[collection_name]
        count = collection.count_documents({})
        logger.info(f"Found {count} documents in collection {collection_name}")
        
        if count == 0:
            return

        # Get time range
        min_start = collection.find_one(sort=[("start_time", 1)])["start_time"]
        max_end = collection.find_one(sort=[("end_time", -1)])["end_time"]
        
        logger.info(f"Earliest Start Time: {min_start}")
        logger.info(f"Latest End Time:     {max_end}")
        
        # Print a valid payload snippet
        if isinstance(min_start, datetime):
             min_ts = int(min_start.timestamp())
             max_ts = int(max_end.timestamp())
        else:
             min_ts = int(min_start) / 1000
             max_ts = int(max_end) / 1000
             
        logger.info("\nSUGGESTED PAYLOAD TIMES:")
        logger.info(f"start_time: {min_ts}")
        logger.info(f"end_time:   {max_ts}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if mongo_client:
            mongo_client.close()
        ssh_manager.disconnect()

if __name__ == "__main__":
    inspect_collection("kefar_saba", "24774bcb-a6f6-4e23-aa49-c100ad717bf0")

