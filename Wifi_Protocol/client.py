import socket
import pickle
import time
import board
from adafruit_ht16k33.matrix import Matrix8x8

i2c = board.I2C()
matrix = Matrix8x8(i2c)

matrix.fill(1)  
time.sleep(15)
t_end = time.time() + 15
while time.time() < t_end:
    matrix.fill(1)
    time.sleep(0.1)
    matrix.fill(0)
    time.sleep(0.1)
HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#hostname = socket.gethostname()
#ip_address = socket.gethostbyname(hostname)
#print(ip_address)
s.connect(('10.0.0.141', 1234))
message=''
while True:
    #print("New loop")
    #print(message)
    full_msg=''
    new_msg = True
    while True:
        
        msg = s.recv(16)

        if new_msg == True:
            #print("new msg len: ", msg[:HEADERSIZE])
            msglen = int(msg[:HEADERSIZE])
            new_msg = False
        
        #print(f"full message length: {msglen}")

        full_msg = full_msg + msg.decode("utf-8")

        #print("This is the message length:")
        #print(len(full_msg))

        if len(full_msg) - HEADERSIZE == msglen:
            #print("full msg recieved")
            message = full_msg[HEADERSIZE:]
            #print(message)
            break
    if message == "Acknowledged":
        print("Acknoledged")
        break
    SOS = "Requesting Help!"
    SOS = f"{len(SOS):<{HEADERSIZE}}" + SOS
    s.send(bytes(SOS, "utf-8"))
    #print("Done")
matrix.fill(1)
#count = 0
while True:
    full_msg_two=b''
    new_msg = True
    while True:
        msg_two = s.recv(16)
        if new_msg == True:
            matrix.fill(0)
            #print("new msg len: ", msg_two[:HEADERSIZE])
            msglen = int(msg_two[:HEADERSIZE])
            new_msg = False

        #print(f"full message length: {msglen}")

        full_msg_two = full_msg_two + msg_two

        #print(len(full_msg_two))

        if len(full_msg_two) - HEADERSIZE == msglen:
            #print("full msg recieved")
            #count = count+1
            #print(count)
            coords = pickle.loads(full_msg_two[HEADERSIZE:])
            print(coords)
            break
    if coords == "Process Complete":
        break
t_end_two = time.time() + 15
while time.time() < t_end_two:
    matrix.fill(1)
    time.sleep(1)
    matrix.fill(0)
    time.sleep(1)
