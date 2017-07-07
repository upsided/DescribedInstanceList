#!/usr/bin/env python3

# this thins the list out
# to the bare essentials

import sys, json


usage = "json2json.py input.json output.json"

def eprint(*args, **kwargs):
    """just like print() but to stderr"""
    print(*args, file=sys.stderr, **kwargs)
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        eprint(usage)
        sys.exit(1)
    
    filein = sys.argv[1]
    fileout = sys.argv[2]
    #eprint(filein, fileout)
    #sys.exit(0)
    
    f = open(filein)
    data = json.loads(f.read())
    f.close()
    
    munged = []
    
    copyfields = ['domain', 'title', 'statuses', 'users', 'connections', 'open_registrations', 'blacklisted']
    for instance in data:
        #eprint(instance['domain'])
        d = {}
        for c in copyfields:
            if c in instance:
                if instance[c] == "?":
                    d[c] = None
                else:
                    d[c] = instance[c]
            else:
                d[c] = None
            
        munged.append(d)
    
    munged = sorted(munged, key=lambda x: x['domain'])
    f = open(fileout, "w")
    f.write(json.dumps(munged, indent=2, sort_keys=True))
    f.close()
    