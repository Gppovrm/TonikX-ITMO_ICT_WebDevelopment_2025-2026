import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 8080))

client.send(b"GET / HTTP/1.1\r\n\r\n")

response = client.recv(4096).decode('utf-8')
print(response)

client.close()