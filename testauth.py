import requests, urllib3, time, threading
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

IP = '10.149.161.41'
USER = 'admin'
PASSWORD = 'Nutanix/4u!'

def main():
  #basic_auth()
  #session_auth()
  #concurrent_basic_auth()
  concurrent_session_auth()

def basic_auth():
  start = time.time()

  for i in range(100):
    # Make session
    session = requests.Session()
    session.auth = (USER, PASSWORD)
    session.verify = False                              
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

    url = 'https://{}:9440/api/nutanix/v1/cluster/'.format(IP)
    response = session.get(url)
    print("{}: {}".format(i+1, response))

  t = time.time() - start
  print('{} seconds'.format(t))

def concurrent_basic_auth():
  start = time.time()

  def fun(i):
    session = requests.Session()
    session.auth = (USER, PASSWORD)
    session.verify = False                              
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    url = 'https://{}:9440/api/nutanix/v1/cluster/'.format(IP)
    response = session.get(url)
    print("{}: {}".format(i+1, response))

  workers = []
  for i in range(100):
    worker = threading.Thread(target=fun, args=(i,))
    worker.start()
    workers.append(worker)

  for worker in workers:
    worker.join()

  t = time.time() - start
  print('{} seconds'.format(t))


def session_auth():
  start = time.time()

  # Make session
  session = requests.Session()
  session.auth = (USER, PASSWORD)
  session.verify = False                              
  session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  url = 'https://{}:9440/api/nutanix/v1/cluster/'.format(IP)
  response = session.get(url)
  print("{}: {}".format(1, response))
  session.auth = None 
  
  for i in range(1, 100):
    response = session.get(url)
    print("{}: {}".format(i+1, response))

  t = time.time() - start
  print('{} seconds'.format(t))

def concurrent_session_auth():

  def fun(session, i):
    url = 'https://{}:9440/api/nutanix/v1/cluster/'.format(IP)
    response = session.get(url)
    print("{}: {}".format(i+1, response))

  start = time.time()

  # Make session
  session = requests.Session()
  session.auth = (USER, PASSWORD)
  session.verify = False                              
  session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  url = 'https://{}:9440/api/nutanix/v1/cluster/'.format(IP)
  response = session.get(url)
  print("{}: {}".format(1, response))
  
  workers = []
  for i in range(1, 99):
    worker = threading.Thread(target=fun, args=(session, i))
    worker.start()
    workers.append(worker)

  for worker in workers:
    worker.join()

  t = time.time() - start
  print('{} seconds'.format(t))

if __name__ == '__main__':
  main()