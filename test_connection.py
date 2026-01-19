import requests
import time

URL = "http://127.0.0.1:5001/health"
print(f"Testing {URL}...")
try:
    resp = requests.get(URL, timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")

URL_KEY = "http://127.0.0.1:5001/create_key"
print(f"\nTesting {URL_KEY}...")
headers = {"Authorization": "Bearer super_secret_admin_key_123"}
payload = {"duration": "1d"}
try:
    resp = requests.post(URL_KEY, json=payload, headers=headers, timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
