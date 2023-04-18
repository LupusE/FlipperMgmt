#!/usr/bin/env python3

import re
import os
from os import walk
from os import path
import hashlib
import sqlite3

search_dir = path.dirname('../Flipper-IRDB/')
sqlite_db = '../flipper_irdb.db'

include_extension = ([".ir"])
exclude_folder = set([
                    search_dir+'/_Converted_',
                    search_dir+'/.git*'
                    ])
categories = next(os.walk(search_dir))[1]

btn_pattern = re.compile(r"""
                name: (.*)\n
                type: (.*)\n
                (protocol|frequency): (.*)\n
                (address|duty_cycle): (.*)\n
                (command|data): (.*)\n
                """, re.VERBOSE | re.MULTILINE)



## Get folder and files
######################################

def get_irfiles():

    for root, dir, files in walk(search_dir, topdown=True):
        for irfile in files:
            full_irpath = path.normpath(str(root) + '/' + str(irfile))
            if (not (full_irpath).startswith(tuple(exclude_folder))):
                if(irfile.endswith(tuple(include_extension))):

                    con = sqlite3.connect(sqlite_db)
                    cur = con.cursor()
                    cur.execute("CREATE TABLE IF NOT EXISTS irfile(category,brand,file,md5hash)")
                    cur.execute("CREATE TABLE IF NOT EXISTS irbutton(name,type,protocol,address,command,md5hash)")

                    ircat = get_irfileheader(full_irpath)[0]
                    irbrand = get_irfileheader(full_irpath)[1]
                    irfname = get_irfileheader(full_irpath)[2]
                    irfhash = get_irfileheader(full_irpath)[3]
                    
                    cur.execute("INSERT INTO irfile VALUES ('"+ircat+"', '"+irbrand+"', '"+irfname+"', '"+irfhash+"')")
                    con.commit()

                    get_irbutton(full_irpath)
                    
                else:
                    pass
                pass
            else:
                pass
        else:
            pass

    
## Get file header
######################################

def get_irfileheader(full_irpath):
    splitcategory = os.path.normpath(full_irpath).split(os.sep)[-3]
    ## correct category for console/Nintendo/Gameboy/ and similar
    if splitcategory not in categories:
       splitcategory = os.path.normpath(full_irpath).split(os.sep)[-4]
    splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
    splitfile = os.path.normpath(full_irpath).split(os.sep)[-1]
    ## create hash for identify changes
    with open(str(full_irpath), "rb") as md5file:
        digest = hashlib.file_digest(md5file, "md5")

    return(splitcategory, splitbrand, splitfile, digest.hexdigest())


## Parse buttons
######################################

def get_irbutton(full_irpath):
    readfile = open(full_irpath,'r')
    irbuff = readfile.read()
    readfile.close()

    con = sqlite3.connect(sqlite_db)
    cur = con.cursor()

    with open(str(full_irpath), "rb") as md5file:
    	filehash = hashlib.file_digest(md5file, "md5").hexdigest()

    for match in btn_pattern.finditer(irbuff):
        #return(match.group(1).strip(), match.group(2).strip(), match.group(4).strip(), match.group(6).strip(), match.group(8).strip())

        btnname = match.group(1).strip()
        btntype = match.group(2).strip()
        btnprot = match.group(4).strip()
        btnaddr = match.group(6).strip()
        btncomm = match.group(8).strip()

        cur.execute("INSERT INTO irbutton VALUES ('"+btnname+"', '"+btntype+"', '"+btnprot+"', '"+btnaddr+"', '"+btncomm+"', '"+filehash+"')")
        
    con.commit()

if __name__ == '__main__':
    get_irfiles()
    print("Find your database at:", sqlite_db)
    
