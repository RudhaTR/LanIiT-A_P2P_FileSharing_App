import unittest
import sqlite3
import hashlib
from user_management import registerUser, loginUser, hashPassword

# test_user_management.py

class TestUserManagement(unittest.TestCase):

    def setUp(self):
        # Set up a temporary database for testing
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL)'''
        )
        self.conn.commit()

    def tearDown(self):
        # Close the database connection after each test
        self.conn.close()

    def test_register_user_success(self):
        # Test successful user registration
        registerUser('testuser', 'testpassword')
        self.cursor.execute(
            '''SELECT * FROM users WHERE username = ?''',
            ('testuser',)
        )
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], 'testuser')

    def test_register_existing_user(self):
        # Test registering an existing user raises ValueError
        registerUser('testuser', 'testpassword')
        with self.assertRaises(ValueError):
            registerUser('testuser', 'testpassword')

    def test_login_user_success(self):
        # Test successful user login
        registerUser('testuser', 'testpassword')
        loginUser('testuser', 'testpassword')
        self.cursor.execute(
            '''SELECT * FROM users WHERE username = ?''',
            ('testuser',)
        )
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], 'testuser')

    def test_login_user_invalid_password(self):
        # Test login with invalid password raises ValueError
        registerUser('testuser', 'testpassword')
        with self.assertRaises(ValueError):
            loginUser('testuser', 'wrongpassword')

    def test_login_user_nonexistent(self):
        # Test login with non-existent user raises ValueError
        with self.assertRaises(ValueError):
            loginUser('nonexistentuser', 'testpassword')

    def test_hash_password(self):
        # Test password hashing
        password = 'testpassword'
        hashed = hashPassword(password)
        self.assertEqual(hashed, hashlib.sha256(password.encode()).hexdigest())

if __name__ == '__main__':
    unittest.main()
from user_management import registerUser, conn, cursor

# test_user_management.py

class TestUserManagement(unittest.TestCase):

    def setUp(self):
        # Create a fresh database for each test
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL)''')
        conn.commit()

    def tearDown(self):
        # Drop the users table after each test
        cursor.execute('''DROP TABLE users''')
        conn.commit()

    def test_register_user_success(self):
        # Test successful user registration
        registerUser('testuser', 'testpassword')
        cursor.execute('''SELECT * FROM users WHERE username = ?''', ('testuser',))
        user = cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], 'testuser')

    def test_register_user_already_exists(self):
        # Test registering a user that already exists
        registerUser('testuser', 'testpassword')
        with self.assertRaises(ValueError):
            registerUser('testuser', 'testpassword')

if __name__ == '__main__':
    unittest.main()