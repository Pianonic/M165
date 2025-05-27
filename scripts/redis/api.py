import redis
import json
import time
from datetime import datetime

class GameLeaderboardAPI:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def close(self):
        """Verbindung schliessen"""
        self.redis.close()
    
    def add_player_score(self, player_id, username, score):
        """Spieler zur Rangliste hinzufügen"""
        # Spieler zur Rangliste hinzufügen (Sorted Set)
        self.redis.zadd("leaderboard:score", {player_id: score})
        
        # Spielerdetails speichern
        self.redis.hset(f"player:{player_id}", mapping={
            "username": username,
            "score": score,
            "last_update": datetime.now().isoformat()
        })
        
        return True
    
    def get_leaderboard(self, start=0, end=9):
        """Rangliste abrufen"""
        # Spieler-IDs mit Scores vom Sorted Set abrufen
        leaderboard_data = self.redis.zrevrange("leaderboard:score", start, end, withscores=True)
        
        # Vollständige Spielerdaten abrufen
        result = []
        for player_id, score in leaderboard_data:
            player_data = self.redis.hgetall(f"player:{player_id}")
            player_data["rank"] = start + 1 + leaderboard_data.index((player_id, score))
            player_data["score"] = score
            result.append(player_data)
        
        return result
    
    def track_achievement(self, player_id, achievement_id):
        """Achievement freischalten und in Echtzeit verfolgen"""
        # Achievement zur Spieler-Sammlung hinzufügen
        self.redis.sadd(f"achievements:{player_id}", achievement_id)
        
        # Zeitstempel für Freischaltung setzen
        timestamp = time.time()
        self.redis.hset(f"achievement:{player_id}:{achievement_id}", "unlocked_at", timestamp)
        
        # Globalen Achievement-Zähler erhöhen
        self.redis.hincrby("stats:achievements", achievement_id, 1)
        
        # Event zum Feed hinzufügen
        event = {
            "player_id": player_id,
            "type": "achievement",
            "achievement_id": achievement_id,
            "timestamp": timestamp
        }
        self.redis.lpush("game:events", json.dumps(event))
        self.redis.ltrim("game:events", 0, 99)  # Nur die neuesten 100 Events behalten
        
        return True
    
    def get_player_achievements(self, player_id):
        """Errungenschaften eines Spielers abrufen"""
        return self.redis.smembers(f"achievements:{player_id}")
    
    # Beispiel für eine Aggregation
    def get_achievement_stats(self):
        """Statistiken zu freigeschalteten Achievements"""
        # In Redis können wir Achievements mit Hashes zählen
        return self.redis.hgetall("stats:achievements")
    
    # Beispiel für eine Projektion
    def get_player_summary(self, player_id):
        """Zusammenfassung eines Spielers"""
        # Basisdaten abrufen
        player_data = self.redis.hgetall(f"player:{player_id}")
        
        # Anzahl der Achievements (Kardinalität des Sets)
        achievement_count = self.redis.scard(f"achievements:{player_id}")
        
        # Ranglistenposition
        rank = self.redis.zrevrank("leaderboard:score", player_id)
        
        # Ergebnisse kombinieren (Projektion)
        summary = {
            "player_id": player_id,
            "username": player_data.get("username", "Unknown"),
            "score": player_data.get("score", 0),
            "rank": rank + 1 if rank is not None else None,
            "achievements": achievement_count
        }
        
        return summary
    
    # Online-Status und Spielerstatistiken
    def set_player_online(self, player_id, ttl=3600):
        """Spieler als online markieren (mit automatischem Timeout)"""
        self.redis.set(f"online:{player_id}", 1, ex=ttl)
    
    def get_online_players(self):
        """Anzahl und Liste der aktuell online-Spieler"""
        online_keys = self.redis.keys("online:*")
        player_ids = [key.split(":")[1] for key in online_keys]
        
        # Spielerdaten für Online-Spieler abrufen
        online_players = []
        for player_id in player_ids:
            player_data = self.redis.hgetall(f"player:{player_id}")
            if player_data:
                online_players.append({
                    "player_id": player_id,
                    "username": player_data.get("username", "Unknown")
                })
        
        return {
            "count": len(online_players),
            "players": online_players
        }

# Verwendung der API
api = GameLeaderboardAPI()

# Spieler zur Rangliste hinzufügen
api.add_player_score("player1", "GamerX", 1500)
api.add_player_score("player2", "ProGamer", 2200)
api.add_player_score("player3", "Noob123", 800)
print("Spieler zur Rangliste hinzugefügt")

# Rangliste abrufen
leaderboard = api.get_leaderboard()
print("\nRangliste:")
for player in leaderboard:
    print(f"{player['rank']}. {player['username']} - {player['score']} Punkte")

# Achievements tracken
api.track_achievement("player1", "first_win")
api.track_achievement("player2", "first_win")
api.track_achievement("player2", "ten_wins")
print("\nAchievements freigeschaltet")

# Spielerzusammenfassung anzeigen (Projektion)
summary = api.get_player_summary("player2")
print("\nSpieler-Zusammenfassung (Projektion):")
print(f"Spieler: {summary['username']}")
print(f"Punkte: {summary['score']}")
print(f"Rang: {summary['rank']}")
print(f"Achievements: {summary['achievements']}")

# Achievement-Statistiken anzeigen (Aggregation)
achievement_stats = api.get_achievement_stats()
print("\nAchievement-Statistiken (Aggregation):")
for achievement_id, count in achievement_stats.items():
    print(f"{achievement_id}: {count} Spieler")

# Online-Status setzen und abfragen
api.set_player_online("player1")
api.set_player_online("player2")
online = api.get_online_players()
print(f"\nAktuell online: {online['count']} Spieler")
for player in online['players']:
    print(f"- {player['username']}")

api.close()