# DEMO
#
# 0 : Setup. Delete networks and vms on Demo1-4.
#
# 1 : Demo1. Get cluster info without class based implementation
# 2 : Demo1. Get cluster info with class (recomendation)
#
# 3 : Demo2. Create Network. HTTP Post
# 4 : Demo2. Read Network. HTTP Get
# 5 : Demo2. Update Netowrk. HTTP Put
# 6 : Demo2. Delete Network. HTTP Delete
#
# 7 : Demo3. Create VM from image
# 8 : Demo4. Create VM from image with specific IP
#

DEMO = 0

IP = '10.149.161.41'
USER = 'admin'
PASSWORD = 'Nutanix/4u!'

def main():
  if DEMO == 0:
    setup()
  elif DEMO == 1:
    demo1_1()
  elif DEMO == 2:
    demo1_2()
  elif DEMO == 3:
    demo2_1()
  elif DEMO == 4:
    demo2_2()
  elif DEMO == 5:
    demo2_3()
  elif DEMO == 6:
    demo2_4()
  elif DEMO == 7:
    demo3()
  elif DEMO == 8:
    demo4()
  else:
    'Please set 0-8 on val DEMO.'

def demo1_1():
  # Make session
  session = requests.Session()
  session.auth = (USER, PASSWORD)
  session.verify = False                              
  session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  # Send request and get response
  url = 'https://{}:9440/api/nutanix/v1/cluster/'.format(IP)
  print('HTTP Method:GET')
  print('URL:{}'.format(url))
  print()
  response = session.get(url)

  # Check success or not from response code
  print('Response code:{}\n'.format(response.status_code))
  if not response.ok:
    print('Failed to get cluster info.')
    exit(-1)

  # Content of response body. JSON
  response_json = response.json()
  print('Response Body (JSON)')
  print(json.dumps(response_json, indent=2))
  print()

  # Pick up items you want to check from JSON.
  print('Cluster name: {}'.format(response_json['name']))
  print('Cluster version: {}'.format(response_json['version']))


def demo1_2():
  rest_client = NutanixRestApiClient(IP, USER, PASSWORD)
  d = rest_client.get_cluster_info()
  print(json.dumps(d, indent=2))


def demo2_1():
  rest_client = NutanixRestApiClient(IP, USER, PASSWORD)
  d = rest_client.create_network(name='REST_NETWORK', vlan='165')
  print(json.dumps(d, indent=2))


def demo2_2():
  # Get All
  client = NutanixRestApiClient(IP, USER, PASSWORD)
  d = client.get_networks()
  print('GET All networks')
  print(json.dumps(d, indent=2))
  print()

  # Get via name. 
  # Caution. Same name entities(network) can exist.
  d = client.get_network(name='REST_NETWORK')
  print('Print Specific network: name=REST_NETWORK')
  print(json.dumps(d, indent=2))
  print()

  # Get via UUID (recommend)
  # Able to distinguish 2+ of same name entities.
  uuid = d['uuid']
  d = client.get_network(uuid=uuid)
  print('Print Specific network: uuid={}'.format(uuid))
  print(json.dumps(d, indent=2))
  print()


def demo2_3():
  # Get UUID
  client = NutanixRestApiClient(IP, USER, PASSWORD)
  d = client.get_network(name='REST_NETWORK')
  uuid = d['uuid']

  # Update
  d = client.update_network(uuid=uuid, name='REST_NETWORK_UPDATED', vlan='999')
  print(json.dumps(d, indent=2))

  # Check updated entity
  d = client.get_network(uuid=uuid)
  print(json.dumps(d, indent=2))


def demo2_4():
  client = NutanixRestApiClient(IP, USER, PASSWORD)
  networks = client.get_networks()

  for network in networks:
    if network['name'] in ['REST_NETWORK', 'REST_NETWORK_UPDATED']:
      uuid = network['uuid']
      d = client.delete_network(uuid=uuid)
      print(json.dumps(d, indent=2))


def demo3():
  client = NutanixRestApiClient(IP, USER, PASSWORD)
  image_uuid = client.get_image(name='IMG_CENT7_ENG')['uuid']
  network_uuid = client.get_network(name='VLAN-168')['uuid']

  d = client.create_vm_from_image(name='REST_VM1', 
    memory_mb='2048', num_vcpus=2, num_cores=1, 
    image_uuid=image_uuid, network_uuid=network_uuid)
  print(json.dumps(d, indent=2))


