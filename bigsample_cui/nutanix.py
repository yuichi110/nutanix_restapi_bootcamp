'''
Python wrapper for Nutanix REST API.

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

import requests
import json
import traceback
import logging

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

TIMEOUT_CONNECTION = 2
TIMEOUT_READ = 5

class NutanixRestApiClient:
  def __init__(self, ip, username, password):

    # Test IP and Port reachability
    is_port_open = True
    import socket
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(TIMEOUT_CONNECTION) # seconds
      s.connect((ip, 9440))
      s.shutdown(2)
    except Exception as e:
      is_port_open = False

    if not is_port_open:
      raise Exception('Unable to connect Nutanix Cluster "{}". Please check ip and port.'.format(ip))

    # Make url base
    self.index_url = 'https://{}:9440'.format(ip)
    self.v1_url = 'https://{}:9440/PrismGateway/services/rest/v1'.format(ip)
    self.v2_url = 'https://{}:9440/PrismGateway/services/rest/v2.0'.format(ip)

    # Make session
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False                              
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

    # Test session
    is_requests_ok = True
    url = self.v1_url + "/cluster"
    try:
      resp = session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))
    except:
      is_requests_ok = False

    if not is_requests_ok:
      raise Exception('Able to access. But unexpected error happens. Please check server status.')

    if resp.status_code != 200:
      raise Exception('Able to access. But unable to get cluster info. Please check your credential.')

    # OK
    self.session = session


  def get_vm_names(self):
    error_dict = {}
    try:
      url = self.v2_url + '/vms/'
      resp = self.session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))
      if resp.status_code != 200:
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      d = json.loads(resp.text)
      vms = []
      for vm in d['entities']:
        vms.append(vm['name'])
      vms.sort()
      return (True, vms)

    except Exception as e:
      error_dict['error'] = str(e)
      error_dict['stacktrace'] = traceback.format_exc()
      return (False, error_dict)

  def get_vm_disks(self, vm_name):
    error_dict = {}
    try:
      url = self.v2_url + '/vms/?include_vm_disk_config=true'
      resp = self.session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))

      if resp.status_code != 200:
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      d = json.loads(resp.text)
      vm_d = {}
      for vm in d['entities']:
        if vm['name'] == vm_name:
          vdisks = []
          for vdisk in vm['vm_disk_info']:
            if vdisk['is_cdrom']:
              continue
            vdisks.append(vdisk['disk_address']['disk_label'])
          return (True, vdisks)

      # Unable to find the vm. Raise error.
      error_dict['method'] = 'get'
      error_dict['url'] = url
      error_dict['code'] = resp.status_code
      error_dict['text'] = resp.text
      raise Exception('Receive expected response. But unable to find the vm "{}".'.format(vm_name))

    except Exception as e:
      error_dict['error'] = str(e)
      error_dict['stacktrace'] = traceback.format_exc()
      return (False, error_dict)


  def get_container_names(self):
    error_dict = {}
    try:
      url = self.v1_url + '/containers'
      resp = self.session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))
      if resp.status_code != 200:
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      d = json.loads(resp.text)
      container_names = []
      for cont in d['entities']:
        container_names.append(cont['name'])
      return (True, container_names)

    except Exception as e:
      error_dict['error'] = str(e)
      error_dict['stacktrace'] = traceback.format_exc()
      return (False, error_dict)


  def get_image_names(self):
    error_dict = {}
    try:
      url = self.index_url + '/api/nutanix/v0.8/images'
      resp = self.session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))
      if resp.status_code != 200:
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      d = json.loads(resp.text)
      image_names = []
      for image in d['entities']:
        image_names.append(image['name'])
      return (True, image_names)

    except Exception as e:
      error_dict['error'] = str(e)
      error_dict['stacktrace'] = traceback.format_exc()
      return (False, error_dict)


  def create_image(self, vm_name, vm_disk, target_container, image_name):
    error_dict = {}
    try:
      vdisk_uuid = ''
      source_container_uuid = ''
      source_container_name = ''
      target_container_uuid = ''

      # get vdisk_uuid and source_container_uuid 
      url = url = self.v2_url + '/vms/?include_vm_disk_config=true'
      resp = self.session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))
      if resp.status_code != 200:
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      d = json.loads(resp.text)
      for vm in d['entities']:
        if vm['name'] != vm_name:
          continue
        for vdisk in vm['vm_disk_info']:
          if vdisk['disk_address']['disk_label'] == vm_disk:
            vdisk_uuid = vdisk['disk_address']['vmdisk_uuid']
            source_container_uuid = vdisk['storage_container_uuid']
            break
        break
      if vdisk_uuid == '':
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Unable to get vdisk_uuid etc. Please check both vm_name and vdisk_label.')

      # get source_container_name and target_container_uuid
      url = self.v1_url + '/containers'
      resp = self.session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))
      if resp.status_code != 200:
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      d = json.loads(resp.text)
      for cont in d['entities']:
        if cont['containerUuid'] == source_container_uuid:
          source_container_name = cont['name']
        if cont['name'] == target_container:
          target_container_uuid = cont['containerUuid']
      if source_container_name == '':
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Unable to find source container name from uuid="{}".'.format(source_container_uuid))

      if target_container_uuid == '':
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Unable to find container which has name "{}"'.format(target_container))

      # build request body for image creation
      nfs_url = 'nfs://127.0.0.1/{}/.acropolis/vmdisk/{}'.format(source_container_name, vdisk_uuid)
      payload = {
        "name": image_name,
        "annotation": "",
        "imageType": 'DISK_IMAGE',
        "imageImportSpec": {
          "containerUuid": target_container_uuid,
          "url": nfs_url,
        }
      }
      json_payload = json.dumps(payload)

      # create image with body
      url = self.index_url + '/api/nutanix/v0.8/images'
      resp = self.session.post(url, data=json_payload, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))
      if resp.status_code not in [200, 201]:
        error_dict['method'] = 'post'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        error_dict['request_body'] = json_payload
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      # return task uuid
      d = json.loads(resp.text)
      return (True, d['taskUuid'])

    except Exception as e:
      error_dict['error'] = str(e)
      error_dict['stacktrace'] = traceback.format_exc()
      return (False, error_dict)


  def get_task_status(self, task_uuid):
    error_dict = {}
    try:
      url = self.index_url + '/api/nutanix/v0.8/tasks/{}'.format(task_uuid)
      resp = self.session.get(url, timeout=(TIMEOUT_CONNECTION, TIMEOUT_READ))

      if resp.status_code != 200:
        error_dict['method'] = 'get'
        error_dict['url'] = url
        error_dict['code'] = resp.status_code
        error_dict['text'] = resp.text
        raise Exception('Receive unexpected response code "{}".'.format(resp.status_code))

      respd = json.loads(resp.text)
      retd = {
        'uuid': respd['uuid'],
        'method': respd['metaRequest']['methodName'],
        'percent': respd.get('percentageComplete', 0),
        'status': respd['progressStatus'],
      }
      return (True, retd)

    except Exception as e:
      error_dict['error'] = str(e)
      error_dict['stacktrace'] = traceback.format_exc()
      return (False, error_dict)