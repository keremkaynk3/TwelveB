import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect("registered.db")

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                note TEXT,
                checked INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                note2 TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                dark_mode INTEGER
            )
        ''')
        self.conn.commit()  # Veritabanında değişiklikleri kaydet
        print("Tables added successfully.")

    def close(self):
        # Veritabanı bağlantısını kapat
        self.conn.close()


# Sınıfı kullanarak bir veritabanı oluşturma ve tablo ekleme işlemi
db = DatabaseManager('registered.db')
db.create_tables()
db.close()
