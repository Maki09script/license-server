import requests
import json

URL = "http://127.0.0.1:5001/validate"
# Use a key that likely exists or create one first
# I'll create one first
URL_CREATE = "http://127.0.0.1:5001/create_key"
headers = {"Authorization": "Bearer super_secret_admin_key_123"}
key_resp = requests.post(URL_CREATE, json={"duration": "1d"}, headers=headers)
print(f"Create Key: {key_resp.text}")
key = key_resp.json()['key']

print(f"Validating Key: {key}")
payload = {
    "key": key,
    "hwid": "TEST_HWID_123"
}
resp = requests.post(URL, json=payload)
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text}")
