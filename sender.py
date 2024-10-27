import socket
import threading
import os
import sqlite3
import hashlib
import time

# Set up database connection
DBconn = sqlite3.connect('p2p_system.db', check_same_thread=False)
cursor = DBconn.cursor()

# Create the files table
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filesize INTEGER NOT NULL,
        filetype TEXT NOT NULL,
        username TEXT NOT NULL,
        upload_date DATETIME DEFAULT CURRENT_TIMESTAMP)'''
)
DBconn.commit()

# Lock for thread-safe DB operations
db_lock = threading.Lock()

def store_file_metadata(filename, filesize, filetype, username):
    with db_lock:
        cursor.execute(
            '''INSERT INTO files (filename, filesize, filetype, username) 
               VALUES (?, ?, ?, ?)''',
            (filename, filesize, filetype, username)
        )
        DBconn.commit()

def broadcast_file_info(files, username, port=12345, interval=5, stop_event=None):
    # Broadcast information about the files being shared
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
       # sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #testing on local host
        message = f"User: {username} | Available files: " + ", ".join(files)
        while not stop_event.is_set():
            try:
                sock.sendto(message.encode(), ('<broadcast>', port))
                print(f"Broadcasting: {message}")
                time.sleep(interval)  # Sleep to prevent network spamming
            except Exception as e:
                print(f"Broadcast error: {e}")

def stop_broadcast_after_timeout(stop_event, timeout=180):
    time.sleep(timeout)  # Wait for 3minutes  (180 seconds)
    stop_event.set()     # Stop broadcasting


def send_file(filename, recipient_ip, port): #Need to send the nwe port to the recipient so it can connect to it to recieve files and still send the file name reqd
    # Send the file in chunks to avoid memory overload
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((recipient_ip, port))
            with open(filename, 'rb') as f:
                print(f"Sending {filename} to {recipient_ip}...")
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    sock.sendall(chunk)
            print(f"File {filename} sent to {recipient_ip}")
        except Exception as e:
            print(f"Failed to send {filename} to {recipient_ip}: {e}")

def listen_for_requests(port, username):
    # Listen for incoming requests and send files
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', port))
        sock.listen()
        print(f"Listening for file requests on port {port}...")
        while True:
            conn, addr = sock.accept()
            with conn:
                print(f"Connected by {addr}")
                requested_file = conn.recv(1024).decode()  # Receive requested file name
                if os.path.exists(requested_file):
                    newport = port + 1
                    conn.sendall(b"READY")  # Confirm file availability
                    conn.sendall(str(newport).encode())  # Send the new port to the recipient
                    send_file(requested_file, addr[0], newport)  # Use a separate port for file transfer
                    store_file_metadata(requested_file, os.path.getsize(requested_file),
                                        os.path.splitext(requested_file)[1], username)
                else:
                    conn.sendall(b"ERROR: File not found")
                    print(f"File {requested_file} not found.")

def main():
    files = [f for f in os.listdir() if os.path.isfile(f)]  # List all files in the current directory
    username = "user123"  # Replace with actual username from the login process

    # Start broadcasting file info in a separate thread
    stop_event = threading.Event() 
    broadcastThread = threading.Thread(target=broadcast_file_info, args=(files, username,stop_event))
    broadcastThread.start()

    timer_thread = threading.Thread(target=stop_broadcast_after_timeout, args=(stop_event,))
    timer_thread.start()


    # Start listening for file requests
    listen_for_requests(12345, username)
    timer_thread.join()
    broadcastThread.join()
    

if __name__ == '__main__':
    main()
   
