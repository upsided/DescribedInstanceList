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

from bs4 import BeautifulSoup, CData, FeatureNotFound   # pip3 install bs4
import requests                 # pip3 install requests
import sys, os, re
import random
import json
import time
import threading, queue

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
    
languageMap = { #FIXME: these should be in native tongue
"ab":"Abkhaz", "aa":"Afar", "af":"Afrikaans", "ak":"Akan", "sq":"Albanian", "am":"Amharic",
"ar":"Arabic", "an":"Aragonese", "hy":"Armenian", "as":"Assamese", "av":"Avaric",
"ae":"Avestan", "ay":"Aymara", "az":"Azerbaijani", "bm":"Bambara", "ba":"Bashkir",
"eu":"Basque", "be":"Belarusian", "bn":"Bengali,", "bh":"Bihari", "bi":"Bislama",
"bs":"Bosnian", "br":"Breton", "bg":"Bulgarian", "my":"Burmese", "ca":"Catalan", 
"ch":"Chamorro", "ce":"Chechen", "ny":"Chichewa,", "zh":"Chinese", "cv":"Chuvash", 
"kw":"Cornish", "co":"Corsican", "cr":"Cree", "hr":"Croatian", "cs":"Czech", 
"da":"Danish", "dv":"Divehi,", "nl":"Dutch", "dz":"Dzongkha", "en":"English", 
"eo":"Esperanto", "et":"Estonian", "ee":"Ewe", "fo":"Faroese", "fj":"Fijian", 
"fi":"Finnish", "fr":"French", "ff":"Fula,", "gl":"Galician", "ka":"Georgian", 
"de":"German", "el":"Greek", "gn":"Guaraní", "gu":"Gujarati", "ht":"Haitian,", "ha":"Hausa",
 "he":"Hebrew", "hz":"Herero", "hi":"Hindi", "ho":"Hiri", "hu":"Hungarian", 
 "ia":"Interlingua", "id":"Indonesian", "ie":"Interlingue", "ga":"Irish", "ig":"Igbo", 
 "ik":"Inupiaq", "io":"Ido", "is":"Icelandic", "it":"Italian", "iu":"Inuktitut", 
 "ja":"Japanese", "jv":"Javanese", "kl":"Kalaallisut,", "kn":"Kannada", "kr":"Kanuri", 
 "ks":"Kashmiri", "kk":"Kazakh", "km":"Khmer", "ki":"Kikuyu,", "rw":"Kinyarwanda", 
 "ky":"Kyrgyz", "kv":"Komi", "kg":"Kongo", "ko":"Korean", "ku":"Kurdish", "kj":"Kwanyama", 
 "la":"Latin", "lb":"Luxembourgish,", "lg":"Ganda", "li":"Limburgish,", "ln":"Lingala", 
 "lo":"Lao", "lt":"Lithuanian", "lu":"Luba-Katanga", "lv":"Latvian", "gv":"Manx", 
 "mk":"Macedonian", "mg":"Malagasy", "ms":"Malay", "ml":"Malayalam", "mt":"Maltese", 
 "mi":"Māori", "mr":"Marathi", "mh":"Marshallese", "mn":"Mongolian", "na":"Nauruan", 
 "nv":"Navajo,", "nd":"Northern", "ne":"Nepali", "ng":"Ndonga", "nb":"Norwegian", 
 "nn":"Norwegian", "no":"Norwegian", "ii":"Nuosu", "nr":"Southern", "oc":"Occitan", 
 "oj":"Ojibwe,", "cu":"Old", "om":"Oromo", "or":"Oriya", "os":"Ossetian,", 
 "pa":"(Eastern)", "pi":"Pāli", "fa":"Persian", "pl":"Polish", "ps":"Pashto,", 
 "pt":"Portuguese", "qu":"Quechua", "rm":"Romansh", "rn":"Kirundi", "ro":"Romanian", 
 "ru":"Russian", "sa":"Sanskrit", "sc":"Sardinian", "sd":"Sindhi", "se":"Northern", 
 "sm":"Samoan", "sg":"Sango", "sr":"Serbian", "gd":"Scottish", "sn":"Shona", 
 "si":"Sinhalese,", "sk":"Slovak", "sl":"Slovene", "so":"Somali", "st":"Southern", 
 "es":"Spanish", "su":"Sundanese", "sw":"Swahili", "ss":"Swati", "sv":"Swedish", 
 "ta":"Tamil", "te":"Telugu", "tg":"Tajik", "th":"Thai", "ti":"Tigrinya", "bo":"Tibetan", 
 "tk":"Turkmen", "tl":"Tagalog", "tn":"Tswana", "to":"Tonga", "tr":"Turkish", 
 "ts":"Tsonga", "tt":"Tatar", "tw":"Twi", "ty":"Tahitian", "ug":"Uyghur", 
 "uk":"Ukrainian", "ur":"Urdu", "uz":"Uzbek", "ve":"Venda", "vi":"Vietnamese", 
 "vo":"Volapük", "wa":"Walloon", "cy":"Welsh", "wo":"Wolof", "fy":"Western", "xh":"Xhosa", 
 "yi":"Yiddish", "yo":"Yoruba", "za":"Zhuang,", "zu":"Zulu"
 }
 

