import sqlite3
from datetime import datetime

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ----------------------
# Ініціалізація бази
# ----------------------
def init_db():
    # Ролі користувачів
    cursor.execute('''CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        name TEXT,
        role TEXT
    )''')

    # Мапінг повідомлень admin -> user
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages_mapping (
        id INTEGER PRIMARY KEY,
        admin_message_id INTEGER,
        user_message_id INTEGER
    )''')

    # Онлайн-режими
    cursor.execute('''CREATE TABLE IF NOT EXISTS online_status (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        mode TEXT,
        last_active TIMESTAMP
    )''')

    # Бан, мут, чорний список
    cursor.execute('''CREATE TABLE IF NOT EXISTS bans_mutes_blacklist (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER,
        type TEXT,
        silent INTEGER,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Статистика пересилань
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats_forwarding (
        id INTEGER PRIMARY KEY,
        from_id INTEGER,
        to_id INTEGER,
        message_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Нотатки
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        note TEXT,
        added_by INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Нагадування
    cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text TEXT,
        remind_time TIMESTAMP,
        created_by INTEGER
    )''')

    conn.commit()

# ----------------------
# Функції для ролей
# ----------------------
def add_role(telegram_id, username, name, role):
    cursor.execute("INSERT OR REPLACE INTO roles (telegram_id, username, name, role) VALUES (?,?,?,?)",
                   (telegram_id, username, name, role))
    conn.commit()

def get_role(telegram_id):
    cursor.execute("SELECT role FROM roles WHERE telegram_id=?", (telegram_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# ----------------------
# Онлайн-режими
# ----------------------
def set_online(telegram_id, mode):
    now = datetime.now()
    cursor.execute("INSERT OR REPLACE INTO online_status (telegram_id, mode, last_active) VALUES (?,?,?)",
                   (telegram_id, mode, now))
    conn.commit()

def remove_online(telegram_id):
    cursor.execute("DELETE FROM online_status WHERE telegram_id=?", (telegram_id,))
    conn.commit()

def get_online():
    cursor.execute("SELECT telegram_id, mode, last_active FROM online_status")
    rows = cursor.fetchall()
    return [{"telegram_id":r[0], "mode":r[1], "last_active":r[2]} for r in rows]

# ----------------------
# Мапінг повідомлень
# ----------------------
def save_forward_mapping(admin_id, user_id):
    cursor.execute("INSERT INTO messages_mapping (admin_message_id, user_message_id) VALUES (?,?)",
                   (admin_id, user_id))
    conn.commit()

def get_user_message_id(admin_message_id):
    cursor.execute("SELECT user_message_id FROM messages_mapping WHERE admin_message_id=?",
                   (admin_message_id,))
    res = cursor.fetchone()
    return res[0] if res else None

# ----------------------
# Користувачі
# ----------------------
def get_user_info(telegram_id):
    cursor.execute("SELECT telegram_id, username, name, role FROM roles WHERE telegram_id=?", (telegram_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return {"telegram_id": row[0], "username": row[1], "name": row[2], "role": row[3], "group_name":"Полюс Поділля", "group_id":-1002646171857, "added_by":"Santa"}

# ----------------------
# Інші базові функції можна додавати для notes, reminders, bans і т.д.
# ----------------------
