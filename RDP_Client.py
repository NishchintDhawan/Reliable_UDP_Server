from socket import *
import time
import sys
import random
import datetime
import hashlib
import struct

IP_ADDR = sys.argv[1]
PORT = sys.argv[2]
FILENAME = sys.argv[3]
PORT = int(PORT)
s = socket(AF_INET,SOCK_DGRAM)
server_addr = (IP_ADDR, PORT)

# (name, seq. no., ack. no., payload)

#send SYN packet.

def packet_string(name, seq_no, ack_no, payload):
    pack_str = name + "," + str(seq_no) + "," + str(ack_no) + "," + str(payload)  
    return pack_str

seq_no = 0
ack_no = 0

syn = packet_string("SYN", seq_no, ack_no, "1")

s.settimeout(1)

while(True):
    try:
        print("sending syn")
        s.sendto(syn, server_addr)
        data, address = s.recvfrom(1024)
        l = data.split(",")
        name = l[0]
        if(l[0]=="ACK"):
            print("recieved ACK")
            seq_no = int(data.split(",")[2])
            ack_no = int(data.split(",")[1]) + len(data.split(",")[3])
            ack = packet_string("ACK", seq_no, ack_no, "1")
            s.sendto(ack, server_addr)
            break
    except timeout as e:
        continue

# GET: (GET, seq_no, ack_no, payload length)

seq_no = 1
ack_no = 1
y = ""
send_flag = False
recieved = ""

md5_requested_file = ""
md5_recieved_file = ""

get_req = packet_string("GET", seq_no, ack_no, FILENAME)
s.sendto(get_req, server_addr)

while True:
           
    try:
    
        data, address = s.recvfrom(1024)
        
        seq_no = int(data.split(",")[2])
        ack_no = int(data.split(",")[1]) + len(data.split(",")[3])

        pkt = packet_string("ACK", seq_no, ack_no,"1")  

        if(str(data.split(",")[0])=="DATA"):
            x = data.split(",")
            x = x[3:]
            
            z = ",".join(x)
            
            y += z
 
            s.sendto(pkt,server_addr)
            print("packet recieved")

        if(str(data.split(",")[0])=="FIN"):
            pkt = packet_string("ACK", seq_no, ack_no,"1") 
            s.sendto(pkt, server_addr)
            
            break        
        
        if(str(data.split(",")[0]) == "MD5"):
            pkt = packet_string("ACK", seq_no, ack_no,"1") 
            s.sendto(pkt, server_addr)
            md5_requested_file = (data.split(",")[3])
            continue              


    except timeout as e :
        print("timeout, didnt receive packet.")
        continue

print(y)

print("MD5 of requested file:", md5_requested_file)

h = hashlib.md5()
h.update(y)
print("MD5 of reecieved file:", h.hexdigest())

new_file = open("recieved_file.txt", "w+")

new_file.write(y)

s.close()

  
