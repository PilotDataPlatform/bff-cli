import requests

url = "http://127.0.0.1:5080/v1/dataset/testdataredcap2"
def auth(payload=None):
        if not payload:
            payload = {
                "username": "jzhang7",
                "password": "Indoc1234567!"
            }
        response = requests.post("http://10.3.7.217:5061/v1/users/auth", json=payload)
        data = response.json()
        # print(f'auth: {data}')
        return data["result"].get("access_token")

token = auth()
headers = {'Authorization': 'Bearer ' + token}
res = requests.get(url, headers=headers)
print(res.text)
