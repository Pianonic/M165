from redis import Redis

class RedisPermissions:
    def __init__(self, host='localhost', port=6379, password=None):
        self.redis = Redis(host=host, port=port, password=password)

    def create_user(self, username, password, permissions):
        self.redis.execute_command('ACL SETUSER', username, 'on', f'>{password}', *permissions)

    def delete_user(self, username):
        self.redis.execute_command('ACL DELUSER', username)

    def list_users(self):
        return self.redis.execute_command('ACL LIST')

    def get_user_permissions(self, username):
        return self.redis.execute_command('ACL GETUSER', username)

    def set_user_permissions(self, username, permissions):
        self.redis.execute_command('ACL SETUSER', username, *permissions)

    def close(self):
        self.redis.close()