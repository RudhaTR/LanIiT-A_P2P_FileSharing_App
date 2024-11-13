import sqlite3
import hashlib
from db_utils import registerUser, loginUser, initialize_tables


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
