#!/usr/bin/env python3
"""
usage:
json2markdown.py in_filename.json out_filename.md

This renders a markdown file using instance data in the .json
which was previously generated with federation2json.py

"""


import json
import sys
import time

theDate = time.asctime()
head = """
# Described Instance List
As of %s

This is a list of Mastodon instances with descriptions and contact information. It also contains preview links, so that you can better decide which instance to join.

I have removed instances that aren't accepting open registrations. Some instances couldn't be reached, so they are left out as well.This extra metadata comes from list.mastodon.xyz/instances.json, since I do not know how to query the federation myself.

To view stats about the instance (and visit its about page) click its name. To see a preview of toots at the instance, click "preview."

The search function of your browser might help you find the instance you're looking for.

Please note that some instances may contain offensive content!
""" % theDate

def eprint(*args, **kwargs):
    """just like print() but for stderr"""
    print(*args, file=sys.stderr, **kwargs)

def NameHead(inst) -> str:
    """
    given an instance dictionary, return a heading markdown that contatins 
    the name of the instance and a preview link at mastoview
    """
    out = "## [" + inst['title'] + "] "
    out = "## [%s](%s) [(preview)](http://www.unmung.com/mastoview?url=%s&view=local)\n" % (inst['domain'], inst['url'], inst['domain'])
    return out

def Tagline(i: dict) -> str:
    """
    given an instance dictionary, return markdown of its short description
    or long description if we must...
    """
    if 'tagline' in i.keys():
        out =  i['tagline']
    else:
        if 'nameplate' in i.keys():
            out =  i['nameplate'] # fallback if parsed wrong
        else:
            out = "no description\n\n"

    return out

def str2int2str(thing):
    """
    given a string of a possible integer,
    return a nice looking version like 34,395
    or just use the string if something goes wrong
    """
    i = 0
    try:
        i = int(thing)
        return format (i, ',d')
    except:
        return thing
    
def Users(i: dict) -> str:
    """
    given a instance dictionary, return markdown paragraph showing some
    general stats like | users: 20 | toots: 5,3894 | connections: 338 |
    """
    out = ""
    if 'users' in i.keys():
        u = str2int2str(i['users'])
        out = out + "| Users: %s " % u
    if 'statuses' in i.keys():
        s = str2int2str(i['statuses'])
        out = out + "| Toots: %s " % s
    if 'connections' in i.keys():
        c = str2int2str(i['connections'])
        out = out + "| Connections: %s " % c

    if len(out) > 0: out = out + "|"
    out = "\n" + out + "\n\n"
    return out

def Description(i: dict) -> str:
    """
    given an instance dictionary,
    return the markdown for the long description
    """
    if 'description' not in i.keys():
        return ""

    out = "<details><summary>(more)</summary>"
    out = out + i['description'] + "\n</details>\n\n"
    return out

def Email(i: dict) -> str:
    """
    given an instance dictionary,
    return the markdown (with linke) for the email
    or "not available" if it doesn't exist
    """
    if 'email' in i.keys():
        out = "Email: [%s](mailto:%s)\n\n" % (i['email'], i['email'])
        return out
    else:
        out = "Email: Not Available\n\n"
    return out

def Admin(i: dict) -> str:
    """
    given an instance dictionary,
    return the markdown for the admin (of assumed form @gargron)
    in a handy link that can be clicked on an HTML page
    to read the admin's profile.
    """
    if 'admin' in i.keys():
        out = "Admin: [%s@%s](https://%s/%s)\n\n" % (i['admin'], i['domain'], i['domain'], i['admin'] )
        return out
    else:
        out = "Admin: Not Available\n\n"
    return out

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print ("usage: json2markdown.py input.json output.md")
        sys.exit(1)

    InFile = open(sys.argv[1])

    instances = json.loads(InFile.read())
    InFile.close()

    #instances = sorted(instances, key=lambda u: 100.0-u['uptime'])

    OutFile = open(sys.argv[2], "w+")

    OutFile.write(head)
    for i in instances:
        eprint("Generating markdown for: %s" % i['domain'])
        if i['reachable']:
            if 'openRegistrations' in i.keys() and i['openRegistrations']:
                OutFile.write(NameHead(i))
                OutFile.write(Users(i))
                OutFile.write(Tagline(i))
                OutFile.write("\n\n")
                OutFile.write(Description(i))
                OutFile.write(Email(i))
                OutFile.write(Admin(i))

    OutFile.close()
