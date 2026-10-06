import json
import pathlib
import urllib.request

payload = json.dumps({
    'name': 'Ali Valiyev',
    'phone': '+998901234567',
    'email': 'ali@example.com',
    'course': 'Asosiy buxgalteriya'
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8000/api/register',
    data=payload,
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req, timeout=10) as response:
    print('STATUS', response.status)
    print(response.read().decode('utf-8'))

customers_path = pathlib.Path('C:/Users/user/Desktop/website/customers.json')
data = json.loads(customers_path.read_text(encoding='utf-8'))
print('CUSTOMERS', len(data))
print(data[-1])
