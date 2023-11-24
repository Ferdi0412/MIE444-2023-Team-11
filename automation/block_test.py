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

## Ferdi magic line ----
import sys, os; print(os.path.dirname(os.path.dirname(__file__))); sys.path.append(os.path.dirname(os.path.dirname(__file__))); from MASTER_PYTHON.connector.sender import Team_11_Robot as Team_11_Client; _=sys.path.pop()
##                  ----

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
def comSensorSweep(numberSweeps):
    print("[SENSOR-SWEEP]")
    sensorData = robot.ultrasonic_json(numberSweeps)
    #print(sensorData)
    flread = 0
    frread = 0
    lread = 0
    rread = 0
    bread = 0
    gread = 0

    successfulSweeps = [0,0,0,0,0]

    for i in range(0,numberSweeps):
        if sensorData['FL'][i] > 0.1 and sensorData['FL'][i] < 72:
            flread = flread + sensorData['FL'][i]
            successfulSweeps[0] = successfulSweeps[0] + 1

        if sensorData['FR'][i] > 0.1 and sensorData['FR'][i] < 72:
            frread = frread + sensorData['FR'][i]
            successfulSweeps[1] = successfulSweeps[1] + 1

        if sensorData['R'][i] > 0.1 and sensorData['R'][i] < 72:
            rread = rread + sensorData['R'][i]
            successfulSweeps[2] = successfulSweeps[2] + 1

        if sensorData['B'][i] > 0.1 and sensorData['B'][i] < 72:
            bread = bread + sensorData['B'][i]
            successfulSweeps[3] = successfulSweeps[3] + 1

        if sensorData['L'][i] > 0.1 and sensorData['L'][i] < 72:
            lread = lread + sensorData['L'][i]
            successfulSweeps[4] = successfulSweeps[4] + 1

        #if sensorData['G'][i] > 1 and sensorData['G'][i] < 72:
            #gread = gread + sensorData['G'][i]
            #successfulSweeps[5] = successfulSweeps[5] + 1
    #print(successfulSweeps)
    sensorSuccessful = True
    sensorSuccessful = all(successfulSweeps)
    # for i in range(6):
    #     if successfulSweeps[i] == 0:
    #         sensorSuccessful = False
    if sensorSuccessful:
        flread = flread / successfulSweeps[0]
        frread = frread / successfulSweeps[1]
        lread = lread / successfulSweeps[2]
        rread = rread / successfulSweeps[3]
        bread = bread / successfulSweeps[4]
        #gread = gread / successfulSweeps[5]
        outputData = [frread,flread,rread,lread,bread]
    else:
        print('Error detection')
        outputData = comSensorSweep(numberSweeps)
    return(outputData)

def simSensorSweep(numberSweeps):

    flread = 0
    frread = 0
    lread = 0
    rread = 0
    bread = 0

    successfulSweeps = [0,0,0,0,0]

    for i in range(0,numberSweeps):
        transmit('u0')
        #time.sleep(0.2)
        #print(f"Ultrasonic 0 reading: {round(responses[0], 3)}")
        if responses[0] > 1 and responses[0] < 72:
            flread = flread + responses[0]
            successfulSweeps[0] = successfulSweeps[0] + 1

        transmit('u1')
        #time.sleep(0.2)
        #print(f"Ultrasonic 1 reading: {round(responses[0], 3)}")
        if responses[0] > 1 and responses[0] < 60:
            rread = rread + responses[0]
            successfulSweeps[1] = successfulSweeps[1] + 1

        transmit('u2')
        #time.sleep(0.2)
        #print(f"Ultrasonic 2 reading: {round(responses[0], 3)}")
        if responses[0] > 1 and responses[0] < 60:
            lread = lread + responses[0]
            successfulSweeps[2] = successfulSweeps[2] + 1

        transmit('u3')
        #time.sleep(0.2)
        #print(f"Ultrasonic 3 reading: {round(responses[0], 3)}")
        if responses[0] > 1 and responses[0] < 60:
            bread = bread + responses[0]
            successfulSweeps[3] = successfulSweeps[3] + 1

        transmit('u4')
        #wtime.sleep(0.2)
        #print(f"Ultrasonic 3 reading: {round(responses[0], 3)}")
        if responses[0] > 1 and responses[0] < 60:
            frread = frread + responses[0]
            successfulSweeps[4] = successfulSweeps[4] + 1
    print(successfulSweeps)
    flread = flread / successfulSweeps[0]
    frread = frread / successfulSweeps[1]
    lread = lread / successfulSweeps[2]
    rread = rread / successfulSweeps[3]
    bread = bread / successfulSweeps[4]

    return([frread,flread,rread,lread,bread])

