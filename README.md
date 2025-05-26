# Gaming Achievement System

This project implements a gaming achievement system using MongoDB and Redis as the backend databases. The system allows for flexible storage of player data, achievements, and real-time statistics, making it suitable for online gaming applications.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Pianonic/M165.git
   cd M165
   ```

2. **Install Dependencies**
   Make sure you have Python and pip installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application with Docker**
   The project includes a `compose.yml` file for easy setup of MongoDB and Redis services. To start the services, run:
   ```bash
   docker compose up -d
   ```

## Usage Examples

### MongoDB Scripts

- **Data Filling**
  To generate and insert test data into the MongoDB database, run:
  ```bash
  python scripts/mongodb/data_fill.py
  ```

- **Manage Permissions**
  To set up user roles and permissions for MongoDB, execute:
  ```bash
  python scripts/mongodb/permissions.py
  ```

- **Backup and Restore**
  To backup or restore the MongoDB database, use:
  ```bash
  python scripts/mongodb/backup_restore.py
  ```

- **Replica Set Setup**
  To configure a MongoDB replica set, run:
  ```bash
  python scripts/mongodb/replica_setup.py
  ```

- **API Interaction**
  Use the API script to interact with the MongoDB database:
  ```bash
  python scripts/mongodb/api.py
  ```

### Redis Scripts

- **Data Filling**
  To generate and insert test data into the Redis database, run:
  ```bash
  python scripts/redis/data_fill.py
  ```

- **Manage Permissions**
  To set up user roles and permissions for Redis, execute:
  ```bash
  python scripts/redis/permissions.py
  ```

- **Backup and Restore**
  To backup or restore the Redis database, use:
  ```bash
  python scripts/redis/backup_restore.py
  ```

- **Replication Setup**
  To configure Redis replication, run:
  ```bash
  python scripts/redis/replication_setup.py
  ```

- **API Interaction**
  Use the API script to interact with the Redis database:
  ```bash
  python scripts/redis/api.py
  ```