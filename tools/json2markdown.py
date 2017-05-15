#!/usr/bin/env python3
import json
import sys
import time

theDate = time.asctime()
head = """
# Described Instance List
As of %s

This is a list of Mastodon instances with descriptions and contact information. It also contains preview links, so that you can better decide which instance to join.

I have removed instances that aren't accepting open registrations. Some instances couldn't be reached, so they are left out as well. The list is sorted by server uptime percentage. This extra metadata comes from list.mastodon.xyz/instances.json, since I do not know how to query the federation myself.

To view stats about the instance (and visit its about page) click its name. To see a preview of toots at the instance, click "preview."

The search function of your browser might help you find the instance you're looking for.

Please note that some instances may contain offensive content!
""" % theDate

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def NameHead(inst) -> str:
    out = "## [" + inst['name'] + "] "
    out = "## [%s](%s) [(preview)](http://www.unmung.com/mastoview?url=%s&view=local)\n" % (inst['name'], inst['url'], inst['name'])
    return out

def Tagline(i: dict) -> str:
    if 'tagline' in i.keys():
        out =  i['tagline']
    else:
        if 'nameplate' in i.keys():
            out =  i['nameplate'] # fallback if parsed wrong
        else:
            out = "no description\n\n"

    return out

def Users(i: dict) -> str:
    out = ""
    if 'users' in i.keys():
        out = out + "| Users: %s " % i['users']
    if 'statuses' in i.keys():
        out = out + "| Toots: %s " % i['statuses']
    if 'connections' in i.keys():
        out = out + "| Connections: %s " % i['connections']
    if len(out) > 0: out = out + "|"
    out = "\n" + out + "\n\n"
    return out

def Description(i: dict) -> str:
    if 'description' not in i.keys():
        return ""

    out = "<details><summary>(more)</summary>"
    out = out + i['description'] + "\n</details>\n\n"
    return out

def Email(i: dict) -> str:
    if 'email' in i.keys():
        out = "Email: [%s](mailto:%s)\n\n" % (i['email'], i['email'])
        return out
    else:
        out = "Email: Not Available\n\n"
    return out

def Admin(i: dict) -> str:
    if 'admin' in i.keys():
        out = "Admin: [%s@%s](https://%s/%s)\n\n" % (i['admin'], i['name'], i['name'], i['admin'] )
        return out
    else:
        out = "Admin: Not Available\n\n"
    return out

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print ("usage: toMarkdown.py input.json output.md")
        sys.exit(1)

    In = open(sys.argv[1])

    instances = json.loads(In.read())
    In.close()

    instances = sorted(instances, key=lambda u: 100.0-u['uptime'])

    Out = open(sys.argv[2], "w+")

    Out.write(head)
    for i in instances:
        eprint(i['name'])
        if i['reachable']:
            if 'openRegistrations' in i.keys() and i['openRegistrations']:
                Out.write(NameHead(i))
                Out.write(Users(i))
                Out.write(Tagline(i))
                Out.write("\n\n")
                Out.write(Description(i))
                Out.write(Email(i))
                Out.write(Admin(i))

    Out.close()
