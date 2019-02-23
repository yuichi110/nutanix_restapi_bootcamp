'''
Nutanix REST API Bootcamp.

Lesson11.
Making function which handles REST API

Good Point.
Easy to understand rather than flat script.
Bad point is many args. And how "IP" is used.
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
IMAGE_NAME = 'REST_CENT7_IMG'

VM_NAME = 'REST_TEST_VM2'
VM_MEMORY_MB = 2048
VM_CPU_NUM = 1
VM_CPU_CORE = 2

def get_session(user, password):
  session = requests.Session()
  session.auth = (user, password)
  session.verify = False                              
  session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  url = 'https://{}:9440/PrismGateway/services/rest/v1/cluster'.format(IP)
  response = session.get(url)
  if not response.ok:
    raise Exception("Failed to establish session to the server.")
  return session

def get_network_uuid(session, name):
  url = 'https://{}:9440/PrismGateway/services/rest/v2.0/networks'.format(IP)
  response = session.get(url)
  if not response.ok:
    raise Exception('Failed to get networks.')
  
  network_uuid = ''
  d = json.loads(response.text)
  for network in d['entities']:
    if network['name'] == name:
      network_uuid = network['uuid']
      break
  if network_uuid == '':
    raise Exception('Unable to find network')
  return network_uuid

def get_image_uuid_size(session, name):
  url = 'https://{}:9440/PrismGateway/services/rest/v2.0/images'.format(IP)
  response = session.get(url)
  if not response.ok:
    raise Exception('Failed to get images.')

  vmdisk_uuid = ''
  vmdisk_size = 0
  d = json.loads(response.text)
  for image in d['entities']:
    if image['name'] == name:
      vmdisk_uuid = image['vm_disk_id']
      vmdisk_size = image['vm_disk_size']
      break
  if vmdisk_uuid == '':
    raise Exception('Unable to find image')
  return (vmdisk_uuid, vmdisk_size)

def create_image(session, name, memory_mb, cpu_num, cpu_core, vdisk_uuid, vdisk_size, network_uuid):
  url = 'https://{}:9440/PrismGateway/services/rest/v2.0/vms?include_vm_disk_config=true&include_vm_nic_config=true'.format(IP)
  body_dict = {
    "name": name,
    "memory_mb": memory_mb,
    "num_vcpus": cpu_num,
    "description": "",
    "num_cores_per_vcpu": cpu_core,
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
            "vmdisk_uuid": vdisk_uuid
          },
          "minimum_size": vdisk_size
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
    print(response.status_code)
    raise Exception('Failed to create vm. Reason:{}'.format(response.text))

  d = json.loads(response.text)
  task_uuid = d['task_uuid']
  return task_uuid


session = get_session(USER, PASSWORD)
network_uuid = get_network_uuid(session, NETWORK_NAME)
(image_uuid, image_size) = get_image_uuid_size(session, IMAGE_NAME)
task_uuid = create_image(session, VM_NAME, VM_MEMORY_MB, VM_CPU_NUM, VM_CPU_CORE, image_uuid, image_size, network_uuid)