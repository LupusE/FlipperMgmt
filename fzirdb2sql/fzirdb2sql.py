#!/usr/bin/env python3

import re
import os
import hashlib
import sqlite3
import csv
import sys

## Try to parse raw data to compareable format
rawanalysis = 1
if sys.version_info <= (3,9):
    print("No RAW Analysis possible. Function match() available from Python 3.10")
    print("Python version found:", sys.version)
    rawanalysis = 0

## add _CONVERTED_ directory = 1
exclude_converted = 1

dir_fzirdb = os.path.join(os.getcwd(), '..', 'Flipper-IRDB')
db_fzirdb = os.path.join(os.getcwd(), '..', 'flipper_irdblite.db')

category_fzirdb = next(os.walk(dir_fzirdb))[1]

ext_irdb_include = (['.ir'])
dir_irdb_exclude = set([ os.path.join(dir_fzirdb, '.git*') ])
if exclude_converted == 0:
    dir_irdb_exclude.append(os.path.join(dir_fzirdb,'_Converted_'))

## IR file pattern for one button in regex
btn_pattern = re.compile(r"""
                name: (.*)\n
                type: (.*)\n
                (protocol|frequency): (.*)\n
                (address|duty_cycle): (.*)\n
                (command|data): (.*)\n
                """, re.VERBOSE | re.MULTILINE)


## Get filtered [folder/files, md5hash] as list
######################################

def get_irfiles(dir_fzirdb):
    irpath_list = []
    for root, dir, files in os.walk(dir_fzirdb, topdown=True):
        for irfile in files:
            if (not root.startswith(tuple(dir_irdb_exclude)) and (irfile.endswith(tuple(ext_irdb_include)))):
                    irfilepath = os.path.join(root, irfile)
                    with open(str(irfilepath), 'rb') as md5file:
                        digest = hashlib.file_digest(md5file, 'md5')
                    irpath_list.append([irfilepath, digest.hexdigest()])
            else:
                pass
    print(("{} IR files from {} to process").format(len(irpath_list),dir_fzirdb))
    
    return(irpath_list)

    
## Get file header (category, brand, filename, MD5)
######################################

def get_irdbattibutes(full_irpath):

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
    ## create hash as PK for SQL
    with open(str(full_irpath), 'rb') as md5file:
        digest = hashlib.file_digest(md5file, 'md5')

    return(splitcategory, splitbrand, splitfile, digest.hexdigest(), splitsource)


## Get file header (comments)
######################################

def get_irdbcomments(irfile):
    comments = []
    commentstr = ""

    with open(irfile, 'r') as filecomments:
        for line in filecomments:
            if line.startswith("#") and (len(line.strip())) > 1:
                comments.append(line)

    commentstr = "".join(comments)
    #print(commentstr)
    return(commentstr)


## Parse buttons (name, type, protcol/frequency, address/duty_cycle, command/data)
######################################

def get_irbuttons(full_irpath):
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

    # if 'type = raw' then 'proto = frequency', 'address = dutycycle', 'command = data'
    # Frequency is technically fixed at 38MHz for the Flipper Zero
    #   but due to tollerance 40/36 are possible
    # Dutycycle: % of time on (bursts) to be one signal.
    #   To be interpreted as on, the signal must be on 33% of 562,2 us
    # Data is a string of the captued values.
    #   Each value represents alternating length in ms of on/off

    return(buttons)

## Write parsed items to database
######################################

