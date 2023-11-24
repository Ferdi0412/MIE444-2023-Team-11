#MODIFIED COMSENSORSWEEP FUNCTION
def comSensorSweep(numberSweeps):
    sensorData = robot.ultrasonic_json(numberSweeps)
    
    flread = 0
    frread = 0
    lread = 0
    rread = 0
    bread = 0
    gread = 0
    
    successfulSweeps = [0,0,0,0,0,0]
    
    for i in range(0,numberSweeps):
        if sensorData['fl'][i] > 1 and sensorData['fl'][i] < 72:
            flread = flread + sensorData['fl'][i]
            successfulSweeps[0] = successfulSweeps[0] + 1
            
        if sensorData['fr'][i] > 1 and sensorData['fr'][i] < 72:
            frread = frread + sensorData['fr'][i]
            successfulSweeps[1] = successfulSweeps[1] + 1
            
        if sensorData['r'][i] > 1 and sensorData['r'][i] < 72:
            rread = rread + sensorData['r'][i]
            successfulSweeps[2] = successfulSweeps[2] + 1
            
        if sensorData['b'][i] > 1 and sensorData['b'][i] < 72:
            bread = bread + sensorData['b'][i]
            successfulSweeps[3] = successfulSweeps[3] + 1
            
        if sensorData['l'][i] > 1 and sensorData['l'][i] < 72:
            lread = lread + sensorData['l'][i]
            successfulSweeps[4] = successfulSweeps[4] + 1
            
        if sensorData['g'][i] > 1 and sensorData['g'][i] < 72:
            gread = gread + sensorData['g'][i]
            successfulSweeps[5] = successfulSweeps[5] + 1
    
    sensorSuccessful = True
    for i in range(6):
        if successfulSweeps[i] == 0:
            sensorSuccessful = False
    if sensorSuccessful:
        flread = flread / successfulSweeps[0]
        frread = frread / successfulSweeps[1]
        lread = lread / successfulSweeps[2]
        rread = rread / successfulSweeps[3]
        bread = bread / successfulSweeps[4]
        gread = gread / successfulSweeps[5]
        outputData = [frread,flread,rread,lread,bread,gread]
    else:
        outputData = comSensorSweep(numberSweeps)
    return(outputData)