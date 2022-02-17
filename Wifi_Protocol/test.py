import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print(ip_address)
