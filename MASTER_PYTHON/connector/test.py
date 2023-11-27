if __name__ == '__main__':
    import sender

    robot = sender.Team_11_Robot("COM12", 2)

    robot.led('\x20', 255, 255)
    robot.move_forward(2)
