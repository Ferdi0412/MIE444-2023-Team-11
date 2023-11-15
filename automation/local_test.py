'''
This file is part of SimMeR, an educational mechatronics robotics simulator.
Initial development funded by the University of Toronto MIE Department.
Copyright (C) 2023  Ian G. Bennett

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

# Basic echo client, for testing purposes
# Code modified from examples on https://realpython.com/python-sockets/
# and https://www.geeksforgeeks.org/python-display-text-to-pygame-window/

import socket
import struct
import time
import math
from threading import Thread
import _thread
from datetime import datetime

class NoConnection (Exception):
    pass

def transmit(data):
    """Sends data to simmer, and returns response."""
    global responses
    #print(f"Sending {data}")
    err = False
    ## TX
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT_TX))
            s.send(data.encode('utf-8'))
        except (ConnectionRefusedError, ConnectionResetError, TimeoutError, EOFError) as exc:
            #_thread.interrupt_main()
            raise exc
            err = True
    if err:
        raise NoConnection

    ## RX
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            try:
                #while True:
                    s2.connect((HOST, PORT_RX))
                    res_raw = s2.recv(1024)
                    if res_raw:
                        #print(f"|- Received response from simulator: {res_raw}")
                        res = bytes_to_list(res_raw)
                        #print(f"|- Decoded to: {res}")
                        break
            except (ConnectionRefusedError, ConnectionResetError, TimeoutError):
                #_thread.interrupt_main()
                err = True
        if err:
            raise NoConnection

    ## Response received...
    responses = res
    return res

def receive():
    global responses
    global time_rx
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            try:
                s2.connect((HOST, PORT_RX))
                response_raw = s2.recv(1024)
                if response_raw:
                    responses = bytes_to_list(response_raw)
                    time_rx = datetime.now().strftime("%H:%M:%S")
            except (ConnectionRefusedError, ConnectionResetError):
                print('Rx connection was refused or reset.')
                _thread.interrupt_main()
            except TimeoutError:
                print('Response not received from robot.')
                _thread.interrupt_main()

def bytes_to_list(msg):
    num_responses = int(len(msg)/8)
    data = struct.unpack("%sd" % str(num_responses), msg)
    return data


### Network Setup ###
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT_TX = 61200     # The port used by the *CLIENT* to receive
PORT_RX = 61201     # The port used by the *CLIENT* to send data

# Received responses
responses = [False]
time_rx = 'Never'

# Create tx and rx threads
## NOTE: Running blocking transmit call - will mess with async receive Thread
# Thread(target = receive, daemon = True).start()

# Run the sequence of commands
#RUNNING = True
#cmd_sequence = ['w0-36', 'r0-90', 'w0-36', 'r0-90', 'w0-12', 'r0--90', 'w0-24', 'r0--90', 'w0-6', 'r0-720']
def sensorSweep(numberSweeps):
    
    flread = 0
    frread = 0
    lread = 0
    rread = 0
    bread = 0
    
    for i in range(0,numberSweeps):
        transmit('u0')
        #time.sleep(0.2)
        #print(f"Ultrasonic 0 reading: {round(responses[0], 3)}")
        flread = flread + responses[0]
    
        transmit('u1')
        #time.sleep(0.2)
        #print(f"Ultrasonic 1 reading: {round(responses[0], 3)}")
        rread = rread + responses[0]
    
        transmit('u2')
        #time.sleep(0.2)
        #print(f"Ultrasonic 2 reading: {round(responses[0], 3)}")
        lread = lread + responses[0]
    
        transmit('u3')
        #time.sleep(0.2)
        #print(f"Ultrasonic 3 reading: {round(responses[0], 3)}")
        bread = bread + responses[0]
    
        transmit('u4')
        #wtime.sleep(0.2)
        #print(f"Ultrasonic 3 reading: {round(responses[0], 3)}")
        frread = frread + responses[0]
    
    flread = flread / numberSweeps
    frread = frread / numberSweeps
    lread = lread / numberSweeps
    rread = rread / numberSweeps
    bread = bread / numberSweeps
    
    return([frread,flread,rread,lread,bread])

def moveForward(fDistance):
    transmit('w0-'+str(fDistance))
    currentlyTranslating = True
    while currentlyTranslating:
        transmit('w0-0')
        if responses[0] == math.inf:
            currentlyTranslating = False
    return()
    
def rotateRight(rDistance):
    transmit('r0-'+str(rDistance))
    currentlyRotating = True
    while currentlyRotating:
        transmit('r0-0')
        if responses[0] == math.inf:
            currentlyRotating = False
    return()

def rotateLeft(rDistance):
    transmit('r0--'+str(rDistance))
    currentlyRotating = True
    while currentlyRotating:
        transmit('r0-0')
        if responses[0] == math.inf:
            currentlyRotating = False
    return()

def align(located):
    degreesRotated = 0
    diagAlign = False
    wallAlign = False
    while not diagAlign and not wallAlign:
        readings = sensorSweep(3)
        #print(readings)
        
        diagCheck = True
        for i in readings:
            if i > 8:
                diagCheck = False
        closeCheck = readings[0] - readings[1]
        #print(closeCheck)
        if closeCheck < 0:
                closeCheck = -closeCheck
        #print(str(closeCheck))
        if closeCheck < 0.1 and readings[0] < 9.6 and (readings[2] > 12 or readings[3] > 12 or readings[4] > 12):
            wallAlign = True
        elif diagCheck:
            diagAlign = True
        else:
            transmit('r0-3')
            degreesRotated += 3
            #print('Beginning Rotation')
            time.sleep(0.1)
            currentlyRotating = True
            while currentlyRotating:
                transmit('r0-0')
                time.sleep(0.1)
                if responses[0] == math.inf:
                    currentlyRotating = False
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')
                    
    if diagAlign:
        print('Diagonally Aligned')
    else:
        print('Wall Aligned')
    
    print('Degrees Rotated: '+str(degreesRotated))
        
    if located:
        if wallAlign:
            lockList = [0-degreesRotated, 90-degreesRotated, 180-degreesRotated, 270-degreesRotated, 360-degreesRotated]
            turnList = [0,-90,-180,-270,0]
        else:
            lockList = [45-degreesRotated, 135-degreesRotated, 225-degreesRotated, 315-degreesRotated, 405-degreesRotated]
            turnList = [-45,-135,-225,-315,-45]
        for k in range(len(lockList)):
            if lockList[k] < 0:
                lockList[k] = -lockList[k]
        print(lockList)
        minLockListIndex = lockList.index(min(lockList))
        realignRotate = turnList[minLockListIndex]
        print('r0-'+str(realignRotate))
        transmit('r0-'+str(realignRotate))
        currentlyRotating = True
        while currentlyRotating:
            transmit('r0-0'+str(realignRotate))
            time.sleep(0.1)
            if responses[0] == math.inf:
                currentlyRotating = False
                #print('Rotation Complete')
            #else:
                #print('Still Rotating')
                
    else:
        if diagAlign:
            transmit('r0--45')
            currentlyRotating = True
            while currentlyRotating:
                transmit('r0-0')
                time.sleep(0.1)
                if responses[0] == math.inf:
                    currentlyRotating = False
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')
                    
        readings = sensorSweep(1)
        if readings[0] < 12:
            transmit('r0-90')
            currentlyRotating = True
            while currentlyRotating:
                transmit('r0-0')
                time.sleep(0.1)
                if responses[0] == math.inf:
                    currentlyRotating = False
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')
                    
    return()

def center():
    readings = sensorSweep(10)
    for i in range(len(readings)):
        while readings[i] > 12:
            readings[i] = readings[i] - 12
    
    for j in range(len(readings)):
        if readings[j] > 9.6:
            readings[j] = readings[j] - 12
            
    fbDifference = ((readings[0]+readings[1])/2) - readings[4]
    lrDifference = readings[2] - readings[3]
    
    #print(str(fbDifference) + ',' + str(lrDifference))
    if fbDifference > 0 and (readings[0] < 3.5 or readings[1] < 3.5):
        fbDifference = 0
    
    if fbDifference < 0 and readings[4] < 3.5:
        fbDifference = 0
    
    if lrDifference > 0 and readings[2] < 3.5:
        lrDifference = 0
        
    if lrDifference < 0 and readings[3] < 3.5:
        lrDifference = 0
    
    transmit('w0-'+str(fbDifference/2))
    currentlyTranslating = True
    while currentlyTranslating:
        transmit('w0-0')
        time.sleep(0.1)
        if responses[0] == math.inf:
            currentlyTranslating = False
    
    transmit('d0-'+str(lrDifference/2))
    currentlyTranslating = True
    while currentlyTranslating:
        transmit('d0-0')
        time.sleep(0.1)
        if responses[0] == math.inf:
            currentlyTranslating = False
    
    return()
#ct = 0
#while RUNNING:

    #if ct < len(cmd_sequence):
        #transmit('u0')
        #time.sleep(0.1)
        #print(f"Ultrasonic 0 reading: {round(responses[0], 3)}")
        #transmit('u1')
        #time.sleep(0.1)
        #print(f"Ultrasonic 1 reading: {round(responses[0], 3)}")
        #transmit('u2')
        #time.sleep(0.1)
        #print(f"Ultrasonic 2 reading: {round(responses[0], 3)}")
        #transmit('u3')
        #time.sleep(0.1)
        #print(f"Ultrasonic 3 reading: {round(responses[0], 3)}")

        #transmit(cmd_sequence[ct])
        #time.sleep(0.1)

        #if responses[0] == math.inf:
            #ct += 1

        #time.sleep(0.1)
    #else:
        #RUNNING = False
        #print("Sequence complete!")

#input('Begin Align Function')
#align(True)
#input('Begin Center Function')
#center()
def roomDetector():
    information = sensorSweep(10)
    modInformation = [((information[0]+information[1])/2),information[2],information[3],information[4]]
    numberOfWalls = 0
    roomSequence = [True, True, True, True]
    for i in range(len(modInformation)):
        if modInformation[i] < 12:
            roomSequence[i] = True
            numberOfWalls = numberOfWalls + 1
        else:
            roomSequence[i] = False
    
    if numberOfWalls == 3:
        roomType = 'D'
    elif numberOfWalls == 2:
        print(roomSequence)
        if roomSequence == [True, False, False, True] or roomSequence == [False, True, True, False]:
            roomType = 'H'
        else:
            roomType = 'C'
    elif numberOfWalls == 1:
        roomType = 'T'
    else:
        roomType = 'F'
    print('Room Type Identified: '+roomType)
    return(information, roomType)

def findNewLocations(locationList,maze,roomType,stepOne):
    newList = []
    if stepOne:
        for i in range(len(maze)):
            for j in range(len(maze[i])):
                if maze[i][j] == roomType:
                    newList.append(str(i)+str(j)+'U')
    else:
        mazeBoundY = len(maze)
        mazeBoundX = len(maze[0])
        
        for i in range(len(locationList)):
            infoCheck = [*locationList[i]]
            #print(str(infoCheck))
            if int(infoCheck[0]) != 0:
                if maze[int(infoCheck[0])-1][int(infoCheck[1])] == roomType:
                    newList.append((str(int(infoCheck[0])-1))+infoCheck[1]+'N')
                    
            if int(infoCheck[0]) != (mazeBoundY - 1):
                if maze[int(infoCheck[0])+1][int(infoCheck[1])] == roomType:
                    newList.append((str(int(infoCheck[0])+1))+infoCheck[1]+'S')
            
            if int(infoCheck[1]) != 0:
                if maze[int(infoCheck[0])][int(infoCheck[1])-1] == roomType:
                    newList.append(infoCheck[0]+(str(int(infoCheck[1])-1))+'W')

            if int(infoCheck[1]) != (mazeBoundX - 1):
                if maze[int(infoCheck[0])][int(infoCheck[1])+1] == roomType:
                    newList.append(infoCheck[0]+(str(int(infoCheck[1])+1))+'E')
    
    print('Unmodified New List: ' + str(newList))
    
    counter = 0
    
    while counter < len(newList):
        if newList.count(newList[counter]) > 1:
            newList.remove(newList[counter])
        counter = counter + 1
    
    print('New List:' + str(newList))
    return(newList)

def localizer():
    locationList = []
    localized = False
    
    firstRow = ['C','T','H','C','E','D','E','D']
    secondRow = ['T','C','E','C','H','F','H','T']
    thirdRow = ['H','E','D','E','E','H','E','H']
    fourthRow = ['C','H','T','H','H','C','E','D']
    
    maze = [firstRow, secondRow, thirdRow, fourthRow]
    
    align(False)
    center()
    information, roomType = roomDetector()
    locationList = findNewLocations(locationList,maze,roomType,True)
    
    while not localized:
        input('Next Step: ')
        information = sensorSweep(10)
        if information[0] < 12 or information[1] < 12:
            align(True)
            if information[3] < 12:
                rotateLeft(90)
            else:
                rotateRight(90)
            center()
        else:
            moveForward(12)
            center()
            information, roomType = roomDetector()
            locationList = findNewLocations(locationList,maze,roomType,False)
        if len(locationList) == 1:
            localized = True
            
    print('Localization Complete')
    return(locationList[0])
        
        
    



input('Begin Sequence: ')
robotLocation = localizer()