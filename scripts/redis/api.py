from datetime import datetime
import json
import time
import redis

class GameLeaderboardAPI:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def close(self):
        """Verbindung schließen"""
        self.redis.close()
    
    def add_player_score(self, player_id, username, score):
        """Spieler zur Rangliste hinzufügen"""
        self.redis.zadd("leaderboard:score", {player_id: score})
        self.redis.hset(f"player:{player_id}", mapping={
            "username": username,
            "score": score,
            "last_update": datetime.now().isoformat()
        })
        return True
    
    def get_leaderboard(self, start=0, end=9):
        """Rangliste abrufen"""
        leaderboard_data = self.redis.zrevrange("leaderboard:score", start, end, withscores=True)
        result = []
        for player_id, score in leaderboard_data:
            player_data = self.redis.hgetall(f"player:{player_id}")
            player_data["rank"] = start + 1 + leaderboard_data.index((player_id, score))
            player_data["score"] = score
            result.append(player_data)
        return result
    
    def track_achievement(self, player_id, achievement_id):
        """Achievement freischalten und in Echtzeit verfolgen"""
        self.redis.sadd(f"achievements:{player_id}", achievement_id)
        timestamp = time.time()
        self.redis.hset(f"achievement:{player_id}:{achievement_id}", "unlocked_at", timestamp)
        self.redis.hincrby("stats:achievements", achievement_id, 1)
        event = {
            "player_id": player_id,
            "type": "achievement",
            "achievement_id": achievement_id,
            "timestamp": timestamp
        }
        self.redis.lpush("game:events", json.dumps(event))
        self.redis.ltrim("game:events", 0, 99)
        return True
    
    def get_player_achievements(self, player_id):
        """Errungenschaften eines Spielers abrufen"""
        return self.redis.smembers(f"achievements:{player_id}")
    
    def get_achievement_stats(self):
        """Statistiken zu freigeschalteten Achievements"""
        return self.redis.hgetall("stats:achievements")
    
    def get_player_summary(self, player_id):
        """Zusammenfassung eines Spielers"""
        player_data = self.redis.hgetall(f"player:{player_id}")
        achievement_count = self.redis.scard(f"achievements:{player_id}")
        rank = self.redis.zrevrank("leaderboard:score", player_id)
        summary = {
            "player_id": player_id,
            "username": player_data.get("username", "Unknown"),
            "score": player_data.get("score", 0),
            "rank": rank + 1 if rank is not None else None,
            "achievements": achievement_count
        }
        return summary
    
    def set_player_online(self, player_id, ttl=3600):
        """Spieler als online markieren (mit automatischem Timeout)"""
        self.redis.set(f"online:{player_id}", 1, ex=ttl)
    
    def get_online_players(self):
        """Anzahl und Liste der aktuell online-Spieler"""
        online_keys = self.redis.keys("online:*")
        player_ids = [key.split(":")[1] for key in online_keys]
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