def emergencyCheck(information):
    emergencyList = [False,False,False,False,False]
    wallAlert = False
    for i in range(5):
        if information[i] < 2:
            emergencyList[i] = True
            wallAlert = True
    return wallAlert,emergencyList

def comEmergencyMoveSideways(right):
    if right:
        angle = 10
    else:
        angle = -10

    robot.rotate(angle)
    rotating = True
    while rotating:
        switch = robot.is_active()
        if switch == False:
            rotating = False
    robot.move_forward(1)
    moving = True
    while moving:
        switch = robot.is_active()
        if switch == False:
            moving = False
    robot.rotate(-angle)
    rotating = True
    while rotating:
        switch = robot.is_active()
        if switch == False:
            rotating = False
    return()

def simEmergencyMoveSideways(right):
    if right:
        transmit('d0--1')
    else:
        transmit('d0-1')
    currentlySideMoving = True
    while currentlySideMoving:
        transmit('d0-0')
        if responses[0] == math.inf:
            currentlySideMoving = False
    return()

def comEmergencyMove(emergencyList,direction):
    if emergencyList[0] or emergencyList[1]:
        robot.move_forward(-1)
        print('Emergency Moving Back')
    elif emergencyList[2]:
        #comEmergencyMoveSideways(True)
        if direction:
            robot.rotate(-10)
        else:
            robot.rotate(10)
    elif emergencyList[3]:
        #comEmergencyMoveSideways(False)
        if direction:
            robot.rotate(10)
        else:
            robot.rotate(-10)
    else:
        robot.move_forward(1)
    emergencyMoving = True
    while emergencyMoving:
        switch = robot.is_active()
        if switch == False:
            emergencyMoving = False
    return()

def simEmergencyMove(emergencyList):
    if emergencyList[0] or emergencyList[1]:
        transmit('w0--1')
        print('Emergency Moving Back')
    elif emergencyList[2]:
        simEmergencyMoveSideways(True)
        #print('Emergency Moving Right')
        transmit('r0-10')
        currentlySideMoving = True
        while currentlySideMoving:
            transmit('d0-0')
            if responses[0] == math.inf:
                currentlySideMoving = False
    elif emergencyList[3]:
        simEmergencyMoveSideways(False)
        #print('Emergency Moving Left')
        transmit('r0--10')
        currentlySideMoving = True
        while currentlySideMoving:
            transmit('d0-0')
            if responses[0] == math.inf:
                currentlySideMoving = False
    else:
        transmit('w0-1')
        print('Emergency Moving Forward')
    currentlyMoving = True
    while currentlyMoving:
        transmit('w0-0')
        if responses[0] == math.inf:
            currentlyMoving = False
    return()

def comMoveForward(fDistance):
    print('Moving Forward')
    print('Initial Distance: '+str(fDistance))
    robot.move_forward(fDistance)
    currentlyTranslating = True
    while currentlyTranslating:
        switch = robot.is_active()
        if switch == False:
            currentlyTranslating = False
        ## Retry ONCE if invalid readdings
        ## TODO: Handle this better
        currentDistance = comSensorSweep(1)
        wallAlert, emergencyList = emergencyCheck(currentDistance)
        if wallAlert:
            percentMoved = (robot.progress())/100
            print('Percentage Moved: ')
            distanceMoved = fDistance * percentMoved
            distanceRemaining = fDistance - distanceMoved
            if distanceRemaining > 0:
                direction = True
            else:
                direction = False
            comEmergencyMove(emergencyList, direction)
            print('Moving '+str(distanceRemaining))
            comMoveForward(distanceRemaining)
            currentlyTranslating = False
    return()

def simMoveForward(fDistance):
    initialDistance = simSensorSweep(5)
    initialDistanceFront = (initialDistance[0]+initialDistance[1])/2
    transmit('w0-'+str(fDistance))
    currentlyTranslating = True
    while currentlyTranslating:
        transmit('w0-0')
        if responses[0] == math.inf:
            currentlyTranslating = False
        currentDistance = simSensorSweep(1)
        currentDistanceFront = (currentDistance[0]+currentDistance[1])/2
        wallAlert, emergencyList = emergencyCheck(currentDistance)
        if wallAlert:
            distanceMoved = initialDistanceFront - currentDistanceFront
            distanceRemaining = fDistance - distanceMoved
            transmit('xx')
            simEmergencyMove(emergencyList)
            print('Moving '+str(distanceRemaining))
            simMoveForward(distanceRemaining)
            currentlyTranslating = False
    return()

