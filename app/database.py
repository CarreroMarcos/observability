import os

def check_db_connection():
    db_path = os.getenv("DB_PATH", "test.db")
    try:
        with open(db_path, 'r'):
            return True
    except FileNotFoundError:
        return False
