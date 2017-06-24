#!/usr/bin/env python3
#from listFun import listFun
from Cheetah.Template import Template #pip3 install cheetah3
from bs4 import BeautifulSoup, CData, FeatureNotFound # pip3 install bs4

import sys, time, json, re
import os, math

# templat files are relative to the script file directory
if __name__ == "__main__":
  scriptpath = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"
else:
  scriptpath = ""

PAGE_TEMPLATE = scriptpath +    "templates/described-page.tmpl"
SCRIPTS_TEMPLATE = scriptpath + "templates/scripts.tmpl"
STYLE_TEMPLATE = scriptpath +   "templates/style.tmpl"

SHORTEN_TO = 10
SHORTEN_TO = None

def eprint(*args, **kwargs):
    "just like print() but for stderr"
    print(*args, file=sys.stderr, **kwargs)
    
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


def truncateToots(instances: list, limit: int):
    for i in instances:
        if 'tootSample' in i:
            i['tootSample'] = i['tootSample'][:limit]
    return instances

def deferAllImages(soup: BeautifulSoup) -> BeautifulSoup:
    for img in soup.findAll("img"):
        if 'src' in img.attrs:
            img['data-original'] = img['src']
            img['src']=""
            if 'class' in img.attrs:
                img['class'].append("lazy")
            else:
                img['class'] = ["lazy"]
            #eprint(img.prettify())
    return soup
       
def valueReduce(listofValues, by=2):
    returnList = []
    c = 0
    sum = 0
    for x in listofValues:
        sum = sum+x
        c = c+1
        if (c == by):
          returnList.append(sum/by)
          sum = 0
          c = 0
    if sum != 0:
      returnList.append(sum/c)
      
    return returnList


def filterTag(value, listofValues: list, labels: list) -> str:
    """
    find the percentile of value in sorted listofValues
    and use it as an index to the list of labels.
    return the label found
    """
    try:
        value = int(value)
    except ValueError:
        return None

    #probably not necessary:
    listofValues = valueReduce(listofValues, by=len(labels)*3)
    if value >= listofValues[-1]:
      return labels[-1]
    if value <= listofValues[0]:
      return labels[0]
      
    length = len(listofValues)
    chunkSize = (length+1)//len(labels) #larger chunk size avoids out-of range errors due to rounding
    
    #eprint (value, chunkSize, length, listofValues[-1])
    for i,v in enumerate(listofValues):
        if value < v:
            index = i//chunkSize
            #eprint(i, length, len(labels), chunkSize, index)
            if index >= len(labels):
                return labels[-1]
            else:
                return labels[index]
    
    return labels[-1]

    
        
def filterTagOld(value, listofValues: list, labels: list) -> str:
    """
    This version does it by simple max/min. 
    """
    try:
        value = int(value)
    except ValueError:
        return None

    max = listofValues[-1]
    min = listofValues[0]
    range = max-min
    if range <= 0: return labels[0]
    
    factor = (value - min)/range
    
    #eprint(factor, value, max, min)
    index = math.floor(len(labels) * (factor) - .0001)
    
    if index < 0: return labels[0]
    
    return labels[index]
    
    
