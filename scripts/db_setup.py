import psycopg2
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to default "postgres" database to create your project DB
conn = psycopg2.connect(
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)
conn.autocommit = True
cursor = conn.cursor()

# Check if target database exists
cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
exists = cursor.fetchone()

if not exists:
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"✅ Database {DB_NAME} created successfully.")
else:
    print(f"⚠️ Database {DB_NAME} already exists.")

cursor.close()
conn.close()

# Connect to the actual project DB to create table
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS github_repos (
    id SERIAL PRIMARY KEY,
    repo_name TEXT UNIQUE NOT NULL,
    description TEXT,
    stars INTEGER,
    forks INTEGER,
    last_updated TIMESTAMP,
    readme TEXT
);
""")
conn.commit()
print("✅ Table 'github_repos' ensured.")

cursor.close()
conn.close()
print("✅ Database setup completed.")