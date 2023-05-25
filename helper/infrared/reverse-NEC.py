#!/usr/bin/env python3

import re

full_irpath = 'helper/Flipper-IRDB/Miscellanous/Brand_Unknown/HDMI_Switch.ir'


btn_pattern = re.compile(r"""
                name: (.*)\n
                type: (.*)\n
                (protocol|frequency): (.*)\n
                (address|duty_cycle): (.*)\n
                (command|data): (.*)\n
                """, re.VERBOSE | re.MULTILINE)

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

        btnaddr_arr = btnaddr.split(" ")
        btncomm_arr = btncomm.split(" ")

        sserdda = format(int(((bin(int('1'+btnaddr_arr[0], 16))[3:])[::-1]), 2),'X').zfill(2)
        dnammoc = format(int(((bin(int('1'+btncomm_arr[0], 16))[3:])[::-1]), 2),'X').zfill(2)

        buttons.append(btnname+","+btntype+","+btnprot+","+btnaddr.replace(btnaddr_arr[0],sserdda)+","+btncomm.replace(btncomm_arr[0],dnammoc))

    return(buttons)


if __name__ == '__main__':
    revbtns = get_irbutton(full_irpath)

    print("Filetype: IR signals file\nVersion: 1")

    for revbtn in revbtns:
        revbtn = revbtn.split(",")
        print("#\nname: ",revbtn[0],"\ntype: ",revbtn[1],"\nprotocol: ",revbtn[2],"\naddress: ",revbtn[3],"\ncommand: ",revbtn[4])
    