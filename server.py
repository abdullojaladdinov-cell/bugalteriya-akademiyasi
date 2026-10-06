import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'customers.json')


def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_customers():
    ensure_data_file()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []


def save_customer(customer):
    customers = load_customers()
    customers.append(customer)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)


def clear_customers():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        file_path = parsed.path

        if file_path == '/api/customers':
            customers = load_customers()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(customers, ensure_ascii=False).encode('utf-8'))
            return

        if file_path == '/api/customers/export':
            customers = load_customers()
            csv_lines = ['name,phone,email,course,registered_at']
            for customer in customers:
                row = [
                    str(customer.get('name', '')).replace(',', ' '),
                    str(customer.get('phone', '')).replace(',', ' '),
                    str(customer.get('email', '')).replace(',', ' '),
                    str(customer.get('course', '')).replace(',', ' '),
                    str(customer.get('registered_at', '')).replace(',', ' '),
                ]
                csv_lines.append(','.join(row))

            csv_data = '\n'.join(csv_lines).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="customers.csv"')
            self.end_headers()
            self.wfile.write(csv_data)
            return

        if file_path in ('', '/'):
            file_path = '/index.html'
        elif file_path == '/admin':
            file_path = '/admin.html'

        safe_path = os.path.normpath(file_path.lstrip('/'))
        full_path = os.path.join(BASE_DIR, safe_path)

        if os.path.exists(full_path) and os.path.isfile(full_path):
            self.serve_file(full_path)
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not found')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/register':
            content_length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(content_length)

            data = {}
            try:
                if self.headers.get('Content-Type', '').startswith('application/json'):
                    data = json.loads(raw.decode('utf-8'))
                else:
                    form_data = parse_qs(raw.decode('utf-8'))
                    for key, value in form_data.items():
                        data[key] = value[0]
            except Exception:
                data = {}

            name = str(data.get('name', '')).strip()
            phone = str(data.get('phone', '')).strip()
            email = str(data.get('email', '')).strip()
            course = str(data.get('course', '')).strip()

            if not name or not phone or not email:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Barcha maydonlar to'ldirilishi kerak."}, ensure_ascii=False).encode('utf-8'))
                return

            from datetime import datetime

            entry = {
                'name': name,
                'phone': phone,
                'email': email,
                'course': course,
                'registered_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            save_customer(entry)
            print('\n=== YANGI MIJOZ REGISTRATSIYASI ===')
            print(json.dumps(entry, ensure_ascii=False, indent=2))
            print('===================================\n')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Ro\'yxatdan o\'tish muvaffaqiyatli bajarildi.'}, ensure_ascii=False).encode('utf-8'))
            return

        if parsed.path == '/api/customers/clear':
            clear_customers()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Ro\'yxat tozalandi.'}, ensure_ascii=False).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not found')

    def serve_file(self, full_path):
        extension = os.path.splitext(full_path)[1].lower()
        mime_types = {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.json': 'application/json; charset=utf-8',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml',
        }

        self.send_response(200)
        self.send_header('Content-Type', mime_types.get(extension, 'application/octet-stream'))
        self.end_headers()

        with open(full_path, 'rb') as f:
            self.wfile.write(f.read())


if __name__ == '__main__':
    ensure_data_file()
    server = ThreadingHTTPServer(('0.0.0.0', 8000), Handler)
    print('Server running on http://localhost:8000')
    server.serve_forever()
