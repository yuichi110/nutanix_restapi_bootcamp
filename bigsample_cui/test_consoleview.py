'''
Test moduel for consoleview.py (framework itself)

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

if __name__ != '__main__':
  print("Please don't import module \"test_consoleview\". It is only for testing.")
  print('Abort.')
  exit(1)

from consoleview import ConsoleView
KEY_ENTER = ConsoleView.KEY_ENTER
KEY_ESC = ConsoleView.KEY_ESC
KEY_TAB = ConsoleView.KEY_TAB
show_text_input_form = ConsoleView.show_text_input_form
autocomplete = ConsoleView.autocomplete

import logging
TEST_LOG_NAME = 'test.log'
TEST_LOG_LEVEL = logging.DEBUG
TEST_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s :%(message)s'

def test_show_text_input_form():
  pass

def test_autocomplete():
  text = 'a'
  candidates = ['abcdef', 'abd', 'abcd']
  new_text = autocomplete(text, candidates, debug=True)


if __name__ == '__main__':
  logging.basicConfig(filename=TEST_LOG_NAME, level=TEST_LOG_LEVEL, format=TEST_LOG_FORMAT)
  test_autocomplete()