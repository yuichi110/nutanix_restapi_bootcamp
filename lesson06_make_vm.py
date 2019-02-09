'''
Nutanix REST API Bootcamp.

Lesson06.
Complex sample.
Create Guest VM with these param
 - Network
 - Image (You need container if creating VM from scratch)
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

NETWORK_NAME = 'REST_NETWORK'
IMAGE_NAME = 'IMG_CENT7_REST'

VM_NAME = 'REST_TEST_VM'
VM_MEMORY_MB = 2048
VM_CPU_NUM = 1
VM_CPU_CORE = 2

session = requests.Session()
session.auth = (USER, PASSWORD)
session.verify = False                              
session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

# (1) Get network uuid
print('(1) Get network uuid')
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks'.format(IP)
response = session.get(url)
if not response.ok:
  print('Abort. Failed to get networks.')
  exit(1)

network_uuid = ''
d = json.loads(response.text)
for network in d['entities']:
  if network['name'] == NETWORK_NAME:
    network_uuid = network['uuid']
    break
if network_uuid == '':
  print('Abort. There is no network which has name "{}".'.format(NETWORK_NAME))
  exit(1)
print('network_name="{}", uuid="{}"'.format(NETWORK_NAME, network_uuid))
print()


# (2) Get image uuid and size
print('(2) Get image(vdisk) uuid')
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/images'.format(IP)
response = session.get(url)
if not response.ok:
  print('Abort. Failed to get images.')
  exit(1)

vmdisk_uuid = ''
vmdisk_size = 0
d = json.loads(response.text)
for image in d['entities']:
  if image['name'] == IMAGE_NAME:
    vmdisk_uuid = image['vm_disk_id']
    vmdisk_size = image['vm_disk_size']
    break
if vmdisk_uuid == '':
  print('Abort. There is no image which has name "{}".'.format(IMAGE_NAME))
  exit(1)
print('image_name="{}", uuid="{}'.format(IMAGE_NAME, vmdisk_uuid))
print()

# (3) Create image
print('(3) Create new guest vm with network and image.')
url = 'https://{}:9440/PrismGateway/services/rest/v2.0/vms?include_vm_disk_config=true&include_vm_nic_config=true'.format(IP)
body_dict = {
  "name": VM_NAME,
  "memory_mb": VM_MEMORY_MB,
  "num_vcpus": VM_CPU_NUM,
  "description": "",
  "num_cores_per_vcpu": VM_CPU_CORE,
  "vm_disks": [
    {
      "is_cdrom": True,
      "is_empty": True,
      "disk_address": {
        "device_bus": "ide"
      }
    },
    {
      "is_cdrom": False,
      "disk_address": {
        "device_bus": "scsi"
      },
      "vm_disk_clone": {
        "disk_address": {
          "vmdisk_uuid": vmdisk_uuid
        },
        "minimum_size": vmdisk_size
      }
    }
  ],
  "vm_nics": [
    {
      "network_uuid": network_uuid,
    }
  ],
  "affinity": None,
  "vm_features": {
    "AGENT_VM": False
  }
}
body_text = json.dumps(body_dict)
response = session.post(url, data=body_text)
if not response.ok:
  print('Abort. Failed to create VM.')
  print(response.text)
  exit(1)

d = json.loads(response.text)
task_uuid = d['task_uuid']
print('task_uuid={}'.format(task_uuid))