import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import importlib

# Импортируем Lambda-функцию
# Предполагается, что в lambda_function.py есть функция lambda_handler
try:
    from lambda_function import lambda_handler
except ImportError as e:
    print(f"Ошибка импорта lambda_handler: {e}")
    lambda_handler = None

class YandexLambdaHandler(BaseHTTPRequestHandler):
    """HTTP-обработчик для Yandex Serverless Containers"""

    def log_message(self, format, *args):
        """Выводим логи в stdout (Yandex Cloud соберет их)"""
        print(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')

    def do_PUT(self):
        self._handle_request('PUT')

    def do_DELETE(self):
        self._handle_request('DELETE')

    def do_PATCH(self):
        self._handle_request('PATCH')

    def _handle_request(self, method):
        """Преобразует HTTP-запрос в событие для Lambda и возвращает ответ"""

        # Получаем длину тела запроса
        content_length = int(self.headers.get('Content-Length', 0))

        # Читаем тело запроса
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''

        # Преобразуем HTTP-запрос в структуру, похожую на API Gateway событие
        # (чтобы ваша Lambda-функция могла обрабатывать его как обычно)
        event = {
            'httpMethod': method,
            'path': self.path,
            'headers': dict(self.headers),
            'queryStringParameters': self._parse_query_string(),
            'body': body,
            'isBase64Encoded': False,
            'requestContext': {
                'http': {
                    'method': method,
                    'path': self.path,
                    'protocol': self.request_version,
                    'sourceIp': self.client_address[0],
                    'userAgent': self.headers.get('User-Agent', '')
                }
            }
        }

        # Вызываем Lambda-функцию
        if lambda_handler is None:
            self._send_response(500, {'error': 'Lambda handler not found'})
            return

        try:
            # Вызываем вашу функцию
            response = lambda_handler(event, {})

            # Отправляем ответ
            status_code = response.get('statusCode', 200)
            headers = response.get('headers', {})
            body = response.get('body', '')

            # Если body - это словарь, преобразуем в JSON
            if isinstance(body, dict):
                body = json.dumps(body)
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/json'

            self._send_response(status_code, body, headers)

        except Exception as e:
            print(f"Ошибка при выполнении Lambda-функции: {e}")
            self._send_response(500, {'error': str(e)})

    def _parse_query_string(self):
        """Парсит query-параметры из URL"""
        parsed = urllib.parse.urlparse(self.path)
        return urllib.parse.parse_qs(parsed.query)

    def _send_response(self, status_code, body, headers=None):
        """Отправляет HTTP-ответ"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')

        if headers:
            for key, value in headers.items():
                self.send_header(key, value)

        self.end_headers()

        # Если body - это строка, отправляем как есть, иначе преобразуем в JSON
        if isinstance(body, str):
            self.wfile.write(body.encode('utf-8'))
        elif isinstance(body, dict):
            self.wfile.write(json.dumps(body).encode('utf-8'))
        else:
            self.wfile.write(str(body).encode('utf-8'))

def main():
    """Запускает HTTP-сервер"""
    port = int(os.environ.get('PORT', 8080))

    print(f"Starting HTTP server on port {port}")
    print(f"Lambda handler: {lambda_handler}")

    server = HTTPServer(('0.0.0.0', port), YandexLambdaHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == '__main__':
    main()