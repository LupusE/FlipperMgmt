#!/usr/bin/env python3

import sqlite3
from contextlib import redirect_stdout

target_dir = 'assets'
sqlite_db = os.path.normpath(os.getcwd()+'/../flipper_irdblite.db')

def get_buttons(ircategory):
    con = sqlite3.connect(sqlite_db)
    cur = con.cursor()
    
    match ircategory:
        case 'TVs':
            where_clause = "irfile.category = 'TVs' AND btntrans.button IN ('Power','Vol_up','Vol_dn','Mute','Ch_next','Ch_prev')"
            target_file = 'tv.ir'
        case 'Audio':
            where_clause = "irfile.category = 'Audio_Receivers' AND btntrans.button IN ('Power','Vol_up','Vol_dn','Mute')"
            target_file = 'audio.ir'
        case 'Projectors':
            where_clause = "irfile.category = 'Projectors' AND btntrans.button IN ('Power','Vol_up','Vol_dn','Mute')"
            target_file = 'projectros.ir'
        case 'Fans':
            where_clause = "irfile.category = 'Fans' AND btntrans.button IN ('Power','Mode','Speed_dn','Speed_up','Rotate','Timer')"
            target_file = 'fans'
        case default:
           where_clause = "irfile.category = 'TVs' AND btntrans.button IN ('Power','Vol_up','Vol_dn','Mute','Ch_next','Ch_prev')"
           target_file = 'tv.ir'

    sql = ("""
                SELECT btntrans.button
	            ,irbutton.type
                ,irbutton.protocol
	            ,irbutton.address
	            ,irbutton.command
	            ,'# ' || COUNT(irbutton.name)
	    FROM irbutton
		    JOIN irfile ON (irbutton.md5hash = irfile.md5hash)
			LEFT JOIN btntrans ON (irbutton.name = btntrans.name)
        WHERE %s
	    GROUP BY irbutton.protocol,irbutton.address,irbutton.command
	    ORDER BY COUNT(irbutton.name) DESC; """) % where_clause
    print(sql)

    buttons = cur.execute(sql)
	
    with open(target_dir+target_file, 'w') as tfile:
        with redirect_stdout(tfile):
            print("Filetype: IR library file")
            print("Version: 1")
            print("#")
            
            for button in buttons:
                btnname = "name: "+button[0]
                btntype = "type: "+button[1]
                if button[1] == 'parsed':
                    btnproto = "protocol: "+button[2]
                    btnaddress = "address: "+button[3]
                    btncommand = "command: "+button[4]
                if button[1] == 'raw':
                    btnproto = "frequency: "+button[2]
                    btnaddress = "duty_cycle: "+button[3]
                    btncommand = "data: "+button[4]
    
                print(btnname)
                print(btntype)
                print(btnproto)
                print(btnaddress)
                print(btncommand)
                print("#")

if __name__ == '__main__':
    get_buttons('TVs')
    #get_buttons('Audio')
    #get_buttons('Projectors')
    #get_buttons('Fans')
    
    print("Find your assets file at:", target_dir)