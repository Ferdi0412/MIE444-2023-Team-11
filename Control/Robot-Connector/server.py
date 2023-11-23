COM = "COM13"

from json import dumps as _dumps

import os, sys; sys.path.append(os.path.dirname(__file__))

from robot_server import get_server, Message, SocketTimeout, PORT

from robot import Team_11_Robot, NoMotorAck, NoUltrasonics, SingleMotorAck

owner = None

if __name__ == '__main__':
    server = get_server(port=PORT, timeout=2000)

    robot = Team_11_Robot(COM)

    while True:
        try:
            requestor, request = server.recv_multipart()

        except SocketTimeout:
            continue

        except ValueError: ## Unpacking stuff went wrong
            continue

        request_type, *request_body = request.split(b'\n')
        request_body = b'\n'.join(request_body)

        try:
            match ( request_type ):
                case Message.MOVE_FORWARD:
                    distance = float(request_body)
                    reply = str(robot.move_forward(distance)).encode('utf-8')

                case Message.ROTATE:
                    angle = float(request_body)
                    robot.move_forward(distance)
                    reply = b'ACKNOWLEDGED'

                case Message.STOP:
                    reply = robot.stop()

                case Message.GET_ACTIVE:
                    reply = robot.get_active()

                case Message.GET_PROGRESS:
                    reply = robot.get_progress()

                case Message.SET_LED:
                    red, green, blue = request_body.split(b'\n')
                    robot.set_led(float(red), float(green), float(blue))
                    reply = b'ACKNOWLEDGED'

                case Message.SET_LED_OFF:
                    robot.set_led_off()
                    reply = b'ACKNOWLEDGED'

                case Message.GET_ULTRASONICS:
                    reply = _dumps(robot.get_ultrasonics()).encode('utf-8')

                case Message.IS_OWNER:
                    reply = str(request_body == owner).encode('utf-8')

                case Message.GET_OWNERSHIP:
                    owner = requestor
                    reply = b'ACKNOWLEDGED'

                case _:
                    reply = b'INVALID'

            server.send_multipart([requestor, reply])

        except (NoMotorAck, NoUltrasonics, SingleMotorAck,):
            server.send_multipart([requestor, b'FAILED'])

        except Exception:
            server.send_multipart([requestor, b'FATAL'])