def simMoveRight(dDistance):
    initialDistance = simSensorSweep(5)
    initialDistanceFront = initialDistance[3]
    transmit('d0-'+str(dDistance))
    currentlyTranslating = True
    while currentlyTranslating:
        transmit('d0-0')
        if responses[0] == math.inf:
            currentlyTranslating = False
        currentDistance = simSensorSweep(1)
        currentDistanceRight = currentDistance[3]
        wallAlert, emergencyList = emergencyCheck(currentDistance)
        if wallAlert:
            distanceMoved = initialDistanceFront - currentDistanceRight
            distanceRemaining = dDistance - distanceMoved
            simEmergencyMove(emergencyList)
            simMoveRight(distanceRemaining)
            currentlyTranslating = False
    return()

def comRotateRight(rDistance):
    robot.rotate(rDistance)
    currentlyRotating = True
    while currentlyRotating:
        switch = robot.is_active()
        if switch == False:
            currentlyRotating = False
    return()

def simRotateRight(rDistance):
    transmit('r0-'+str(rDistance))
    currentlyRotating = True
    while currentlyRotating:
        transmit('r0-0')
        if responses[0] == math.inf:
            currentlyRotating = False
    return()

def comRotateLeft(rDistance):
    robot.rotate(-rDistance)
    currentlyRotating = True
    while currentlyRotating:
        switch = robot.is_active()
        if switch == False:
            currentlyRotating = False
    return()

def simRotateLeft(rDistance):
    transmit('r0--'+str(rDistance))
    currentlyRotating = True
    while currentlyRotating:
        transmit('r0-0')
        if responses[0] == math.inf:
            currentlyRotating = False
    return()

def comMoveRight(dDistance):
    if dDistance > 0:
        comRotateRight(90)
        comMoveForward(dDistance)
        comRotateLeft(90)
    else:
        dDistanceTrue = -dDistance
        comRotateLeft(90)
        comMoveForward(dDistanceTrue)
        comRotateRight(90)
    return()

def sensorSweep(numberSweeps,selectSimmer):
    if selectSimmer:
        information = simSensorSweep(numberSweeps)
    else:
        ## TODO: Handle this better.
        ## Retry ONCE incase of ZERO division
        information = comSensorSweep(numberSweeps)
    return information

def moveForward(fDistance,selectSimmer):
    if selectSimmer:
        simMoveForward(fDistance)
    else:
        comMoveForward(fDistance)
    return()

def moveRight(dDistance, selectSimmer):
    if selectSimmer:
        simMoveRight(dDistance)
    else:
        comMoveRight(dDistance)
    return()

def rotateLeft(rDistance, selectSimmer):
    print('')
    print('Rotate Left')
    if selectSimmer:
        simRotateLeft(rDistance)
    else:
        comRotateLeft(rDistance)
    return()

def rotateRight(rDistance, selectSimmer):
    print('')
    print('Rotate Right')
    if selectSimmer:
        simRotateRight(rDistance)
    else:
        comRotateRight(rDistance)
    return()

def align(located,selectSimmer):
    print('')
    print('Beginning Align')
    degreesRotated = -45
    diagAlign = False
    wallAlign = False
    rotateLeft(45, selectSimmer)
    while not diagAlign and not wallAlign:
        readings = sensorSweep(3,selectSimmer)
        #print(readings)

        diagCheck = True
        for i in readings:
            if i > 10:
                diagCheck = False
        closeCheck = readings[0] - readings[1]
        #print(closeCheck)
        if closeCheck < 0:
                closeCheck = -closeCheck
        #print(str(closeCheck))
        if closeCheck < 0.5 and readings[0] < 9.6 and (readings[2] > 12 or readings[3] > 12 or readings[4] > 12):
            wallAlign = True
        elif diagCheck:
            diagAlign = True
        else:
            rotateRight(15,selectSimmer)
            degreesRotated = degreesRotated + 15
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
            lockList = [-45-degreesRotated,45-degreesRotated, 135-degreesRotated, 225-degreesRotated, 315-degreesRotated, 405-degreesRotated]
            turnList = [45,-45,-135,-225,-315,-45]
        for k in range(len(lockList)):
            if lockList[k] < 0:
                lockList[k] = -lockList[k]
        #print(lockList)
        minLockListIndex = lockList.index(min(lockList))
        realignRotate = turnList[minLockListIndex]
        #print('r0-'+str(realignRotate))
        print('Rotating back: '+str(realignRotate))
        rotateRight(realignRotate, selectSimmer)
                #print('Rotation Complete')
            #else:
                #print('Still Rotating')

    else:
        if diagAlign:
            rotateLeft(45, selectSimmer)
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')

        readings = sensorSweep(1, selectSimmer)
        if readings[0] < 12:
            rotateRight(90, selectSimmer)
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')

    return()

