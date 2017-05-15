#!/usr/bin/env python3

def json2Wiki(jsonFilename: str) -> str:
    In = open(jsonFilename, "r")
    instances = json.loads(In.read())
    In.close()

    instances = sorted(instances, key=lambda u: 100.0-u['uptime'])
    return toWikiCode(instances)

def toWikiCode(aboutInstances: dict) -> str:
    output = u"""== Instance Descriptions (and Caveat) ==
    This is a spidered list of the top 100 instances with descriptions. They are ranked by the performance score given at [https://instances.mastodon.xyz/list https://instances.mastodon.xyz/list]. This list is probably not recent. These instances may not allow open registration, may not have a lot of users, and '''may contain offensive content'''.
    \n"""

    if True:
        for about in aboutInstances:
            output = output + ("===" + "[" + about['url'] + " " + about['domain'] + "] ===\n")
            output = output + ("====[http://www.unmung.com/mastoview?url=" + about['domain'] + "&view=local (Preview This Instance)]====\n\n")
            if 'tagline' in about.keys():
                output = output + "==== Description ====\n"+(about['tagline'] + '\n')
            else:
                output = output + "==== Description ====\n"+(about['nameplate'] + '\n')

            #output = output + ("==== Description ====\n" )
            #output = output + (about['description'] + '\n')
            output = output + ("==== Contact ====\n")

            if 'admin' in about.keys():
                output = output + ("Admin: " + about['admin'] + "@" + about['domain'] + '\n')
            else:
                output = output + ("Admin: Not Available\n")

            if 'email' in about.keys():
                output = output + ("Email: " + "[mailto:" + about['email'] + " " + about['email'] + "]\n")
            else:
                output = output +("Email: Not Available\n")

            output = output + ("----\n")

            if False:
                output = output + ("###" + "[" + about['url'] + "]" + "(" + about['name'] + ")")
                output = output + ("####" + about['tagline'])
                output = output + ("----")
                output = output + (about['description'])
                output = output + ("----")
                output = output + ("\n\n\n")
    else:
        output = output + '{|\n!    scope="col" | Instance \n!  scope="col" | Preview\n!    scope="col" | Description\n!    scope="col" | Contact\n'
        for about in aboutInstances:
            output = output + "|-\n" # row start
            output = output + "| "
            output = output + ("[" + about['url'] + " " + about['domain'] + "]\n")
            output = output + "| "
            output = output + ("[http://www.unmung.com/mastoview?url=" + about['domain'] + "&view=local (preview)]\n")
            output = output + "| "
            if 'tagline' in about.keys():
                output = output + about['tagline'] + '\n'
            else:
                output = output + about['nameplate'] + '\n'
            output = output + "| "
            if 'admin' in about.keys():
                output = output + "Admin: " + about['admin'] + "@" + about['domain'] + '\n'
            else:
                output = output + "Admin: Not Available\n"

            if 'email' in about.keys():
                output = output + ("Email: " + "[mailto:" + about['email'] + " " + about['email'] + "]\n")
            else:
                output = output +("Email: Not Available\n")
            output = output + "-| \n" #end row


    # because Wiki markup needs extra newlines
    o2 =""
    for l in output.splitlines():
        o2 = l + "\n"
    return o2
