#!/usr/bin/env python3

import sqlite3
from contextlib import redirect_stdout

target_file = '../../tv.ir'
sqlite_db = '../../flipper_irdb.db'

def get_buttons():
    con = sqlite3.connect(sqlite_db)
    cur = con.cursor()
    
    buttons = cur.execute("""
                SELECT btntrans.button
	            ,irbutton.type
                ,irbutton.protocol
	            ,irbutton.address
	            ,irbutton.command
	            ,'# ' || COUNT(irbutton.name)
	    FROM irbutton
		    JOIN irfile ON (irbutton.md5hash = irfile.md5hash)
			LEFT JOIN btntrans ON (irbutton.name = btntrans.name)
	    WHERE irbutton.Type LIKE 'parsed' AND irfile.category = 'TVs' AND btntrans.button IN ('Power','Vol_up','Vol_dn','Mute','Ch_next','Ch_prev')
	    GROUP BY irbutton.protocol,irbutton.address,irbutton.command
	    ORDER BY COUNT(irbutton.name) DESC; """)
    
    with open(target_file, 'w') as tfile:
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
    get_buttons()
    print("Find your assets file at:", target_file)