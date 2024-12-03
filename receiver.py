import socket
import threading
import time
import os
import queue
from utils import broadcast_discovery, multicast_discovery, request_file
        
def search_for_file(filename, peers):
    # Function to search for files from discovered peers
    available_peers = []
    for peer_ip, info in peers.items():
        if filename in info['files']:
            available_peers.append([peer_ip, info['username']])
    return available_peers

def display_files(peers):
    # Function to display files shared by discovered peers
    for peer_ip, info in peers.items():
        print(f"Peer: {info['username']} ({peer_ip})")
        print("Files: ", ", ".join(info['files']))

def getBroadcastedFiles():
    # Function to get the broadcasted files
    q = queue.Queue()
    # Start peer discovery in a separate thread
    broadcast_discovery(q,discovery_time=3)
    peers = q.get()
    return peers
    


def guiReceiver(selected_files,download_folder):
    
    #peers = getBroadcastedFiles()
    #display_files(selected_files)
    file_requests = selected_files
    
    # Collect requested files
    '''
    file_requests = []
    while True:
        filename = input("Enter the filename you want to request (or 'done' to finish): ")
        if filename.lower() == 'done':
            break
        available_peers = search_for_file(filename, peers)
        if available_peers:
            peer_ips = [peer[0] for peer in available_peers]
            print(f"File '{filename}' is available from: {available_peers}")
            selected_peer = input("Enter the peer IP to request the file from: ")
            if(selected_peer in peer_ips):
                file_requests.append((selected_peer, filename))
            else:
                print("Invalid peer IP.")
        else:
            print(f"File '{filename}' not found on any peers.")
            '''

    # Request files concurrently from the selected peers
    download_threads = []
    for peer_ip, filename in file_requests:
        thread = threading.Thread(target=request_file, args=(peer_ip, filename,download_folder),daemon=True)
        download_threads.append(thread)

    # Wait for all downloads to complete
    for thread in download_threads:
        thread.start()
        
    

def main():

    download_folder = r"E:\MYFILES\Study\Sem5\CN\project\testing"  # Default Folder to save downloaded files
    q = queue.Queue()
    # Start peer discovery in a separate thread
    discovery_thread = threading.Thread(target=broadcast_discovery, args=(q,))
    #discovery_thread = threading.Thread(target=multicast_discovery, args=(q,))
    discovery_thread.start()
    discovery_thread.join()  # Wait for discovery to complete

    peers = q.get()

    display_files(peers)
    
    # Collect requested files
    file_requests = []
    while True:
        filename = input("Enter the filename you want to request (or 'done' to finish): ")
        if filename.lower() == 'done':
            break
        available_peers = search_for_file(filename, peers)
        if available_peers:
            peer_ips = [peer[0] for peer in available_peers]
            print(f"File '{filename}' is available from: {available_peers}")
            selected_peer = input("Enter the peer IP to request the file from: ")
            if(selected_peer in peer_ips):
                file_requests.append((selected_peer, filename))
            else:
                print("Invalid peer IP.")
        else:
            print(f"File '{filename}' not found on any peers.")

    # Request files concurrently from the selected peers
    download_threads = []
    for peer_ip, filename in file_requests:
        thread = threading.Thread(target=request_file, args=(peer_ip, filename,download_folder))
        thread.start()
        download_threads.append(thread)

    # Wait for all downloads to complete
    for thread in download_threads:
        thread.join()

        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
