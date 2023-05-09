import sys
import socket
import types
import getopt
import random
import os
from urllib.parse import urlparse
import subprocess
import pickle

def getURL():
        url = sys.argv[1]
        return url
    
def getChainfile():
        chainfile = ""
        if len(sys.argv) == 2:
                chainfile = "chaingang.txt"
        elif len(sys.argv) == 4:
                try:
                        opts, args = getopt.getopt(sys.argv[2:], "c:")
                except getopt.GetoptError as err:
                        print(err)
                        sys.exit(2)
                for opt, arg in opts:
                        if opt == "-c":
                                chainfile = arg
                        else:
                                assert False, "unhandled option"
        return chainfile
      
def readChainfile(filename):
        try:
                f = open('chaingang.txt', 'r')
        except FileNotFoundError as err:
                print("Unable to find chaingang.txt.")
        else:
                print("File found.")
        content = f.read().splitlines()
        return content

def getRandomSS(SSlist):
        next = random.choice(SSlist[1:])
        return next

def getSSaddr(ssIP, ssPort):
        return (ssIP, int(ssPort))

def getPayload(SSlist, url):
        SSlist.append(url)
        return SSlist
    
 def removeNextSS(SSlist, ssIP):
        for item in SSlist:
                if ssIP in item:
                        SSlist.remove(item)
        temp = int(SSlist[0]) - 1
        SSlist[0] = str(temp)
        return SSlist

def runcmd(cmd, verbose = False, *args, **kwargs):
        process = subprocess.Popen(
                cmd,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True
        )
        std_out, std_err = process.communicate()
        if verbose:
                print(std_out.strip(), std_err)
        pass

#main program
print("awget:")

if len(sys.argv) == 2:
        url = getURL()
        # print("URL to retrieve: " + url)
        print("Request: " + url)
        file = getChainfile()
        # print("Chainfile to read from: " + file)
        SSlist = readChainfile(file)
        print("Chain list is: " + str(SSlist))

if len(sys.argv) == 4:
        url = getURL()
        # print("URL to retrieve: " + url)
        print("Request: " + url)
        file = getChainfile()
        # print("Chainfile to read from: " + file)
        SSlist = readChainfile(file)
        print("Chain list is: " + str(SSlist))
        
nextSS = getRandomSS(SSlist)
ssIP = nextSS.split(" ")[0]
ssPort = nextSS.split(" ")[1]
getPayload(SSlist, url)
connid = 1
# print("Next random SS IP: " + ssIP)
# print("Next random SS port: " + ssPort)
print(f"Next SS is <{ssIP}, {ssPort}>")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SSaddr = getSSaddr(ssIP, ssPort)
# print("Starting connection {} to {}...".format(connid, SSaddr))

try:
        sock.connect(SSaddr)
except ConnectionRefusedError as err:
        print(err)
        sys.exit(2)
      
      
# print("Connection established.")
# print("Stripping next ss from payload...")
newPayload = removeNextSS(SSlist, ssIP)
# print("New payload: "+ str(newPayload))
# print("Sending payload: " + str(newPayload))

picklepayload = pickle.dumps(newPayload)
sock.send(picklepayload)

print("Waiting for file...")
print("..")

# incomingfile = sock.recv(1024).decode()
# print(incomingfile)

filename = sock.recv(1024).decode()
filename = os.path.basename(filename)
with open(filename, "wb") as f:
        while True:
                bytes_read = sock.recv(1024)
                if not bytes_read:
                        break
                f.write(bytes_read)
sock.close()

print(f"Received file {filename}")
print("Goodbye!")
