btnaddr = "AA 00 00"
btnaddr_arr = btnaddr.split(" ")

#print(format(bin(int('1'+btnaddr_arr[0], 16))).zfill(2))
#print(bin(int('1'+btnaddr_arr[0], 16)))
#binary_str = bin(int(btnaddr_arr[0], 16)) #[2:].zfill(8)
#binary = bin(binary_str)
#print(binary_str)
print(bin(int(btnaddr_arr[0], 16))[2:].zfill(8))
btnaddr2 = (''.join(['1' if i == '0' else '0' for i in bin(int(btnaddr_arr[0], 16))[2:].zfill(8)]))
print(hex(int(btnaddr2,2))[2:])


#sserdda = format((bin(int('1'+btnaddr_arr[0], 16))[3:])).zfill(2)