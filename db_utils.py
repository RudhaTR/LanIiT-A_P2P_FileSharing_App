# db_utils.py
import sqlite3
import hashlib
import threading

_db_lock = threading.Lock()
_connection = None

def get_db_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect('p2p_system.db', check_same_thread=False)
    return _connection


def initialize_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    with _db_lock:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )'''
        )
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filesize INTEGER NOT NULL,
                filetype TEXT NOT NULL,
                filepath TEXT NOT NULL,
                username TEXT NOT NULL,
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )'''
        )
        conn.commit()

def hashPassword(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registerUser(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM users WHERE username = ?''',
        (username,)
    )
    if cursor.fetchone() is not None:
        print('Username already exists')
        return False

    hashedPassword = hashPassword(password)
    cursor.execute(
        '''INSERT INTO users (username, password) VALUES (?, ?)''',
        (username, hashedPassword)
    )
    conn.commit()

    print('User registered successfully')
    return True


def loginUser(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashedPassword = hashPassword(password)
    cursor.execute(
        '''SELECT * FROM users WHERE username = ? AND password = ?''',
        (username, hashedPassword)
    )
    if cursor.fetchone() is None:
        print('Invalid username or password')
        return False

    print('User logged in successfully')
    return True

def store_file_metadata(filename, filesize, filetype, filepath, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    with _db_lock:
        cursor.execute("SELECT * FROM files WHERE filename = ?", (filename,))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO files (filename, filesize, filetype, filepath, username) VALUES (?, ?, ?, ?, ?)",
                (filename, filesize, filetype, filepath, username)
            )
        conn.commit()

def retrieve_file_metadata(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    retrieve_file = None
    with _db_lock:
        retrieve_file = cursor.execute("SELECT filename,filepath FROM files WHERE username = ?", (username,))
    
    files = retrieve_file.fetchall()

    if files:
        print(f"Files available for {username}:")
        for row in files:
            print(row[0])  # row[0] contains the filename since we only selected "filename"
    else:
        print(f"No files available for {username}")
    return files