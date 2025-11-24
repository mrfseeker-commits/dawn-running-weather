import sqlite3
import os

def add_alias_column():
    db_path = 'instance/weather.db'
    
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(saved_locations)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'alias' in columns:
            print("Column 'alias' already exists.")
        else:
            print("Adding 'alias' column...")
            cursor.execute("ALTER TABLE saved_locations ADD COLUMN alias TEXT")
            conn.commit()
            print("Successfully added 'alias' column.")
            
    except Exception as e:
        print(f"Error adding column: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_alias_column()
