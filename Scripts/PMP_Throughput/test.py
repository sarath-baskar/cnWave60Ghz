import requests

url = "https://10.110.186.145/api/v2/setNetworkOverridesConfig"

payload = r'{"overrides": "{\"envParams\":{\"CAMBIUM_L2_BRIDGE_IFACE\":\"nic1\"}}"}' 
headers = {
  'Content-Type': 'text/plain'
}

response = requests.request("POST", url, headers=headers, data=payload,verify=False)

op={}
op= response.json()
print(op)

