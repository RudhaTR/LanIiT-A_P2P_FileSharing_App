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
    # Convert the IP address and subnet mask to binary
    ip_parts = list(map(int, ip.split('.')))
    netmask_parts = list(map(int, netmask.split('.')))
    
    ip_binary = ''.join([bin(part)[2:].zfill(8) for part in ip_parts])
    netmask_binary = ''.join([bin(part)[2:].zfill(8) for part in netmask_parts])
    
    # Calculate the network address by doing a bitwise AND
    network_binary = ''.join([str(int(ip_binary[i]) & int(netmask_binary[i])) for i in range(32)])
    
    # The broadcast address is the network address with the inverse of the netmask
    broadcast_binary = network_binary[:len(netmask_binary)] + '1' * (32 - len(netmask_binary))
    
    # Convert the broadcast address back to the dotted decimal format
    broadcast_ip = '.'.join([str(int(broadcast_binary[i:i+8], 2)) for i in range(0, 32, 8)])
    
    return broadcast_ip

def broadcast_message(message):
    ip, netmask = get_wifi_ip_and_subnet()
    if ip and netmask:
        broadcast_address = calculate_broadcast_address(ip, netmask)
        print(f"Broadcasting to {broadcast_address}...")
        
        # Create a UDP socket and broadcast the message
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.sendto(message.encode(), (broadcast_address, 12345))  # 5005 is an example port
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
            while True:
                # Receive data from the socket (blocking)
                data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
                print(f"Received message: {data.decode()} from {addr}")
        except socket.timeout:
            print(f"Timeout reached ({timeout} seconds), no more messages.")
        except Exception as e:
            print(f"Error receiving broadcast: {e}")

# Example usage
#receive_broadcast(port=5005)

# Example usage
broadcast_message("Hello, this is a broadcast message")