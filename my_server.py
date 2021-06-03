import socket
from socket import AF_INET, SOCK_DGRAM
import crcmod
import math
import os
import hashlib

host = ''
port = 6666
bufsize = 1015
sockaddr = (host, port)
name = 'name'
size = 0
data_hash = 'hash'
addr = ('192.168.30.12', 5555)
uServerSock = socket.socket(AF_INET, SOCK_DGRAM)
uServerSock.bind(sockaddr)
count = 0
prev_number = 1
sendnum = 3


def make_file():
    files = os.listdir('packages') # get list of all data
    data = [int(number) for number in files] # change array format from string to int
    data = sorted(data) #sorted 1, 2, 3...
    with open(name, "wb") as f: # open our file (picture)
        for i in data:
            with open('packages/' + str(i), "rb") as d: # open data
                buf = d.read()
            d.close()
            f.write(buf)
            os.remove('packages/' + str(i))
    f.close()
    # os.rmdir('packages')

def clear_file(name):
    with open(name, "wb") as f:
        pass
    
def check_package(package):
    crc32_func = crcmod.mkCrcFun(0x104c11db7, initCrc=0, xorOut=0xFFFFFFFF)
    data = b''
    data = package
    data = data[15:] #cut number and crc from the package
    crc = crc32_func(data) #counting my crc
    while crc < 1000000000:
        crc *= 10 
    package_crc = package[5:15] #finding package crc
    if int(crc) != int(package_crc):
        return False
    return True
     
def get_packages():
    global addr, bufsize, sendnum 
    packages = ['1', '1', '1']
    for i in range(sendnum):
        package, addr = uServerSock.recvfrom(bufsize)
        if check_package(package) == True:
            packages[i] = package
    print("pack len ", len(packages))
    return packages

def get_info():
    global name, size, data_hash, count, addr
    data, addr = uServerSock.recvfrom(bufsize)
    if (check_package(data) == True):
        data = data[15:len(data)] #cut the packge for data
        data = data.decode()
        info = data.split('!') #split the data into pats
        name = info[0]
        size = info[1]
        data_hash = info[2]
        count = math.ceil(int(size) / 967)
        print("Name ", name)
        print("Size ", size)
        print("Hash ", data_hash)
        print("Count ", count)
        uServerSock.sendto("Info get".encode(), addr)
 
def get_hash_file():
    hash_md5 = hashlib.md5()
    with open(name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def check_hash(hash1, hash2):
    if hash1 != hash2:
        return False
    return True
   
def get_file():
    global addr
    got_packages_num = 0
    while (got_packages_num != count):
        packages = get_packages()
        print("Got packages")
        got_packages_num += len(packages)
        print("Num got packages ", got_packages_num)
        answer = ''
        for package in packages:
            data = package
            number = data[:5]
            number = int(number)
            print("Package num ", number)
            data = data[15:]
            answer += str(number) + ' '
            print("Answer ", answer)
            with open('packages/' + str(number), "wb") as f:
                f.write(data) 
        if(len(answer) != 0):
            print("Answer sent")
            uServerSock.sendto(answer.encode(), addr) #send numbers of received packages

def download_file():
    global addr
    get_info()
    get_file()
    make_file()
    my_hash = get_hash_file()
    print("my hash ", my_hash)
    print("data ha ", data_hash)
    if check_hash(data_hash, my_hash) == False:
        uServerSock.sendto("Repeat".encode(), addr)
        download_file()

#start program
#clear_file("1.jpg")
download_file()  
a = input("Konec")       