import time
import sys
import pyzed.sl as sl
import cv2
import csv
import math
import socket
import pickle
import jetson.inference
import jetson.utils
import numpy as np
from pymultiwii import MultiWii
from sys import stdout
from findCoordinates import get_cartesian, get_latlon


def main():
    #setup socket server
    HEADERSIZE = 10
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('192.168.43.10', 1234))
    s.listen(5)
    clientsocket, address = s.accept()

    #USB connection for pyMultiWii
    board = MultiWii("/dev/ttyACM0")


    #Waiting for SOS signal
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
                print("[Helper Drone] Time: " + str(time.strftime('%H:%M:%S')) + " Help signal received from Distress Drone")
                if message == "Requesting Help!":
                    i = i + 1
                #print(i)
                break
	

    #Acknoledging SOS signal
    b = 0
    time.sleep(2)
    while True:
        ack_msg = "Acknowledged"
        ack_msg = f"{len(ack_msg):<{HEADERSIZE}}" + ack_msg
        clientsocket.send(bytes(ack_msg, "utf-8"))
        b = b + 1
        if b > 0:
            break

    init = sl.InitParameters()
    cam = sl.Camera()
    status = cam.open(init)
    runtime = sl.RuntimeParameters()
    mat = sl.Mat()
    #depth_map = sl.Mat()
    point_cloud = sl.Mat()
    depth_map = sl.Mat()

    #depth configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.coordinate_units = sl.UNIT.MILLIMETER

    #check for errors
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()
    
    timeStamp = time.time()
    fpsFiltered=0
    net=jetson.inference.detectNet('ssd-mobilenet-v2', ['--model=/home/morsestudio/Downloads/jetson-inference/python/training/detection/ssd/models/Drone_Detectv2/ssd-mobilenet.onnx', '--labels=/home/morsestudio/Downloads/jetson-inference/python/training/detection/ssd/models/Drone_Detectv2/labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'], threshold=0.5)
    dispW=2560
    dispH=720
    font = cv2.FONT_HERSHEY_SIMPLEX


    #loading Aruco Dictionary and Parameters``  `
    ARUCO_DICT = {
        "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
        "DICT_4X4_50": cv2.aruco.DICT_4X4_50
    }
    arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT["DICT_4X4_50"])
    arucoParams = cv2.aruco.DetectorParameters_create()

    #creating csv file and formatting rows
    with open("3-3-test1.csv", "w+") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp(Epoch)", "Direction", "X-coordinate(mm)", "Y-coordinate(mm)", "Z-coordinate(mm)", "Slave Latitude", "Slave Longitude"])
    # for 'q' key whisch is a wait key for exiting
    #print("  Quit the video reading:     q\n")

    #Starting loop
    count = 0
    while True: 
        err = cam.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            cam.retrieve_image(mat)
            #converted to opencv usable array using get_data()
            image_opencv = mat.get_data()
            gray = cv2.cvtColor(image_opencv, cv2.COLOR_BGR2GRAY)
            #Detecting Aruco markers
            (corners, ids, rejected) = cv2.aruco.detectMarkers(gray, arucoDict, parameters=arucoParams)
            #check for atleast 1 aruco marker
            if count == 30:
                time.sleep(1)
                done = "Process Complete"
                print("[Helper Drone] Time: " + str(time.strftime('%H:%M:%S')) + " "+ done)
                done_msg = pickle.dumps(done)
                done_msg = bytes(f"{len(done_msg):<{HEADERSIZE}}", "utf-8") + done_msg
                clientsocket.send(done_msg)
                break
            if len(corners) > 0: 
                ids = ids.flatten()
                #loop detected aruco corners
                for (markerCorner, markerID) in zip(corners, ids):
                    #marker corners are returned in top-left, top-right, bottom-right, and bottom-left order
                    corners = markerCorner.reshape((4,2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners

                    #converting corner coordinates to int type
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))

                    #drawing a box around aruco marker for visualization (can comment out if needed)
                    cv2.line(image_opencv, topLeft, topRight, (0,255,0), 2)
                    cv2.line(image_opencv, topRight, bottomRight, (0,255,0), 2)
                    cv2.line(image_opencv, bottomRight, bottomLeft, (0,255,0), 2)
                    cv2.line(image_opencv, bottomLeft, topLeft, (0,255,0), 2)

                    #computing center, will use for depth calculation
                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)

                    #getting point cloud data
                    cam.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
                    point3D = point_cloud.get_value(cX, cY)
                    xyz_coords = point3D[1]
                    x = xyz_coords[0]
                    y = xyz_coords[1]
                    z = xyz_coords[2]

                    #getting timestamp from zed
                    #timestamp = cam.get_timestamp(sl.TIME_REFERENCE.IMAGE)
                    #time = timestamp.get_seconds()

                    #Getting lat and lon from flight controller
                    GPSdata = board.getData(MultiWii.RAW_GPS)
                    lat = GPSdata[0]
                    lon = GPSdata[1]

                    #Find cartesian coordinates (Mx,My,Mz) of Master drone using lat, lon
                    Mx,My,Mz = get_cartesian(lat,lon)

                    #Find cartesian coordinates of slave drone using vector transformation
                    Sx = Mx+(x/1000)
                    Sy = My+(y/1000)
                    Sz = Mz+(z/1000)

                    #Find latitude, longitude of slave drone using cartesian coordinates(Sx,Sy,Sz) 
                    slave_lat, slave_lon = get_latlon(Sx,Sy,Sz)

                    latitude = float(slave_lat)
                    longitude = float(slave_lon)

                    #Apending data to csv file
                    with open("3-3-test1.csv", "a") as csvfile: 
                        writer = csv.writer(csvfile)
                        writer.writerow([time, markerID, x, y, z, slave_lat, slave_lon])
                    
                    array = [latitude, longitude]
                    coord_msg = pickle.dumps(array)
                    coord_msg = bytes(f"{len(coord_msg):<{HEADERSIZE}}", "utf-8") + coord_msg)
                    clientsocket.send(coord_msg)
                    count = count + 1
                    time.sleep(0.5)
                    
            elif err == sl.ERROR_CODE.SUCCESS:
                height=image_opencv.shape[0]
                width = image_opencv.shape[1]

                frame = cv2.cvtColor(image_opencv, cv2.COLOR_BGR2RGBA).astype(np.float32)
                frame = jetson.utils.cudaFromNumpy(frame)
                
                detections=net.Detect(frame, width, height)
                for detect in detections:
                    ID = detect.ClassID
                    item = net.GetClassDesc(ID)
                    top = int(detect.Top)
                    left = int(detect.Left)
                    bottom = int(detect.Bottom)
                    right = int(detect.Right)
                    #print(item, top, left, bottom, right)
                    cv2.rectangle(image_opencv, (left, top), (right, bottom), (0,0,255), 2)
                    cv2.putText(image_opencv, str(item), (left + 5, top + 30), font, 1, (0,0,255),2)

                dt = time.time() - timeStamp
                timeStamp = time.time()
                fps = 1/dt
                fpsFiltered = 0.9*fpsFiltered + 0.1*fps

                cv2.putText(image_opencv, str(round(fpsFiltered, 1)) + ' fps ', (0,30), font, 1, (255,0,0), 2)


    cam.close()
    sys.exit()


if __name__ == "__main__":
    main()
