#!/usr/bin/env python3
"""
usage:
json2sqlite.py in_filename.json out_filename.md

This creates or replaces out_file.sqlite with the instance data
from in_filename.json. 

in_filename.json is presumed to have been rendered with federation2json.py
"""

import json
import sys
import sqlite3

theSchema = """create table instances(
domain text primary key,
name text,
title text,
language text,
language_name text,
language_name_native text,
url text,
uri text,
version text,
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


def CreateInstanceRecord(aDict, theDB):
    """
    given an instance dictionary and the SQLite DB,
    insert its data into the db table 'instances'
    """
    command = "insert into instances ("

    # some keys won't be in the schema.
    # So store the valid keys in keylist
    # side effect: it creates an order for the dict :-)
    keylist = []    
    
    # discover valid keys
    for k in aDict.keys():
        # try to fit the schema as stated above
        try:
            # cause an exception if key doesn't exist in DB
            temp = theDB.execute ("select %s from instances" % k)
            keylist.append(k)
        except sqlite3.OperationalError as e: # KLUDGGGGGGEEEE
            if str(e)[0:14] == 'no such column':
                pass # not a problem, just skip
            else:
                raise

    # So now the DICT must be split into 2 lists:
    # a key list, and a value list
    # then munged into SQL syntax
    
    # build a string similar to  "name, description, url) VALUES (?, ?, ?)"
    # where number of '?' == number of valid keys
    # I have yet to find a non-buggy way to use '?' for the key names,
    # so for now, it's gonna be raw text.
    for k in keylist:
        command = command + " " + k + ","

    command = command[0:-1] # remove last comma

    command  = command + ")"
    command = command + " VALUES (" + ', '.join('?' * len(keylist) )
    command  = command + ")"

    # build the values list
    valueList = []
    for k in keylist:
        valueList.append(aDict[k])

    #eprint(command)
    theDB.execute(command, valueList)
    theDB.commit()
    return command + repr(valueList)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        eprint("Usage: json2sqlite.py input.json output.sqlite")
        exit(1)

    fin = open(sys.argv[1])
    instances = json.loads(fin.read())
    fin.close()

    fout = sqlite3.connect(sys.argv[2])

    # delete table if it exists in specified DB
    # Why? Well because this code might change schema
    # that's why.
    try:
        fout.execute("drop table instances;")
    except sqlite3.OperationalError: # no table
        pass
        
    # create "instances" table in DB
    fout.execute(theSchema)
    
    # and there ya have it 
    for i in instances:
        CreateInstanceRecord(i, fout)

    fout.close()
