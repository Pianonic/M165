import redis
import random
import json
import time
from faker import Faker

# Verbindung zu Redis herstellen (mit Admin-Benutzer für volle Rechte)
r = redis.Redis(host='localhost', port=6379, db=0, username='admin', password='admin123')
fake = Faker()

# Redis löschen für Neustart
r.flushdb()

# Leaderboard für Spielerlevel erstellen
leaderboard_key = "leaderboard:level"
for i in range(1, 101):
    player_id = f"player:{i}"
    username = fake.user_name()
    level = random.randint(1, 100)
    
    # Spieler im Leaderboard hinzufügen (Sorted Set)
    r.zadd(leaderboard_key, {player_id: level})
    
    # Spielerinfo in Hash speichern
    r.hset(player_id, "username", username)
    r.hset(player_id, "level", level)
    r.hset(player_id, "xp", level * random.randint(100, 200))
    r.hset(player_id, "wins", random.randint(0, 200))
    r.hset(player_id, "losses", random.randint(0, 200))
    
    # Achievement-Zähler simulieren
    if random.random() > 0.5:
        r.sadd(f"achievements:{player_id}", "first_win")
    
    if random.random() > 0.7:
        r.sadd(f"achievements:{player_id}", "ten_wins")
    
    # Spielzeit-Statistik
    r.hset(f"playtime:{player_id}", "total", random.randint(1, 500))
    
    # Für einige Spieler Online-Status setzen
    if random.random() > 0.7:
        r.set(f"online:{player_id}", 1, ex=3600)  # Ablauf nach 1 Stunde

# Globale Spiel-Statistiken
r.set("stats:total_players", 100)
r.incrby("stats:games_played", random.randint(5000, 10000))
r.incrby("stats:achievements_unlocked", random.randint(300, 500))

# Live-Feed der letzten Events simulieren
for i in range(20):
    event = {
        "player": fake.user_name(),
        "action": random.choice(["win", "achievement", "level_up", "join"]),
        "timestamp": int(time.time()) - random.randint(0, 3600)
    }
    r.lpush("game:events", json.dumps(event))

print("Redis-Datenbank erfolgreich befüllt")