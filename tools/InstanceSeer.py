#!/usr/bin/env python3

"""
Crawl the fediverse to discover domains

python3 InstanceSeer.py yourJsonFile.json

I will read yourJsonFile.json, add more instances as I find them,
and rewrite yourJsonFile.json to reflect changes.

JSON is in this stucture:

[
 {domain: 'mastodon.social', nextURL: 'https://mastodon.social/api/v1/timelines/public?' }
 {...}
]

This is so it can be used with the "federation2json.py" script.

"""

STARTER_INSTANCE = "mastodon.social"
THREADS_MAX = 50 # Warning: I need at least 2 to grab stuff
MAX_PAGE_GRAB = 3 
# this will take the form {'domain.social': {'nextURL': nextURL}}
instance_collection = {}

from bs4 import BeautifulSoup, CData, FeatureNotFound   # pip3 install bs4
import requests                 # pip3 install requests
import sys, os, re
import random
import json
import time
import threading, queue

def eprint(*args, **kwargs):
    """just like print() but to stderr"""
    print(*args, file=sys.stderr, **kwargs)

def writeInstances():
    global instance_collection;
    filename = sys.argv[1]
    eprint("Saving to %s..." % (filename))
    listicle = []
    #convert to list for compatibility with federation2json.py
    for k,v in instance_collection.items():
        d  = v
        d['domain'] = k
        listicle.append(d)
        
    f = open(filename, "w")
    s = json.dumps(listicle, indent=4, sort_keys=True)
    eprint("LENGTH of WRITE: ", len(s))
    f.write(s)
    f.close()

def readInstances():
    global instance_collection;
    filename = sys.argv[1]
    try:
        f = open(filename)
    except Exception as e:
        eprint("couldn't open file ", e)
        return {}

    
    data = json.loads(f.read())
    # convert to a dictionary format
    # for easier lookup by domain
    d = {}
    for item in data:
        d[item['domain']] = item
          
    f.close()
    instance_collection = d
    
getDomainFromAcct = re.compile(r'.+@([^@]+)$')
def extractDomainFromAcct(acct): # acct in form "upside@octodon.social"
    m = getDomainFromAcct.match(acct)
    if m == None:
        return None
    else:
        return m[1]
getDomain = re.compile("^https?:\/\/([^/]+)\/")
def extractDomainFromURL(url):
    m = getDomain.match(url)
    if m == None:
        return None
    else:
        return m[1]
           
def grabMoreToots (url):
    eprint("Grabbing toots at ", url)
    r = requests.get(url, timeout=8.0) #large timeout because we're just peepoles!
    r.raise_for_status()

    if r.status_code != 200:
        eprint("Deciding not to download instances.mastodon.xyz because of strange status code " + str(r.status_code))
        return None, None
    else:
        return r.json(), r.links['next']['url']

       
def scrapeForInstances(domain):
    nextURL = "https://%s/api/v1/timelines/public?limit=40" % domain
    
    queueLock.acquire()
    if domain not in instance_collection:
        instance_collection[domain] = {'nextURL': nextURL}
    else:
        # this is bad because the unreachable tag is saved to disk, and it results in
        # permaban from grabbing. Most of these peeps are gnusocial instances, though
        # so I don't worry
        if 'unreachable' in instance_collection[domain] and instance_collection[domain]['unreachable']:
            queueLock.release()
            return
    
    if 'nextURL' not in instance_collection[domain]:
        instance_collection[domain]['nextURL'] = nextURL
        
    nextURL = instance_collection[domain]['nextURL']
    queueLock.release()
    
    if nextURL == None: return
    
    tries = 0
    while True:
        tries = tries+1
        try:
            toots, nextURL = grabMoreToots(nextURL)
            queueLock.acquire()
            instance_collection[domain]['nextURL'] = nextURL
            queueLock.release()
        except KeyboardInterrupt as e:
            raise e;
        except Exception as e:
            eprint("%s is unreacheable, so skipping..." % nextURL, str(e))
            queueLock.acquire()
            instance_collection[domain]['unreachable'] = True
            queueLock.release()
            break
            
        instanceFound = False
        for t in toots:
            dom = extractDomainFromAcct(t['account']['acct'])
            if dom == None:
                dom = extractDomainFromURL(t['url'])
                
            if dom == None:
                eprint('NONE domain?')
                eprint(t)
            
            queueLock.acquire()
            if dom not in instance_collection:
                instanceFound = True
                eprint ("FOUND NEW INSTANCE: ", dom)
                nextURL = "https://%s/api/v1/timelines/public?limit=40" % dom
                instance_collection[dom] = {'nextURL': nextURL}
                queueLock.release()
                eprint("putting %s in queue..." % dom)
                while True:
                    try:
                        workQueue.put(dom, False)
                        break
                    except queue.Full:
                        pass
            else:
                queueLock.release()
                
        queueLock.acquire()
        if instanceFound: writeInstances()
        queueLock.release()

        if nextURL == None or tries >= MAX_PAGE_GRAB:
            break

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
    while not exitFlag:
        i= None
        queueLock.acquire()
        if not workQueue.empty():
            i = q.get()
            #eprint ("%s processing %s" % (threadName, i['name']))
            queueLock.release()
            d = scrapeForInstances(i)
        else:
            queueLock.release()



def DoItAll():
    # Create new threads
    global exitFlag
    global queueLock
    global workQueue
    global instance_collection
    global threadList

    exitFlag = False
    queueLock = threading.Lock()
    workQueue = queue.Queue(THREADS_MAX*50) # wild guess that one instance won't fill 50 more...
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
    klist = list(instance_collection.keys()) # needed to avoid change of dict while queuing stuff
    random.shuffle(klist)
    for k in klist:
        eprint("Adding %s to queue" % k)
        #queueLock.acquire()
        while True:
            try: 
                workQueue.put(k, False)
                break
            except queue.Full:
                pass
        #queueLock.release()

    eprint ("Done adding work")
    # Wait for queue to empty
    time.sleep(10) # recursive, so work might add work...
    while not workQueue.empty():
        #eprint("Queue still has work...")
        time.sleep(10) # recursive, so work might add work...
        pass

    # Notify threads it's time to exit
    eprint("Setting exit flag...")
    exitFlag = True

    # Wait for all threads to complete
    for t in threads:
        t.join()
               
if __name__ == "__main__":
    
    if 'THREADS' in os.environ:
        THREADS_MAX=int(os.environ['THREADS'])
    # eprint(sys.argv[1])
    readInstances()
    if len(instance_collection.keys()) == 0:
        eprint("Scraping from scratch")
        URL = "https://%s/api/v1/timelines/public?limit=40" % STARTER_INSTANCE
        instance_collection[STARTER_INSTANCE] = {'nextURL': URL}
        DoItAll()
    else:
        eprint("Scraping from existing file %s..." % (sys.argv[1]))
        #index = random.choice(list(instance_collection.keys()))
        #scrapeForInstances(index)
        DoItAll()
    
    writeInstances()
    eprint("Instance count: ", len(list(instance_collection.keys())))
    