import os
#from os import walk
#from os import path


## add _CONVERTED_ directory = 1
ext_converted = 1

dir_fzirdb = os.path.join(os.getcwd(), '..', 'Flipper-IRDB')
db_fzirdb = os.path.join(os.getcwd(), '..', 'flipper_irdblite.db')

category_fzirdb = next(os.walk(dir_fzirdb))[1]

ext_irdb_include = (['.ir'])
dir_irdb_exclude = set([ os.path.normpath(dir_fzirdb+'/.git*') ])
if ext_converted == 0:
    dir_irdb_exclude.append(os.path.normpath(dir_fzirdb+'/_Converted_'))



## Get filtered 'folder/files' as list
######################################

def get_irfiles(dir_fzirdb):
    irpath_list = []
    for root, dir, files in os.walk(dir_fzirdb, topdown=True):
        for irfile in files:
            if (not root.startswith(tuple(dir_irdb_exclude)) and (irfile.endswith(tuple(ext_irdb_include)))):
                    #irpath_list.append(root+'/'+irfile)
                    irpath_list.append(os.path.join(root, irfile))
            else:
                pass
    print("IR files FlipperIRDB to process: ", len(irpath_list))
    return(irpath_list)


get_irfiles(dir_fzirdb)