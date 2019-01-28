'''
Test module for nutanix.py (Python REST API wrapper)

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

from nutanix import NutanixRestApiClient

# PARAM FOR SESSION
CLUSTER_IP = '10.149.27.41'
CLUSTER_USER = 'admin'
CLUSTER_PASSWORD = 'Nutanix/4u!'

def test_login():
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD)

def test_get_vm_names():
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD)
  result = session.get_vm_names()
  print(result)

def test_get_vm_disks():
  VM = 'REST_TEST_VM'
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD)
  result = session.get_vm_disks(VM)
  print(result)

def test_get_container_names():
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD)
  result = session.get_container_names()
  print(result)

def test_get_image_names():
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD)
  result = session.get_image_names()
  print(result)

def test_create_image():
  VM_NAME = 'REST_TEST_VM'
  VDISK_LABEL = 'scsi.0'
  TARGET_CONTAINER = 'container'
  IMAGE_NAME = 'TEST_REST_IMAGE'
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD)
  result = session.create_image(VM_NAME, VDISK_LABEL, TARGET_CONTAINER, IMAGE_NAME)
  print(result)  

def test_get_task_status():
  TASK_UUID = '6cdfc297-f788-482e-a76e-ed3408f1f180'
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD)
  result = session.get_task_status(TASK_UUID)
  print(result)

if __name__ == '__main__':
  test_get_task_status()
