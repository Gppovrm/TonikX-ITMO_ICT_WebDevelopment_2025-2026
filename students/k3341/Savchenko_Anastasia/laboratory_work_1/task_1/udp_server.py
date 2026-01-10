import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM создаем UDP протокол

server.bind(('localhost', 1234))

message_client, address_client = server.recvfrom(1024)
print(message_client.decode('utf-8'))
server.sendto("Hello, client".encode('utf-8'), address_client)

server.close()


