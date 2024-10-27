import socket
import threading
import time

peers = {} # Dictionary to store discovered peers and their shared files

def broadcast_discovery(port=12345, discovery_time=10):
    # Broadcasts user presence on the LAN
     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #testing on local host
        sock.bind(("", port))
        print("Listening for peer broadcasts...")
        
        # Discover peers broadcasting within a time window
        start_time = time.time()
        while time.time() - start_time < discovery_time:
            data, addr = sock.recvfrom(1024)
            message = data.decode()

            if addr[0] not in peers:
    
                # Extract username and file list from the message
                try:
                    parts = message.split(" | ")
                    username = parts[0].split(": ")[1]
                    files = parts[1].split(": ")[1].split(", ")

                    print(f"Discovered peer {addr[0]} : {username}\n")
                    
                    # Store peer IP, username, and available files
                    peers[addr[0]] = {'username': username, 'files': files}
                except Exception as e:
                    print(f"Error parsing broadcast from {addr[0]}: {e}")
        
        print(f"Discovery complete. Peers found: {peers}")
    

def search_for_file(filename, peer_list):
    # Function to search for files from discovered peers
    available_peers = []
    for peer_ip, info in peers.items():
        if filename in info['files']:
            available_peers.append([peer_ip, info['username']])
    return available_peers

def display_files():
    # Function to display files shared by discovered peers
    for peer_ip, info in peers.items():
        print(f"Peer: {info['username']} ({peer_ip})\n")
        print("Files: ", ", ".join(info['files']), "\n")

import socket

def request_file(peer_ip, filename, main_port=12345):
    # Connect to peer on the main port to request the file
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((peer_ip, main_port))
            sock.sendall(filename.encode())  # Send filename request
            
            # Wait for response from the sender
            response = sock.recv(1024).decode()
            if response == "READY":
                time.sleep(0.1)  # Wait for the sender to send next message
                new_port = int(sock.recv(1024).decode())  # Receive the new port for file transfer
                print(f"File '{filename}' available on port {new_port}. Initiating download...")
                time.sleep(0.5)# time for sender to setup socket
                receive_file(peer_ip, new_port, filename)
            else:
                print(f"File '{filename}' not available from {peer_ip}")
        except Exception as e:
            print(f"Error connecting to {peer_ip} for file '{filename}': {e}")


def receive_file(peer_ip, port, filename):
    max_retries = 5
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as file_sock:
                print(f"Attempting to connect to {peer_ip}:{port} (Attempt {attempt + 1}/{max_retries})")
                file_sock.connect((peer_ip, port))
                
                local_filename = f"{peer_ip}_{filename}"
                with open(local_filename, 'wb') as f:
                    print(f"Receiving file '{filename}' from {peer_ip}...")
                    while True:
                        data = file_sock.recv(4096)
                        if not data:
                            break
                        f.write(data)
                print(f"File '{filename}' received and saved as '{local_filename}'")
                return True
        except ConnectionRefusedError:
            if attempt < max_retries - 1:
                print(f"Connection failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect after {max_retries} attempts")
                return False
        except Exception as e:
            print(f"Error receiving file '{filename}' from {peer_ip}: {e}")
            return False

    

def main():
    # Start broadcasting user presence
    threading.Thread(target=broadcast_discovery).start()

    def main():
    # Start peer discovery in a separate thread
        discovery_thread = threading.Thread(target=broadcast_discovery)
        discovery_thread.start()
        discovery_thread.join()  # Wait for discovery to complete

    display_files()
    
    # Collect requested files
    file_requests = []
    while True:
        filename = input("Enter the filename you want to request (or 'done' to finish): ")
        if filename.lower() == 'done':
            break
        available_peers = search_for_file(filename, peers)
        if available_peers:
            print(f"File '{filename}' is available from: {available_peers}")
            selected_peer = input("Enter the peer IP to request the file from: ")
            file_requests.append((selected_peer, filename))
        else:
            print(f"File '{filename}' not found on any peers.")

    # Request files sequentially from the selected peers
    for peer_ip, filename in file_requests:
        request_file(peer_ip, filename)

        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
