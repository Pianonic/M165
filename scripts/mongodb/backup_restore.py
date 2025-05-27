import subprocess
import os
from datetime import datetime

# Konfiguration
MONGODB_USER = "admin"
MONGODB_PASSWORD = "adminpassword123"
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/?authSource=admin"
DB_NAME = "game_stats"
BACKUP_DIR = "./mongodb_backups"
MONGODUMP_PATH = r"scripts\mongodb\db_tools\mongodump.exe"
MONGORESTORE_PATH = r"scripts\mongodb\db_tools\mongorestore.exe"

os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_mongodb():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = os.path.join(BACKUP_DIR, f"backup_{ts}")

    result = subprocess.run([
        MONGODUMP_PATH, "--uri", MONGODB_URI, "--db", DB_NAME, "--out", backup_path
    ], capture_output=True, text=True)

    return backup_path if result.returncode == 0 else None

def restore_mongodb(backup_path, target_db):
    db_backup_path = os.path.join(backup_path, DB_NAME)

    result = subprocess.run([
        MONGORESTORE_PATH, "--uri", MONGODB_URI, "--db", target_db, db_backup_path
    ], capture_output=True, text=True)

    return result.returncode == 0

def main():
    backup_path = backup_mongodb()

    if not backup_path:
        print("Backup fehlgeschlagen.")
        return
    
    restored_db = f"{DB_NAME}_restored"

    if not restore_mongodb(backup_path, restored_db):
        print("Restore fehlgeschlagen.")
        return
    
    print(f"Backup erfolgreich als {restored_db} wiederhergestellt.")

if __name__ == "__main__":
    main()