def center(selectSimmer):
    print('')
    print('Beginning center')
    readings = sensorSweep(10, selectSimmer)
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

    moveForward(fbDifference/2, selectSimmer)
    if selectSimmer:
        moveRight(lrDifference/2, selectSimmer)
    #else:
        #if lrDifference > 0:
            #rotateRight(5, selectSimmer)
        #else:
            #rotateLeft(5, selectSimmer)

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
def roomDetector(selectSimmer):
    information = sensorSweep(10, selectSimmer)
    modInformation = [((information[0]+information[1])/2),information[2],information[3],information[4]]
    print(modInformation)
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

    #print('Unmodified New List: ' + str(newList))

    counter = 0

    while counter < len(newList):
        if newList.count(newList[counter]) > 1:
            newList.remove(newList[counter])
        counter = counter + 1

    print('New List:' + str(newList))
    return(newList)

def localizer(selectSimmer):
    locationList = []
    localized = False

    firstRow = ['C','T','H','C','E','D','E','D']
    secondRow = ['T','C','E','C','H','F','H','T']
    thirdRow = ['H','E','D','E','E','H','E','H']
    fourthRow = ['C','H','T','H','H','C','E','D']

    maze = [firstRow, secondRow, thirdRow, fourthRow]

    align(False, selectSimmer)
    center(selectSimmer)
    information, roomType = roomDetector(selectSimmer)
    locationList = findNewLocations(locationList,maze,roomType,True)

    while not localized:
        input('Next Step: ')
        information = sensorSweep(10, selectSimmer)
        if (information[0]+information[1])/2 < 8:
            align(True, selectSimmer)
            if information[3] < 8:
                print('Rotating Right')
                rotateRight(90, selectSimmer)
            else:
                print('Rotating Left')
                rotateLeft(90, selectSimmer)
            center(selectSimmer)
        else:
            moveForward(12, selectSimmer)
            center(selectSimmer)
            information, roomType = roomDetector(selectSimmer)
            locationList = findNewLocations(locationList,maze,roomType,False)
        if len(locationList) == 1:
            localized = True

    print('Localization Complete')
    return(locationList[0])

def directionalSensorSweep(robotLocation,numberSweeps,selectSimmer):
    information = sensorSweep(numberSweeps,selectSimmer)
    locationData = [*robotLocation]
    if locationData[2] == 'N':
        nRead = (information[0] + information[1])/2
        eRead = information[3]
        sRead = information[4]
        wRead = information[2]
    elif locationData[2] == 'E':
        nRead = information[2]
        eRead = (information[0]+information[1])/2
        sRead = information[3]
        wRead = information[4]
    elif locationData[2] == 'S':
        nRead = information[4]
        eRead = information[2]
        sRead = (information[0]+information[1])/2
        wRead = information[3]
    else:
        nRead = information[3]
        eRead = information[4]
        sRead = information[2]
        wRead = (information[0]+information[1])/2
    return([nRead,eRead,sRead,wRead])

