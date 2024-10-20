import socket
import threading
import time

peers = {} # Dictionary to store discovered peers and their shared files

def broadcast_discovery(port=12345, discovery_time=10):
    # Broadcasts user presence on the LAN
     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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
            available_peers.append(peer_ip)
    return available_peers

def display_files():
    # Function to display files shared by discovered peers
    for peer_ip, info in peers.items():
        print(f"Peer: {info['username']} ({peer_ip})\n")
        print("Files: ", ", ".join(info['files']), "\n")
    

def request_file(peer_ip, filename):
    # Function to send a request for a specific file
    pass

def main():
    # Start broadcasting user presence
    threading.Thread(target=broadcast_discovery).start()

    def main():
    # Start peer discovery in a separate thread
        discovery_thread = threading.Thread(target=broadcast_discovery)
        discovery_thread.start()
        discovery_thread.join()  # Wait for discovery to complete

        
if __name__ == '__main__':
    main()
