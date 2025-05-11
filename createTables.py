import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect("twelveb.db")
        self.conn.execute("PRAGMA foreign_keys = ON")

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table with security question
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                security_question TEXT NOT NULL,
                security_answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Pages table (like Notion pages)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                icon TEXT,
                cover_image TEXT,
                color TEXT DEFAULT '#ffffff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                parent_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(parent_id) REFERENCES pages(id) ON DELETE SET NULL
            )
        ''')

        # Sticky notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sticky_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                content TEXT,
                color TEXT DEFAULT '#ffff00',
                position_x INTEGER DEFAULT 0,
                position_y INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE
            )
        ''')

        # Blocks table (for page content)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                type TEXT NOT NULL,  -- text, heading, list, code, etc.
                content TEXT,
                properties TEXT,  -- JSON string for additional properties
                position INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE
            )
        ''')

        # Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color TEXT,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Page-Tag relationship
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_tags (
                page_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY(page_id, tag_id),
                FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE,
                FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')

        # User settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,
                dark_mode INTEGER DEFAULT 0,
                font_size INTEGER DEFAULT 16,
                theme TEXT DEFAULT 'default',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        self.conn.commit()
        print("Tables created successfully.")

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = DatabaseManager('twelveb.db')
    db.create_tables()
    db.close()
