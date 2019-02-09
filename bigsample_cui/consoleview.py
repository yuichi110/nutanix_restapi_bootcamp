'''
Framework for making Curses based UI.

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

import curses
import logging
import time
import json
import threading
import traceback


###
### Utility Class
###

class _IntendedException(Exception):
  pass

class _VoidLogger():
  def critical(self, message): pass
  def error(self, message): pass
  def warning(self, message): pass
  def info(self, message): pass
  def debug(self, message): pass


###
### Main
###

class ConsoleView:

  ###
  ### Public VAL
  ###

  KEY_ENTER = 'CV_KEY_ENTER'
  KEY_ESC = 'CV_KEY_ESC'
  KEY_TAB = 'CV_KEY_TAB'

  ###
  ### Logger for init
  ###

  @staticmethod
  def create_logger(log_file='consoleview.log', level=logging.INFO, formatter='%(message)s'):
      logger = logging.getLogger('ConsoleViewLogger')
      logger.setLevel(level)
      handler = logging.FileHandler(log_file)  
      handler.setFormatter(logging.Formatter(formatter))
      logger.addHandler(handler)
      return logger

  ###
  ### Constructor and destructor
  ###

  def __init__(self, logger=_VoidLogger()):
    logger.debug('ConsoleView.__init__() : Start.')

    # Shared Objects
    class Shared:
      def __str__(self):
        # Object dump
        text = ''
        for (key, value) in vars(self).items():
          text += '{} : {}\n'.format(key, value)
        return text

    # Params
    self._refresh_rate = 100

    # Private vars
    self._shared = Shared()
    self._logger = logger
    self._init_funs = []
    self._util_funs = []
    self._showtop = None
    self._keymap = {}
    self._thread_funs = []
    self._did_auto_init = False

    # Fasten response for Escape Key
    import os
    os.environ.setdefault('ESCDELAY', '25')
    
    logger.debug('ConsoleView.__init__() : End.')


  def __del__(self):
    # Threads are stopped automatically since they are daemon mode.
    pass


  ###
  ### Public instance methods
  ###

  def add_fun_init(self, fun):
    if self._did_auto_init:
      raise Exception('Error: Unable to add function after start.')
    self._init_funs.append(fun)


  def add_fun_util(self, fun_name, fun):
    if self._did_auto_init:
      raise Exception('Error: Unable to add function after start.')
    self._util_funs.append((fun_name, fun))
    

  def add_fun_showtop(self, fun):
    if self._showtop != None:
      raise Exception('Error: Only 1 function can be registered as showtop.')
    if self._did_auto_init:
      raise Exception('Error: Unable to add function after start.')
    self._showtop = fun


  def add_fun_thread(self, fun, interval):
    if self._did_auto_init:
      raise Exception('Error: Unable to add function after start.')
    self._thread_funs.append((fun, interval))


  def add_fun_keycalled(self, key, fun):
    if self._did_auto_init:
      raise Exception('Error: Unable to add function after start.')
    if len(key) > 1:
      raise Exception('Error: Key must be single character Number or Alphabet.')
    if not key.isalnum():
      raise Exception('Error: Key must be single character Number or Alphabet.')
    if key in self._keymap:
      raise Exception('Error: The key "{}" is already assigned for another function.'.format(key))
    self._keymap[key] = fun


  def start(self, debug_showtop=False):
    self._logger.debug('ConsoleView.start() : start')
    # Go in to curses mode with wrapper.
    curses.wrapper(self._start, debug_showtop)
    # Go out from cureses mode. Console will become normal mode.
    self._logger.debug('ConsoleView.start() : end')    


  ###
  ### Methods for debug tests. Please don't call on production.
  ###

  def test_get_shared(self):
    self._auto_init()
    return self._shared


  def test_call_keyfun(self, key):
    if key not in self._keymap:
      raise Exception('Error. Key "{}" is not added yet.'.format(key))
    warning = curses.wrapper(self._test_call_keyfun, key)
    return warning


  ###
  ### Public static methods
  ###

  @staticmethod
  def show_text_input_form(stdscr, deco_list, y, x, initial_text, index, warning, logger=_VoidLogger()):
    
    # show cursor
    curses.curs_set(1) 
    text = initial_text

    while True:

      # init
      stdscr.clear()
      for (dx, dy, dtext) in deco_list:
        stdscr.addstr(dx, dy, dtext)
      stdscr.addstr(y, x, text)
      stdscr.move(y, x + index)
      stdscr.refresh()

      # key input 
      key = stdscr.getkey()
      logger.debug('ConsoleView.show_text_input_form() : key input "{}"'.format(key))

      # Arrow Keys
      if len(key) != 1:
        if key == 'KEY_LEFT':
          if index != 0:
            index -= 1
        elif key == 'KEY_RIGHT':
          if len(text) > index:
            index += 1
        continue

      # Special Keys
      keycode = ord(key)
      if keycode == 1:       # Ctrl-A
        pass
      elif keycode == 5:     # Ctrl-E
        pass
      elif keycode == 11:    # Ctrl-K
        pass
      elif keycode == 9:     # Tab
        return (ConsoleView.KEY_TAB, index, text)
      elif keycode == 10:    # New line
        return (ConsoleView.KEY_ENTER, index, text)
      elif keycode == 27:    # Escape
        return (ConsoleView.KEY_ESC, index, initial_text)
      elif keycode == 127:   # Delete
        if index != 0:
          text = text[:index-1] + text[index:]
          index -= 1

      # Alphabet, Number etc.
      keycode = ord(key)
      if keycode >= 32 and keycode <= 126:
        text = text[:index] + key + text[index:]
        index += 1


  @staticmethod
  def autocomplete(text, candidates, logger=_VoidLogger()):
    # Autocomplete function with N-Tree Algorithm like T-CAM.
    # When Candidates are ["abcdef", "abd", "abcd"].
    # Adds "\n" on each words ["abcdef\n", "abd\n", "abcd\n"].
    # And then, create this tree.
    #
    # "a" --- "b" -+- "c" --- "d" -+- "e" --- "f" --- "\n"
    #              |               |
    #              +- "d" --- "\n" +- "\n"
    #
    # It will be achieved as recursive dict.
    #
    # {
    #   "a": {
    #     "b": {
    #       "c": {
    #         "d": {
    #           "\n": {},
    #           "e": {
    #             "f": {
    #               "\n": {}
    #             }
    #           }
    #         }
    #       },
    #       "d": {
    #         "\n": {}
    #       }
    #     }
    #   }
    # }
    #
    # And Track it as possible as text can.
    # (1) Move to the node by text chars.
    # (2) Check the next nodes
    #      - If current node has only 1 child and it is not "\n", move to next node
    #      - Else : End
    # (3) Add node-char to the text and Move to next node.
    # (4) Go to (2) 
    #
    # With above sample, autocompete will work as,
    #  text    : return-text
    #  - ''    : ab
    #  - a     : ab
    #  - ab    : ab
    #  - abx   : abx (Unable to track. Return original text.)
    #  - abd   : abd
    #  - abc   : abcd
    #  - abcde : abcdef

    logger.debug('ConsoleView.autocomplete() : Start.')
    original_text = text

    # Check whether candidate is ok.
    for candidate in candidates:
      if '\n' in candidate:
        raise Exception("Candidate words can't contain NEW-LINE")

    # Make tree.
    logger.debug('ConsoleView.autocomplete() : Make tree from candidates.')
    d = {}
    for candidate in candidates:
      candidate += '\n'

      # Move to head node of the tree. And looping by each character
      current_dict = d
      for c in candidate:

        if c in current_dict:
          # The character is in current position -> do nothing.
          pass
        else:
          # Not in current position -> add the char.
          current_dict[c] = {}

        # Move to next node
        current_dict = current_dict[c]

    # Dump tree.
    json_text = json.dumps(d, sort_keys=True, indent=2)
    logger.debug('ConsoleView.autocomplete() : Tree\n{}'.format(json_text))

    # Check whether able to autocomplete or not. If not, return oritinal text.
    logger.debug('ConsoleView.autocomplete() : Check whether able to autocomplete or not.')
    current_dict = d
    # Looping via each character.
    for c in text:
      if c not in current_dict:
        # Unable to do autocompletion.
        return text

      # Move to next node.
      current_dict = current_dict[c]

    # Able to do autocomplete.
    # Track the tree as possible as text can.
    logger.debug('ConsoleView.autocomplete() : Track tree as possible as text can.')
    while True:
      # no candidate or 2+ candidates. End autocompletion.
      if '\n' in current_dict:
        # having 1 or 2+ candidate.
        # 1  Candidate   -> End.
        # 2+ Candidates. -> 1 Candidate end at this node. Unable to track next. End.
        break
      if len(current_dict) > 1:
        # 2+ Candidates -> End.
        break

      # Having only 1 key
      # Get the char and get next node.
      (c, next_dict) = next(iter(current_dict.items()))

      # Add char to the text
      text += c

      # Move to next node.
      current_dict = next_dict
        
    # Done. return autocompleted text.
    logger.debug(
      'ConsoleView.autocomplete() : Original-Text="{}", Autocompleted-Text="{}"'.format(
        original_text, text))
    return text


  ###
  ### Private instance methods
  ###

  def _auto_init(self):
    # Automatically called when App is started on 
    # - Production : start()
    # - Debug : test_get_shared(), test_call_keyfun()

    # Only 1 time.

    if self._did_auto_init:
      return
    self._did_auto_init = True

    self._logger.debug('ConsoleView._auto_init() : Start.')
    try:
      # Initialize shared
      self._logger.debug('Initializing SHARED via Init-functions')
      for fun in self._init_funs:
        self._logger.debug(' - {}'.format(fun))
        fun(self._shared)
      if len(self._init_funs) == 0:
        self._logger.debug(' * No init-functions are registerd. Skip.')

      # Register util funs
      self._logger.debug('Registering Util-functions to SHARED')
      for (fun_name, fun) in self._util_funs:
        self._logger.debug(' - {}'.format(fun))
        setattr(self._shared, fun_name, fun)
      if len(self._util_funs) == 0:
        self._logger.debug(' * No util-functions are registerd. Skip.')

      # Private Thread Worker Class
      class Worker(threading.Thread):
        def __init__(self, caller, shared, fun, interval, logger, *args, **kwargs):
          self.caller = caller
          self.fun = fun
          self.shared = shared
          self.interval = interval
          self.logger = logger
          super(Worker, self).__init__(*args, **kwargs)

        def run(self):
          while True:
            try:
              time.sleep(self.interval)
              flag_quit = self.fun(self.shared, self.logger)
              if flag_quit:
                return
            except Exception as e:
              self.logger.error('\n' + traceback.format_exc())

      # Start threads
      self._logger.debug('Starting thread-functions as daemon threads.')
      for (fun, interval) in self._thread_funs:
        self._logger.debug(' - {}'.format(fun))
        worker = Worker(self, self._shared, fun, interval, self._logger)
        # Start daemon thread. 
        # It will be stopped automatically when main(this one) thread ends.
        worker.daemon = True
        worker.start()
      if len(self._thread_funs) == 0:
        self._logger.debug(' * No thread-functions are registerd. Skip.')

      # If no showtop is registered, quit app with error.
      if self._showtop == None:
        raise _IntendedException('showtop must be set.')

      # Dump key functions for debug.
      self._logger.debug('Listing all Key-functions mapping.')
      pairs = sorted(self._keymap.items(), key=lambda kv:kv[0])
      for (key, fun) in pairs:
        self._logger.debug(' - key "{}" : function "{}"'.format(key, fun))
      if len(self._keymap) == 0:
        self._logger.debug(' * No key-functions are registerd. Skip.')

    except _IntendedException as e:
      self._logger.error('ConsoleView._auto_init() : Failed with error "{}".'.format(e))
      print('Application failed at init with error "{}".'.format(e))
      print('Abort.')
      exit(1)

    except Exception as e:
      self._logger.error('ConsoleView._auto_init() : Failed with unexpected error.')
      self._logger.error('\n' + traceback.format_exc())
      print('Application failed at init with unexpected error "{}".'.format(e))
      print('Abort.')
      exit(1)

    self._logger.debug('ConsoleView._auto_init() : End.')


  def _start(self, stdscr, debug):
    self._logger.debug('ConsoleView._start() : Start.')

    # Suppress debug logging normally. Since it is too noisy.
    def logging_debug(text):
      if not debug:
        return
      self._logger.debug(text)

    self._auto_init()
    warning = ''

    # start looping
    self._logger.debug('ConsoleView._start() : Entering infinite UI loop.')
    while True:
      try:
        stdscr.clear()
        self._showtop(self._shared, stdscr, warning, self._logger)
        # hide cursor
        curses.curs_set(0)
        stdscr.refresh()

        # Set timeout to refresh top ui periodically.
        stdscr.timeout(self._refresh_rate) 
        key = stdscr.getkey()
        # If no key input happens within refresh-rate, go to "except curses.error".

        # Had key input.
        # Remove timeout for keymap functions
        stdscr.timeout(-1)   

        if len(key) != 1:
          # Special keys. Might be ARROW KEY.
          logging_debug('ConsoleView.start() : Key input. Special key "{}"'.format(key))
          continue

        if ord(key) == 27:
          # Escape key means quit this app. Break infinite loop.
          logging_debug('ConsoleView._start() : Key input "Escape". Quitting')
          break

        if key in self._keymap:
          # Registerd keys. Go to the value function.
          logging_debug('ConsoleView._start() : Key input. Registered key "{}"'.format(key))
          fun = self._keymap[key]
          warning = fun(self._shared, stdscr, self._logger)

        else:
          # Other keys. Ignore.
          logging_debug('ConsoleView._start() : Key input. Non-Registerd key "{}"'.format(key))

      except curses.error as e:
        if str(e) != 'no input':
          warning = 'Error. Unexpected error happens. Please check log.'
          self._logger.error('\n' + traceback.format_exc())
          time.sleep(0.1)

      except Exception as e:
        warning = 'Error. Unexpected error happens. Please check log.'
        self._logger.error('\n' + traceback.format_exc())
        time.sleep(0.1)

    self._logger.debug('ConsoleView._start() : End.')


  def _test_call_keyfun(self, stdscr, key):
    # Calle via test_call_keyfun with Curses Wrapper.
    self._auto_init()
    fun = self._keymap[key]
    warning = fun(self._shared, stdscr, self._logger)
    return warning

