#!/usr/bin/env python3

"""
usage:
federation2json.py out_filename.json

This will scrape all instances known at https://instances.mastodon.xyz/instances.json
for about info and contact info, and put the results in a
.json of your choosing.

"""
#shorten run time when testing. You can also set the environ variable "TEST"
TEST_ONLY = False

"""
Randomize to spread out the load of many people using tool at once.
There's not much I can do about the Mastodon.xyz GET, but I can at least
reduce the pinging of an individual server to 100/20min or approx
surge of 10 hits in a minute if 100 crazy people run buildall.sh at the exact same time
"""
RANDOMIZE = True
THREADS_MAX = 1 # jack it up to 50 for faster download
DEFAULT_MASTER = 'https://instances.mastodon.xyz/instances.json'
#DEFAULT_MASTER = 'https://upsided.github.io/instances.json'
REQUEST_TIMEOUT = 20.0

from bs4 import BeautifulSoup, CData, FeatureNotFound   # pip3 install bs4
import requests                 # pip3 install requests
import sys, os, re
import random
import json
import time
import threading, queue

import AboutThisInstance as about
about.REQUEST_TIMEOUT = REQUEST_TIMEOUT

PARSER = 'lxml' # not much difference IMO, but nerds like it, so
PARSER = 'html.parser' # Actually there is a difference: lxml deletes my data

H5PARSER = 'html5lib' # "html5lib" advertises as a complete and lenient parser that produces valid HTML5


try:
    s = BeautifulSoup("Test", PARSER)
except FeatureNotFound:
    eprint("Couldn't find '%s', using builtin parser for HTML" % PARSER)
    PARSER = 'html.parser' 

try:
    s = BeautifulSoup("Test", H5PARSER)
except FeatureNotFound:
    eprint("Couldn't find '%s', using builtin parser for HTML 5" % H5PARSER)
    H5PARSER = 'html.parser' 

about.PARSER = PARSER

def eprint(*args, **kwargs):
    """just like print() but to stderr"""
    print(*args, file=sys.stderr, **kwargs)
    
def PullInstanceList(url=None, filename=None):
    """
    Download json from https://instances.mastodon.xyz/instances.json
    and return it as a dict

    Alternatively, crash with sys.exit(-1)
    """
    if url == None:
        url = DEFAULT_MASTER
    
    if filename != None:
        # get the json from the file
        f = open(filename)
        s = f.read()
        return json.loads(s)
        
    r = requests.get(url)
    r.raise_for_status()

    if r.status_code != 200:
        eprint("Deciding not to download instances.mastodon.xyz because of strange status code " + str(r.status_code))
        sys.exit(-1) #prob should be an exception but hey
    else:
        return r.json()

class workerThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        eprint( "Starting " + self.name)
        process_data(self.name, self.q)
        eprint ("Exiting " + self.name)

def process_data(threadName, q):
    global exitFlag
    global aboutInstances
    while not exitFlag:
        i= None
        queueLock.acquire()
        if not workQueue.empty():
            i = q.get()
            #eprint ("%s processing %s" % (threadName, i['name']))
            queueLock.release()
            d, error = about.AboutThisInstance(i['domain'], updateDict=i, tootSample=False)
            #eprint ("%s done processing %s" % (threadName, d['domain']))

            queueLock.acquire()
            #eprint("%s appending %s" % (threadName, d['domain']))
            aboutInstances.append(d)
            queueLock.release()
        else:
            queueLock.release()



