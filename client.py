import requests

response = requests.post("http://127.0.0.1:5000/hello/world")

print(response.text)
print(response.status_code)