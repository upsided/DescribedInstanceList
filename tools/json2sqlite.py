#!/usr/bin/env python3
import json
import sys
import sqlite3

theSchema = """create table instances(
domain text primary key,
name text,
url text,
nameplate text,
tagline text,
description text,
admin text,
email text,
html text,
uptime real,
up integer,
reachable integer,
lastCheck real,
error text,
https_score real,
https_rank text,
ipv6 integer,
openRegistrations integer,
users integer,
statuses integer,
connections integer,
stuff text
);
"""

def eprint(*args, **kwargs):
    """just like print() but to stderr"""
    print(*args, file=sys.stderr, **kwargs)

def deFudge(i):
    if type(i) == bool:
        if i:
            return "1"
        else:
            return "0"
    if type(i) == str:
        return repr(i)

    return str(i)

def InsertCommand(aDict, theDB):
    command = "insert into instances ("
    keylist = []
    for k in aDict:
        keylist.append(k)

    for k in keylist:
        command = command + " " + k + ","
    command = command[0:-1] # remove last comma

    command  = command + ")"
    command = command + " VALUES (" + ', '.join('?' * len(keylist) )
    command  = command + ")"

    varlist = []
    for k in keylist:
        varlist.append(aDict[k])
    #eprint(command)
    theDB.execute(command, varlist)
    theDB.commit()
    return command + repr(varlist)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        eprint("Usage: json2sqlite.py input.json output.sqlite")
        exit(1)
    fin = open(sys.argv[1])
    instances = json.loads(fin.read())
    fin.close()

    fout = sqlite3.connect(sys.argv[2])
    try:
        fout.execute("drop table instances;")
    except sqlite3.OperationalError: # no table
        pass
    fout.execute(theSchema)
    for i in instances:
        #print(genInsertCommand(i))
        InsertCommand(i, fout)

    fout.close()
