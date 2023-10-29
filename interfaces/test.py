from to_control import RobotContol

print("Response: ", RobotContol().connect().send_recv('G'))
