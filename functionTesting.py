import socket
import struct
import psutil




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

def broadcast_message(message):
    ip, netmask = get_wifi_ip_and_subnet()
    if ip and netmask:
        broadcast_address = calculate_broadcast_address(ip, netmask)
        print(f"Broadcasting to {broadcast_address}...")
        
        # Create a UDP socket and broadcast the message
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.sendto(message.encode(), (broadcast_address, 5005))  # 5005 is an example port
    else:
        print("No Wi-Fi interface found.")


def receive_broadcast(port=5005, timeout=10):
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        # Allow the socket to receive broadcast messages
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the port to listen for incoming messages
        sock.bind(('', port))
        
        # Set the timeout for receiving data
        sock.settimeout(timeout)

        print(f"Listening for broadcast messages on port {port}...")

        try:
                # Receive data from the socket (blocking)
            data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
            print(f"Received message: {data.decode()} from {addr}")
        except socket.timeout:
            print(f"Timeout reached ({timeout} seconds), no more messages.")
        except Exception as e:
            print(f"Error receiving broadcast: {e}")

def serverTesting():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5000))  # Bind to all interfaces on port 5000
    server_socket.listen(1)
    print("Server listening on port 5000")
    conn, addr = server_socket.accept()
    print("Connection from:", addr)

def clientTesting():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.1.x', 12345))  # Replace with server's IP
    print("Connected to server")
    s.close()

def check_multicast_support(multicast_group="224.0.0.1", port=5007):
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Allow multiple sockets to use the same port number
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to a specific port and all network interfaces
        sock.bind(('', port))

        # Try to join a multicast group
        mreq = socket.inet_aton(multicast_group) + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        print("Multicast is supported.")
        return True

    except OSError as e:
        print(f"Multicast is not supported: {e}")
        return False

    finally:
        sock.close()
# Example usage
#receive_broadcast(port=5005)

# Example usage
#broadcast_message("Hello, this is a broadcast message")

check_multicast_support()