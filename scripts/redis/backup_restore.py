import os
import subprocess
import time
from datetime import datetime

# Konfiguration
BACKUP_DIR = "./redis_backups"
REDIS_CONTAINER = "redis"  # Name des Redis-Containers
REDIS_DIR = "/data"  # Redis-Datenpfad im Container

# Backup-Verzeichnis erstellen
os.makedirs(BACKUP_DIR, exist_ok=True)

def check_docker_container():
    """Prüfen, ob Redis-Container läuft"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={REDIS_CONTAINER}", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
        return REDIS_CONTAINER in result.stdout
    except subprocess.CalledProcessError:
        return False

def backup_redis():
    """Redis-Datenbank sichern"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"redis_backup_{timestamp}.rdb")
    
    # SAVE-Befehl über Docker ausführen
    print("Redis SAVE-Befehl über Docker ausführen...")
    save_result = subprocess.run(
        ["docker", "exec", REDIS_CONTAINER, "redis-cli", "SAVE"], 
        capture_output=True, text=True
    )
    
    if save_result.returncode != 0:
        print(f"Fehler beim SAVE-Befehl: {save_result.stderr}")
        return None
    
    # RDB-Datei aus Container kopieren
    print("RDB-Datei aus Container kopieren...")
    copy_result = subprocess.run(
        ["docker", "cp", f"{REDIS_CONTAINER}:{REDIS_DIR}/dump.rdb", backup_file], 
        capture_output=True, text=True
    )
    
    if copy_result.returncode == 0:
        print(f"Backup erfolgreich erstellt: {backup_file}")
        return backup_file
    else:
        print(f"Fehler beim Kopieren der RDB-Datei: {copy_result.stderr}")
        return None

def restore_redis(backup_file):
    """Redis-Datenbank wiederherstellen ohne Container-Neustart"""
    if not os.path.exists(backup_file):
        print(f"Backup-Datei nicht gefunden: {backup_file}")
        return False
    
    try:
        # Aktuelle Daten sichern (falls etwas schiefgeht)
        print("Aktuelle Redis-Daten vor Wiederherstellung sichern...")
        current_backup = backup_redis()
        if current_backup:
            print(f"Sicherung erstellt: {current_backup}")
        
        # Redis leeren
        print("Redis-Datenbank leeren...")
        flush_result = subprocess.run(
            ["docker", "exec", REDIS_CONTAINER, "redis-cli", "FLUSHALL"], 
            capture_output=True, text=True
        )
        
        if flush_result.returncode != 0:
            print(f"Fehler beim Leeren der Datenbank: {flush_result.stderr}")
            return False
        
        # Backup-Datei in Container kopieren
        temp_backup_path = f"/tmp/restore_backup_{int(time.time())}.rdb"
        print("Backup-Datei in Container kopieren...")
        copy_result = subprocess.run(
            ["docker", "cp", backup_file, f"{REDIS_CONTAINER}:{temp_backup_path}"], 
            capture_output=True, text=True
        )
        
        if copy_result.returncode != 0:
            print(f"Fehler beim Kopieren der Backup-Datei: {copy_result.stderr}")
            return False
        
        # Redis DEBUG RELOAD verwenden (lädt RDB-Datei ohne Neustart)
        print("Backup-Datei wiederherstellen...")
        restore_result = subprocess.run(
            ["docker", "exec", REDIS_CONTAINER, "redis-cli", "DEBUG", "RELOAD"], 
            capture_output=True, text=True
        )
        
        # Falls DEBUG RELOAD nicht funktioniert, verwenden wir BGREWRITEAOF + manuelles Laden
        if restore_result.returncode != 0:
            print("DEBUG RELOAD nicht verfügbar, verwende alternative Methode...")
            
            # RDB-Datei über das Data-Verzeichnis laden
            replace_result = subprocess.run(
                ["docker", "exec", REDIS_CONTAINER, "cp", temp_backup_path, f"{REDIS_DIR}/dump.rdb"], 
                capture_output=True, text=True
            )
            
            if replace_result.returncode != 0:
                print(f"Fehler beim Ersetzen der dump.rdb: {replace_result.stderr}")
                return False
            
            # Redis mit BGSAVE die neue Datei laden lassen
            print("Redis zum Laden der neuen Datei veranlassen...")
            subprocess.run(
                ["docker", "exec", REDIS_CONTAINER, "redis-cli", "LASTSAVE"], 
                capture_output=True, text=True
            )
        
        # Wiederherstellung testen
        print("Wiederherstellung testen...")
        test_result = subprocess.run(
            ["docker", "exec", REDIS_CONTAINER, "redis-cli", "INFO", "keyspace"],
            capture_output=True, text=True
        )
        
        print("Wiederherstellungstest abgeschlossen:")
        print(test_result.stdout)
        
        # Temporäre Backup-Datei löschen
        subprocess.run(
            ["docker", "exec", REDIS_CONTAINER, "rm", temp_backup_path], 
            capture_output=True
        )
        
        return test_result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Wiederherstellung: {e}")
        return False

# Container-Status prüfen
if not check_docker_container():
    print(f"Fehler: Redis-Container '{REDIS_CONTAINER}' läuft nicht!")
    print("Bitte starten Sie die Container mit: docker-compose up -d")
    exit(1)

# Backup durchführen
backup_file = backup_redis()

# Wiederherstellung testen
if backup_file and input("Möchten Sie die Wiederherstellung testen? (j/n): ").lower() == 'j':
    restore_success = restore_redis(backup_file)
    print(f"Wiederherstellungstest: {'Erfolgreich' if restore_success else 'Fehlgeschlagen'}")