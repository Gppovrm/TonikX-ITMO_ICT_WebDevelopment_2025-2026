import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto("Hello, server".encode('utf-8'), ('localhost', 1234))
print(client.recvfrom(1024)[0].decode('utf-8'))

client.close()

# https://www.youtube.com/watch?v=esLgiMLbRkI - TCP vs UDP Sockets in Python