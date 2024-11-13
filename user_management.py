import sqlite3
import hashlib
from db_utils import registerUser, loginUser, initialize_tables

# conn = sqlite3.connect('p2p_system.db')
# cursor = conn.cursor()

# cursor.execute(
#     '''CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT NOT NULL,
#     password TEXT NOT NULL)'''
# )

# def hashPassword(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def registerUser(username, password):
#     cursor.execute(
#         '''SELECT * FROM users WHERE username = ?''',
#         (username,)
#     )
#     if cursor.fetchone() is not None:
#         raise ValueError('Username already exists')

#     hashedPassword = hashPassword(password)
#     cursor.execute(
#         '''INSERT INTO users (username, password) VALUES (?, ?)''',
#         (username, hashedPassword)
#     )
#     conn.commit()

#     print('User registered successfully')


# def loginUser(username, password):
#     hashedPassword = hashPassword(password)
#     cursor.execute(
#         '''SELECT * FROM users WHERE username = ? AND password = ?''',
#         (username, hashedPassword)
#     )
#     if cursor.fetchone() is None:
#         raise ValueError('Invalid username or password')

#     print('User logged in successfully')




def main():
    initialize_tables() 
    while True:
        action = input("Choose an action: (register/login/exit): ").strip().lower()
        
        if action == 'register':
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            try:
                registerUser(username, password)
            except ValueError as e:
                print(e)

        elif action == 'login':
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            try:
                loginUser(username, password)
            except ValueError as e:
                print(e)

        elif action == 'exit':
            print("Exiting...")
            break
        
        else:
            print("Invalid action. Please choose 'register', 'login', or 'exit'.")

if __name__ == '__main__':
    main()
