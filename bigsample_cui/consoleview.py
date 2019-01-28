'''
Framework for making Curses based UI.

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

import curses
import logging
import time
import threading
import traceback
import os
os.environ.setdefault('ESCDELAY', '25')

KEY_ENTER = 'CV_KEY_ENTER'
KEY_ESC = 'CV_KEY_ESC'
KEY_TAB = 'CV_KEY_TAB'

class ConsoleView:
  def __init__(self, logfile, level=logging.INFO, formatter='%(message)s'):
    logging.basicConfig(filename=logfile, level=level, format=formatter)

    class Shared:
      def __str__(self):
        text = ''
        for (key, value) in vars(self).items():
          text += '{} : {}\n'.format(key, value)
        return text

    self.shared = Shared()
    self.inits = []
    self.showtop = None
    self.keymap = {}
    self.thread_funs = []
    self.thread_list = []
    self.going_to_exit = False

    self.did_setup = False
    self.stdscr = curses.initscr()

  def add_init(self, fun):
    self.inits.append(fun)

  def add_utilfun(self, name, fun):
    setattr(self.shared, name, fun)

  def add_showtop(self, fun):
    self.showtop = fun

  def add_keyfun(self, key, fun):
    self.keymap[key] = fun

  def add_thread_fun(self, fun, interval):
    self.thread_funs.append((fun, interval))

  def _test_get_shared(self):
    return self.shared

  def _test_call_keyfun(self, key):
    if not self.did_setup:
      self._setup()

    if key not in self.keymap:
      raise Exception('key "{}" is not added yet.'.format(key))
    self.keymap[key](self.shared, self.stdscr)

    self.going_to_exit = True
    for worker in self.thread_list:
      worker.join()

  def _setup(self):
    self.did_setup = True

    # Private Thread Worker Class
    class Worker(threading.Thread):
      def __init__(self, caller, shared, fun, interval, *args, **kwargs):
        self.caller = caller
        self.fun = fun
        self.shared = shared
        self.interval = interval
        super(Worker, self).__init__(*args, **kwargs)

      def run(self):
        logging.debug('thread run')
        while True:
          try:
            time.sleep(self.interval)
            if self.caller.going_to_exit:
              return
            flag_quit = self.fun(self.shared)
            if flag_quit:
              return
          except Exception as e:
            logging.error(traceback.format_exc())

    # initialize shared
    logging.debug('Initialize shared')
    for fun in self.inits:
      fun(self.shared)

    # start threads
    logging.debug('Start threads')
    for (fun, interval) in self.thread_funs:
      logging.debug(' - {}'.format(fun))
      worker = Worker(self, self.shared, fun, interval)
      worker.start()
      self.thread_list.append(worker)

  def _end(self):
    curses.nocbreak()
    self.stdscr.keypad(False)
    curses.echo()
    curses.endwin()

  def start(self):

    if not self.did_setup:
      self._setup()

    # get curses-stdscr and make warning text
    stdscr = self.stdscr
    warning = ''

    # start looping
    logging.debug('Start Loop')
    while True:
      try:
        stdscr.clear()
        self.showtop(self.shared, stdscr, warning)
        curses.curs_set(0) # hide cursor
        stdscr.refresh()

        stdscr.timeout(1000)
        key = stdscr.getkey()
        stdscr.timeout(-1)

        if key not in self.keymap:
          if len(key) == 1:
            if ord(key) == 27:
              # escape button -> stop thread -> exit
              self.going_to_exit = True
              for worker in self.thread_list:
                worker.join()
              break
        else:
          logging.debug('ConsoleView.start: key="{}"'.format(key))
          warning = self.keymap[key](self.shared, stdscr)

      except curses.error as e:
        if str(e) != 'no input':
          logging.error(traceback.format_exc())

      except Exception as e:
        logging.error(traceback.format_exc())

    self._end()


def showTextInputForm(stdscr, deco_list, y, x, initial_text, index, warning):
  curses.curs_set(1) # show cursor
  text = initial_text

  while True:

    stdscr.clear()
    for (dx, dy, dtext) in deco_list:
      stdscr.addstr(dx, dy, dtext)
    stdscr.addstr(y, x, text)
    stdscr.move(y, x + index)
    stdscr.refresh()

    key = stdscr.getkey()

    if len(key) != 1:
      logging.debug('Input key: "{}"'.format(key))
    else:
      logging.debug('Input key: "{}", ord: "{}"'.format(key, ord(key)))

    # special char
    if len(key) != 1:
      if key == 'KEY_LEFT':
        if index != 0:
          index -= 1
        pass
      elif key == 'KEY_RIGHT':
        if len(text) > index:
          index += 1

      logging.debug('Index: {}'.format(index))
      continue

    else:
      keycode = ord(key)
      if keycode == 1:       # Ctrl-A
        pass
      elif keycode == 5:     # Ctrl-E
        pass
      elif keycode == 11:    # Ctrl-K
        pass

      elif keycode == 9:     # tab
        return (KEY_TAB, index, text)
      elif keycode == 10:    # new line
        return (KEY_ENTER, index, text)
      elif keycode == 27:    # escape
        return (KEY_ESC, index, initial_text)

      elif keycode == 127:   #delete
        if index != 0:
          text = text[:index-1] + text[index:]
          index -= 1

    # check char is one of characters
    keycode = ord(key)
    if keycode >= 32 and keycode <= 126:
      text = text[:index] + key + text[index:]
      index += 1

def autocomplete(text, candidates):
  d = {}
  for candidate in candidates:
    candidate += '\n'
    current_dict = d
    for c in candidate:
      if c not in current_dict:
        current_dict[c] = {}
      current_dict = current_dict[c]

  current_dict = d
  for c in text:
    if c not in current_dict:
      # unable to do completion
      return text
    current_dict = current_dict[c]

  while True:
    # no candidate or 2+ candidates
    if '\n' in current_dict:
      break
    if len(current_dict) > 1:
      break

    # having only 1 key
    (c, next_dict) = next(iter(current_dict.items()))
    text += c
    current_dict = next_dict
      
  return text