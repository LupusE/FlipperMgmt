## Based on https://forum.flipperzero.one/t/how-to-emulate-fdx-b-cat-tag-hex/13050/10
## Purpose is to convert Flipper Zero 125 kHz Dumps [FDX-B] from hex to dec and back.
## Generate Flipper Zero .rfid file, if filename is given.

from contextlib import redirect_stdout


def animalid2hex(animal_id=""): # convert 15 digit animal id to hex data [FDX-B]
    animal_id = animal_id.replace("-","").replace(" ","")
    if not animal_id or (not len(animal_id) == 15):
        animal_id = int(input("Enter the 15 digit of animal id: "))
    
    print("Clean ID: ",animal_id)
    last_10_bits_reversed = bin(int(str(animal_id)[:3]))[2:].zfill(10)[::-1]
    first_38_bits_reversed = bin(int(str(animal_id)[3:]))[2:].zfill(38)[::-1]
    hex_data = (hex(int((first_38_bits_reversed + last_10_bits_reversed), 2))[2:].zfill(12)).upper() + "0001000010"

    print("22 character hex data [FDX-B]: ", hex_data)
    return(hex_data)


def hex2animalid(hex_data=""): # convert hex data [FDX-B] to 15 digit base 10 animal id
    hex_data = hex_data.replace(":","").replace(" ","")

    if (not hex_data) or (not len(hex_data) == 22):
        hex_data = input("Enter 22 character of hex data [FDX-B]: ")
    if not hex_data.endswith("0001000010"):
        print("It's not an animal tag!")

    print("Clean Hex: ", hex_data)
    binary_num = bin(int(hex_data[:12], 16))[2:].zfill(48)
    first_38_decimal = (int(((binary_num[:38])[::-1]), 2))
    last_10_decimal = (int(((binary_num[38:])[::-1]), 2))
    animal_id = int(str(last_10_decimal)[:3] + (str(first_38_decimal)[:12]).zfill(12))

    print("Animal ID: ", animal_id)
    return(animal_id)

def write_rfidfile(filename, rfid_data=""):
    with open(filename, 'w') as tfile:
        with redirect_stdout(tfile):
            print("Filetype: Flipper RFID key")
            print("Version: 1")
            print("Key type: FDX-B")
            print("Data:", ' '.join(rfid_data[i:i+2] for i in range(0, len(rfid_data), 2)))


if __name__ == '__main__':
    filename = ""
    filename = input("Enter filename. [Enter to skip]: ")
    data = input("Enter ID:")
    data = (data.replace(":","").replace("-", "").replace(" ","")).upper()
    
    match len(data):
        case 22:
            hex2animalid(data)
            rfid_data = data
        case 15:
            rfid_data = animalid2hex(data)
        case _:
            print("ID not valid (animal tag or hex [FDX-B])")
    
    if filename:
        write_rfidfile(filename, rfid_data)
