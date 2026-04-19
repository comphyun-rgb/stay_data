import sys
import os

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db

if __name__ == "__main__":
    print("Running database initialization...")
    init_db()
    print("Database tables initialized.")