def DoItAll(instances):
    # Create new threads
    global exitFlag
    global queueLock
    global workQueue
    global aboutInstances
    global threadList

    exitFlag = False
    queueLock = threading.Lock()
    workQueue = queue.Queue(THREADS_MAX*3)
    aboutInstances = []
    threadList = []
    
    threads = []

    for t in range(THREADS_MAX):
        threadList.append('Thread-' + str(t))



    threadID = 1
    for tName in threadList:
        thread = workerThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1

    # Fill the queue
    for i in instances:
        eprint("Adding %s" % i['domain'])
        #queueLock.acquire()
        workQueue.put(i)
        #queueLock.release()
    eprint ("Done adding work")
    # Wait for queue to empty
    while not workQueue.empty():
        #eprint("Queue still has work...")
        time.sleep(2)
        pass

    # Notify threads it's time to exit
    eprint("Setting exit flag...")
    exitFlag = True

    # Wait for all threads to complete
    for t in threads:
        t.join()

domainCheck = re.compile(r'^[a-z0-9]+\.?([a-z0-9-]+\.?)*\.[a-z0-9]+$')
def deleteShittyDomains(data):
  result = []
  for item in data:
    if 'domain' not in item and 'name' in item:
      item['domain'] = item['name']
      
    if 'domain' in item:
      item['domain'] = item['domain'].lower()
      item['domain'] = item['domain'].strip()
      item['domain'] = item['domain'].rstrip('/')
      
      parts = item['domain'].split('.')
      if len(parts) < 2:
        eprint("removing shitty domain ", item['domain'])
        continue
      
      if len (parts[-1]) < 2:
        eprint("removing shitty domain ", item['domain'])
        continue
      if False: 
        if len (parts[-2]) < 2: # this is not always true (there are 1 letter domains in some countries...)
          eprint("removing shitty domain ", item['domain'])
          continue    

      if domainCheck.match(item['domain']):
        if 'blacklisted' in item and item['blacklisted']:
          eprint("Skipping blacklisted domain %s" % item['domain'])
          continue
        result.append(item)
      else:
        eprint("removing shitty domain ", item['domain'])

  return result

def removeDuplicates(instanceList):
  """
  sigh.
  """
  d = {}
  for i in instanceList:
    d[i['domain']] = i
  
  i = []
  for k,v in d.items():
    i.append(v)
  
  return i
    
  
# I'm doing it the easy/breakbable way.
# 1. Download instance list from Mastodon.xyz.
# 2. Download about pages of all instances, parse this, and merge it.
# 3. Dump all of this into the .json output file

# it requires about 30 minutes of uninterrupted run.
# But, this keeps the code sane, so :shrug:

if __name__ == "__main__":
    if 'TEST' in os.environ and os.environ['TEST']:
        TEST_ONLY=True

    if 'THREADS' in os.environ:
        THREADS_MAX=int(os.environ['THREADS'])
        
    # if a .json file is specified, redownload info from
    # all those instances and create an updated version
    # this can help with bashing mastodon.xyz & gets a minor speed boost
    jsonFile = None
    if 'JSON_FILE' in os.environ:
        jsonFile = os.environ['JSON_FILE']
        eprint("Using the data in '%s'...." % jsonFile)
        
    filenameOut = "described_instances.json"
    if len(sys.argv) > 1:
        filenameOut = sys.argv[1]

    # Download the starter list 
    json_data = PullInstanceList(filename=jsonFile)

    if RANDOMIZE:
        random.shuffle(json_data)
    
    json_data = deleteShittyDomains(json_data)
        
    if TEST_ONLY:
        random.shuffle(json_data)
        json_data = json_data[0:10]

    # discover and store various info for each instance
    # place it in global "aboutInstances"

    DoItAll(json_data)

    aboutInstances = removeDuplicates(aboutInstances)
    # write the JSON output 

    f = open(filenameOut, "w")
    f.write(json.dumps(aboutInstances, indent=4, separators=(',', ': ')))
    f.close()

    # print out the fields we find
    # this is useful in deciding the SCHEMA
    # (but is bad for *using* as schema, since it's downloaded from net
    fields = {}
    eprint(len(aboutInstances))
    for i in aboutInstances:
        for k,v in i.items():
            fields[k] = v
    
    eprint("FIELDS FOUND:")
    for k in fields:
        eprint(k)

