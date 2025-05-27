import redis

# Verbindung zu Redis herstellen
r = redis.Redis(host='localhost', port=6379, db=0)

online_players = r.keys("online:*")
print(f"Aktuell online: {len(online_players)} Spieler")