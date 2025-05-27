import redis

# Verbindung zu Redis herstellen
r = redis.Redis(host='localhost', port=6379, db=0)

leaderboard_key = "leaderboard:level"
top_players = r.zrevrange(leaderboard_key, 0, 9, withscores=True)
print("Top 10 Spieler nach Level:")
for player_id, score in top_players:
    username = r.hget(player_id.decode(), "username").decode()
    print(f"{username} - Level {int(score)}")