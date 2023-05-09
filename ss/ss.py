import sys
import socket
import types
import getopt
import random
import os
from urllib.parse import urlparse
import subprocess
import pickle

SEPARATOR = "<SEPARATOR>"

def getPortNumber():
        port = 0
        if len(sys.argv) is 3:
                try:
                        opts, args = getopt.getopt(sys.argv[1:], "p:")
                except getopt.GetoptError as err:
                        print(err)
                        sys.exit(2)
                for opt, arg in opts:
                        if opt == "-p":
                                port = arg
                        else:
                                assert False, "unhandled option"
        else:
                port = 20000
        return port

def getHostName():
        hostName = socket.gethostname()
        return hostName

def getHostIP(hostname):
        ip = socket.gethostbyname(hostname)
        return ip

def getURL(payload_in):
        size = len(payload_in)
        url = payload_in[size - 1]
        return url

def isLast(payload_in):
        if int(payload_in[0]) == 0:
                return True
        else:
                return False

def getRandSS(payload_in):
        rand_indx = random.randint(1, (len(payload_in) - 1) - 1)
        nextSS = payload_in[rand_indx]
        return nextSS

def removeNextSS(payload_in, nextSS):
        payload_in.remove(nextSS)
        temp = int(payload_in[0]) - 1
        payload_in[0] = temp
        
        
 def runcmd(cmd, verbose = False, *args, **kwargs):
        process = subprocess.Popen(
                cmd,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True
        )
        std_out, std_err = process.communicate()
        # if verbose:
        #       print(std_out.strip(), std_err)
        pass

#main program

myport = getPortNumber()
myhostname = getHostName()
myip = getHostIP(myhostname)
# print("SS is running on host name {} ({}) and port {}".format(myhostname, myip, myport))
print(f"ss <{myip}, {myport}>")

listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listeningSocket.bind((myip, int(myport)))
listeningSocket.listen(4)

# print("Listening for incoming connections...")
csocket, addr = listeningSocket.accept()
# print("Connection recieved")

filename=""

recv_data = csocket.recv(1024)
if recv_data:
        payload_in = pickle.loads(recv_data)
        # print("Payload: " + str(payload_in))
        url = getURL(payload_in)
        print("Request: " + url)

if isLast(payload_in) == True:
        print("Chainlist is empty")
        if url.find("/") == -1:
                filename = "index.html"
                print("Issuing wget for file " + filename)
                # print("filename: " + filename)
                wget_cmd = "wget -O " + filename + " " + str(url)
                # print("wget command:  " + wget_cmd)
                runcmd(wget_cmd, verbose = True)
                # print("sending file...")              
        else:
                urlstr = urlparse(url)
                filename = os.path.basename(urlstr.path)
                print("Issuing wget for file " + str(filename))
                # print("Filename: " + filename)
                wget_cmd = "wget -O " + filename + " " + str(url)
                # print("wget command:  " + wget_cmd)
                runcmd(wget_cmd, verbose = True)
                # print("sending file...")
        print("File received")
        ## send to previous ss          
        # csocket.sendall(b"here is your file")
        ##
        print("Relaying file...")
        csocket.send(f"{filename}".encode())
        with open(filename, "rb") as f:
                while True:
                        bytes_read = f.read(1024)
                        if not bytes_read:
                                break
                        csocket.sendall(bytes_read)
        print("Goodbye!")
        
 if isLast(payload_in) == False:
        nextSS = getRandSS(payload_in)
        print("Next ss is: " + str(nextSS))
        ssIP = nextSS.split(" ")[0]
        ssPort = int(nextSS.split(" ")[1])
        removeNextSS(payload_in, nextSS)
        # print("list after removing next: " + str(payload_in))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SSaddr = (ssIP, ssPort)
        # print("Starting connection to {}...".format(SSaddr))

        try:
                sock.connect(SSaddr)
        except ConnectionRefusedError as err:
                print(err)
                sys.exit(2)

        # print("Connection established.")

        picklepayload = pickle.dumps(payload_in)
        sock.send(picklepayload)

        print("Waiting for file")
        print("...")
        #recieves from ss
        # incomingfile = sock.recv(1024)
        # print(incomingfile)
        filename = sock.recv(1024).decode()
        filename = os.path.basename(filename)
        with open(filename, "wb") as f:
                while True:
                        bytes_read = sock.recv(1024)
                        if not bytes_read:
                                break
                        f.write(bytes_read)
                        
        print("Relaying file...")
        #send back to prev ss
        # csocket.send(b"hello from ss")
        csocket.send(f"{filename}".encode())
        with open(filename, "rb") as f:
                while True:
                        bytes_read = f.read(1024)
                        if not bytes_read:
                                break
                        csocket.sendall(bytes_read)
        os.remove(filename)

        print("Goodbye!")
        csocket.close()
        sock.close()
        listeningSocket.close()
