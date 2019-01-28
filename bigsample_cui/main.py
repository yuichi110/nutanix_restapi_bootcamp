'''
Nutanix AHV Image register.
Make image from guest vm vdisk.

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

from consoleview import ConsoleView, showTextInputForm, autocomplete
from consoleview import KEY_ENTER, KEY_ESC, KEY_TAB
from nutanix import NutanixRestApiClient
import logging

MAIN_LOG_NAME = 'main.log'
MAIN_LOG_LEVEL = logging.INFO
MAIN_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s :%(message)s'

###
### INIT
###

def init(shared):
  shared.ip = ''
  shared.username = ''
  shared.password = ''
  shared.session = None
  shared.vm_name = ''
  shared.vdisk_label = ''
  shared.target_container = ''
  shared.image_name = ''

  # For Main and Thread
  shared.task_uuid = ''
  shared.task_percent = 0
  shared.task_status = ''


###
### UTILITY
###


def clear_session(shared):
  shared.session = None
  shared.vm_name = ''
  shared.vdisk_label = ''
  shared.target_container = ''
  shared.image_name = ''
  shared.task_uuid = ''
  shared.task_percent = 0
  shared.task_status = ''


def clear_task(shared):
  shared.task_uuid = ''
  shared.task_percent = 0
  shared.task_status = ''


###
### SHOW TOP
###


def showtop(shared, stdscr, warning):
  stdscr.addstr(0, 0, '1. Cluster IP       : {}'.format(shared.ip))
  stdscr.addstr(1, 0, '2. Cluster Username : {}'.format(shared.username))
  hidden_password = '*' * len(shared.password)
  stdscr.addstr(2, 0, '3. Cluster Password : {}'.format(hidden_password))

  if shared.session is not None:
    login_status = 'Login'
  else:
    allok = True
    if shared.ip == '':
      allok = False
    if shared.username == '':
      allok = False
    if shared.password == '':
      allok = False
    if allok:
      login_status = 'Not Login. Try.'
    else:
      login_status = 'Not Login. Please fill 1-3 first.'
  stdscr.addstr(3, 0, '4. Login Status     : {}'.format(login_status))

  stdscr.addstr(4, 0, '5. VM name          : {}'.format(shared.vm_name))
  stdscr.addstr(5, 0, '6. vDisk location   : {}'.format(shared.vdisk_label))

  stdscr.addstr(6, 0, '7. Target Container : {}'.format(shared.target_container))
  stdscr.addstr(7, 0, '8. Image name       : {}'.format(shared.image_name))

  if shared.task_status == '':
    task_text = ''
  else:
    task_text = '{}, Progress {}%'.format(shared.task_status, shared.task_percent)
  stdscr.addstr(8, 0, '9. Create image     : {}'.format(task_text))

  stdscr.addstr(10, 0, '1-9 : choose action')
  stdscr.addstr(11, 0, 'Esc : Quit')

  if warning != '':
    stdscr.addstr(12, 0, 'Warning: {}'.format(warning))


###
### THREAD FUNCTIONS
### 


def poll_task(shared):
  flag_quit = False
  
  if shared.session == None:
    return flag_quit
  if shared.task_uuid == '':
    return flag_quit
  if shared.task_percent == 100:
    return flag_quit

  (success, retd) = shared.session.get_task_status(shared.task_uuid)
  if not success:
    return flag_quit

  shared.task_status = retd['status']
  shared.task_percent = retd['percent']
  return flag_quit


###
### KEY INPUT FUNCTIONS
### 


def show_input_ip(shared, stdscr):
  logging.debug('show_ip_input:start')

  def validate_format(text):
    try:
      words = text.split('.')
      if len(words) != 4:
        return False
      for word in words:
        v = int(word)
        if v < 0:
          return False
        if v > 255:
          return False
    except:
      return False
    return True

  deco_list = [
    (0, 0, 'Please input cluster ip address.')
  ]
  ip = shared.ip
  index = len(ip)
  warning = ''

  while True:
    logging.debug('  call showTextInputForm')
    (key, index, text) = showTextInputForm(stdscr, deco_list, 1, 0, ip, index, warning)
    logging.debug('  key={}'.format(key))

    if key == KEY_ESC:
      break
    elif key == KEY_ENTER:
      if validate_format(text):
        shared.ip = text
        shared.clear_session(shared)
        break
      else:
        ip = text
    elif key == KEY_TAB:
      # ignore
      pass

  logging.debug('show_ip_input:end')
  return ''


def show_input_username(shared, stdscr):
  def validate_format(text):
    for c in text:
      keycode = ord(c)
      if not (keycode >= 32 and keycode <= 126):
        return False
    return True
  
  print('input_username')
  deco_list = [
    (0, 0, 'Please input cluster user name.')
  ]
  username = shared.username
  index = len(username)
  warning = ''

  while True:
    (key, index, text) = showTextInputForm(stdscr, deco_list, 1, 0, username, index, warning)
    if key == KEY_ESC:
      break
    elif key == KEY_ENTER:
      if validate_format(text):
        shared.username = text
        shared.clear_session(shared)
        break
      else:
        ip = text
    elif key == KEY_TAB:
      # ignore
      pass

  return ''


def show_input_password(shared, stdscr):
  def validate_format(text):
    for c in text:
      keycode = ord(c)
      if not (keycode >= 32 and keycode <= 126):
        return False
    return True
  
  print('input_password')
  deco_list = [
    (0, 0, 'Please input cluster password.')
  ]
  password = shared.password
  index = len(password)
  warning = ''

  while True:
    (key, index, text) = showTextInputForm(stdscr, deco_list, 1, 0, password, index, warning)
    if key == KEY_ESC:
      break
    elif key == KEY_ENTER:
      if validate_format(text):
        shared.password = text
        shared.clear_session(shared)
        break
      else:
        ip = text
    elif key == KEY_TAB:
      # ignore
      pass

  return ''


def try_login(shared, stdscr):
  try:
    if not shared.ip:
      return 'Unable to try login without IP.'
    if not shared.username:
      return 'Unable to try login without username.'
    if not shared.password:
      return 'Unable to try login without password.'

    shared.session = NutanixRestApiClient(shared.ip, shared.username, shared.password)

  except Exception as e:
    shared.session = None
    return 'Error happens. Please check log.'

  return ''


def show_input_vm_name(shared, stdscr):
  if shared.session is None:
    return 'Please login first.'

  (success, vms) = shared.session.get_vm_names()
  if not success:
    return 'API failed. Please try login again.'

  def validate_format(text):
    if text == '':
      # initialize
      return True

    return text in vms

  print('input_vm_name')
  text = shared.vm_name
  index = len(text)
  warning = ''

  while True:
    filtered_vms = list(filter(lambda x: x.startswith(text), vms))
    deco_list = [
      (0, 0, 'Please input vm name.'),
      (4, 0, str(filtered_vms))
    ]

    (key, index, text) = showTextInputForm(stdscr, deco_list, 1, 0, text, index, warning)

    if key == KEY_ESC:
      break
    elif key == KEY_ENTER:
      if validate_format(text):
        shared.vm_name = text
        shared.vdisk_label = ''
        shared.clear_task(shared)
        break
      else:
        warning = 'Not good'
    elif key == KEY_TAB:
      text = autocomplete(text, vms)
      index = len(text)
 
  return ''


def show_input_vdisk_label(shared, stdscr):
  if shared.vm_name == '':
    return 'Please input vm name first.'

  (success, labels) = shared.session.get_vm_disks(shared.vm_name)
  if not success:
    return 'API failed. Please try login again.'

  def validate_format(text):
    if text == '':
      # initialize
      return True
    return text in labels

  print('input_vdisk_label')
  text = shared.vdisk_label
  index = len(text)
  warning = ''

  while True:
    filtered_vdisks = list(filter(lambda x: x.startswith(text), labels))
    deco_list = [
      (0, 0, 'Please input vdisk label.'),
      (4, 0, str(filtered_vdisks))
    ]   

    (key, index, text) = showTextInputForm(stdscr, deco_list, 1, 0, text, index, warning)

    if key == KEY_ESC:
      break
    elif key == KEY_ENTER:
      if validate_format(text):
        shared.vdisk_label = text
        shared.clear_task(shared)
        break
      else:
        warning = 'Not good'
    elif key == KEY_TAB:
      text = autocomplete(text, labels)
      index = len(text)      

  return ''


def show_input_target_container(shared, stdscr):
  if shared.session is None:
    return 'Please login first.'

  (success, containers) = shared.session.get_container_names()
  if not success:
    return 'API failed. Please try login again.'

  def validate_format(text):
    if text == '':
      # initialize
      return True
    return text in containers

  print('input_target_container')
  text = shared.target_container
  index = len(text)
  warning = ''

  while True:
    filtered_containers = list(filter(lambda x: x.startswith(text), containers))
    deco_list = [
      (0, 0, 'Please input target container name.'),
      (4, 0, str(filtered_containers))
    ]   

    (key, index, text) = showTextInputForm(stdscr, deco_list, 1, 0, text, index, warning)

    if key == KEY_ESC:
      break
    elif key == KEY_ENTER:
      if validate_format(text):
        shared.target_container = text
        shared.clear_task()
        break
      else:
        warning = 'Not good'
    elif key == KEY_TAB:
      text = autocomplete(text, containers)
      index = len(text)

  return ''


def show_input_image_name(shared, stdscr):
  if shared.session is None:
    return 'Please login first.'

  (success, image_names) = shared.session.get_image_names()
  if not success:
    return 'API failed. Please try login again.'

  def validate_format(text):
    if text == '':
      # initialize
      return True
    # don't allow same name
    return text  not in image_names

  print('input_image_name')
  text = shared.image_name
  index = len(text)
  warning = ''

  deco_list = [
    (0, 0, 'Please input image name.'),
  ]
  while True:
    (key, index, text) = showTextInputForm(stdscr, deco_list, 1, 0, text, index, warning)

    if key == KEY_ESC:
      break
    elif key == KEY_ENTER:
      if validate_format(text):
        shared.image_name = text
        shared.clear_task(shared)
        break
      else:
        warning = 'Not good'
    elif key == KEY_TAB:
      pass

  return ''


def create_image(shared, stdscr):
  if shared.session is None:
    return 'Please login first.'
  if shared.vm_name == '':
    return 'Please input source vm name first.'
  if shared.vdisk_label == '':
    return 'Please input vdisk label first.'
  if shared.target_container == '':
    return 'Please input target container name first.'
  if shared.image_name == '':
    return 'Please input image name first.'

  (success, task_uuid) = shared.session.create_image(
    shared.vm_name, shared.vdisk_label, shared.target_container, shared.image_name)
  if not success:
    return 'Image creation failed.'

  (success, task_dict) = shared.session.get_task_status(task_uuid)
  if not success:
    return 'Failed to get task status.'

  shared.task_uuid = task_dict['uuid']
  shared.task_status = task_dict['status']
  shared.task_percent = task_dict['percent']
  return ''


###
### START
###

if __name__ == '__main__':
  view = ConsoleView(MAIN_LOG_NAME, MAIN_LOG_LEVEL, MAIN_LOG_FORMAT)
  view.add_init(init)
  view.add_utilfun('clear_session', clear_session)
  view.add_utilfun('clear_task', clear_task)
  view.add_thread_fun(poll_task, 1)
  view.add_showtop(showtop)

  view.add_keyfun('1', show_input_ip)
  view.add_keyfun('2', show_input_username)
  view.add_keyfun('3', show_input_password)
  view.add_keyfun('4', try_login)
  view.add_keyfun('5', show_input_vm_name)
  view.add_keyfun('6', show_input_vdisk_label)
  view.add_keyfun('7', show_input_target_container)
  view.add_keyfun('8', show_input_image_name)
  view.add_keyfun('9', create_image)

  view.start()