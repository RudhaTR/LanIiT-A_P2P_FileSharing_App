import socket
import threading
import os
import sqlite3
import hashlib
import time
import psutil
from db_utils import store_file_metadata, retrieve_file_metadata,initialize_tables
from utils import get_wifi_ip_and_subnet, calculate_broadcast_address, broadcast_file_info, multicast_file_info, stop_broadcast_after_timeout,listen_for_requests


def get_files_from_user(username):
    files = []
    while True:
        filepath = input("Enter the file path to share (or type 'done' to finish): ")
        if filepath.lower() == 'done':
            break
        elif os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            filetype = os.path.splitext(filename)[1]
            files.append({'path': filepath, 'name': filename, 'size': filesize, 'type': filetype})
            print(f"Added {filename}")
            store_file_metadata(filename, filesize, filetype,filepath,username)
        else:
            print(f"Invalid file path: {filepath}")
    return files

def main():

    initialize_tables()
    username = "user123"  # Replace with actual username from the login process
    broadcast_address = None
        
    file_metadata = retrieve_file_metadata(username)  # Display files available for sharing
    user_files = get_files_from_user(username)  # Get files from user
    file_dict = {file['name']: file['path'] for file in user_files}
    for row in file_metadata:
            file_dict[row[0]] = row[1]
            
    file_names = list(file_dict.keys())  # Extract file names for broadcasting
    
        # Start broadcasting file info in a separate thread
        
    ip, netmask = get_wifi_ip_and_subnet()
    #if ip and netmask:
    broadcast_address = calculate_broadcast_address(ip, netmask)
    stop_event = threading.Event() # Event to signal threads to stop
    broadcastThread = threading.Thread(target=broadcast_file_info, args=(file_names, username,stop_event,broadcast_address))
    #broadcastThread = threading.Thread(target=multicast_file_info, args=(file_names, username,stop_event))
    timer_thread = threading.Thread(target=stop_broadcast_after_timeout, args=(stop_event,))
    listener_thread = threading.Thread(target=listen_for_requests, args=(12346, username, stop_event,file_dict))

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
       # DBconn.close()
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
   
