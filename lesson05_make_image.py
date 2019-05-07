'''
Nutanix REST API Bootcamp.

Lesson05.
Complex sample.
Create Image(vDisk or ISO) from NFS Server.
'''

import time
import json
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

IP = '10.149.20.41'
USER = 'admin'
PASSWORD = 'Nutanix/4u123!'

NFS_IP = '10.149.245.50'
NFS_PORT = 2049

#IMAGE_URL = 'nfs://10.149.245.50/Public/bootcamp/centos7_min_raw'
IMAGE_URL = 'nfs://10.149.245.50/Public/bootcamp/centos7_min.iso'
#IMAGE_NAME = 'IMG_CENT7_REST'
IMAGE_NAME = 'ISO_CENT7_REST'
CONTAINER_NAME = 'container'


# (0) Check whether NFS Server is open or not.
import socket
try:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((NFS_IP, NFS_PORT))
  s.shutdown(2)
  print('Able to connect to NFS Server {}:{} from this PC.'.format(NFS_IP, NFS_PORT))
except:
  print('Unable to connect to NFS Server {}:{} from this PC.'.format(NFS_IP, NFS_PORT))
  print('Abort')
  exit()

print('Make session to Nutanix Server')
session = requests.Session()
session.auth = (USER, PASSWORD)
session.verify = False                              
session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

# (1) GET CONTAINER UUID
print('(1) Get container UUID')
url = 'https://{}:9440/PrismGateway/services/rest/v1/containers'.format(IP)
response = session.get(url)
if not response.ok:
  print('Abort. response code is not 200')
  print('response.text')
  exit(1)
#print(json.dumps(json.loads(response.text), indent=2))

d = json.loads(response.text)
#print(json.dumps(d, indent=2))


container_uuid = ''
for container in d['entities']:
  if container['name'] == CONTAINER_NAME:
    container_uuid = container['containerUuid']
if container_uuid == '':
  print('Abort. Container "{}" doesn\'t exist'.format(CONTAINER_NAME))
  exit(1)
print('uuid={}'.format(container_uuid))
print()

# (2) Create image and get Task UUID
print('(2) Create image from NFS Server to the container and get the task UUID')
is_iso = IMAGE_URL.lower().endswith('.iso')
image_type = 'ISO_IMAGE' if is_iso else 'DISK_IMAGE'
print('imageType={}'.format(image_type))
body_dict = {
  "name": IMAGE_NAME,
  "annotation": "",
  "imageType": image_type,
  "imageImportSpec": {
    "containerUuid": container_uuid,
    "url": IMAGE_URL,
  }
}
body_text = json.dumps(body_dict)
url = 'https://{}:9440/api/nutanix/v0.8/images'.format(IP)
response = session.post(url , data=body_text)
if not response.ok:
  exit(1)
print('image creation task was created.')
d = json.loads(response.text)
task_uuid = d['taskUuid']
print('task_uuid={}'.format(task_uuid))
print()

# (3) Polling Task status till image creation task finished
print('(3) Polling image creation task status till image creattion task finish.')
url = 'https://{}:9440/api/nutanix/v0.8/tasks/{}'.format(IP, task_uuid)
while True:
  response = session.get(url)
  if not response.ok:
    exit(1)
  d = json.loads(response.text)
  task_name = d['metaRequest']['methodName']
  task_percent = d.get('percentageComplete', 0)
  task_status = d['progressStatus']

  print('Task name:{}, Status:{}, Percent:{}'.format(task_name, task_status, task_percent))
  if task_percent == 100:
    break
  time.sleep(0.5)

print('finish.')
