from nutanix import NutanixRestApiClient
import time
import logging

###
### Please update param.
###

class NET_Main:

  @classmethod
  def setup(cls, session, ip):
    if not Utility.is_ip_ok(ip, [10], [149], range(0, 127), range(0, 256)):
      raise Exception('Error: Wrong IP')
    
    cls.setup_container(session)
    cls.setup_image(session)
    cls.setup_network(session, ip)

  @classmethod
  def setup_container(cls, session):
    containers = [
      'container', 
      'NutanixManagementShare',
    ]
    Utility.setup_container(session, containers)

  @classmethod
  def setup_image(cls, session):
    target_container = 'container'
    images = [
      # Name, Url
      ('virtio_1.1.3',        'nfs://10.149.245.50/Public/labtool/iso/virtio_1.1.3.iso'),

      ('iso-cent6-min',       'nfs://10.149.245.50/Public/labtool/iso/centos6_min.iso'),
      ('iso-cent7-min',       'nfs://10.149.245.50/Public/labtool/iso/centos7_min.iso'),
      ('iso-win2012r2-eng',   'nfs://10.149.245.50/Public/labtool/iso/winserv2012r2_eng.iso'),

      ('img-foundation4.3.1', 'nfs://10.149.245.50/Public/labtool/foundationvm/Foundation_VM-4.3.1-disk-0.qcow2'),
      ('img-centos7-eng',     'nfs://10.149.245.50/Public/labtool/image/centos7_eng_raw'),
    ]
    Utility.setup_image(session, images, target_container)

  @classmethod
  def setup_network(cls, session, ip):
    third = int(ip.split('.')[2])

    dhcp_from = '10.149.{}.50'.format(third)
    dhcp_to = '10.149.{}.199'.format(third)
    pool = [(dhcp_from, dhcp_to)]
    networks = [
      # Name, VLAN, NETWORK, PREFIX, GATEWAY, POOL, DNS
      ('NET-10.149', 0, '10.149.0.0', 17, '10.149.0.1', pool, '8.8.8.8'),
    ]
    Utility.setup_network(session, networks)


class NET_Training:

  @classmethod
  def setup(cls, session, ip):
    if not Utility.is_ip_ok(ip, [10], [149], range(160, 165), range(0, 256)):
      raise Exception('Error: Wrong IP')
    
    cls.setup_container(session)
    cls.setup_image(session)
    cls.setup_network(session, ip)

  @classmethod
  def setup_container(cls, session):
    containers = [
      'container', 
      'NutanixManagementShare',
    ]
    Utility.setup_container(session, containers)

  @classmethod
  def setup_image(cls, session):
    target_container = 'container'
    images = [
      # Name, Url
      ('ISO_CENT7_MIN',     'nfs://10.149.245.50/Public/bootcamp/centos7_min.iso'),
      ('IMG_CENT7_JPN', 'nfs://10.149.245.50/Public/bootcamp/centos7_jpn_raw'),
      ('IMG_CENT7_ENG', 'nfs://10.149.245.50/Public/bootcamp/centos7_eng_raw'),
    ]
    Utility.setup_image(session, images, target_container)

  @classmethod
  def setup_network(cls, session, ip):
    third = int(ip.split('.')[2])

    networks = [
      # Name, VLAN, 
      ('TEST-168', 168),
    ]
    Utility.setup_network(session, networks)

###
### Private
###

