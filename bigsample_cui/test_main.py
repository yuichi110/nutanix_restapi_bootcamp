'''
Test moduel for main.py (ahv image create)

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

if __name__ != '__main__':
  print("Please don't import module \"test_main\". It is only for testing.")
  print('Abort.')
  exit(1)

from consoleview import *
from main import *

import logging
TEST_LOG_NAME = 'test.log'
TEST_LOG_LEVEL = logging.DEBUG
TEST_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s :%(message)s'
LOGGER = ConsoleView.create_logger(TEST_LOG_NAME, TEST_LOG_LEVEL, TEST_LOG_FORMAT)


TEST_IP = '10.149.27.41'
TEST_USER = 'admin'
TEST_PASSWORD = 'Nutanix/4u!'


###
### Test utility
###

def get_initialized_view():
  view = ConsoleView(LOGGER)
  view.add_fun_init(init)
  view.add_fun_util('clear_session', clear_session)
  view.add_fun_util('clear_task', clear_task)
  view.add_fun_thread(poll_task, 1)
  view.add_fun_showtop(showtop)
  view.add_fun_keycalled('1', show_input_ip)
  view.add_fun_keycalled('2', show_input_username)
  view.add_fun_keycalled('3', show_input_password)
  view.add_fun_keycalled('4', try_login)
  view.add_fun_keycalled('5', show_input_vm_name)
  view.add_fun_keycalled('6', show_input_vdisk_label)
  view.add_fun_keycalled('7', show_input_target_container)
  view.add_fun_keycalled('8', show_input_image_name)
  view.add_fun_keycalled('9', create_image)
  return view


def get_logined_view():
  view = get_initialized_view()
  shared = view.test_get_shared()
  shared.ip = TEST_IP
  shared.username = TEST_USER
  shared.password = TEST_PASSWORD

  # Do Login
  warning = view.test_call_keyfun('4')
  if shared.session == None:
    raise Exception('Login failed.')
  return view


def logging_result(warning, shared):
  LOGGER.debug('\n=== Warning ===\n{}\n==============='.format(warning))
  LOGGER.debug('\n==== Shared ====\n{}================'.format(shared))


###
### Tests
###

def test_show_input_ip():
  view = get_initialized_view()
  LOGGER.debug('test_show_input_ip() : start')

  shared = view.test_get_shared()
  warning = view.test_call_keyfun('1')
  logging_result(warning, shared)

  LOGGER.debug('test_show_input_ip() : end')


def test_show_input_username():
  view = get_initialized_view()
  LOGGER.debug('test_show_input_username() : start')

  shared = view.test_get_shared()
  warning = view.test_call_keyfun('2')
  logging_result(warning, shared)

  LOGGER.debug('test_show_input_username() : end')


def test_show_input_password():
  view = get_initialized_view()
  LOGGER.debug('test_show_input_password() : start')

  shared = view.test_get_shared()
  warning = view.test_call_keyfun('3')
  logging_result(warning, shared)

  LOGGER.debug('test_show_input_password() : end')


def test_try_login():
  # TEST PARAMS
  IP = TEST_IP
  USER = TEST_USER
  PASSWORD = TEST_PASSWORD

  view = get_initialized_view()
  LOGGER.debug('test_try_login() : start')

  shared = view.test_get_shared()
  shared.ip = IP
  shared.username = USER
  shared.password = PASSWORD
  warning = view.test_call_keyfun('4')
  logging_result(warning, shared)

  LOGGER.debug('test_try_login() : end')


def test_show_input_vm_name():
  view = get_logined_view()
  LOGGER.debug('test_show_input_vm_name() : start')

  shared = view.test_get_shared()
  warning = view.test_call_keyfun('5')
  logging_result(warning, shared)

  LOGGER.debug('test_show_input_vm_name() : end')


def test_show_input_vdisk_label():
  # TEST PARAMS
  VM_NAME = 'rest_test'

  view = get_logined_view()
  LOGGER.debug('test_show_input_vdisk_label() : start')

  shared = view.test_get_shared()
  shared.vm_name = VM_NAME
  warning = view.test_call_keyfun('6')
  logging_result(warning, shared)

  LOGGER.debug('test_show_input_vdisk_label() : end')


def test_show_input_target_container():
  view = get_logined_view()
  LOGGER.debug('test_show_input_target_container() : start')

  shared = view.test_get_shared()
  warning = view.test_call_keyfun('7')
  logging_result(warning, shared)

  LOGGER.debug('test_show_input_target_container() : end')


def test_show_input_image_name():
  view = get_logined_view()
  LOGGER.debug('test_show_input_image_name() : start')

  shared = view.test_get_shared()
  warning = view.test_call_keyfun('8')
  logging_result(warning, shared)

  LOGGER.debug('test_show_input_image_name() : end')


def test_create_image():
  # TEST PARAMS
  VM_NAME = 'rest_test'
  VDISK_LABEL = 'scsi.0'
  TARGET_CONTAINER = 'container'
  IMAGE_NAME = 'REST_TEST_IMAGE'

  view = get_logined_view()
  LOGGER.debug('test_create_image() : start')

  shared = view.test_get_shared()
  shared.vm_name = VM_NAME
  shared.vdisk_label = VDISK_LABEL
  shared.target_container = TARGET_CONTAINER
  shared.image_name = IMAGE_NAME
  warning = view.test_call_keyfun('9')
  logging_result(warning, shared)

  LOGGER.debug('test_create_image() : end')


if __name__ == '__main__':
  print('Test start')
  #test_show_input_ip()
  #test_show_input_username()
  #test_show_input_password()
  test_try_login()

  #test_show_input_vm_name()
  #test_show_input_vdisk_label()
  #test_show_input_target_container()
  #test_show_input_image_name()
  #test_create_image()
  print('Test end')