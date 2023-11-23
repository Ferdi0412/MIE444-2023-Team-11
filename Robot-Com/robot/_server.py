########################
### CUSTOM LIBRARIES ###
########################
## Expose local modules
import sys, os; sys.path.append(os.path.dirname(__file__))

## Import local modules
from _socket_wrapper import get_server as _get_server, SocketTimeout
import config as _config
import control_robot as _robot

## Cleanup
_ = sys.path.pop()


MOTOR_FAILED     = (_robot.NoMotorAck, _robot.SingleMotorAck,)
ULTRASONIC_ERROR = (_robot.NoUltrasonics,)

####################
### SERVER CLASS ###
####################
class Team_11_Server:
    def __init__(self, *, timeout: int = 1000):
        self._server = _get_server(_config.SERVER_SOCKET, timeout=timeout)
        self._owner  = None

    def start(self, robot_com_port: str) -> None:
        """Blocking server startup. robot_timeout is timeout for serial read in MS."""
        robot = _robot.Team_11_Robot(robot_com_port)
        while True:
            try:
                requestor, msg = self._server.recv_multipart()

            except SocketTimeout:
                continue

            msg_head, *msg_body = msg.split(b'\n')
            msg_body = b'\n'.join(msg_body)

            reply = self._handle_request(requestor, msg_head, msg_body, robot)

            print(f"Replying with {reply}")

            self._server.send_multipart([requestor, msg_head + b'\n' + reply])



    def _handle_request(self, requestor: bytes, msg_head: bytes, msg_body: bytes, robot: _robot.Team_11_Robot) -> bytes:
        """Handles a request, and returns the required reply."""
        match (msg_head):
            case _config.Command.MOVE_FORWARD:
                if requestor == self._owner:
                    return self._handle_forward(msg_body, robot)
                else:
                    return _config.Response.NEED_OWN

            case _config.Command.ROTATE:
                if requestor == self._owner:
                    return self._handle_rotate(msg_body, robot)
                else:
                    return _config.Response.NEED_OWN

            case _config.Command.IS_ACTIVE:
                return self._handle_is_active(robot)

            case _config.Command.GET_PROGRESS:
                return self._handle_get_progress(robot)

            case _config.Command.STOP:
                return self._handle_stop(robot)

            case _config.Command.LED:
                return self._handle_led(msg_body, robot)

            case _config.Command.LED_OFF:
                return self._handle_led_off(robot)

            case _config.Command.CLAIM_OWN:
                self._owner = requestor
                return b''

            case _config.Command.ULTRASONIC:
                return self._handle_ultrasonic(robot)

            case _config.Command.ULTRASONIC_TABLE:
                return self._handle_ultrasonic_table(msg_body, robot)

            case _:
                return _config.Response.INVALID_REQ





    def _handle_forward(self, msg_body: bytes, robot: _robot.Team_11_Robot) -> bytes:
        """Handle forward motion to robot."""
        try:
            distance = float(msg_body.decode('utf-8'))
        except ValueError:
            return _config.Response.INVALID_PAR

        try:
            return str(robot.move_forward(distance)).encode('utf-8')
        except MOTOR_FAILED:
            return _config.Response.FAILED



    def _handle_rotate(self, msg_body: bytes, robot: _robot.Team_11_Robot) -> bytes:
        """Handle rotate requests to robot."""
        try:
            angle = float(msg_body.decode('utf-8'))
        except ValueError:
            return _config.Response.INVALID_PAR

        try:
            return str(robot.rotate(angle)).encode('utf-8')
        except MOTOR_FAILED:
            return _config.Response.FAILED



    def _handle_is_active(self, robot: _robot.Team_11_Robot) -> bytes:
        """Handle IS-ACTIVE requests."""
        try:
            return str(int(robot.get_active())).encode('utf-8')
        except MOTOR_FAILED:
            return _config.Response.FAILED

        except ValueError:
            return _config.Response.FAILED



    def _handle_get_progress(self, robot: _robot.Team_11_Robot) -> bytes:
        """Handle GET-PROGRESS requests."""
        try:
            return str(robot.get_progress()).encode('utf-8')
        except MOTOR_FAILED:
            return _config.Response.FAILED



    def _handle_stop(self, robot: _robot.Team_11_Robot) -> bytes:
        """Handle STOP requests."""
        try:
            return str(robot.stop()).encode('utf-8')
        except MOTOR_FAILED:
            return _config.Response.FAILED



    def _handle_led(self, msg_body: bytes, robot: _robot.Team_11_Robot) -> bytes:
        """Handle LED requests."""
        try:
            r, g, b = msg_body.decode('utf-8').split('\n')
            r, g, b = int(r), int(g), int(b)
        except ValueError:
            return _config.Response.INVALID_PAR
        robot.set_led(r, g, b)
        return b''



    def _handle_led_off(self, robot: _robot.Team_11_Robot) -> bytes:
        robot.set_led_off()
        return b''



    def _handle_ultrasonic(self, robot: _robot.Team_11_Robot) -> bytes:
        try:
            return str(robot.get_ultrasonics()).encode('utf-8')
        except ULTRASONIC_ERROR:
            return _config.Response.FAILED



    def _handle_ultrasonic_table(self, msg_body: bytes, robot: _robot.Team_11_Robot) -> bytes:
        try:
            measurement_count = int(msg_body)
        except ValueError:
            return _config.Response.INVALID_PAR

        try:
            return robot.get_ultrasonics_DataFrame(measurement_count).to_json().encode('utf-8')
        except ULTRASONIC_ERROR:
            return _config.Response.FAILED
