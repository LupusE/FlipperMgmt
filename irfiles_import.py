#!/usr/bin/env python3

import re
import os
from os import walk
from os import path
import hashlib
import sqlite3
import csv

dir_fzirdb = os.path.normpath(os.getcwd()+'/../Flipper-IRDB')
db_fzirdb = os.path.normpath(os.getcwd()+'/../flipper_irdblite.db')

category_fzirdb = next(os.walk(dir_fzirdb))[1]

ext_irdb_include = (['.ir'])
dir_irdb_exclude = set([
                    #os.path.normpath(dir_fzirdb+'/_Converted_'),
                    os.path.normpath(dir_fzirdb+'/.git*')
                    ])

btn_pattern = re.compile(r"""
                name: (.*)\n
                type: (.*)\n
                (protocol|frequency): (.*)\n
                (address|duty_cycle): (.*)\n
                (command|data): (.*)\n
                """, re.VERBOSE | re.MULTILINE)



## Get filtered 'folder/files' as list
######################################

def get_irfiles(dir_fzirdb):
    list_irpath = []
    for root, dir, files in walk(dir_fzirdb, topdown=True):
        for irfile in files:
            if (not root.startswith(tuple(dir_irdb_exclude)) and (irfile.endswith(tuple(ext_irdb_include)))):
                    list_irpath.append(root+'/'+irfile)
            else:
                pass
    
    return(list_irpath)

    
## Get file header (category, brand, filename, MD5)
######################################

def get_irfileheader(full_irpath):

    splitcategory = ''
    splitbrand = ''
    splitsource = ''

    if (full_irpath.find(os.path.join('_Converted_','CSV'))) >= 0:
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-3]
        splitcategory = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitsource = 'CSV'
    elif (full_irpath.find(os.path.join('_Converted_','Pronto'))) >= 0:
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitcategory = 'NULL'
        splitsource = 'Pronto'
    elif (full_irpath.find(os.path.join('_Converted_','IR_Plus'))) >= 0:
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitcategory = 'NULL'
        splitsource = 'IR_Plus'
    #elif (full_irpath.find(os.path.join('_Converted_'))) >= 0:
    #    return('')
 
    else:
        splitcategory = os.path.normpath(full_irpath).split(os.sep)[-3]
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitsource = 'IRDB'
        ## correct category for console/Nintendo/Gameboy/ and similar
        if splitcategory not in category_fzirdb:
            splitcategory = os.path.normpath(full_irpath).split(os.sep)[-4]
            splitbrand = os.path.normpath(full_irpath).split(os.sep)[-3]
        if splitcategory in ['git']:
            splitcategory = os.path.normpath(full_irpath).split(os.sep)[-2]
            splitbrand = 'NULL'
    
    splitfile = os.path.normpath(full_irpath).split(os.sep)[-1].replace("'","")
    ## create hash for identify changes
    with open(str(full_irpath), 'rb') as md5file:
        digest = hashlib.file_digest(md5file, 'md5')

    return(splitcategory, splitbrand, splitfile, digest.hexdigest(), splitsource)


## Get file header (comments, MD5)
######################################

def get_irfilecomments(irfile):
    comments = []
    commentstr = ""

    with open(irfile, 'r') as filecomments:
        for line in filecomments:
            if line.startswith("#") and (len(line.strip())) > 1:
                comments.append(line)

    commentstr = "".join(comments)
    #print(commentstr)
    return(commentstr)


## Parse buttons (name, type, protcol/frequncy, address/duty_cycle, command/data)
######################################

def get_irbutton(full_irpath):
    # read file to buffer, to find multiline regex
    readfile = open(full_irpath,'r')
    irbuff = readfile.read()
    readfile.close()

    buttons = []
    for match in btn_pattern.finditer(irbuff):
        btnname = match.group(1).strip().replace("'","")
        btntype = match.group(2).strip()
        btnprot = match.group(4).strip()
        btnaddr = match.group(6).strip()
        btncomm = match.group(8).strip()

        buttons.append(btnname+","+btntype+","+btnprot+","+btnaddr+","+btncomm)

    return(buttons)


## Add extra tables (button translation)
######################################

def translate_buttons():
    con = sqlite3.connect(db_fzirdb)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS btntrans;")
    cur.execute("CREATE TABLE IF NOT EXISTS btntrans ('id', 'name','button');")

    with open('db/csv/Flipper-IRDB2SQLite_btn-transl.csv','r') as translate:
        translate_dr = csv.DictReader(translate, delimiter=';')
        toSQLitedb = [(i['ID'], i['Button'], i['Translate']) for i in translate_dr]

    cur.executemany("INSERT INTO btntrans VALUES (?, ?, ?);", toSQLitedb)
    con.commit()
    con.close()

    print("Buttons translation table (btntrans) created in",db_fzirdb)


## Write parsed items to database
######################################

def write_sqlite():
    try:
        con = sqlite3.connect(db_fzirdb)    
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS irfile;")
        cur.execute("DROP TABLE IF EXISTS irbutton;")
        cur.execute("DROP TABLE IF EXISTS ircomment;")
        cur.execute("CREATE TABLE IF NOT EXISTS irfile (category,brand,file,md5hash,source);")
        cur.execute("CREATE TABLE IF NOT EXISTS irbutton (name,type,protocol,address,command,md5hash);")    
        cur.execute("CREATE TABLE IF NOT EXISTS ircomment (comment,md5hash);")

    except OSError as e:
        print(e)

    print("Getting header and buttons for database",db_fzirdb)
    for irfile in get_irfiles(dir_fzirdb):
        irheader = get_irfileheader(irfile)
        #print(("INSERT INTO irfile VALUES ('{}', '{}','{}','{}')").format(irheader[0],irheader[1],irheader[2],get_irfileheader(irfile)[3]),irheader[4])
        cur.execute(("INSERT INTO irfile VALUES ('{}', '{}','{}','{}','{}')").format(irheader[0],irheader[1],irheader[2],get_irfileheader(irfile)[3],irheader[4]))

        ircomments = get_irfilecomments(irfile)
        if (len(ircomments)) != 0:
            ircomments = ircomments.replace("'","")
            cur.execute(("INSERT INTO ircomment VALUES ('{}', '{}')").format(ircomments,get_irfileheader(irfile)[3]))

        for irbutton in get_irbutton(irfile):
            irbuttons = (irbutton.split(','))
            #print(("INSERT INTO irbutton VALUES ('{}', '{}','{}','{}','{}','{}')").format(irbuttons[0],irbuttons[1],irbuttons[2],irbuttons[3],irbuttons[4],get_irfileheader(irfile)[3]))
            cur.execute(("INSERT INTO irbutton VALUES ('{}', '{}','{}','{}','{}','{}')").format(irbuttons[0],irbuttons[1],irbuttons[2],irbuttons[3],irbuttons[4],get_irfileheader(irfile)[3]))

    con.commit()
    con.close()
    print("Header and buttons written in database",db_fzirdb)


## Execute progam
######################################

if __name__ == '__main__':
    write_sqlite()
    print("Find your database at:", db_fzirdb)
    translate_buttons()
    
