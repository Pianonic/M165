from datetime import datetime
import pymongo


class GameStatsAPI:
    def __init__(self, uri="mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client["game_stats"]
        self.players = self.db["players"]
        self.achievements = self.db["achievements"]
    
    def close(self):
        """Close the connection"""
        self.client.close()
    
    def create_player(self, username, email):
        """Create a new player"""
        player_data = {
            "username": username,
            "email": email,
            "created_at": datetime.now().isoformat(),
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
        """Update player statistics"""
        update_data = {}
        for key, value in stats_update.items():
            update_data[f"stats.{key}"] = value
        
        result = self.players.update_one(
            {"username": username},
            {"$set": update_data}
        )
        
        return result.modified_count
    
    def unlock_achievement(self, username, achievement_id):
        """Unlock achievement for player"""
        achievement = self.achievements.find_one({"id": achievement_id})
        if not achievement:
            return False
        
        player = self.players.find_one({
            "username": username,
            "achievements.id": achievement_id
        })
        
        if player:
            return False
        
        achievement_data = {
            "id": achievement_id,
            "name": achievement["name"],
            "unlocked_at": datetime.now().isoformat()
        }
        
        result = self.players.update_one(
            {"username": username},
            {"$push": {"achievements": achievement_data}}
        )
        
        return result.modified_count > 0
    
    def get_player_profile(self, username):
        """Retrieve player profile"""
        return self.players.find_one({"username": username})
    
    def get_leaderboard(self, stat="level", limit=10):
        """Retrieve leaderboard based on a statistic"""
        return list(self.players.find().sort(f"stats.{stat}", -1).limit(limit))
    
    def get_achievement_stats(self):
        """Statistics for unlocked achievements"""
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
    
    def get_players_summary(self, limit=10):
        """Summary of players with projection"""
        projection = {
            "username": 1,
            "stats.level": 1,
            "stats.wins": 1,
            "stats.losses": 1,
            "achievements": {"$size": "$achievements"},
            "_id": 0
        }
        
        return list(self.players.find({}, projection).limit(limit))