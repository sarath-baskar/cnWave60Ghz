import requests

def request(url,payload,req_type):
    headers = {'Content-Type': 'text/plain'}
    response = requests.request(req_type,url,headers=headers,data=payload,verify=False)
    assert response.status_code==200
    return response.json()


