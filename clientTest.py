import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.1.x', 12345))  # Replace with server's IP
print("Connected to server")
s.close()
