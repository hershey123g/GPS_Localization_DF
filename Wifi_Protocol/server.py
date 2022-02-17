import socket
import pickle
import time

#setup socket server
HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('10.0.0.141', 1234))
s.listen(5)

clientsocket, address = s.accept()  

i = 0
while i < 5:
    full_msg=''
    new_msg = True
    space_holder = "0"
    space_holder = f"{len(space_holder):<{HEADERSIZE}}" + space_holder
    clientsocket.send(bytes(space_holder, "utf-8"))
    #print("This is the initial length: ")
    #print(len(full_msg))
    while True:
        msg = clientsocket.recv(16)
        if new_msg == True:
            #print("new msg len: ", msg[:HEADERSIZE])
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        #print(f"full message length: {msglen}")

        full_msg = full_msg + msg.decode("utf-8")

        #print(len(full_msg))

        if len(full_msg) - HEADERSIZE == msglen:
            #print("full msg recieved")
            #print(full_msg[HEADERSIZE:])
            message = full_msg[HEADERSIZE:]
            print(message)
            if message == "Requesting Help!":
                i = i + 1
            #print(i)
            break
time.sleep(1)
b = 0
while True:
    ack_msg = "Acknowledged"
    ack_msg = f"{len(ack_msg):<{HEADERSIZE}}" + ack_msg
    clientsocket.send(bytes(ack_msg, "utf-8"))
    b = b + 1
    if b > 0:
        break
print("Sending coordinates")
count = 0
while True:
    time.sleep(1)
    array = [1,2,3,4,5,6,7,8,9]
    coord_msg = pickle.dumps(array)
    coord_msg = bytes(f"{len(coord_msg):<{HEADERSIZE}}", "utf-8") + coord_msg
    clientsocket.send(coord_msg)
    count = count + 1
    if count > 4:
        time.sleep(1)
        done = "Process Complete"
        done_msg = pickle.dumps(done)
        done_msg = bytes(f"{len(done_msg):<{HEADERSIZE}}", "utf-8") + done_msg
        clientsocket.send(done_msg)
        break
clientsocket.close()


    