def eprint(*args, **kwargs):
    """just like print() but to stderr"""
    print(*args, file=sys.stderr, **kwargs)

def default(dictionary: dict, key, default) -> dict:
    if key not in dictionary:
        dictionary[key] = default
    return dict

# munging purifies the fields so they can be used in html and stuff
# without much mod
def munge(instanceList: list, tootLimit=None) -> list:
    purifyList = ['description', 'tagline', 'title']
    neededList = ['users', 'connections', 'statuses', 'language', 'language_name' ]
    copy = []
    for i in instanceList:
        if i['reachable'] == False:
            continue
        
        default(i, 'tootSample', [])
        default(i, 'name', i['domain'])
        default(i, 'title', i['name'])

        default(i, 'nameplate', "no description")
        default(i, 'tagline', i['nameplate'])
        default(i, 'description', i['tagline'])

        default(i, 'email', "")
        default(i, 'admin', "")
    
        if 'language' in i and i['language']  in languageMap:
            i['language_name'] = languageMap[i['language']]
            
        #replace required but missing with "?"
        for n in neededList:
            if n not in i:
                i[n] = "?" #FIXME: this is bad for SQL and just in general icky
        
        # class tags for filtering
        i['class_tags'] = []
        
        if tootLimit != None:
            i['tootSample'] = i['tootSample'][:tootLimit]
            
        for toot in i['tootSample']:
            toot['avvi'] = toot['account']['avatar']
            toot['content_text'] = toText(toot['content'])
            toot['content_html'] = purify(toot['content'])

        for field in purifyList:
            i[field+"_raw"] = i[field]
            i[field] = purify(i[field], absoluteURL="https://" + i['domain']+"/")
        copy.append(i)
    return copy            

def purifyText(sometext: str) -> str:
    " lots of room for improvement "
    s = re.sub(r'<[^>]*script[^>]*>', '', sometext)
    s = re.sub(r'<', '&lt;', s)
    s = re.sub(r'>', '&gt;', s)
    s = re.sub(r'"', '&quot;', s)
    return s

Newline2Para=re.compile(r'\n([^\n]+)\n')
def purify(sometext: str, absoluteURL=None) -> str:

    s = re.sub(r'<script[^<]+</script>', "", sometext)

    s = BeautifulSoup(s, PARSER)
    if len(s.findAll()) == 0:
        s =  purifyText(s.get_text())
        return Newline2Para.sub(r'<p>\1</p>', s)
    
        # remove CData crap
    for cd in s.findAll(text=True):
        if isinstance(cd, CData):
            cd.replaceWith('')

    # remove scripts
    while s.script != None: s.script.decompose()

    while s.embed != None: s.embed.decompose()
    
    if absoluteURL!= None:
        for link in s.find_all('a', href=True):
            # stuff with colon is absolute (not always true, but screw it,
            # I'm not writing a map of all protocol handlers
            if link['href'].find(':') < 0:
                eprint ("Absolutifying URL %s" % (link['href']) )
                l = link['href'].strip().lstrip('./').lstrip('/')
                link['href'] = absoluteURL + l
                eprint ("absolutified to %s " %  link['href'] )

        for img in s.find_all('img', src=True):
            if img['src'].find(':') < 0:
                eprint ("Absolutifying URL %s" % (img['src']) )
                l = img['src'].strip().lstrip('./').lstrip('/')
                img['src'] = absoluteURL + l
                eprint ("absolutified to %s " %  img['src'] )
                
    s = s.prettify()

    # remove repetitive </br> cuz damn
    #s = re.sub(r'(\s*</?br/?>\n?)+', '<br>', s)
    return s    

