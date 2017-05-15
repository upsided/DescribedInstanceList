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

from bs4 import BeautifulSoup   # pip3 install bs4
import requests                 # pip3 install requests
import sys, os
import random
import json
import time


def eprint(*args, **kwargs):
    """just like print() but to stderr"""
    print(*args, file=sys.stderr, **kwargs)

def PullInstanceList():
    """
    Download json from https://instances.mastodon.xyz/instances.json
    and return it as a dict

    Alternatively, crash with sys.exit(-1)
    """

    url = 'https://instances.mastodon.xyz/instances.json'
    r = requests.get(url)

    if r.status_code != 200:
        sys.exit(-1)
    else:
        return (json.loads(r.text))

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

    filenameOut = "described_instances.json"
    if len(sys.argv) > 1:
        filenameOut = sys.argv[1]

    json_data = PullInstanceList()

    if TEST_ONLY:
        random.shuffle(json_data)
        json_data = json_data[0:10]

    aboutInstances = []
    for instance in json_data :
        d = {}

        for key in instance.keys():
            d[key] = instance[key]

        url = "https://" + instance['name'] + "/about/more"

        eprint ("Downloading \"" + url + "\"...")
        r  = False
        try:
            r = requests.get(url, timeout=1.0)
            if 'error' in d: del d['error']
        except Exception as e:
            eprint ("Couldn't download " + url + "(%s)" % str(e))
            d['error'] = str(e)

        # add more info
        
        if r != False and r.status_code == 200:
            aboutDict = ExtractAboutInfo(r.text)
            for key in aboutDict.keys():
                d[key] = aboutDict[key]
            d['url'] = url
            d['html'] = r.text
            d['domain'] = instance['name']
            d['reachable'] = True
        else:
            d['reachable'] = False

        d['lastCheck'] = time.time()

        if d['reachable']:
            # try to get the json description
            # it's the "short description" so we put it in 'tagline'
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
                    
                    for k,v in theDict.items():
                        if len(v)>0:
                            d[k] = v
            
            except Exception as e: # so many exception types, hard to do anything but this
              eprint ("Skipping extra JSON info for " + url + "(%s)" % str(e))
          
                       
        aboutInstances.append(d)

    f = open(filenameOut, "w")
    f.write(json.dumps(aboutInstances, indent=4, separators=(',', ': ')))
    #print (aboutInstances)
    f.close()
    sys.exit(0)
