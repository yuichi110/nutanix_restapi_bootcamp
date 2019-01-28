'''
Test moduel for main.py (ahv image create)

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

from consoleview import *
from main import *

TEST_LOG_NAME = 'test.log'
TEST_LOG_LEVEL = logging.DEBUG
TEST_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s :%(message)s'

def test_input_ip():
  view = ConsoleView(LOG_NAME, LOG_LEVEL, LOG_FORMAT)
  view.add_init(init)
  view.add_utilfun('clear_session', clear_session)
  view.add_utilfun('clear_task', clear_task)
  view.add_thread_fun(poll_task, 1)
  view.add_showtop(showtop)
  view.add_keyfun('1', show_ip_input)

  shared = view._test_get_shared()
  view._test_call_keyfun('1')
  logging.debug('Value: {}'.format(shared.ip))

if __name__ == '__main__':
  test_input_ip()

