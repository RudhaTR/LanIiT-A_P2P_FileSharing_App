import socket
import threading
import os
import sqlite3
import hashlib
import time
import psutil
import queue
from db_utils import store_file_metadata, retrieve_file_metadata,initialize_tables
import gzip
import shutil
import globalLogger
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import padding

#-------------------------------------------------------------------SENDER FUNCTIONS------------------------------------------------------------------------------------------------------------------------------
def get_wifi_ip_and_subnet():
    # Get all network interfaces and their addresses
    interfaces = psutil.net_if_addrs()
    
    # Look for the 'Wi-Fi' interface (can also be 'WLAN' on some systems)
    for interface_name, interface_addresses in interfaces.items():
        if 'Wi-Fi' in interface_name:  # or 'Ethernet', adjust as per your interface name
            for address in interface_addresses:
                if address.family == socket.AF_INET:
                    ip_address = address.address
                    netmask = address.netmask
                    return ip_address, netmask
    return None, None

def calculate_broadcast_address(ip, netmask):
# Convert the IP address and subnet mask to binary form (each as a 32-bit integer)
    ip_parts = list(map(int, ip.split('.')))
    netmask_parts = list(map(int, netmask.split('.')))
    
    # Convert IP and subnet mask to binary 32-bit integers
    ip_bin = sum([ip_parts[i] << (8 * (3 - i)) for i in range(4)])
    netmask_bin = sum([netmask_parts[i] << (8 * (3 - i)) for i in range(4)])
    
    # Calculate broadcast address by ORing the IP with the inverse of the subnet mask
    inverse_mask_bin = ~netmask_bin & 0xFFFFFFFF
    broadcast_bin = ip_bin | inverse_mask_bin
    
    # Convert back to dotted decimal format
    broadcast_ip = '.'.join([str((broadcast_bin >> (8 * i)) & 0xFF) for i in reversed(range(4))])
    
    return broadcast_ip

def setup_file_transfer(port):
    # Setup a server socket for file transfer
    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.bind(('', port))
    transfer_socket.listen(1)
    return transfer_socket,transfer_socket.getsockname()[1]

def broadcast_file_info(files, username, stop_event,broadcast_ip, port=12345, interval=5):
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
                sock.sendto(message.encode(), (broadcast_ip, port))
               # sock.sendto(message.encode(), ('127.0.0.1', port))
                print(f"Broadcasting, IP {broadcast_ip}: {message}")
               # time.sleep(interval)  # Sleep to prevent network spamming
                total_time = 0
                while total_time < interval and not stop_event.is_set():
                    time.sleep(check_interval)
                    total_time += check_interval
            except Exception as e:
                print(f"Broadcast error: {e}")

def multicast_file_info(files, username, stop_event, port=12345, interval=5,multicast_group='224.0.0.1'):
    # Broadcast information about the files being shared
    # Split sleep into smaller intervals to check stop_event more frequently
    check_interval = 0.5  # Check every 0.5 seconds
    total_time = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        message = f"User: {username} | Available files: " + ", ".join(files)

        while not stop_event.is_set():
            try:
                sock.sendto(message.encode(), (multicast_group, port))
      
                print(f"Broadcasting(multicast): {message}")
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


def send_file(filepath, recipient_ip, transfer_socket): #Need to send the nwe port to the recipient so it can connect to it to recieve files and still send the file name reqd
    # Send the file in chunks to avoid memory overload
    port = transfer_socket.getsockname()[1]
    filename = os.path.basename(filepath)
   
    try:
        print(f"Waiting for connection on port {port}...")
        conn, addr = transfer_socket.accept()
        compressedFilePath = compressFile(filepath)
        giveGuiInfoToSender(filename,recipient_ip)
        with conn:
    
            with open(compressedFilePath, 'rb') as f:
                print(f"Sending {filename} to {recipient_ip}...")

                startTime = time.time()
                
                while True:
                    chunk = f.read(65535)
                    if not chunk:
                        break
                    conn.sendall(chunk)

        endTime = time.time()

        cleanup_file(compressedFilePath)
        
        print(f"File {filename} sent to {recipient_ip}")
        if(endTime - startTime != 0):
                speed = os.path.getsize(filepath) / (endTime - startTime) / (1024 * 1024)
                print(f"File transfer rate is {speed:.2f} MB/s")
                giveGuiInfoToSender(filename,recipient_ip,speed,end=1)
        else:
            giveGuiInfoToSender(filename,recipient_ip,end=1)
        
                
    except Exception as e:
        print(f"Failed to send {filename} to {recipient_ip}: {e}")
    finally:
        transfer_socket.close()

def listen_for_requests(port, username,stop_event,file_dict):
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

                    if requested_file in file_dict:
                        filepath = file_dict[requested_file]
                        transfer_socket, newport = setup_file_transfer(0)  # Get a new port
                        
                        # Send READY and new port
                        conn.sendall(b"READY")
                        time.sleep(0.1)  # Small delay to prevent message mixing
                        conn.sendall(str(newport).encode())
                        
                        # Start file transfer in a new thread
                        transfer_thread = threading.Thread(
                            target=send_file,
                            args=(filepath, addr[0], transfer_socket)
                        )
                        transfer_thread.start()
            
                    else:
                        conn.sendall(b"ERROR: File not found")
                        print(f"File {requested_file} not found.")
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Error handling request: {e}")