def write2sqlite():
    try:
        con = sqlite3.connect(db_fzirdb)    
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS irfile;")
        cur.execute("DROP TABLE IF EXISTS irbutton;")
        cur.execute("DROP TABLE IF EXISTS ircomment;")
        cur.execute("CREATE TABLE IF NOT EXISTS irfile (category,brand,file,md5hash,source);")
        cur.execute("CREATE TABLE IF NOT EXISTS irbutton (name,type,protocol,address,command,md5hash);")    
        cur.execute("CREATE TABLE IF NOT EXISTS ircomment (comment,md5hash);")
        #cur.execute("DROP TABLE IF EXISTS rawdata;") # old
        #cur.execute("DROP TABLE IF EXISTS rawheader;") # old
        #cur.execute("DROP TABLE IF EXISTS rawmeta;") # old
        cur.execute("DROP TABLE IF EXISTS rawbutton;")        
        if rawanalysis == 1:
            cur.execute("CREATE TABLE IF NOT EXISTS rawbutton (name,header,binarydata,tail,bit,divident,md5hash);")

    except OSError as e:
        print(e)

    print("Getting header and buttons for database",db_fzirdb)
    for irfile in get_irfiles(dir_fzirdb):
        irheader = get_irdbattibutes(irfile)
        cur.execute(("INSERT INTO irfile VALUES ('{}', '{}','{}','{}','{}');").format(irheader[0],irheader[1],irheader[2],irheader[3],irheader[4]))

        ircomments = get_irdbcomments(irfile)
        if (len(ircomments)) != 0:
            ircomments = ircomments.replace("'","") # dirty hack, because sqlite using ' itself
            cur.execute(("INSERT INTO ircomment VALUES ('{}','{}');").format(ircomments,irheader[3]))

        for irbutton in get_irbuttons(irfile):
            irbuttons = (irbutton.split(','))
            cur.execute(("INSERT INTO irbutton VALUES ('{}','{}','{}','{}','{}','{}');").format(irbuttons[0],irbuttons[1],irbuttons[2],irbuttons[3],irbuttons[4],irheader[3]))
            if irbuttons[1] == 'raw' and rawanalysis == 1:
                binary_button = button_raw2binary(irbuttons[4])
                if len(binary_button) > 1:
                    raw_header = ' '.join(binary_button[1])
                    #print(irbuttons[0],binary_button[0],raw_header,binary_button[2],binary_button[3],binary_button[4],irheader[3])
                    cur.execute(("INSERT INTO rawbutton VALUES ('{}','{}','{}','{}','{}','{}','{}');").format(irbuttons[0],binary_button[0],raw_header,binary_button[2],binary_button[3],binary_button[4],irheader[3]))
                    
    con.commit()
    con.close()
    print("Header and buttons written in database",db_fzirdb)

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

# -- Old ----------
# Get min value from array. Devide all values though and convert to INT
# Assume 15000 is the absolute maximum of transmitted mark or space
# Split array by gaps greater than maximum
# -- Old ----------
#
# The goal is to convert from ...912 840 2829... to ...1 3 1... to
# compare with other signals in the database, regardless of repeats.

def button_raw2binary(btn_data):

    # The recorded pulse is alternate on/off
    ### Header 
    # Significant longer than data.
    # At least one long on to calibrate the AGC, followed by a an even or shorter off
    ### Data
    ## Manchester encoding, signal 1ms: (Bi-phase coding)
    # - 0 -> Off 0,5ms/On  0,5ms (signal 1ms) - 1:1
    # - 1 -> On  0,5ms/Off 0,5ms (signal 1ms) - 1:1
    ## Pulse distance control:
    # - 0 -> On 0,1ms/Off 0,9ms (signal 1ms) - 1:9
    # - 1 -> On 0,1ms/Off 1,9ms (signal 2ms) - 1:19
    ## Pulse length control:
    # - 0 -> On 0,5ms/Off 0,5ms (signal 1ms) - 1:1
    # - 1 -> On 0,5ms/Off 1,5ms (signal 2ms) - 1:3

    try:
        data_raw = [int(numeric_string) for numeric_string in btn_data.split(" ")]
    except:
        #print("Nonnumeric value. No import for {}".format(btn_data))
        return()

    divisor = 562.2 #min(data_raw) # old
    if divisor == 0:
        #print("Prevent dividing by zero. No import for {}".format(btn_data))
        return()

    data_normalized = []
    for data_value in data_raw:
        data_normalized.append(int(data_value/divisor))

    data_headdatatail = []
    chunk_size = 2
    loopcnt = 0
    bitcnt = 0
    for chunk in [data_normalized[i:i + chunk_size] for i in range(0, len(data_normalized), chunk_size)]:
        if loopcnt == 0: # handle header data
            data_headdatatail.append(chunk)
        else:
            if len(chunk) == 2: # errorhandling, if last chunk is cut
                                # could be valid! Regarding some protcol
                match chunk[0]*chunk[1]:
                    case 1:
                        data_headdatatail.append(1)
                        bitcnt += 1
                    case 2: # 3 is correct, but there is a tolerance
                        data_headdatatail.append(0)
                        bitcnt += 1
                    case 3:
                        data_headdatatail.append(0)
                        bitcnt += 1
                    case _:
                        data_headdatatail.append(chunk) # just add tail
            else:
                continue # skip smaller chunks
        loopcnt += 1
    #print(data_headdatatail, bitcnt, "bit")

    data_binary = []
    irdata = 1
    step = 8
    for x in range(irdata, bitcnt, step):
        data_binary.append(''.join(map(str,data_headdatatail[x:x+step])))
 
    data_head = data_headdatatail[0]
    data_tail = data_headdatatail[bitcnt+1:]

    return(data_head, data_binary, data_tail, bitcnt, divisor)


## Execute program
######################################

if __name__ == '__main__':
    
    write2sqlite()
    print("Find your database at:", db_fzirdb)
    translate_buttons()
    
