import subprocess
import os
import time

# Configuration
REDIS_BASE_PORT = 6379
REDIS_INSTANCES = 3  # 1 Master, 2 Slaves
DATA_DIR = "./redis_cluster"

def setup_redis_replication():
    """Redis replication setup with Sentinel."""
    # Create directories for Redis instances
    for i in range(REDIS_INSTANCES):
        instance_dir = f"{DATA_DIR}/redis_{i}"
        os.makedirs(instance_dir, exist_ok=True)
        
        # Port for this instance
        port = REDIS_BASE_PORT + i
        
        # Redis configuration
        redis_conf = f"""
            port {port}
            dir {instance_dir}
            dbfilename dump.rdb
            logfile {instance_dir}/redis.log
            daemonize yes
        """
        
        # For Slaves (i > 0) add master configuration
        if i > 0:
            redis_conf += f"replicaof localhost {REDIS_BASE_PORT}\n"
        
        # Save configuration
        with open(f"{instance_dir}/redis.conf", "w") as f:
            f.write(redis_conf)
        
        # Start Redis server
        print(f"Starting Redis instance on port {port}...")
        subprocess.run(["redis-server", f"{instance_dir}/redis.conf"], check=True)
    
    # Wait for all Redis instances to start
    time.sleep(3)
    
    # Check replication status
    print("\nChecking replication status...")
    subprocess.run(["redis-cli", "-p", str(REDIS_BASE_PORT), "INFO", "replication"])
    
    print("\nRedis replication setup completed.")
    print(f"Master: localhost:{REDIS_BASE_PORT}")
    print(f"Slaves: localhost:{REDIS_BASE_PORT + 1}, localhost:{REDIS_BASE_PORT + 2}")

# Execute the setup
setup_redis_replication()