def demo4():
  client = NutanixRestApiClient(IP, USER, PASSWORD)
  image_uuid = client.get_image(name='IMG_CENT7_ENG')['uuid']
  network_uuid = client.get_network(name='VLAN-165')['uuid']

  d = client.create_vm_from_image_with_ip(name='REST_VM2', 
    memory_mb='2048', num_vcpus=2, num_cores=1, 
    image_uuid=image_uuid, network_uuid=network_uuid, ip_address='10.149.165.100')
  print(json.dumps(d, indent=2))


###
### MAIN
###

# Environment check
import sys
if sys.version_info.major != 3:
  print('Please run this script on Python 3.')
  exit(-1)

try:
  import requests
except:
  print('Please install package "requests" first.')
  exit(-1)

import socket, json, traceback

# Suppress useless message for insecure https (not certified).
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


class NutanixRestApiClient():

  def __init__(self, ip, user, password):

    # Check IP and Port.
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(2) # seconds
      s.connect((ip, 9440))
      s.shutdown(2)
    except Exception as e:
      raise Exception('Unable to connect Nutanix Cluster "{}". Please check ip and port.'.format(ip))
      
    # Make session
    session = requests.Session()
    session.auth = (user, password)
    session.verify = False                              
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

    # Check credential
    response = session.get('https://{}:9440/api/nutanix/v1/cluster'.format(ip))
    if not response.ok:
      raise Exception('Able to connect, but unable to login. Please check cluster credential.')

    self._session = session
    self._v08_urlbase = 'https://{}:9440/api/nutanix/v0.8'.format(ip)
    self._v1_urlbase = 'https://{}:9440/api/nutanix/v1'.format(ip)
    self._v2_urlbase = 'https://{}:9440/api/nutanix/v2.0'.format(ip)


  # Sample (1) : Get VM info

  def get_cluster_info(self):
    return self._get_v1('/cluster/')
    

  # Sample (2) : CRUD for network

  def create_network(self, name, vlan):
    body_dict = {
      'name' : name,
      'vlan_id' : str(vlan)
    }
    return self._post_v2('/networks/', body_dict)

  def get_networks(self):
    return self._get_v2('/networks/')['entities']

  def get_network(self, name='', uuid=''):
    if not name and not uuid:
      raise Exception('Please provide name or uuid')
    if name and uuid:
      raise Exception('Please provide one of name or uuid. Not both.') 

    if name:
      response_dict = self._get_v2('/networks/')
      for network in response_dict['entities']:
        if name == network['name']:
          return network
      raise Exception("Unable to find network you requested.")
    else:
      try:
        return self._get_v2('/networks/' + uuid)
      except:
        raise Exception("Unable to find network you requested.")

  def update_network(self, uuid, name, vlan):
    body_dict = {
      'name': name,
      "vlan_id": str(vlan)
    }
    return self._put_v2('/networks/{}'.format(uuid), body_dict)

  def delete_network(self, name='', uuid=''):
    if not name and not uuid:
      raise Exception('Please provide name or uuid')
    if name and uuid:
      raise Exception('Please provide one of name or uuid. Not both.') 
    if name:
      network = self.get_network(name=name)
      uuid = network['uuid']

    return self._delete_v2('/networks/' + uuid)


  # Sample (3) : Create simple VM

  def get_image(self, name='', uuid=''):
    if not name and not uuid:
      raise Exception('Please provide name or uuid')
    if name and uuid:
      raise Exception('Please provide one of name or uuid. Not both.') 

    if name:
      response_dict = self._get_v2('/images/')
      for image in response_dict['entities']:
        if image['name'] == name:
          return image
      raise Exception("Unable to find image you requested.")
    else:
      try:
        return self._get_v2('/images/{}'.format(uuid))
      except:
        raise Exception("Unable to find image you requested.")

  def create_vm_from_image(self, name, memory_mb, num_vcpus, num_cores, image_uuid, network_uuid):
    image = self.get_image(uuid=image_uuid)
    vmdisk_uuid = image['vm_disk_id']
    vmdisk_size = image['vm_disk_size']

    body_dict = {
      "name": name,
      "memory_mb": memory_mb,
      "num_vcpus": num_vcpus,
      "description": "",
      "num_cores_per_vcpu": num_cores,
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

    return self._post_v2('/vms/', body_dict)


  # Sample (4) : Create VM with IP

  def create_vm_from_image_with_ip(self, name, memory_mb, num_vcpus, num_cores, image_uuid, network_uuid, ip_address):
    image = self.get_image(uuid=image_uuid)
    vmdisk_uuid = image['vm_disk_id']
    vmdisk_size = image['vm_disk_size']

    body_dict = {
      "name": name,
      "memory_mb": memory_mb,
      "num_vcpus": num_vcpus,
      "description": "",
      "num_cores_per_vcpu": num_cores,
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
          "requested_ip_address": ip_address
        }
      ],
      "affinity": None,
      "vm_features": {
        "AGENT_VM": False
      }
    }

    return self._post_v2('/vms/', body_dict)


  # methods for clean up.

  def create_network_ipam(self, name, vlan, network_address, prefix, gateway, dns):
    body_dict = {
      'name' : name,
      'vlan_id' : str(vlan),
      'ip_config': {
        'dhcp_options': {
          'domain_name_servers': dns,
        },
        'network_address': network_address,
        'prefix_length': str(prefix),
        'default_gateway': gateway,
        "pool": []
      }
    }
    return self._post_v2('/networks/', body_dict)

  def delete_vm(self, name='', uuid=''):
    if not name and not uuid:
      raise Exception('Please provide name or uuid')
    if name and uuid:
      raise Exception('Please provide one of name or uuid. Not both.')

    if name:
      response_dict = self._get_v2('/vms/')
      for vm in response_dict['entities']:
        if vm['name'] == name:
          uuid = vm['uuid']
      if not uuid:
        raise Exception("Unable to find image you requested.")

    try:
      return self._delete_v2('/vms/{}'.format(uuid))
    except:
      raise Exception("Unable to find image you requested.")


  # API V0.8

  def _post_v08(self, url, body_dict):
    if not url.startswith('/'): url = '/' + url
    response = self._session.post(self._v08_urlbase + url, data=json.dumps(body_dict))
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _get_v08(self, url):
    if not url.startswith('/'): url = '/' + url
    response = self._session.get(self._v08_urlbase + url)
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _put_v08(self, url, body_dict):
    if not url.startswith('/'): url = '/' + url
    response = self._session.put(self._v08_urlbase + url, data=json.dumps(body_dict))
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _delete_v08(self, url):
    if not url.startswith('/'): url = '/' + url
    response = self._session.delete(self._v08_urlbase + url)
    if not response.ok:
      raise Exception("Request failed.")
    try:
      return response.json()
    except:
      return {}


  # API V1

  def _post_v1(self, url, body_dict):
    if not url.startswith('/'): url = '/' + url
    response = self._session.post(self._v1_urlbase + url, data=json.dumps(body_dict))
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _get_v1(self, url):
    if not url.startswith('/'): url = '/' + url
    response = self._session.get(self._v1_urlbase + url)
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _put_v1(self, url, body_dict):
    if not url.startswith('/'): url = '/' + url
    response = self._session.put(self._v1_urlbase + url, data=json.dumps(body_dict))
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _delete_v1(self, url):
    if not url.startswith('/'): url = '/' + url
    response = self._session.delete(self._v1_urlbase + url)
    if not response.ok:
      raise Exception("Request failed.")
    try:
      return response.json()
    except:
      return {}


  # API V2

  def _post_v2(self, url, body_dict):
    if not url.startswith('/'): url = '/' + url
    response = self._session.post(self._v2_urlbase + url, data=json.dumps(body_dict))
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _get_v2(self, url):
    if not url.startswith('/'): url = '/' + url
    response = self._session.get(self._v2_urlbase + url)
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _put_v2(self, url, body_dict):
    if not url.startswith('/'): url = '/' + url
    response = self._session.put(self._v2_urlbase + url, data=json.dumps(body_dict))
    if not response.ok:
      raise Exception("Request failed.")
    return response.json()

  def _delete_v2(self, url):
    if not url.startswith('/'): url = '/' + url
    response = self._session.delete(self._v2_urlbase + url)
    if not response.ok:
      raise Exception("Request failed.")
    try:
      return response.json()
    except:
      return {}


def setup():
  client = NutanixRestApiClient(IP, USER, PASSWORD)

  # delete vms on demo3,4
  try:
    client.delete_vm('REST_VM1')
  except:
    pass
  try:
    client.delete_vm('REST_VM2')
  except:
    pass

  # delete networks on demo2
  demo2_4()

  # create network for demo3,4
  try:
    client.get_network(name='VLAN-168')
  except:
    client.create_network(name='VLAN-168', vlan='168')

  try:
    client.get_network(name='VLAN-165')
  except:
    client.create_network_ipam(name='VLAN-165', vlan='165', 
      network_address='10.149.165.0', prefix='24', gateway='10.149.165.1', dns='8.8.8.8')

  # check whether image exist.
  try:
    client.get_image(name='IMG_CENT7_ENG')
  except:
    print('Please upload image "IMG_CENT7_ENG" to do demo3,4')


if __name__ == '__main__':
  main()
