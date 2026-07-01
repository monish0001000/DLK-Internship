import sys
import os
import sqlite3

def run():
    print("Testing Database Connectivity...")
    try:
        # Resolve path to the backend database
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "..", "backend", "sentinelx.db")
        
        if not os.path.exists(db_path):
            raise Exception(f"Database file not found at {db_path}")

        # Try connecting and querying table list
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        if not tables:
            raise Exception("Database connected but no tables found")

        table_names = [t[0] for t in tables]
        required_tables = ["users", "endpoints", "alerts"]
        
        missing = [t for t in required_tables if t not in table_names]
        if missing:
            raise Exception(f"Missing essential tables: {missing}")

        return True, f"Database connectivity passed ({len(table_names)} tables found)"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, msg = run()
    if success:
        print(f"PASS: {msg}")
        sys.exit(0)
    else:
        print(f"FAIL: {msg}")
        sys.exit(1)
