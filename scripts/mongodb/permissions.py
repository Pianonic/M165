from pymongo import MongoClient
from pymongo.errors import OperationFailure

class MongoDBPermissions:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="game_stats"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def create_user(self, username, password, roles):
        try:
            self.client.admin.command(
                "createUser", username,
                pwd=password,
                roles=roles
            )
            print(f"User '{username}' created with roles: {roles}")
        except OperationFailure as e:
            print(f"Error creating user '{username}': {e}")

    def test_user_permissions(self, username, password):
        user_client = MongoClient(f"mongodb://{username}:{password}@localhost:27017/{self.db.name}")
        try:
            player_count = user_client[self.db.name].players.count_documents({})
            print(f"User '{username}' can read data: {player_count} players found")
            return True
        except OperationFailure:
            print(f"User '{username}' does not have read permissions.")
            return False

    def close(self):
        self.client.close()

# Example usage
if __name__ == "__main__":
    permissions = MongoDBPermissions()
    
    # Create users with different roles
    permissions.create_user("support_user", "support123", [{"role": "read", "db": "game_stats"}])
    permissions.create_user("gamemaster", "master123", [{"role": "readWrite", "db": "game_stats"}])
    permissions.create_user("db_admin", "admin123", [{"role": "dbAdmin", "db": "game_stats"}, {"role": "userAdmin", "db": "game_stats"}])
    
    # Test permissions
    permissions.test_user_permissions("support_user", "support123")
    permissions.test_user_permissions("gamemaster", "master123")
    
    permissions.close()