import json
import redis

# Verbindung zu Redis herstellen
r = redis.Redis(host='localhost', port=6379, db=0)

latest_events = r.lrange("game:events", 0, 5)
print("Neueste Ereignisse:")
for event in latest_events:
    event_data = json.loads(event)
    print(f"{event_data['player']} - {event_data['action']}")