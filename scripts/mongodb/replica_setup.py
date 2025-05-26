import pymongo
import time
import subprocess
import os

# Configuration
REPLICA_SET_NAME = "rs0"
PORTS = [27017, 27018, 27019]
DATA_DIRS = ["./mongo_data/rs0-1", "./mongo_data/rs0-2", "./mongo_data/rs0-3"]

def setup_mongodb_replica_set():
    """Set up MongoDB Replica Set."""
    # Create directories
    for data_dir in DATA_DIRS:
        os.makedirs(data_dir, exist_ok=True)
    
    # Start MongoDB instances
    processes = []
    for i, (port, data_dir) in enumerate(zip(PORTS, DATA_DIRS)):
        cmd = [
            "mongod",
            "--replSet", REPLICA_SET_NAME,
            "--port", str(port),
            "--dbpath", data_dir,
            "--bind_ip", "localhost",
            "--fork",
            "--logpath", f"{data_dir}/mongod.log"
        ]
        
        print(f"Starting MongoDB instance on port {port}...")
        subprocess.run(cmd, check=True)
    
    # Wait for all instances to start
    time.sleep(3)
    
    # Initialize Replica Set
    client = pymongo.MongoClient(f"mongodb://localhost:{PORTS[0]}")
    
    # Replica Set configuration
    config = {
        "_id": REPLICA_SET_NAME,
        "members": [
            {"_id": 0, "host": f"localhost:{PORTS[0]}"},
            {"_id": 1, "host": f"localhost:{PORTS[1]}"},
            {"_id": 2, "host": f"localhost:{PORTS[2]}"}
        ]
    }
    
    # Initialize Replica Set
    print("Initializing Replica Set...")
    result = client.admin.command("replSetInitiate", config)
    print(f"Initialization result: {result}")
    
    # Wait for Replica Set to be ready
    time.sleep(5)
    
    # Check status
    status = client.admin.command("replSetGetStatus")
    print("Replica Set Status:")
    for member in status["members"]:
        print(f"  - {member['name']}: {member['stateStr']}")
    
    client.close()
    
    print("\nMongoDB Replica Set has been successfully set up.")
    print(f"Connection string: mongodb://localhost:{PORTS[0]},localhost:{PORTS[1]},localhost:{PORTS[2]}/?replicaSet={REPLICA_SET_NAME}")

# Execute the setup
setup_mongodb_replica_set()