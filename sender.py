import socket
import threading
import os
import sqlite3
import hashlib

DBconn = sqlite3.connect('p2p_system.db')
cursor = DBconn.cursor()

cursor.execute(
    ''' REATE TABLE IF NOT EXISTS files (id INTEGER AUTOINCREMENT,
    filename TEXT NOT NULL PRIMARY KEY,
    filesize INTEGER NOT NULL,
    filetype TEXT NOT NULL,
    username TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP)'''
)

def store_file_metadata(filename, filesize, filetype, username,upload_date):
    cursor.execute(
        '''INSERT INTO files (filename, filesize, filetype, username,upload_date) VALUES (?, ?, ?, ?,?)''',
        (filename, filesize, filetype, username,upload_date)
    )
    DBconn.commit()


def broadcast_file_info(files):
    # Broadcast information about the files being shared
    pass

def send_file(filename, recipient_ip, port):
    # Function to send the file to the requester
    pass

def listen_for_requests(port):
    # Function to listen for incoming requests and send files
    pass

def main():
    files = []  # Logic to choose files to share
    # Start broadcasting
    username = "user123"  # Replace with actual username from logins
    threading.Thread(target=broadcast_file_info, args=(files,)).start()
    
    # Start listening for requests
    listen_for_requests(12345)
