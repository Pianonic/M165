import pymongo
import random
from faker import Faker
import datetime

# Verbindung zur MongoDB herstellen
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["game_stats"]
players = db["players"]
achievements = db["achievements"]

fake = Faker()

# Achievements definieren
achievement_list = [
    {"id": "first_win", "name": "First Victory", "description": "Win your first match"},
    {"id": "ten_wins", "name": "Winning Streak", "description": "Win 10 matches"},
    {"id": "hundred_games", "name": "Dedicated Player", "description": "Play 100 games"},
    {"id": "max_level", "name": "Master", "description": "Reach max level"}
]

# Achievements in die Datenbank einfügen
achievements.insert_many(achievement_list)

# 100 Spieler generieren
for i in range(100):
    # Zufällige Spielstatistiken
    level = random.randint(1, 100)
    xp = level * random.randint(100, 200)
    playtime = random.randint(1, 500)
    wins = random.randint(0, 200)
    losses = random.randint(0, 200)
    
    # Zufällige Achievements freischalten
    player_achievements = []
    if wins > 0:
        player_achievements.append({
            "id": "first_win",
            "name": "First Victory",
            "unlocked_at": fake.date_time_between(start_date="-1y", end_date="now").isoformat()
        })
    
    if wins >= 10:
        player_achievements.append({
            "id": "ten_wins",
            "name": "Winning Streak",
            "unlocked_at": fake.date_time_between(start_date="-6m", end_date="now").isoformat()
        })
    
    # Spieler erstellen und in die Datenbank einfügen
    player = {
        "player_id": str(i+1),
        "username": fake.user_name(),
        "email": fake.email(),
        "created_at": fake.date_time_between(start_date="-2y", end_date="-1m").isoformat(),
        "last_login": fake.date_time_between(start_date="-1m", end_date="now").isoformat(),
        "stats": {
            "level": level,
            "xp": xp,
            "playtime_hours": playtime,
            "wins": wins,
            "losses": losses
        },
        "achievements": player_achievements
    }
    
    players.insert_one(player)

print(f"Datenbank befüllt: {players.count_documents({})} Spieler und {achievements.count_documents({})} Achievements")