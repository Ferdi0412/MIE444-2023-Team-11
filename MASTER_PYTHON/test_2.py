from connector.sender import Team_11_Robot

robot = Team_11_Robot("COM13", 2000)

robot.move_forward(12)
print(robot.ultrasonic_json(5))
