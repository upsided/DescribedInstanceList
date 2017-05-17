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

from bs4 import BeautifulSoup   # pip3 install bs4
import requests                 # pip3 install requests
import sys, os
import random
import json
import time


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
    'name'          -- name only
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

    for span in s.find_all('span'):
        if u'class' in span.attrs:
            if u'username' in span[u'class']:
                d['admin'] = (span.get_text()).strip()
                if len(d['admin']) == 0:
                    del d['admin']
                break

    for div in s.find_all('div'):
        if u'class' in div.attrs:
            if u'contact-email' in div[u'class']:
                email = div.find_all('strong')
                d['email'] = (email[0].get_text()).strip()
                if len (d['email']) == 0:
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
            d[u'name'] = s.h2.get_text()
            d[u'tagline'] = s.p.get_text()
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
    aboutInstances = []
    for instance in json_data :
        d = {}

        for key in instance.keys():
            d[key] = instance[key]

        url = "https://" + instance['name'] + "/about/more"

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
            d['domain'] = instance['name'] # FIXME: probably the wrong idea here
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

            url = "https://%s/api/v1/instance.json" % instance['name']

            try:
                r = requests.get(url, timeout=1.0)
                if r.status_code == 200:
                    theDict = json.loads(r.text)
                    #eprint(theDict)
                    if 'description' in theDict:
                        if len(theDict['description']) > 0:
                            d['tagline'] = theDict['description']
                        del theDict['description']
                    
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
          
        # WHEW!
        aboutInstances.append(d)

    # write the JSON output 

    f = open(filenameOut, "w")
    f.write(json.dumps(aboutInstances, indent=4, separators=(',', ': ')))
    f.close()

    # print out the fields we find
    # this is useful in decided the SCHEMA
    # (but is bad for *using* as schema, since it's downloaded from net
    fields = {}
    for i in aboutInstances:
        for k,v in i.items():
            fields[k] = v
    
    eprint("FIELDS FOUND:")
    for k in fields:
        eprint(k)

