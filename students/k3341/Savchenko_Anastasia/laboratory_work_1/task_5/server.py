import socket
import sys
from urllib.parse import unquote


class MyHTTPServer:
    # Параметры сервера
    def __init__(self, host, port, server_name):
        self._host = host
        self._port = port
        self._server_name = server_name
        # Хранилище оценок: {дисциплина: [оценки]}
        self._grades = {}

    def serve_forever(self):
        # 1. Запуск сервера на сокете, обработка входящих соединений
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            print(f"Сервер запущен на http://{self._host}:{self._port}")

            while True:
                conn, _ = serv_sock.accept()
                try:
                    self.serve_client(conn)
                except Exception as e:
                    print(f'Ошибка при обработке клиента: {e}')
        finally:
            serv_sock.close()

    def serve_client(self, conn):
        # 2. Обработка клиентского подключения
        try:
            req = self.parse_request(conn)
            resp = self.handle_request(req)
            self.send_response(conn, resp)
        except ConnectionResetError:
            conn = None
        except Exception as e:
            self.send_error(conn, e)

        if conn:
            conn.close()

    def parse_request(self, conn):
        # 3. функция для обработки заголовка http+запроса. Python, сокет предоставляет возможность создать вокруг него некоторую обертку, которая предоставляет file object интерфейс. Это дайте возможность построчно обработать запрос. Заголовок всегда - первая строка. Первую строку нужно разбить на 3 элемента  (метод + url + версия протокола). URL необходимо разбить на адрес и параметры (isu.ifmo.ru/pls/apex/f?p=2143 , где isu.ifmo.ru/pls/apex/f, а p=2143 - параметр p со значением 2143)
        rfile = conn.makefile('rb')

        line = rfile.readline(65537)
        if len(line) > 65536:
            raise Exception('Request line is too long')

        req_line = line.decode('iso-8859-1')
        req_line = req_line.rstrip('\r\n')

        words = req_line.split()
        if len(words) != 3:
            raise Exception('Malformed request line')

        method, target, ver = words

        if ver != 'HTTP/1.1':
            raise Exception('Unexpected HTTP version')

        headers = self.parse_headers(rfile)

        # Читаем тело запроса для POST
        body = None
        if method == 'POST':
            content_length = headers.get('Content-Length')
            if content_length:
                try:
                    body_length = int(content_length)
                    body = rfile.read(body_length).decode('utf-8')
                except:
                    pass

        host = headers.get('Host')
        if not host:
            raise Exception('Host header is missing')

        return {
            'method': method,
            'target': target,
            'version': ver,
            'headers': headers,
            'body': body
        }

    def parse_headers(self, rfile):
        # 4. Функция для обработки headers. Необходимо прочитать все заголовки после первой строки до появления пустой строки и сохранить их в массив.
        headers = {}

        while True:
            line = rfile.readline(65537)
            if len(line) > 65536:
                raise Exception('Header line is too long')

            if line in (b'\r\n', b'\n', b''):
                break

            header_line = line.decode('iso-8859-1').rstrip('\r\n')
            if ': ' in header_line:
                key, value = header_line.split(': ', 1)
                headers[key] = value

        return headers

    def handle_request(self, req):
        # 5. Функция для обработки url в соответствии с нужным методом. В случае данной работы, нужно будет создать набор условий, который обрабатывает GET или POST запрос. GET запрос должен возвращать данные. POST запрос должен записывать данные на основе переданных параметров.
        method = req['method']
        target = req['target']
        body = req.get('body')

        # Разбираем параметры
        params = {}

        if method == 'GET':
            # GET параметры из URL
            if '?' in target:
                path, query_string = target.split('?', 1)
            else:
                path = target
                query_string = ''

            if query_string:
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[unquote(key)] = unquote(value)
        elif method == 'POST':
            # POST параметры из тела запроса
            path = target
            if body:
                for param in body.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[unquote(key)] = unquote(value)
        else:
            path = target

        # Обработка запросов
        if path == '/' and method == 'GET':
            return self.handle_get_grades()

        if path == '/add' and (method == 'GET' or method == 'POST'):
            return self.handle_add_grade(params)

        return self.error_response(404, 'Not Found')

    def handle_get_grades(self):
        # Загружаем HTML шаблон
        with open('index.html', 'r', encoding='utf-8') as f:
            html_template = f.read()

        # Генерируем таблицу с оценками
        grades_table = self.generate_grades_table()

        # Заменяем placeholder в шаблоне
        html = html_template.replace('<!--GRADES_TABLE-->', grades_table)

        headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(html.encode('utf-8'))))
        ]

        return {'status': 200, 'reason': 'OK', 'headers': headers, 'body': html}

    def handle_add_grade(self, params):
        if 'discipline' not in params or 'grade' not in params:
            return self.error_response(400, 'Bad Request', 'Missing discipline or grade parameter')

        discipline = params['discipline']
        grade = params['grade']

        if not grade.isdigit():
            return self.error_response(400, 'Bad Request', 'Grade must be a number')

        grade = int(grade)

        if grade < 1 or grade > 5:
            return self.error_response(400, 'Bad Request', 'Grade must be between 1 and 5')

        if discipline not in self._grades:
            self._grades[discipline] = []

        self._grades[discipline].append(grade)

        headers = [('Location', '/')]
        return {'status': 303, 'reason': 'See Other', 'headers': headers, 'body': ''}

    def send_response(self, conn, resp):
        # 6. Функция для отправки ответа. Необходимо записать в соединение status line вида HTTP/1.1 <status_code> <reason>. Затем, построчно записать заголовки и пустую строку, обозначающую конец секции заголовков.
        wfile = conn.makefile('wb')

        status_line = f"HTTP/1.1 {resp['status']} {resp['reason']}\r\n"
        wfile.write(status_line.encode('iso-8859-1'))

        if 'headers' in resp:
            for key, value in resp['headers']:
                header_line = f"{key}: {value}\r\n"
                wfile.write(header_line.encode('iso-8859-1'))

        wfile.write(b'\r\n')

        if 'body' in resp and resp['body']:
            wfile.write(resp['body'].encode('utf-8'))

        wfile.flush()
        wfile.close()

    def send_error(self, conn, err):
        error_msg = str(err)
        body = error_msg.encode('utf-8')

        headers = [
            ('Content-Type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(body)))
        ]

        resp = {'status': 500, 'reason': 'Internal Server Error', 'headers': headers, 'body': error_msg}
        self.send_response(conn, resp)

    def error_response(self, status, reason, body=None):
        if body is None:
            body = reason

        body_encoded = body.encode('utf-8')
        headers = [
            ('Content-Type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(body_encoded)))
        ]

        return {'status': status, 'reason': reason, 'headers': headers, 'body': body}

    def generate_grades_table(self):
        if not self._grades:
            return '<p>Нет оценок. Добавьте первую оценку!</p>'

        table_html = '''
    <table>
        <tr>
            <th>Дисциплина</th>
            <th>Оценки</th>
        </tr>'''

        for discipline, grades in sorted(self._grades.items()):
            grades_str = ', '.join(map(str, grades))

            table_html += f'''
        <tr>
            <td>{discipline}</td>
            <td>{grades_str}</td>
        </tr>'''

        table_html += '''
    </table>'''

        return table_html


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    name = sys.argv[3] if len(sys.argv) > 3 else 'localhost'

    serv = MyHTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass