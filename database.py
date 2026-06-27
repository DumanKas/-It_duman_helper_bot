import sqlite3

DATABASE_NAME = 'my_database.db'

def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT,
        role TEXT DEFAULT 'user')''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        price INTEGER)''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (service_id) REFERENCES services(id))''')

    conn.commit()
    conn.close()


def add_user(user_id: int, username: str):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users(id, username)
        VALUES(?, ?)''', (user_id, username))
    conn.commit()
    conn.close()


def get_role(user_id: int) -> str:
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return 'user'
    return result[0]  # result = ('user',) — берём первый элемент


def set_role(user_id: int, role: str):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET role = ? WHERE id = ?''', (role, user_id))
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()
    conn.close()
    return result


def add_service(name: str, description: str, price: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO services(name, description, price)
        VALUES(?, ?, ?)''', (name, description, price))
    conn.commit()
    conn.close()


def get_services():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services')
    result = cursor.fetchall()
    conn.close()
    return result


def get_service(service_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def delete_service(service_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()


def add_order(user_id: int, service_id: int, date: str):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders(user_id, service_id, date)
        VALUES(?, ?, ?)''', (user_id, service_id, date))
    conn.commit()
    conn.close()


def get_orders(user_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result


def delete_order(service_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor() 
    cursor.execute('DELETE FROM orders WHERE service_id = ?', (service_id,))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders')
    result = cursor.fetchall()
    conn.close()
    return result