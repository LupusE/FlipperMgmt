import os
import hashlib

dir_fzirdb = os.path.join(os.getcwd(), '..', 'Flipper-IRDB')

exclude_converted = 1


ext_irdb_include = (['.ir'])
dir_irdb_exclude = set([ os.path.join(dir_fzirdb, '.git*') ])
if exclude_converted == 0:
    dir_irdb_exclude.append(os.path.join(dir_fzirdb,'_Converted_'))



## Get filtered 'folder/files' as list
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

get_irfiles(dir_fzirdb)
