import time
import math

def sensorSweep(numberSweeps):
    
    flread = 0
    frread = 0
    lread = 0
    rread = 0
    bread = 0
    
    sensorValues=client.ultrasonic()
    
    for i in range(0,numberSweeps):
        sensorValues = client.ultrasonic()
        frread = frread + sensorValues{"0"}
        rread = rread + sensorValues{"1"}
        bread = bread + sensorValues{"2"}
        lread = lread + sensorValues{"3"}
        flread = flread + sensorValues{"4"}
        #ADD RESPONSES TO VARIABLES
    
    flread = flread / numberSweeps
    frread = frread / numberSweeps
    lread = lread / numberSweeps
    rread = rread / numberSweeps
    bread = bread / numberSweeps
    
    informationList = [flread, frread, lread, rread, bread]
    
    wallAlert = [False, False, False, False, False]
    for i in range(5):
        if informationList[i] < 3:
            wallAlert[i] = True    
    
    return(wallAlert, informationList)

def checkIfMovement():
    moving = client.in_motion()
    return(moving)

def checkMovementProgress():
    progress = client.progress_all()
    return(progress)
    

def emergencyMove(direction):
    if direction == "F":
        client.move(1,0)
    elif direction == "R":
        client.move(0,1)
    elif direction == "L":
        client.move(0,-1)
    else:
        client.move(-1,0)
        
    
    currentlyTranslating = True
    while currentlyTranslating:
        
        moving = checkIfMovement():
        #GET RESPONSE
        if moving == False:
            currentlyTranslating = False
    return()

def move(direction,distance):
    
    client.move(0,4)
    
    currentlyTranslating = True
    while currentlyTranslating:
        moving = checkIfMovement()
        progress = checkMovementProgress()
        progress = progress / 100
        wallAlert, information = sensorSweep(1)
        direction = ['B', 'B', 'R', 'L', 'F']
        for i in range(5):
            if wallAlert[i] == True:
                emergencyMove(direction[i])
                distanceContinue = distance * (1-progress)
                move(direction, distanceContinue)
                currentlyTranslating = False
        if moving == False:
            currentlyTranslating = False
    return()

def rotate(direction, degrees):
    
    wallAlert, information = sensorSweep()
    for i in range(5):
        if wallAlert[i] == True:
            emergencyMove(direction[i])
    
    if direction =="SL":
        degrees = -degrees
        
    #Send "r #"" where r is rotating direction (SR or SL) and # is number of degrees
    client.rotate(degrees)
    currentlyRotating = True
    while currentlyRotating:
        rotating = checkIfMovement()
        if rotating == False:
            currentlyRotating = False
    return()

def align(located):
    rotate('SL', -45)
    degreesRotated = -45
    diagAlign = False
    wallAliwgn = False
    while not diagAlign and not wallAlign:
        wallAlert, readings = sensorSweep(3)
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
            rotate('R', 3)
            degreesRotated += 3
            #print('Beginning Rotation')     
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
            lockList = [-45-degreesRotated, 45-degreesRotated, 135-degreesRotated, 225-degreesRotated, 315-degreesRotated, 405-degreesRotated]
            turnList = [45, -45,-135,-225,-315,-45]
        for k in range(len(lockList)):
            if lockList[k] < 0:
                lockList[k] = -lockList[k]
        print(lockList)
        minLockListIndex = lockList.index(min(lockList))
        realignRotate = turnList[minLockListIndex]
        print('r0-'+str(realignRotate))
        
        if realignRotate > 0:
            rotate('SR', realignRotate)
        else:
            rotate('SL', realignRotate)
                
    else:
        if diagAlign:
            rotate('SL', -45)
                    
        wallAlert, readings = sensorSweep(1)
        if readings[0] < 12:
            rotate('SR', 90)
                       
    return()

def center():
    wallAlert,readings = sensorSweep(10)
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
    
    if fbDifference > 0:
        move('F', fbDifference / 2)
    else:
        move('B', fbDifference / 2)
    
    if lrDifference > 0:
        move('L', lrDifference / 2)
    else:
        move('R', lrDifference / 2)
    
    return()

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
    
    #print('New List:' + str(newList))
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