def moveNorth(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData[2] == 'S':
        align(True, selectSimmer)
        rotateRight(180, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'E':
        align(True, selectSimmer)
        rotateLeft(90, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'W':
        align(True, selectSimmer)
        rotateRight(90, selectSimmer)
        center(selectSimmer)
    moveForward(12, selectSimmer)
    center(selectSimmer)
    locationData[0] = str(int(locationData[0])-1)
    newLocation = str(locationData[0])+str(locationData[1])+'N'
    return(newLocation)

def moveEast(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData[2] == 'W':
        align(True, selectSimmer)
        rotateRight(180, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'S':
        align(True, selectSimmer)
        rotateLeft(90, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'N':
        align(True, selectSimmer)
        rotateRight(90, selectSimmer)
        center(selectSimmer)
    moveForward(12, selectSimmer)
    center(selectSimmer)
    locationData[1] = str(int(locationData[1])+1)
    newLocation = str(locationData[0])+str(locationData[1])+'E'
    return(newLocation)

def moveSouth(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData[2] == 'N':
        align(True, selectSimmer)
        rotateRight(180, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'W':
        align(True, selectSimmer)
        rotateLeft(90, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'E':
        align(True, selectSimmer)
        rotateRight(90, selectSimmer)
        center(selectSimmer)
    moveForward(12, selectSimmer)
    center(selectSimmer)
    locationData[0] = str(int(locationData[0])+1)
    newLocation = str(locationData[0])+str(locationData[1])+'S'
    return(newLocation)

def moveWest(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData[2] == 'E':
        align(True, selectSimmer)
        rotateRight(180, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'N':
        align(True, selectSimmer)
        rotateLeft(90, selectSimmer)
        center(selectSimmer)
    elif locationData[2] == 'S':
        align(True, selectSimmer)
        rotateRight(90, selectSimmer)
        center(selectSimmer)
    moveForward(12, selectSimmer)
    center(selectSimmer)
    locationData[1] = str(int(locationData[1])-1)
    newLocation = str(locationData[0])+str(locationData[1])+'W'
    return(newLocation)

def orientNorth(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData != 'N':
        align(True, selectSimmer)
    if locationData[2] == 'W':
        rotateRight(90)
    elif locationData[2] == 'S':
        rotateRight(180)
    elif locationData[2] == 'E':
        rotateLeft(90)
    newLocation = str(locationData[0])+str(locationData[1])+'N'
    return(newLocation)

def orientEast(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData != 'E':
        align(True, selectSimmer)
    if locationData[2] == 'N':
        rotateRight(90)
    elif locationData[2] == 'W':
        rotateRight(180)
    elif locationData[2] == 'S':
        rotateLeft(90)
    newLocation = str(locationData[0])+str(locationData[1])+'E'
    return(newLocation)

def orientSouth(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData != 'S':
        align(True, selectSimmer)
    if locationData[2] == 'E':
        rotateRight(90)
    elif locationData[2] == 'N':
        rotateRight(180)
    elif locationData[2] == 'W':
        rotateLeft(90)
    newLocation = str(locationData[0])+str(locationData[1])+'S'
    return(newLocation)

def orientWest(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    if locationData != 'W':
        align(True, selectSimmer)
    if locationData[2] == 'S':
        rotateRight(90)
    elif locationData[2] == 'E':
        rotateRight(180)
    elif locationData[2] == 'N':
        rotateLeft(90)
    newLocation = str(locationData[0])+str(locationData[1])+'W'
    return(newLocation)
    
def blockSweep(selectSimmer):
    angles=[]
    center(selectSimmer)
    rotateLeft(45, selectSimmer)
    for i in 31:
        sensorData = sensorSweep(3, selectSimmer)
        highFrontAverage = (sensorData[0] + sensorData[1])/2
        blockSensor = sensorData[5]
        angles.append(highFrontAverage-blockSensor)
        if i < 30:
            rotateRight(3, selectSimmer)
    rotateRight(45, selectSimmer)
    maxVal = max(angles)
    if maxVal > 3:
        blockDetected = True
    angleFromLeft = (angles.index(maxVal))*3
    angleFromCenter = angleFromLeft - 45
    return (angleFromCenter, blockDetected)

def travelToLoadingZone(robotLocation, selectSimmer):
    travelling = True
    rowCheck = False
    columnCheck = False
    blockAlert = False
    blockFound = False
    while travelling:
        #print(robotLocation)
        locationData = [*robotLocation]
        #print(locationData)
        if int(locationData[0]) == 0:
            rowCheck = True
        if int(locationData[1]) == 0:
            columnCheck = True
        if int(locationData[0]) < 2 and columnCheck:
            blockAlert = True
        if int(locationData[1]) < 2 and rowCheck:
            blockAlert = True
        if rowCheck and columnCheck:
            travelling = False
        if blockAlert:
            angleFromCenter, blockDetected = blockSweep(selectSimmer)
            if blockDetected:
                blockFound = True
                rowCheck = True
                columnCheck = True
        if rowCheck and columnCheck:
            travelling = False
        else:
            directionalSensorData = directionalSensorSweep(robotLocation,5,selectSimmer)
            if directionalSensorData[0] < 12 and directionalSensorData[1] < 12 and directionalSensorData[3] < 12:
                robotLocation = moveSouth(robotLocation, selectSimmer)
            elif directionalSensorData[3] < 12:
                robotLocation = moveNorth(robotLocation, selectSimmer)
            else:
                robotLocation = moveWest(robotLocation, selectSimmer)
    return(robotLocation, blockFound, angleFromCenter)

def blockFinder(robotLocation, selectSimmer):
    locationData = [*robotLocation]
    

############
### MAIN ###
############

#input('Begin Sequence: ')
identifier = input('R for robot, S for simmer: ')
if identifier == 'R':
    robot = Team_11_Client('COM5', 10)

    time.sleep(2)

    robot.led(255, 0, 255)
    # robot.claim_ownership()
    selectSimmer = False
else:
    selectSimmer = True
robotLocation = localizer(selectSimmer)
robotLocation = travelToLoadingZone(robotLocation,selectSimmer)
