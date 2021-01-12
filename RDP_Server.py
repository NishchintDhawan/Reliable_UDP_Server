# We will need the following module to generate randomized lost packets
import random
import sys
import time
from socket import *
import struct
import math
import hashlib

# Create a UDP socket 

s = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket.


# (name, seq. no., ack. no., payload)

IP_ADDR = sys.argv[1]
PORT_NUMBER =  sys.argv[2]
PACKET_LOSS = sys.argv[3]
server_addr = (IP_ADDR, int(PORT_NUMBER))

s.bind(server_addr)
client_addr = None

seq_no = 0
ack_no = 0

def packet_string(name, seq_no, ack_no, payload):

    pack_str = name + "," + str(seq_no) + "," + str(ack_no) + "," + (payload) 
    
    return pack_str

def send_data(filename, seq_no, ack_no):
    
    flag = False

    with open(filename, "r") as f:
        s.settimeout(1)
        file_string = f.read()
        index_range = 10
        
        chars = ""
        list_words = []
        
        for i in range(0,len(file_string)):
            chars += file_string[i]

            if(i==0):
                continue
            if(i%1000==0):
                list_words.append(chars)
                chars = ""
                
        if(chars!=""):
            list_words.append(chars)

        h = hashlib.md5()
        h.update(file_string)

        pkt = packet_string("MD5", seq_no, ack_no, h.hexdigest())

        while True:
            try:
                s.sendto(pkt, client_addr)
                data, address = s.recvfrom(1024)
                
                if(data.split(",")[0] == "ACK"):
                    seq_no = int(data.split(",")[2])
                    ack_no = int(data.split(",")[1]) + len(data.split(",")[3])
                    break

            except timeout as e:
                print("packet lost, retransmitting")
            

        print("Length of list words: ", len(list_words))
        i=0

        while(i < len(list_words)):
            try:
                if(PACKET_LOSS=="TRUE"):
                    rand = random.randint(1, 100)
                    if rand > 20 :
                        pkt = packet_string("DATA", seq_no, ack_no, list_words[i] )                  
                        s.sendto(pkt,client_addr)  
                        print("packet sent")
                else:  
                    pkt = packet_string("DATA", seq_no, ack_no, list_words[i] )                  
                    s.sendto(pkt,client_addr)  
                    print("packet sent")

                while True:
                    data, address = s.recvfrom(1024)
                    if(str(data.split(",")[0]) =="ACK"):
                        seq_no = int(data.split(",")[2])
                        ack_no = int(data.split(",")[1]) + len(data.split(",")[3])
                        print("ack recieved")
                        i+=1
                        break
                
            except timeout as e:
                print("packet lost, retransmitting")                

        pkt =  packet_string("FIN",seq_no,ack_no, "1")
        print("sending FIN packet")
        s.sendto(pkt,client_addr)
        while True:
           data, address = s.recvfrom(1024)
           if(data.split(",")[0]=="ACK"):
               print("recieved ACK")
               break

    return


s.settimeout(1)

while True: 
    try:
        data, address = s.recvfrom(1024)
        data = data
        client_addr = address
        l = data.split(",")
        if(l[0]=="SYN"):
            seq_no = 0
            ack_no = 1
            payload = "1"
            ack = packet_string("ACK" ,seq_no , ack_no , payload)
            s.sendto(ack, address)
        elif (l[0] == "GET"):
            seq_no = int(l[2])
            ack_no = int(l[1]) + len(l[3])   
            send_data(l[3], seq_no, ack_no)
            
            
    except timeout as e:
        continue

s.close()