#------------------------------------------------------------------------RECEIVER FUNCTIONS------------------------------------------------------------------------------------------------------------------------------
def broadcast_discovery(q,port=12345, discovery_time=10):
    # Broadcasts user presence on the LAN
     peerList = {}
     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #testing on local host
        sock.bind(("", port))
        sock.settimeout(discovery_time)  # Set a 10-second timeout for recvfrom()
        print("Listening for peer broadcasts...")
        
        # Discover peers broadcasting within a time window
        try:
            start_time = time.time()
            while time.time() - start_time < discovery_time:
                data, addr = sock.recvfrom(1024)
                message = data.decode()

                if addr[0] not in peerList:
        
                    # Extract username and file list from the message
                    try:
                        parts = message.split(" | ")
                        username = parts[0].split(": ")[1]
                        files = parts[1].split(": ")[1].split(", ")

                        print(f"Discovered peer {addr[0]} : {username}")
                        
                        # Store peer IP, username, and available files
                        peerList[addr[0]] = {'username': username, 'files': files}
                    except Exception as e:
                        print(f"Error parsing broadcast from {addr[0]}: {e}")
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error trying to receive broadcast data : {e}")
        
        print(f"Discovery complete. Peers found: {peerList}")
        q.put(peerList)

def multicast_discovery(q,port=12345, discovery_time=10,multicast_group='224.0.0.1'):
    # Multicasts user presence on the LAN
    peerList = {}

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
           # sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #testing on local host
            sock.bind(("", port))

            multicast_request = socket.inet_aton(multicast_group) + socket.inet_aton('0.0.0.0')
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)

            sock.settimeout(10)  # Set a 10-second timeout for recvfrom()
            print("Listening for peer broadcasts(multicast)...")
            
            # Discover peers broadcasting within a time window
            try:
                start_time = time.time()
                while time.time() - start_time < discovery_time:
                    data, addr = sock.recvfrom(1024)
                    message = data.decode()

                    if addr[0] not in peerList:
            
                        # Extract username and file list from the message
                        try:
                            parts = message.split(" | ")
                            username = parts[0].split(": ")[1]
                            files = parts[1].split(": ")[1].split(", ")

                            print(f"Discovered peer {addr[0]} : {username}")
                            
                            # Store peer IP, username, and available files
                            peerList[addr[0]] = {'username': username, 'files': files}
                        except Exception as e:
                            print(f"Error parsing broadcast from {addr[0]}: {e}")
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Error trying to receive broadcast data : {e}")

            print(f"Discovery complete. Peers found: {peerList}")
            q.put(peerList)

def request_file(peer_ip, filename,download_folder = os.getcwd,sendername="", main_port=12346):
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
                giveGuiInfoToReceiver(filename,sendername)
                receive_file(peer_ip, new_port, filename,download_folder,sendername)
            else:
                print(f"File '{filename}' not available from {peer_ip}")
        except Exception as e:
            print(f"Error connecting to {peer_ip} for file '{filename}': {e}")


def receive_file(peer_ip, port, filename, download_folder,sendername=""):
    max_retries = 5
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as file_sock:
                print(f"Attempting to connect to {peer_ip}:{port} (Attempt {attempt + 1}/{max_retries})")
                file_sock.connect((peer_ip, port))
                
                local_filename = os.path.join(download_folder,f"{peer_ip}_{filename}")
                local_filename_compressed = local_filename + '.gz'
                with open(local_filename_compressed, 'wb') as f:
                    print(f"Receiving file '{filename}' from {peer_ip}...")

                    startTime = time.time()
                    while True:
                        data = file_sock.recv(65535)
                        if not data:
                            break
                        f.write(data)
                

                endTime = time.time()
                decompressFile(local_filename_compressed,local_filename)
                cleanup_file(local_filename_compressed)

            speed = (os.path.getsize(local_filename) / (endTime - startTime) / (1024))/1024
            print(f"File '{filename}' received and saved as '{local_filename}'")
            print(f"File transfer rate is {speed:.2f} MB/s")
            giveGuiInfoToReceiver(filename,sendername,speed,end=1)
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
        

#---------------------------------------------------------------UTILITY FUNCTIONS------------------------------------------------------------------------------------------------------------------------------


def cleanup_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Temporary file deleted: {file_path}")


def compressFile(filepath):
    temp_path = filepath + '.gz'
    
    with open(filepath, 'rb') as original_file:
        with gzip.open(temp_path, 'wb') as compressed_file:
            shutil.copyfileobj(original_file, compressed_file)
    
    return temp_path  # Return path to the compressed file
    
def decompressFile(compressed_path, output_path):

    with gzip.open(compressed_path, 'rb') as compressed_file:
        with open(output_path, 'wb') as decompressed_file:
            shutil.copyfileobj(compressed_file, decompressed_file)

def  giveGuiInfoToSender(filename,recipient_ip,speed=0,end=0):
    try:
        message = ""
        if(end == 0):
            message = f"Started sending file {filename} to {recipient_ip}"
        else:
            if(speed!=0):
                message = f"Finished sending file {filename} to {recipient_ip} with speed {speed:.2f} MB/s"
            else:
                message = f"Finished sending file {filename} to {recipient_ip}"

        globalLogger.sendMessageSender(message)
    except Exception as e:
        print(f"Error in giving info to sender: {e}")

def giveGuiInfoToReceiver(filename,sendername,speed=0,end=0):
    try:
        message = ""
        if(end == 0):
            message = f"Started receiving file {filename} from {sendername}"
        else:
            if(speed!=0):
                message = f"Finished receiving file {filename} from {sendername} with speed {speed:.2f} MB/s"

            else:
                message = f"Finished receiving file {filename} from {sendername}"

        globalLogger.sendMessageReceiver(message)
    except Exception as e:
        print(f"Error in giving info to receiver: {e}")


def setDestinationFolder():
    pass


