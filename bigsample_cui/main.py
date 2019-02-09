'''
Nutanix AHV Image register.
Make image from guest vm vdisk.

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

from consoleview import ConsoleView
KEY_ENTER = ConsoleView.KEY_ENTER
KEY_ESC = ConsoleView.KEY_ESC
KEY_TAB = ConsoleView.KEY_TAB
show_text_input_form = ConsoleView.show_text_input_form
autocomplete = ConsoleView.autocomplete

from nutanix import NutanixRestApiClient

import logging
import traceback
MAIN_LOG_NAME = 'main_console.log'
MAIN_LOG_LEVEL = logging.DEBUG
MAIN_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s :%(message)s'


###
### Custom Exception Class for intended raise.
###

class IntendedException(Exception):
  pass


###
### Initialization functions
###

def init(shared):
  # REST API Logging
  shared.has_rest_log = True
  shared.rest_log_name = 'main_rest.log'
  shared.rest_log_level = logging.INFO

  # For main
  shared.ip = ''
  shared.username = ''
  shared.password = ''
  shared.session = None
  shared.vm_name = ''
  shared.vdisk_label = ''
  shared.target_container = ''
  shared.image_name = ''

  # For both main and thread:poll_task
  shared.task_uuid = ''
  shared.task_percent = 0
  shared.task_status = ''


###
### Utility functions for registered functions
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
### ConsoleView Top UI
###

def showtop(shared, stdscr, warning, logger):
  try:
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

  except Exception as e:
    logger.error('\n' + traceback.format_exc())


###
### Thread functions
### 

def poll_task(shared, logger):
  flag_quit = False
  
  try:
    if shared.session == None:
      raise IntendedException('No Session. Abort.')

    if shared.task_uuid == '':
      raise IntendedException('No Polling Task. Abort.')

    if shared.task_percent == 100:
      raise IntendedException('Task was already completed. Abort.')

    # Check status of current task
    (success, task_dict) = shared.session.get_task_status(shared.task_uuid)
    if not success:
      error_dict = task_dict
      logger.error(error_dict)
      raise IntendedException('Error. Polling task "{}" failed.'.format(shared.task_uuid))

    shared.task_status = task_dict['status']
    shared.task_percent = task_dict['percent']

  except IntendedException as e:
    pass

  except Exception as e:
    logger.error('\n' + traceback.format_exc())

  return flag_quit


###
### Key input functions
### 

def show_input_ip(shared, stdscr, logger):
  logger.debug('show_input_ip:start')

  error = ''
  try:
    def validate_format(text):
      if text == '':
        return True

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
      (key, index, text) = show_text_input_form(stdscr, deco_list, 1, 0, ip, index, warning)

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

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'

  logger.debug('show_input_ip:end')
  return error


def show_input_username(shared, stdscr, logger):
  logger.debug('show_input_username:start')

  error = ''
  try:
    def validate_format(text):
      if text == '':
        return True

      for c in text:
        keycode = ord(c)
        if not (keycode >= 32 and keycode <= 126):
          return False
      return True
    
    deco_list = [
      (0, 0, 'Please input cluster user name.')
    ]

    username = shared.username
    index = len(username)
    warning = ''

    while True:
      (key, index, text) = show_text_input_form(stdscr, deco_list, 1, 0, username, index, warning)
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

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'

  logger.debug('show_input_username:end')
  return error


def show_input_password(shared, stdscr, logger):
  logger.debug('show_input_password:start')

  error = ''
  try:
    def validate_format(text):
      if text == '':
        return True

      for c in text:
        keycode = ord(c)
        if not (keycode >= 32 and keycode <= 126):
          return False
      return True
    
    deco_list = [
      (0, 0, 'Please input cluster password.')
    ]

    password = shared.password
    index = len(password)
    warning = ''

    while True:
      (key, index, text) = show_text_input_form(stdscr, deco_list, 1, 0, password, index, warning)
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

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'

  logger.debug('show_input_password:end')
  return error


def try_login(shared, stdscr, logger):
  logger.debug('try_login:start')

  error = ''
  try:
    if not shared.ip:
      raise IntendedException('Unable to try login without IP.')

    if not shared.username:
      raise IntendedException('Unable to try login without username.')

    if not shared.password:
      raise IntendedException('Unable to try login without password.')

    if shared.has_rest_log:
      logger = NutanixRestApiClient.create_logger(shared.rest_log_name, shared.rest_log_level)
      shared.session = NutanixRestApiClient(shared.ip, shared.username, shared.password, logger)
    else:
      shared.session = NutanixRestApiClient(shared.ip, shared.username, shared.password)

  except IntendedException as e:
    error = str(e)
    shared.session = None

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens on login.'
    shared.session = None

  logger.debug('try_login:end')
  return error


def show_input_vm_name(shared, stdscr, logger):
  logger.debug('show_input_vm_name:start')

  error = ''
  try:
    if shared.session is None:
      raise IntendedException('Please login first.')

    (success, vms) = shared.session.get_vm_names()
    if not success:
      error_dict = vms
      logger.error(drror_dict)
      raise IntendedException(error_dict['error'])

    def validate_format(text):
      if text == '':
        return True
      return text in vms

    # Auto complete at first
    text = autocomplete(shared.vm_name, vms)
    index = len(text)
    warning = ''

    while True:
      filtered_vms = list(filter(lambda x: x.startswith(text), vms))
      deco_list = [
        (0, 0, 'Please input vm name.'),
        (4, 0, str(filtered_vms))
      ]

      (key, index, text) = show_text_input_form(stdscr, deco_list, 1, 0, text, index, warning)

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
  
  except IntendedException as e:
    error = str(e)

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'
 
  logger.debug('show_input_vm_name:end')
  return error


def show_input_vdisk_label(shared, stdscr, logger):
  logger.debug('show_input_vdisk_label:start')

  error = ''
  try:
    if shared.vm_name == '':
      raise IntendedException('Please input vm name first.')

    (success, labels) = shared.session.get_vm_disks(shared.vm_name)
    if not success:
      raise IntendedException('API Failed at getting vdisk labels on vm="{}".'.format(shared.vm_name))

    def validate_format(text):
      if text == '':
        return True
      return text in labels

    # Auto complete at first
    text = autocomplete(shared.vdisk_label, labels)
    index = len(text)
    warning = ''

    while True:
      filtered_vdisks = list(filter(lambda x: x.startswith(text), labels))
      deco_list = [
        (0, 0, 'Please input vdisk label.'),
        (4, 0, str(filtered_vdisks))
      ]   

      (key, index, text) = show_text_input_form(stdscr, deco_list, 1, 0, text, index, warning)

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

  except IntendedException as e:
    error = str(e)

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'      

  logger.debug('show_input_vdisk_label:end')
  return error


def show_input_target_container(shared, stdscr, logger):
  logger.debug('show_input_target_container() : start')

  error = ''
  try:
    if shared.session is None:
      raise IntendedException('Please login first.')

    (success, containers) = shared.session.get_container_names()
    if not success:
      raise IntendedException('API failed. Please try login again.')

    def validate_format(text):
      if text == '':
        # initialize
        return True
      return text in containers

    # Auto complete at first
    text = autocomplete(shared.target_container, containers)
    index = len(text)
    warning = ''

    while True:
      filtered_containers = list(filter(lambda x: x.startswith(text), containers))
      deco_list = [
        (0, 0, 'Please input target container name.'),
        (4, 0, str(filtered_containers))
      ]   

      (key, index, text) = show_text_input_form(stdscr, deco_list, 1, 0, text, index, warning)

      if key == KEY_ESC:
        break
      elif key == KEY_ENTER:
        if validate_format(text):
          shared.target_container = text
          shared.clear_task(shared)
          break
        else:
          warning = 'Not good'
      elif key == KEY_TAB:
        text = autocomplete(text, containers)
        index = len(text)

  except IntendedException as e:
    error = str(e)

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'      

  logger.debug('show_input_target_container() : end')
  return error


def show_input_image_name(shared, stdscr, logger):
  logger.debug('show_input_target_container() : start')

  error = ''
  try:
    if shared.session is None:
      raise IntendedException('Please login first.')

    (success, image_names) = shared.session.get_image_names()
    if not success:
      raise IntendedException('API failed. Please try login again.')

    def validate_format(text):
      if text == '':
        # initialize
        return True
      # don't allow same name
      return text  not in image_names

    text = shared.image_name
    index = len(text)
    warning = ''

    deco_list = [
      (0, 0, 'Please input image name.'),
    ]
    while True:
      (key, index, text) = show_text_input_form(stdscr, deco_list, 1, 0, text, index, warning)

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

  except IntendedException as e:
    error = str(e)

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'      

  logger.debug('show_input_target_container() : end')
  return error


def create_image(shared, stdscr, logger):
  logger.debug('show_input_target_container() : start')

  error = ''
  try:
    if shared.session is None:
      raise IntendedException('Please login first.')
    if shared.vm_name == '':
      raise IntendedException('Please input source vm name first.')
    if shared.vdisk_label == '':
      raise IntendedException('Please input vdisk label first.')
    if shared.target_container == '':
      raise IntendedException('Please input target container name first.')
    if shared.image_name == '':
      raise IntendedException('Please input image name first.')

    (success, task_uuid) = shared.session.create_image_from_vm_vdisk(
      shared.vm_name, shared.vdisk_label, shared.target_container, shared.image_name)
    if not success:
      error_dict = task_uuid
      logger.error(error_dict)
      raise IntendedException('Image creation failed.')

    (success, task_dict) = shared.session.get_task_status(task_uuid)
    if not success:
      error_dict = task_uuid
      logger.error(error_dict)
      raise IntendedException('Failed to get task status.')

    shared.task_uuid = task_dict['uuid']
    shared.task_status = task_dict['status']
    shared.task_percent = task_dict['percent']

  except IntendedException as e:
    error = str(e)

  except Exception as e:
    logger.error('\n' + traceback.format_exc())
    error = 'Unexpected error happens.'      

  logger.debug('show_input_target_container() : end')
  return error


###
### START
###

if __name__ == '__main__':
  logger = ConsoleView.create_logger(MAIN_LOG_NAME, MAIN_LOG_LEVEL, MAIN_LOG_FORMAT)
  view = ConsoleView(logger)

  # init
  view.add_fun_init(init)

  # util
  view.add_fun_util('clear_session', clear_session)
  view.add_fun_util('clear_task', clear_task)

  # thread
  view.add_fun_thread(poll_task, 1)

  # showtop
  view.add_fun_showtop(showtop)

  # key
  view.add_fun_keycalled('1', show_input_ip)
  view.add_fun_keycalled('2', show_input_username)
  view.add_fun_keycalled('3', show_input_password)
  view.add_fun_keycalled('4', try_login)
  view.add_fun_keycalled('5', show_input_vm_name)
  view.add_fun_keycalled('6', show_input_vdisk_label)
  view.add_fun_keycalled('7', show_input_target_container)
  view.add_fun_keycalled('8', show_input_image_name)
  view.add_fun_keycalled('9', create_image)

  # start
  view.start()