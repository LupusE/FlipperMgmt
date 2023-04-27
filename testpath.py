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


def get_irfileheader(full_irpath):
    
    splitcategory = os.path.normpath(full_irpath).split(os.sep)[-3]
    splitbrand = os.path.normpath(full_irpath).split(os.sep)[-2]
    ## correct category for console/Nintendo/Gameboy/ and similar
    if splitcategory not in category_fzirdb:
        splitcategory = os.path.normpath(full_irpath).split(os.sep)[-4]
        splitbrand = os.path.normpath(full_irpath).split(os.sep)[-3]
    if splitcategory in ['git']:
        splitcategory = os.path.normpath(full_irpath).split(os.sep)[-2]
        splitbrand = 'NULL'
    
    splitfile = os.path.normpath(full_irpath).split(os.sep)[-1]
    ## create hash for identify changes
    with open(str(full_irpath), 'rb') as md5file:
        digest = hashlib.file_digest(md5file, 'md5')

    return(splitcategory, splitbrand, splitfile, digest.hexdigest())

print(get_irfileheader('/home/lupus/git/Flipper-IRDB/MiniDisc/Sony_RM-D10E.ir'))
print(get_irfileheader('/home/lupus/git/Flipper-IRDB/Projectors/Epson/Epson_EB-575wi.ir'))
print(get_irfileheader('/home/lupus/git/Flipper-IRDB/Consoles/Nintendo/Gameboy/Pokemon_Silver_Mystery_Gift.ir'))