def makeTags(instances):
    class_tags = []

    copy = []
    
    def build(d, name):
        x = []
        for item in d:
            try:
                x.append(int(item[name]))
            except ValueError:
                pass
        #return sorted(list(set(x))) # remove duplicates, dunno if this is more intuitive
        return sorted(x)
        
    status = build(instances, 'statuses')
    user = build(instances, 'users')
    con = build(instances, 'connections')

    #print(status)
    #sys.exit(0)
    
    
    
    languages = {}
    filtergroups = []
    #for dict clarity:
    name = 'name'
    title = 'title'
    id = 'id'
    filters = 'filters'
    
    for i in instances:
        class_tags = []
        if 'language' in i:
            print (i['language'], i['language_name'])
            l =  i['language']
            lname = None
            if 'language_name_native' not in i:
                lname = i['language']
                i['language_name_native'] = lname
            else:
                lname = i['language_name_native']
                
            if len(re.findall(r'^\w+$', l)) > 0:
                class_tags.append("language-" + l)
                if l not in languages:
                    languages[l] = {name: lname,
                                    id: 'language-' + l}
            else:
                class_tags.append("language-unknown")
                languages['unknown'] = {name: 'Unknown', id: 'language-unknown'}
                                
                            
                            
                                
        t = filterTag(i['statuses'], status, ['activity-low', 'activity-medium', 'activity-high'])        
        if t != None: class_tags.append(t)
        else: class_tags.append('activity-unknown')

        t = filterTag(i['users'], user, ['usercount-low', 'usercount-medium', 'usercount-high'])
        if t != None: class_tags.append(t)
        else: class_tags.append('usercount-unknown')

        t = filterTag(i['connections'], con, ['connectioncount-low', 'connectioncount-medium', 'connectioncount-high'])
        if t != None: class_tags.append(t)
        else: class_tags.append('connectioncount-unknown')
    
        if 'email' in i and len(i['email']) != 0:
            class_tags.append("email-yes")
        else:
            class_tags.append("email-no")

        if 'admin' in i and len(i['admin']) != 0:
            class_tags.append("admin-yes")
        else:
            class_tags.append("admin-no")
        
        if 'openRegistrations' in i and i['openRegistrations']:
            class_tags.append("registrations-yes")
        else:
            class_tags.append("registrations-no")

        i['class_tags'] = class_tags                                        
        eprint (i['class_tags'])
        copy.append(i)
    
    # gotta fix lang dict
    lang = []
    for k,v in languages.items():
        lang.append(v)
    # build filtergroups structure
    filtergroups = [ 
                {id: 'activity', title: 'Toot Activity', 
                        'filters': [ 
                        {id: 'activity-low', title:'low'},
                        {id: 'activity-medium', title:'medium'},
                        {id: 'activity-high', title:'high'},
                        {id: 'activity-unknown', title:'unknown'}
                        ]},
                {id: 'usercount', title: 'Users', 
                        filters: [ 
                        {id: 'usercount-low', title:'low'},
                        {id: 'usercount-medium', title:'medium'},
                        {id: 'usercount-high', title:'high'},
                        {id: 'usercount-unknown', title:'unknown'}
                        ]},
                {id: 'connectioncount', title: 'Connections', 
                        filters: [ 
                        {id: 'connectioncount-low', title:'low'},
                        {id: 'connectioncount-medium', title:'medium'},
                        {id: 'connectioncount-high', title:'high'},
                        {id: 'connectioncount-unknown', title:'unknown'}
                        ]},
                {id: 'admin-exists', title: 'Admin contact?',
                        filters: [
                        {id: 'admin-yes', title: 'yes'},
                        {id: 'admin-no', title: 'no'}
                        ]},
                {id: 'email-exists', title: 'Email contact?',
                        filters: [
                        {id: 'email-yes', title: 'yes'},
                        {id: 'email-no', title: 'no'}
                        ]},
                {id: 'accepting-registrations', title: 'Accepting Registrations',
                        filters: [
                        {id: 'registrations-yes', title: 'yes'},
                        {id: 'registrations-no', title: 'no'}
                        ]}
                ]

    #hacky, don't want the extra stuff, just activity and contact
    # filtergroups = filtergroups[:1] + filtergroups[-3:]
    return copy, lang, filtergroups

import hashlib
def calcHash(string:str) -> str:
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.digest()


 

def sortByHash(instancelist):
    l = sorted(instancelist, key=lambda x: calcHash(x['domain']))
    return l

if __name__ == "__main__":
    import datetime
    basename = sys.argv[2]
    justfile = basename.split('/')[-1]
    
    f = open(sys.argv[1])
    instances = json.loads(f.read())
    f.close()

    if SHORTEN_TO != None:
        instances = instances[:SHORTEN_TO]
    
    #instances = munge(instances, tootLimit=16)
    instances = truncateToots(instances, 16)
    instances, languages, filtergroups = makeTags(instances)
    instances = sortByHash(instances)

    for FunVersion in [True, False]:

        theDate = datetime.datetime.utcnow().strftime("%A %d %b %I:%M:%S %p GMT")

        page = {
            'title': "Upside's Instance Picker",
            'scripts': "",
            'style': "",
            'date': theDate,
            'basename': justfile,
            'languages': languages,
            'filtergroups': filtergroups
            }

        data = {'page':page, 'instances': instances, 'FunVersion':FunVersion}

        eprint("rendering with Cheetah...")
        page['style'] = str(Template(file=STYLE_TEMPLATE, searchList=data))
        page['scripts'] = str(Template(file=SCRIPTS_TEMPLATE, searchList=data))
        rendered = str(Template(file=PAGE_TEMPLATE, searchList=data))

        eprint("cleaning up...")
        s = BeautifulSoup(rendered, H5PARSER)
        s = deferAllImages(s)
        s = s.prettify()

        #dunno why I need this here
        s = re.sub(r'(\s*</?br/?>\n?)+', '<br>', s)
        if FunVersion:
            f = open(basename + "-fun.html", "w")
            f.write(str(s))
            f.close()
        else:
            f = open(basename + ".html", "w")
            f.write(str(s))
            f.close()