def toText(someText: str) -> str:
    s = BeautifulSoup(someText, PARSER)
    s = s.get_text()
    return purifyText(s)            


def PullInstanceList(url=None, filename=None):
    """
    Download json from https://instances.mastodon.xyz/instances.json
    and return it as a dict

    Alternatively, crash with sys.exit(-1)
    """
    if url == None:
        url = 'https://instances.mastodon.xyz/instances.json'
    
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

def ExtractAboutInfo(html: str) -> dict:
    """
    Parse the passed HTML of an instance's about page, and extract as much
    info as feasible, returning a dict with keys like:

    'nameplate'     -- name plus short description
    'title_onpage'    -- name of instance on about page
    'tagline'       -- the short description
    'admin'         -- admin contact in form @Gargron, if any
    'email'         -- email contact if any
    'stuff'         -- extra junk that might not have parsed in contact area
    'language'      -- declared language in html doc (not reliable)
    """

    s = BeautifulSoup(html, "html.parser")
    d = {}
    found = False
    panels = []

    theH = s.find('html')
    if 'lang' in theH.attrs:
        d['language'] = theH.attrs['lang']
        eprint("LANGUAGE: " + d['language'])

        
    for div in s.find_all('div'):
        if 'class' in div.attrs:
            for c in div['class']: #can have multiple classes
                if c == u'panel':
                    #eprint ("PANEL###")
                    #eprint (div.prettify())
                    panels.append(div)

    for ownerinfo in s.find_all("div", class_="owner"):
        scrub = ownerinfo.get_text()
        #eprint(scrub, "\n######admin")
        res =  re.findall(r'\B@\w+', scrub)
        if len(res) > 0:
            d['admin'] = res[0]
            eprint("admin:  ", d['admin'])
            break

    if False:            
        for span in s.find_all('span'):
            if u'class' in span.attrs:
                if u'username' in span[u'class']:
                    d['admin'] = (span.get_text()).strip()
                    if len(d['admin']) == 0:
                        del d['admin']
                    break

    for ownerinfo in s.find_all("div", class_="contact-email"):
        scrub = ownerinfo.get_text()
        #eprint(scrub, "\n######email")
        res= re.findall(r'\b\w+@\w+.\w+', scrub)
        if len(res) > 0:
                d['email'] = res[0]
                eprint("email: ", d['email'])
                if len(d['email']) == 0:
                    del d['email']

    todict = [u'nameplate', u'description',  u'stuff' ]
    todict = todict[0:len(panels)]
    x=0
    for item in todict:
        d[item] = panels[x]
        x=x+1

    if u'nameplate' in d.keys():
        s = d[u'nameplate']
        try:
            d[u'title_onpage'] = s.h2.prettify()
            d[u'tagline'] = s.p.prettify()
        except AttributeError:
            pass



    # convert to text
    if 'nameplate' in d.keys():
        d['nameplate'] = d['nameplate'].get_text()
    if 'description' in d.keys():
        d['description'] = d['description'].get_text()
    if 'stuff' in d.keys():
        d['stuff'] = d['stuff'].get_text()

    return d
    
