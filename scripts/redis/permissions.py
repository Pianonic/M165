import redis

def test_user(user):
    print(f"\n=== {user['name'].upper()} Test ({user['desc']}) ===")
    r = redis.Redis(
        host='localhost',
        port=6379,
        username=user['name'],
        password=user['password']
    )
    # Lesetest (immer erwartet erlaubt)
    try:
        count = r.zcard("leaderboard:level")
        print(f"✔ Kann lesen: {count} Spieler im Leaderboard (zcard)")
    except Exception as e:
        print(f"✗ Kann nicht lesen: {e}")
    # Schreibtest
    try:
        r.set(f"test:{user['name']}", "value")
        if user['name'] == 'analytics':
            print("✗ Kann schreiben, sollte aber blockiert sein!")
        else:
            print("✔ Kann schreiben (set)")
        r.delete(f"test:{user['name']}")
    except Exception as e:
        if user['name'] == 'analytics':
            print(f"✔ Kann nicht schreiben (korrekt blockiert): {e}")
        else:
            print(f"✗ Kann nicht schreiben: {e}")
    # Admin-Test
    try:
        r.config_get()
        if user['name'] == 'admin':
            print("✔ Kann Admin-Befehl ausführen (config get)")
        else:
            print("✗ Kann Admin-Befehl ausführen, sollte aber blockiert sein!")
    except Exception as e:
        if user['name'] == 'admin':
            print(f"✗ Kann keinen Admin-Befehl ausführen: {e}")
        else:
            print(f"✔ Kann keinen Admin-Befehl ausführen (korrekt blockiert): {e}")
    r.close()

def test_redis_permissions():
    users = [
        {
            'name': 'analytics',
            'password': 'analytics123',
            'desc': 'Nur Lesezugriff'
        },
        {
            'name': 'gamemaster',
            'password': 'master123',
            'desc': 'Lese- und Schreibrechte'
        },
        {
            'name': 'admin',
            'password': 'admin123',
            'desc': 'Vollzugriff'
        }
    ]
    print("=== REDIS BENUTZER-BERECHTIGUNGEN TEST ===")
    for user in users:
        test_user(user)
    print("\n=== Tests abgeschlossen ===")

if __name__ == "__main__":
    test_redis_permissions()