class Utility:

  @staticmethod
  def is_ip_ok(ip, first, second, third, forth):
    words = ip.split('.')
    for (index, octet) in enumerate([first, second, third, forth]):
      if int(words[index]) not in octet:
        return False
    return True

  @staticmethod
  def setup_container(session, containers):
    print(' - container')

    # get existing containers
    (success, existing_containers) = session.get_container_names()
    if not success:
      raise Exception('Error happens on getting existing container names.')
    print('   Existing containers "{}"'.format(existing_containers))

    # delete useless containers
    for existing_container in existing_containers:
      if existing_container in containers:
        continue
      (success, container_info) = session.get_container_info(existing_container)
      if not success:
        raise Exception('Error happens on getting container info "{}".'.format(existing_container))
      if container_info['usage'] != '0':
        continue
      print('   Deleting useless container "{}"'.format(existing_container))
      (success, _) = session.delete_container(existing_container)
      if not success:
        raise Exception('Error happens on deleting container "{}".'.format(existing_container))  

    # create containers which doesn't exist.
    task_list = []
    for container in containers:
      if container in existing_containers:
        continue
      print('   Creating container "{}"'.format(container))
      (success, taskuuid) = session.create_container(container)
      if not success:
        raise Exception('Error happens on creating container "{}".'.format(container))
      task_list.append(taskuuid)

    # wait till end
    Utility.wait_tasks(session, task_list)


  @staticmethod
  def setup_image(session, images, container):
    print(' - image')

    # check whether container exist or not
    (success, containers) = session.get_container_names()
    if not success:
      raise Exception('Error happens on checking container existance.')
    if container not in containers:
      raise Exception("Upload target container doesn't exist. Abort.")

    # get existing images
    (success, existing_images) = session.get_image_names()
    if not success:
      raise Exception('Error happens on getting existing images names.')
    print('   Existing images "{}"'.format(existing_images))

    # upload images which doesn't exist
    task_list = []
    for (image_name, image_url) in images:
      if image_name in existing_images:
        continue
      print('   Request uploading {} : {}'.format(image_name, image_url))
      (success, taskuuid) = session.upload_image(image_url, container, image_name)
      if not success:
        raise Exception('Error happens on uploading image.')
      task_list.append(taskuuid)

    # wait till end
    Utility.wait_tasks(session, task_list)


  @staticmethod
  def setup_network(session, networks):
    print(' - network')
    (success, existing_networks) = session.get_network_names()
    if not success:
      raise Exception('Error happens on getting existing networks.')

    network_names = []
    for network in networks:
      network_names.append(network[0])

    # delete useless network
    for existing_network in existing_networks:
      if existing_network in network_names:
        continue
      (success, used) = session.is_network_used(existing_network)
      if not success:
        raise Exception('Error happens on getting existing networks.')
      if used:
        continue

      print('   Deleting useless network "{}"'.format(existing_network))
      (success, taskuuid) = session.delete_network(existing_network)
      if not success:
        raise Exception('Error happens on getting existing networks.')

    # Hypervisor
    (success, hypervisor) = session.get_hypervisor()
    if not success:
      raise Exception('Error happens on getting hypervisor.')

    # add new network
    task_list = []
    for network in networks:
      name = network[0]
      if name in existing_networks:
        continue

      print('   Creating network "{}"'.format(name))
      if len(network) == 2:
        (name, vlan) = network
        (success, taskuuid) = session.create_network(name, vlan)
        if not success:
          raise Exception('Error happens on creating network "{}"'.format(name))
      else:
        (ip, vlan, network, prefix, gateway, pool, dns) = network
        if hypervisor != 'AHV':
          (success, taskuuid) = session.create_network(name, vlan)
          if not success:
            raise Exception('Error happens on creating network "{}"'.format(name))
        else:
          (success, taskuuid) = session.create_network_managed(name, vlan, network, prefix, gateway, pool, dns)
          if not success:
            raise Exception('Error happens on creating network "{}"'.format(name))

      task_list.append(taskuuid)

    # wait till end
    Utility.wait_tasks(session, task_list)

  @staticmethod
  def wait_tasks(session, uuids, interval=5):
    first = True
    while(True):
      (success, tasks) = session.get_tasks_status()
      if not success:
        print(tasks)
        continue
        #raise Exception('Error happens on getting tasks status.')

      finished = True
      for task in tasks:
        if task['uuid'] in uuids:
          if first:
            print('Wait till all tasks end. Polling interval {}s.'.format(interval))
            first = False
          print('{} {}% : {}'.format(task['method'], task['percent'], task['uuid']))
          finished = False
        else:
          # Child or other task
          pass

      if finished:
        break
      else:
        print('--')
      time.sleep(interval)

    if not first:
      print('All tasks end.')



if __name__ == '__main__':
  import sys
  if len(sys.argv) != 5:
    print('Syntax: python setup_cluster.py <IP ADDRESS> <USER> <PASSWORD> <CLASS>')
    exit(-1)
  CLUSTER_IP = sys.argv[1]
  CLUSTER_USER = sys.argv[2]
  CLUSTER_PASSWORD = sys.argv[3]
  SETUP_CLASS = sys.argv[4].lower()
  
  if SETUP_CLASS not in ['main', 'training']:
    print('Supported Class: main')
    exit(-1)

  logger = NutanixRestApiClient.create_logger('setup_cluster_rest.log', logging.DEBUG)
  session = NutanixRestApiClient(CLUSTER_IP, CLUSTER_USER, CLUSTER_PASSWORD, logger)
  print('setup start')
  if 'main' == SETUP_CLASS: 
    NET_Main.setup(session, CLUSTER_IP)
  elif 'training' == SETUP_CLASS:
    NET_Training.setup(session, CLUSTER_IP)
  else:
    print('Class "{}" is not supported.'.format(SETUP_CLASS))
    exit(-1)
  print('setup end')
