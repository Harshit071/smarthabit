import os
import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from alembic.config import Config
from alembic import command
from app.database import Base, engine, SessionLocal # Import Base, engine, and SessionLocal

# Wait for the database to be ready
def wait_for_db(db_url: str, max_attempts: int = 10, wait_interval: int = 3):
    print(f"Waiting for database at {db_url}...")
    for i in range(max_attempts):
        try:
            temp_engine = create_engine(db_url)
            with temp_engine.connect():
                print("Database is ready!")
                return True
        except OperationalError:
            print(f"Database not ready, retrying in {wait_interval} seconds... (Attempt {i+1}/{max_attempts})")
            time.sleep(wait_interval)
    print("Database did not become ready within the alotted time.")
    return False


def run_migrations():
    # Use DATABASE_URL from environment variables
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set.")
        sys.exit(1)

    # Ensure database is reachable before proceeding
    if not wait_for_db(database_url):
        sys.exit(1)

    print("Attempting to create tables if they do not exist...")
    try:
        # This will create tables for models that don't exist yet
        Base.metadata.create_all(bind=engine)
        print("Tables created (if they did not exist).")
    except Exception as e:
        print(f"Error creating tables as fallback: {e}")
        # Don't exit, try alembic next

    print("Running Alembic migrations...")
    try:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "alembic")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(alembic_cfg, "head")
        print("Alembic migrations completed successfully.")
    except Exception as e:
        print(f"Error running Alembic migrations: {e}")
        sys.exit(1)

    print("Database setup complete.")


if __name__ == "__main__":
    run_migrations()

