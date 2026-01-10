import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8080))
server.listen(1)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

while True:
    conn, _ = server.accept()

    response = f"""HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(html.encode('utf-8'))}

{html}"""

    conn.send(response.encode('utf-8'))
    conn.close()