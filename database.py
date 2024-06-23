import sqlite3

db_file = 'database.db'

def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            server_url TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_data(chat_id, server_url, username, password):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (chat_id, server_url, username, password) 
        VALUES (?, ?, ?, ?)
    ''', (chat_id, server_url, username, password))
    conn.commit()
    conn.close()

def load_user_data(chat_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT server_url, username, password FROM users WHERE chat_id = ?', (chat_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return {
            'server_url': user_data[0],
            'username': user_data[1],
            'password': user_data[2]
        }
    else:
        return None

init_db()
