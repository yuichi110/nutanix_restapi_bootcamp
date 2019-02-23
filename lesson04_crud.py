'''
Nutanix REST API Bootcamp.

Lesson04.
Easy CRUD.
 - Create　Network
 - Read Network
 - Update Network
 - Delete Network
'''

import time
import json
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

IP = '10.149.9.41'
USER = 'admin'
PASSWORD = 'Nutanix/4u!'
session = requests.Session()
session.auth = (USER, PASSWORD)
session.verify = False                              
session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

# NEW CODE
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks'.format(IP)
response = session.get(url)
if not response.ok:
  print(response.text)
  exit(1)

d = json.loads(response.text)
print(json.dumps(d, indent=2))

networks = d['entities']
for network in networks:


'''
# (1) HTTP GET : Read
print('(1) : HTTP GET : Get all network names')
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks'.format(IP)
response = session.get(url)
if not response.ok:
  print(response.text)
  exit(1)

d = json.loads(response.text)
print(json.dumps(d, indent=2))
network_name_list = []

networks = d['entities']
for network in networks:
  network_name_list.append(network['name'])
print(network_name_list)
print()


# (2) HTTP Post : Create
print('(2) HTTP POST : Create Network Lesson04_Test')
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks'.format(IP)
name = 'Lesson04_Test'
vlan = '1234'
body_dict = {
  "name": name,
  "vlan_id": vlan
}
body_text = json.dumps(body_dict)

response = session.post(url, data=body_text)
if not response.ok:
  print('Response status has problem. Abort')
  print(response.status_code)
  print(response.text)
  exit(1)
print('Created New Network')

print('wait 30 secs')
print()
#time.sleep(30)



# (3) HTTP PUT : Update
print('(3) HTTP PUT : Get Network UUID via name -> Update network via UUID')
# get uuid
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks'.format(IP)
response = session.get(url)
if not response.ok:
  print(response.text)
  exit(1)
d = json.loads(response.text)

name = 'Lesson04_Test'
uuid = ''
for network in d['entities']:
  if network['name'] == name:
    uuid = network['uuid']
if uuid == '':
  print('Unable to find network "{}"'.format(name))
  exit()



# update
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks/{}'.format(IP, uuid)
body_dict = {
  'name': name,
  "vlan_id": '2134'
}
body_text = json.dumps(body_dict)
response = session.put(url, data=body_text)
if not response.ok:
  print(response.text)
  exit(1)
print('Updated Existing network')

print('wait 30 secs')
print()
time.sleep(30)



# (4) HTTP DELETE : Delete
print('(4) HTTP DELETE : Delete Network Lesson04_Test via UUID')
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks/{}'.format(IP, uuid)
response = session.delete(url)
if not response.ok:
  print(response.text)
  exit(1)
print('Deleted network')
'''

