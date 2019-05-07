'''
Nutanix REST API Bootcamp.

Lesson02.
Access to Nutanix cluster with credential.
And get cluster status.
'''

import requests, json
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

IP = '10.149.20.41'
USER = 'admin'
PASSWORD = 'Nutanix/4u123!'

# (1) Make Session
session = requests.Session()
session.auth = (USER, PASSWORD)
session.verify = False                              
session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

# (2) Make URL
url = 'https://{}:9440/PrismGateway/services/rest/v1/cluster'.format(IP)
# 'https://10.149.9.41:9440/PrismGateway/services/rest/v1/cluster'

# (3) Send request and get Response
response = session.get(url)

# (4) Check response code
print('Response Code: {}'.format(response.status_code))
print('Response OK?: {}'.format(response.ok))

# (5) Check response body
print('Response Body:')
print(response.text)

# text -> dict
print(json.dumps(response.json(), indent=2))

# get cluster name from dict

# get uuid from dict

