import sqlite3
import hashlib


conn = sqlite3.connect('p2p_system.db')
cursor = conn.cursor()

cursor.execute(
    '''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL)'''
)

def hashPassword(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registerUser(username, password):
    cursor.execute(
        '''SELECT * FROM users WHERE username = ?''',
        (username,)
    )
    if cursor.fetchone() is not None:
        raise ValueError('Username already exists')

    hashedPassword = hashPassword(password)
    cursor.execute(
        '''INSERT INTO users (username, password) VALUES (?, ?)''',
        (username, hashedPassword)
    )
    conn.commit()

    print('User registered successfully')


def loginUser(username, password):
    hashedPassword = hashPassword(password)
    cursor.execute(
        '''SELECT * FROM users WHERE username = ? AND password = ?''',
        (username, hashedPassword)
    )
    if cursor.fetchone() is None:
        raise ValueError('Invalid username or password')

    print('User logged in successfully')