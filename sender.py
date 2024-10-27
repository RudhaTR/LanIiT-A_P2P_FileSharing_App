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

def setup_file_transfer(port):
    # Setup a server socket for file transfer
    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.bind(('', port))
    transfer_socket.listen(1)
    return transfer_socket

def broadcast_file_info(files, username,  stop_event,port=12345, interval=5):
    # Broadcast information about the files being shared
    # Split sleep into smaller intervals to check stop_event more frequently
    check_interval = 0.5  # Check every 0.5 seconds
    total_time = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #testing on local host
        message = f"User: {username} | Available files: " + ", ".join(files)
        while not stop_event.is_set():
            try:
                sock.sendto(message.encode(), ('<broadcast>', port))
               # sock.sendto(message.encode(), ('127.0.0.1', port))
                print(f"Broadcasting: {message}")
               # time.sleep(interval)  # Sleep to prevent network spamming
                total_time = 0
                while total_time < interval and not stop_event.is_set():
                    time.sleep(check_interval)
                    total_time += check_interval
            except Exception as e:
                print(f"Broadcast error: {e}")

def stop_broadcast_after_timeout(stop_event, timeout=180):
    check_interval = 0.5  # Check every 0.5 seconds
    total_time = 0

    while total_time < timeout and not stop_event.is_set():
        time.sleep(check_interval)
        total_time += check_interval
    stop_event.set()     # Stop broadcasting


def send_file(filename, recipient_ip, port): #Need to send the nwe port to the recipient so it can connect to it to recieve files and still send the file name reqd
    # Send the file in chunks to avoid memory overload
    transfer_socket = setup_file_transfer(port)
    try:
        print(f"Waiting for connection on port {port}...")
        conn, addr = transfer_socket.accept()
        with conn:
            with open(filename, 'rb') as f:
                print(f"Sending {filename} to {recipient_ip}...")
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    conn.sendall(chunk)
                print(f"File {filename} sent to {recipient_ip}")
    except Exception as e:
        print(f"Failed to send {filename} to {recipient_ip}: {e}")
    finally:
        transfer_socket.close()

def listen_for_requests(port, username,stop_event):
    # Listen for incoming requests and send files
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', port))
        sock.listen()
        sock.settimeout(5)  # Set a 1-second timeout for accept()
        print(f"Listening for file requests on port {port}...")
        
        
        while not stop_event.is_set():
            try:
                conn, addr = sock.accept()
                with conn:
                    print(f"Connected by {addr}")
                    requested_file = conn.recv(1024).decode()
                    if os.path.exists(requested_file):
                        newport = port + 1
                        
                        # Send READY and new port
                        conn.sendall(b"READY")
                        time.sleep(0.1)  # Small delay to prevent message mixing
                        conn.sendall(str(newport).encode())
                        
                        # Start file transfer in a new thread
                        transfer_thread = threading.Thread(
                            target=send_file,
                            args=(requested_file, addr[0], newport)
                        )
                        transfer_thread.start()
                        
                        store_file_metadata(
                            requested_file, 
                            os.path.getsize(requested_file),
                            os.path.splitext(requested_file)[1], 
                            username
                        )
                    else:
                        conn.sendall(b"ERROR: File not found")
                        print(f"File {requested_file} not found.")
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Error handling request: {e}")

def main():
    files = [f for f in os.listdir() if os.path.isfile(f)]  # List all files in the current directory
    username = "user123"  # Replace with actual username from the login process

    # Start broadcasting file info in a separate thread
    stop_event = threading.Event() 
    broadcastThread = threading.Thread(target=broadcast_file_info, args=(files, username,stop_event))
    timer_thread = threading.Thread(target=stop_broadcast_after_timeout, args=(stop_event,))
    listener_thread = threading.Thread(target=listen_for_requests, args=(12345, username, stop_event))

    try:
        # Start threads
        broadcastThread.start()
        timer_thread.start()
        listener_thread.start()

        while not stop_event.is_set():
            time.sleep(0.5)  # Check every 0.5 seconds

        # Start listening for file requests
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop_event.set()  # Signal threads to stop
    except Exception as e:
        print(f"Error: {e}")
        stop_event.set()
    finally:
        # Wait for threads to finish
        broadcastThread.join()
        timer_thread.join()
        listener_thread.join()
        print("Cleanup complete")
        DBconn.close()
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
   
