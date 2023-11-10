import time
import math

def sensorSweep(numberSweeps):
    
    flread = 0
    frread = 0
    lread = 0
    rread = 0
    bread = 0
    
    for i in range(0,numberSweeps):
        
        #SEND "US-ALL"
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
    moving = #SEND "M"
    return(moving)

def checkMovementProgress():
    progress = #SEND "P"
    return(progress)
    

def emergencyMove(direction):
    
    #SEND "d 1" where d is direction
    
    currentlyTranslating = True
    while currentlyTranslating:
        
        moving = checkIfMovement():
        #GET RESPONSE
        if moving == False:
            currentlyTranslating = False
    return()

def move(direction,distance):
    
    #SEND "d #" where d is direction and # is distance
    
    currentlyTranslating = True
    while currentlyTranslating:
        moving, progress = checkMovement()
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
    
    #Send "r #"" where r is rotating direction (SR or SL) and # is number of degrees
    
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
    wallAlign = False
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