def grabInfo(instance: dict) -> dict:
        d = {}

        for key in instance.keys():
            d[key] = instance[key]
        
        #fix bad vernacular at .xyz
        d['domain'] = d['name']
        del d['name']

        # the openRegistrations field at .xyz is unreliable
        # so check the join page for text 'closed-registrations-message'
        # and presume this means registrations are closed, otherwise open
        url = "https://" + d['domain'] + "/about"
        try:
            r = requests.get(url, timeout=1.0)
            if r.status_code == 200:
                if 'error' in d: del d['error'] # we succeded, so woot!
                if r.text.find('closed-registrations-message') >= 0:
                    d['openRegistrations'] = False
                else: #FIXME need some extra check for valid form
                    d['openRegistrations'] = True
                
                eprint("%s registrations open: %s" % (d['domain'], d['openRegistrations']))

        except Exception as e: # FIXME: bad but how many request/urllib exceptions must I account for? Unknown...
            eprint ("Couldn't download " + url + "(%s)" % str(e))

        
        url = "https://" + d['domain'] + "/about/more"

        eprint ("Downloading \"" + url + "\"...")

        r  = False # check for failure
        try:
            r = requests.get(url, timeout=1.0)
            if 'error' in d: del d['error'] # we succeded, so woot!
            
        except Exception as e: # FIXME: bad but how many request/urllib exceptions must I account for? Unknown...
            eprint ("Couldn't download " + url + "(%s)" % str(e))
            d['error'] = str(e)

        # add more info scraped from HTML and such        
        if r != False and r.status_code == 200:
            aboutDict = ExtractAboutInfo(r.text)
            for key in aboutDict.keys():
                d[key] = aboutDict[key]
            d['url'] = url
            d['html'] = r.text
            d['reachable'] = True
        else:
            d['reachable'] = False

        d['lastCheck'] = time.time()

        if d['reachable']:
            # try to get the json at the instance itself.
            # this contains:
            #   short description
            #   contact email
            #   and other stuff

            url = "https://%s/api/v1/instance.json" % d['domain']

            try:
                r = requests.get(url, timeout=1.0)
                if r.status_code == 200:
                    theDict = json.loads(r.text)
                    #eprint(theDict)
                    if 'description' in theDict:
                        if len(theDict['description']) > 0:
                            d['tagline'] = theDict['description']
                        del theDict['description'] #prevent overwriting below
                    
                    if 'email' in theDict:
                        if len(theDict['email']) > 0:
                            d['email'] = theDict['email']
                        del theDict['email']
                    
                    # so the extra stuff, add it only
                    # if it's not in my list already
                    # because I dunno if there's a name conflict
                    for k,v in theDict.items():
                        if k not in d and len(v) > 0:
                            d[k] = v
            
            except Exception as e: # so many exception types, hard to do anything but this
              eprint ("Skipping extra JSON info for " + url + "(%s)" % str(e))
          
            # now we get a sample of the local toots at this moment.
            url = "https://%s/api/v1/timelines/public?local=1" % d['domain']
            eprint("Getting toot sample from %s..." % url)
            
            try:
                r = requests.get(url, timeout=1.0)
                if r.status_code == 200:
                    theDict = json.loads(r.text)
                    d['tootSample'] = theDict
            except Exception as e:
                eprint("Skipping toot sample for %s (%s)" % (url, str(e)) )
            
          
        # WHEW!
        return d


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
            d = grabInfo(i)
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
        eprint("Adding %s" % i['name'])
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
    

# I'm doing it the easy/breakbable way.
# 1. Download instance list from Mastodon.xyz.
# 2. Download about pages of all instances, parse this, and merge it.
# 3. Dump all of this into the .json output file

# it requires about 30 minutes of uninterrupted run.
# But, this keeps the code sane, so :shrug:

if __name__ == "__main__":
    if 'TEST' in os.environ and os.environ['TEST']:
        TEST_ONLY=True

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
        
    if TEST_ONLY:
        random.shuffle(json_data)
        json_data = json_data[0:10]

    # discover and store various info for each instance
    # place it in global "aboutInstances"
    DoItAll(json_data)

    eprint ("munging safe versions...")
    aboutInstances = munge(aboutInstances)
    # write the JSON output 

    f = open(filenameOut, "w")
    f.write(json.dumps(aboutInstances, indent=4, separators=(',', ': ')))
    f.close()

    # print out the fields we find
    # this is useful in deciding the SCHEMA
    # (but is bad for *using* as schema, since it's downloaded from net
    fields = {}
    for i in aboutInstances:
        for k,v in i.items():
            fields[k] = v
    
    eprint("FIELDS FOUND:")
    for k in fields:
        eprint(k)

