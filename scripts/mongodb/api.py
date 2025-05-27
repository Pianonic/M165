import pymongo
from bson.objectid import ObjectId
from pprint import pprint
import datetime

class GameStatsAPI:
    def __init__(self, uri="mongodb://admin:adminpassword123@localhost:27017/admin"):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client["game_stats"]
        self.players = self.db["players"]
        self.achievements = self.db["achievements"]
    
    def close(self):
        """Verbindung schließen"""
        self.client.close()
    
    def create_player(self, username, email):
        """Neuen Spieler erstellen"""
        player_data = {
            "username": username,
            "email": email,
            "created_at": datetime.datetime.now().isoformat(),
            "stats": {
                "level": 1,
                "xp": 0,
                "playtime_hours": 0,
                "wins": 0,
                "losses": 0
            },
            "achievements": []
        }
        
        result = self.players.insert_one(player_data)
        return result.inserted_id
    
    def update_player_stats(self, username, stats_update):
        """Spielerstatistiken aktualisieren"""
        update_data = {}
        for key, value in stats_update.items():
            update_data[f"stats.{key}"] = value
        
        result = self.players.update_one(
            {"username": username},
            {"$set": update_data}
        )
        
        return result.modified_count
    
    def unlock_achievement(self, username, achievement_id):
        """Achievement für Spieler freischalten"""
        # Prüfen, ob Achievement existiert
        achievement = self.achievements.find_one({"id": achievement_id})
        if not achievement:
            return False
        
        # Prüfen, ob Spieler das Achievement bereits hat
        player = self.players.find_one({
            "username": username,
            "achievements.id": achievement_id
        })
        
        if player:
            return False  # Achievement bereits freigeschaltet
        
        # Achievement hinzufügen
        achievement_data = {
            "id": achievement_id,
            "name": achievement["name"],
            "unlocked_at": datetime.datetime.now().isoformat()
        }
        
        result = self.players.update_one(
            {"username": username},
            {"$push": {"achievements": achievement_data}}
        )
        
        return result.modified_count > 0
    
    def get_player_profile(self, username):
        """Spielerprofil abrufen"""
        return self.players.find_one({"username": username})
    
    def get_leaderboard(self, stat="level", limit=10):
        """Rangliste basierend auf einer Statistik abrufen"""
        return list(self.players.find().sort(f"stats.{stat}", -1).limit(limit))
    
    # Beispiel für eine Aggregation
    def get_achievement_stats(self):
        """Statistiken zu freigeschalteten Achievements"""
        pipeline = [
            {"$unwind": "$achievements"},
            {"$group": {
                "_id": "$achievements.id",
                "name": {"$first": "$achievements.name"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        return list(self.players.aggregate(pipeline))
    
    # Beispiel für eine Projektion
    def get_players_summary(self, limit=10):
        """Übersicht über Spieler mit Projektion"""
        projection = {
            "username": 1,
            "stats.level": 1,
            "stats.wins": 1,
            "stats.losses": 1,
            "achievements": {"$size": "$achievements"},
            "_id": 0
        }
        
        return list(self.players.find({}, projection).limit(limit))

# Verwendung der API
api = GameStatsAPI()

# Neuen Spieler erstellen
player_id = api.create_player("NewPlayer", "new@example.com")
print(f"Neuer Spieler erstellt mit ID: {player_id}")

# Spielerstats aktualisieren
api.update_player_stats("NewPlayer", {"level": 5, "xp": 1200, "wins": 3})
print("Spielerstats aktualisiert")

# Achievement freischalten
api.unlock_achievement("NewPlayer", "first_win")
print("Achievement freigeschaltet")

# Spieler anzeigen
player = api.get_player_profile("NewPlayer")
print("\nSpieler-Profil:")
pprint(player)

# Projektion verwenden
print("\nSpieler-Übersicht (Projektion):")
summaries = api.get_players_summary(3)
for summary in summaries:
    print(f"{summary['username']} - Level {summary['stats']['level']}, {summary['achievements']} Achievements")

# Aggregation verwenden
print("\nAchievement-Statistiken (Aggregation):")
achievement_stats = api.get_achievement_stats()
for stat in achievement_stats:
    print(f"{stat['name']}: {stat['count']} Spieler")

api.close()