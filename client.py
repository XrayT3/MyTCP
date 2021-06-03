import socket
from socket import AF_INET, SOCK_DGRAM
import os
import crcmod
import hashlib
import math

# host = '127.0.0.1' # localhost
host = '192.168.30.12'
N = 100
port = 6666
bufsize = 967
sockaddr = (host, port)
uClientSock = socket.socket(AF_INET, SOCK_DGRAM)
uClientSock.bind(('192.168.30.12', 8888))
uClientSock.settimeout(1)

#file for send
#file = input('write file address\n')
file = '123.jpg'
# file = '0.txt'
name = os.path.basename(file)
size = str(os.path.getsize(file))
count_packages = math.ceil(int(size) / bufsize)
print('name -', name)
print('size of file -', size, 'byte')
print('count of packages - ', count_packages)

def get_hash_file():
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def make_package(b_data, number):
    crc32_func = crcmod.mkCrcFun(0x104c11db7, initCrc=0, xorOut=0xFFFFFFFF)
    crc = crc32_func(b_data)
    while crc < 1000000000:
        crc *= 10
    b_data = str(crc).encode() + b_data
    while len(number) < 5:
        number = '0' + number
    b_data = number.encode() + b_data
    return b_data

def make_dir():
    number = 1
    with open(name, "rb") as f:
        buf = f.read(bufsize)
        while (buf):
            package = make_package(buf, str(number))
            with open('packages/' + str(number), "wb") as p:
                p.write(package)
            p.close()
            buf = f.read(bufsize)
            number += 1
    f.close()

def check_crc(package):
    crc32_func = crcmod.mkCrcFun(0x104c11db7, initCrc=0, xorOut=0xFFFFFFFF)
    data = package
    data = data[10:]  # cut number and crc from the package
    crc = crc32_func(data)  # counting my crc
    while crc < 1000000000:
        crc *= 10
    package_crc = package[:10]  # finding package crc
    if int(crc) == int(package_crc):
        return True
    return False

#send N packages and return string array with numbers of sent packages
def send_N_packages():
    global N
    files = os.listdir('packages')
    numbers = ''
    for i in range(N):
        if (i == len(files)):
            break
        with open('packages/' + files[i], "rb") as f:
            buf = f.read()
        f.close()
        numbers += str(files[i]) + ' '
        uClientSock.sendto(buf, sockaddr)
    #print(numbers)
    try:
        data, addr = uClientSock.recvfrom(bufsize)
        #print('package - ', data)
        try:
            if check_crc(data):
                data = data[10:]
                #print('data - ', data)
                g_numbers = (data.decode()).split()
                #print('return - ', g_numbers)
                return g_numbers
            else:
                send_N_packages()
        except Exception:
            print('Error decode')
            send_N_packages()
    except socket.timeout:
        #print('Timeout')
        send_N_packages()

def send_file():
    global count_pck
    print('send file')
    while (len(os.listdir('packages')) > 0):
        print('count left packages - ', len(os.listdir('packages')))
        g_numbers = send_N_packages()
        while g_numbers is None:
            g_numbers = send_N_packages()
        for number in g_numbers:
            if os.path.isfile('packages/' + number):
                os.remove('packages/' + number)
            #else:
                #print("Error: %s file not found" % number)

def send_info(package):
    uClientSock.sendto(package, sockaddr)
    try:
        data, addr = uClientSock.recvfrom(bufsize)
        send_file()
    except socket.timeout:
        print('timeout')
        send_info(package)

def make_info():
    info = name + '!' + size + '!' + get_hash_file()
    b_data = info.encode()
    package = make_package(b_data, '00000')
    send_info(package)

# start program
def start():
    make_dir()
    make_info()
    try:
        data, addr = uClientSock.recvfrom(bufsize)
        print('got final answer')
    except socket.timeout:
        print('last_timeout')
    if data.decode() == 'Repeat':
        start()

start()
for i in os.listdir('packages'):
    os.remove('packages/' + str(i))
# os.rmdir('packages')
