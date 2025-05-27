import pymongo
from pymongo import MongoClient

# Verbindung als Admin
client = MongoClient("mongodb://admin:adminpassword123@localhost:27017/admin")

def create_mongodb_users():    
    # Benutzer erstellen
    users = [
        ("support_user", "support123", [{"role": "read", "db": "game_stats"}]),
        ("gamemaster", "master123", [{"role": "readWrite", "db": "game_stats"}]),
        ("db_admin", "admin123", [
            {"role": "dbAdmin", "db": "game_stats"},
            {"role": "userAdmin", "db": "game_stats"},
            {"role": "readWrite", "db": "game_stats"}
        ])
    ]
    
    for username, password, roles in users:
        client.admin.command("createUser", username, pwd=password, roles=roles)
        print(f"{username} erstellt")

def test_user(username, password, expected_write=True):
    print(f"\n{username.upper()} Test:")
    user_client = None
    try:
        user_client = MongoClient(f"mongodb://{username}:{password}@localhost:27017/admin")
        
        # Lesetest
        count = user_client.game_stats.players.count_documents({})
        print(f"✓ Kann lesen: {count} Spieler")
        
        # Schreibtest
        try:
            result = user_client.game_stats.players.insert_one({
                "player_id": f"test_{username}",
                "username": f"{username}_test_player", 
                "test": True
            })
            if expected_write:
                print(f"✓ Kann schreiben: ID {result.inserted_id}")
                # Cleanup
                user_client.game_stats.players.delete_one({"test": True})
            else:
                print("✗ FEHLER: Konnte schreiben obwohl nicht erlaubt!")
        except (pymongo.errors.OperationFailure, pymongo.errors.WriteError) as e:
            if expected_write:
                print(f"✗ FEHLER: Kann nicht schreiben (Code: {e.code})")
            else:
                print(f"✓ Kann nicht schreiben (Code: {e.code})")
        
        # Admin-Test nur für db_admin
        if username == "db_admin":
            try:
                user_client.game_stats.players.create_index("username", unique=True)
                print("✓ Kann Indizes erstellen")
            except pymongo.errors.OperationFailure:
                print("✓ Index existiert bereits")
                
    except Exception as e:
        print(f"✗ Test fehlgeschlagen: {e}")
    finally:
        if user_client:
            user_client.close()

def test_mongodb_permissions():
    print("\n=== BERECHTIGUNGSTESTS ===")
    test_user("support_user", "support123", expected_write=False)
    test_user("gamemaster", "master123", expected_write=True)  
    test_user("db_admin", "admin123", expected_write=True)

def check_mongodb_auth():
    try:
        admin_info = client.admin.command("connectionStatus")
        auth_info = admin_info.get("authInfo", {})
        server_info = client.admin.command("buildInfo")
        
        print("MongoDB Authentication Status:")
        print(f"  User: {auth_info.get('authenticatedUsers', [])}")
        print(f"  Version: {server_info.get('version', 'unknown')}")
        return True
    except Exception as e:
        print(f"Fehler bei Auth-Check: {e}")
        return False

if __name__ == "__main__":
    print("=== MongoDB Benutzer-Berechtigungen Test ===")
    print("\n=== MongoDB-Status ===")
    check_mongodb_auth()
    
    print("\n=== Benutzer-Setup ===")
    create_mongodb_users()
    
    test_mongodb_permissions()
    
    print("\n=== Tests abgeschlossen ===")
    client.close()