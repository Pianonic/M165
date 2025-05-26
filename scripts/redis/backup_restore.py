import os
import shutil
from datetime import datetime
import time

# Configuration
BACKUP_DIR = "./redis_backups"
REDIS_DIR = "/var/lib/redis"

# Create backup directory if it doesn't exist
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_redis():
    """Backup the Redis database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"redis_backup_{timestamp}.rdb")
    
    # Execute the SAVE command
    print("Executing Redis SAVE command...")
    os.system("redis-cli SAVE")
    
    # Copy the RDB file
    print("Copying RDB file...")
    dump_file = os.path.join(REDIS_DIR, "dump.rdb")
    shutil.copy(dump_file, backup_file)
    
    print(f"Backup successfully created: {backup_file}")

def restore_redis(backup_file):
    """Restore the Redis database from a backup file."""
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    # Temporary directory for restoration
    restore_dir = os.path.join(BACKUP_DIR, "restore_test")
    os.makedirs(restore_dir, exist_ok=True)
    
    # Copy the RDB file to the restore directory
    restore_rdb = os.path.join(restore_dir, "dump.rdb")
    shutil.copy(backup_file, restore_rdb)
    
    # Start Redis server with restored data
    print("Starting Redis server with restored data...")
    os.system(f"redis-server --dir {restore_dir} --dbfilename dump.rdb --daemonize yes")
    
    # Wait for the server to start
    print("Waiting for Redis server to start...")
    time.sleep(2)
    
    # Test if the server is running and data is available
    print("Testing restoration...")
    result = os.system("redis-cli INFO keyspace")
    
    if result == 0:
        print("Restoration successful.")
    else:
        print("Restoration failed.")
    
    # Stop the test server
    print("Stopping test server...")
    os.system("redis-cli SHUTDOWN NOSAVE")
    
    return True

# Example usage
if __name__ == "__main__":
    # Uncomment the following line to perform a backup
    backup_redis()
    
    # Uncomment the following line to restore from a backup
    # restore_redis("path/to/your/backup/file.rdb")