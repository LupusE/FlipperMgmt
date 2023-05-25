#!/usr/bin/env python3

import re
import os
from os import walk
from os import path
import hashlib
import sqlite3
import csv

rawanalysis = 1
ext_converted = 1

dir_fzirdb = os.path.normpath(os.getcwd()+'/../Flipper-IRDB')
db_fzirdb = os.path.normpath(os.getcwd()+'/../flipper_irdblite.db')

category_fzirdb = next(os.walk(dir_fzirdb))[1]

ext_irdb_include = (['.ir'])
dir_irdb_exclude = set([
                    os.path.normpath(dir_fzirdb+'/.git*')
                    ])
if ext_converted == 0:
    dir_irdb_exclude.append(os.path.normpath(dir_fzirdb+'/_Converted_'))

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
    print("Count of files to process: ", len(list_irpath))
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
        ## Hack: correct category for console/Nintendo/Gameboy/ and similar
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

## convert type = 'raw' for analysis
######################################

# Get min value from array. Devide all values though and convert to INT
# Assume 15000 is the absolute maximum of transmitted mark or space
# Split array by gaps greater than maximum
#
# The goal is to convert from ...912 840 2829... to ...1 3 1... to
# compare with other signals in the database, regardless of repeats.
#
# Need to analyze if duty_cycle affect the result. Ignored right now.

def convert_raw(btndata,btnname,md5hash,md5count): 
    btndata = btndata.split(' ')
    try:
        btndint = [int(numeric_string) for numeric_string in btndata]
    except:
        cur_execute = ["Nonnumeric value. No import for {} {}".format(md5hash,btnname)]
        return(cur_execute)

    divisor = min(btndint)
    if divisor == 0:
        cur_execute = ["Prevent dividing by zero. No import for {} {}".format(md5hash, btnname)]
        return(cur_execute)
    
    maxdivident = 15000/divisor
    converted = []
    splitlist = []
    cur_execute = []

    # convert values into int by deviding throug smallest value.
    for dividend in btndata:
        factor = int(int(dividend)/int(divisor))
        if factor > maxdivident:
            splitlist.append(factor)
        converted.append(factor)


    # take the converted string, split at huge values (splitlist)
    # not sure now, if the huge values (splitvalue) are important.
    # if the block between the values repeats, count to save storage
    # add sequence for later reassambly
    convrest = converted
    convsplit = []
    convseq = 0
    convrepeat = 0
    splitvalue = 0
    for splitvalue in splitlist:
        if sum(convsplit[-1:], []) == convrest[:convrest.index(splitvalue)]:
            convrepeat = convrepeat + 1
        
        else:
            convsplit.append(convrest[:convrest.index(splitvalue)])
            cur_execute.append(("INSERT INTO rawdata VALUES ('{}', '{}', '{}', '{}', '{}', '{}');").format(btnname,splitvalue,convrest[:convrest.index(splitvalue)],convseq,convrepeat,md5hash))
            convrepeat = 0

        convrest = convrest[convrest.index(splitvalue)+1:] # (splitvalue)+1 for cut splitvalue
        convseq = convseq + 1

    convsplit.append(convrest)
    cur_execute.append(("INSERT INTO rawdata VALUES ('{}', '{}', '{}', '{}', '{}', '{}');").format(btnname,splitvalue,convrest,convseq,convrepeat,md5hash))
    if md5count == 0:
        cur_execute.append(("INSERT INTO rawheader VALUES ('{}', '{}', '{}');").format(divisor,maxdivident,md5hash))
        cur_execute.append(("INSERT INTO rawmeta VALUES ('{}', '{}', '{}');").format(btnname,splitlist,md5hash))

    return(cur_execute)

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
        cur.execute("DROP TABLE IF EXISTS rawdata;")
        cur.execute("DROP TABLE IF EXISTS rawheader;")
        cur.execute("DROP TABLE IF EXISTS rawmeta;")
        if rawanalysis == 1:
            cur.execute("CREATE TABLE IF NOT EXISTS rawdata (btnname,splitvalue,cmdpart,cmdsequence,cmdrepeat,md5hash);")
            cur.execute("CREATE TABLE IF NOT EXISTS rawheader (divisor,maxdivident,md5hash);")
            cur.execute("CREATE TABLE IF NOT EXISTS rawmeta (btnname,splitvalues,md5hash);")
                

    except OSError as e:
        print(e)

    print("Getting header and buttons for database",db_fzirdb)
    for irfile in get_irfiles(dir_fzirdb):
        irheader = get_irfileheader(irfile)
        cur.execute(("INSERT INTO irfile VALUES ('{}', '{}','{}','{}','{}');").format(irheader[0],irheader[1],irheader[2],irheader[3],irheader[4]))

        ircomments = get_irfilecomments(irfile)
        if (len(ircomments)) != 0:
            # dirty hack, because sqlite using ' itself
            ircomments = ircomments.replace("'","")
            cur.execute(("INSERT INTO ircomment VALUES ('{}', '{}');").format(ircomments,irheader[3]))

        md5count = 0
        for irbutton in get_irbutton(irfile):
            irbuttons = (irbutton.split(','))
            cur.execute(("INSERT INTO irbutton VALUES ('{}', '{}','{}','{}','{}','{}');").format(irbuttons[0],irbuttons[1],irbuttons[2],irbuttons[3],irbuttons[4],irheader[3]))
            if irbuttons[1] == 'raw' and rawanalysis == 1:
                for item in convert_raw(irbuttons[4],irbuttons[0],irheader[3],md5count):
                    if item.startswith("INSERT INTO"):
                        cur.execute(item)
                    else:
                        print("Error:", item)
            md5count += 1
                    
    con.commit()
    con.close()
    print("Header and buttons written in database",db_fzirdb)


## Execute program
######################################

if __name__ == '__main__':
    write_sqlite()
    print("Find your database at:", db_fzirdb)
    translate_buttons()
    
