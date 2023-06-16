#!/usr/bin/env python3

import re

#full_irpath = 'helper/Flipper-IRDB/Miscellanous/Brand_Unknown/HDMI_Switch.ir'
#full_irpath = 'helper/Flipper-IRDB/Miscellanous/Brand_Unknown/LED_Candles.ir'
full_irpath = 'helper/Flipper-IRDB/Miscellanous/MovinFlame/MovinFlame_LED_Candle.ir'

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

        buttons.append(btnname+","+btntype+","+btnprot+","+btnaddr+","+btncomm)

    return(buttons)


def button_encode(btn_data):

    # The recorded pulse is alternate on/off
    ### Header 
    # Significant longer than data.
    # At least one long on to calibrate the AGC, oftern followed by a shorter off
    ### Data
    ## Manchester encoding, signal 1ms:
    # - 0 -> Off 0,5ms/On  0,5ms (signal 1ms) - 1:1
    # - 1 -> On  0,5ms/Off 0,5ms (signal 1ms) - 1:1
    ## Pulse distance control:
    # - 0 -> On 0,1ms/Off 0,9ms (signal 1ms) - 1:9
    # - 1 -> On 0,1ms/Off 1,9ms (signal 2ms) - 1:19
    ## Pulse length control:
    # - 0 -> On 0,5ms/Off 0,5ms (signal 1ms) - 1:1
    # - 1 -> On 0,5ms/Off 1,5ms (signal 2ms) - 1:3

    data_raw = [int(numeric_string) for numeric_string in btn_data.split(" ")]
    divisor = min(data_raw)

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

if __name__ == '__main__':
    encbtns = get_irbutton(full_irpath)

    for encbtn in encbtns:
        encbtn = encbtn.split(",")
        encoded = button_encode(encbtn[4])
        print(encoded)
