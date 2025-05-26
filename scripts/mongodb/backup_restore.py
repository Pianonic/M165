import subprocess
import os
from datetime import datetime

# Configuration
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "game_stats"
BACKUP_DIR = "./mongodb_backups"

# Create backup directory
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_mongodb():
    """Backup MongoDB database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    
    # Run mongodump
    result = subprocess.run([
        "mongodump",
        "--uri", MONGODB_URI,
        "--db", DB_NAME,
        "--out", backup_path
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Backup successfully created at: {backup_path}")
        return backup_path
    else:
        print(f"Error during backup: {result.stderr}")
        return None

def restore_mongodb(backup_path, to_db_name="game_stats_restored"):
    """Restore MongoDB database"""
    db_backup_path = os.path.join(backup_path, DB_NAME)
    
    # Run mongorestore
    result = subprocess.run([
        "mongorestore",
        "--uri", MONGODB_URI,
        "--nsFrom", f"{DB_NAME}.*",
        "--nsTo", f"{to_db_name}.*",
        db_backup_path
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Restoration successful to database: {to_db_name}")
        return True
    else:
        print(f"Error during restoration: {result.stderr}")
        return False

# Backup and restoration example
if __name__ == "__main__":
    backup_path = backup_mongodb()
    
    # If backup is successful, test restoration
    if backup_path:
        restore_success = restore_mongodb(backup_path)
        print(f"Restoration test: {'Successful' if restore_success else 'Failed'}")