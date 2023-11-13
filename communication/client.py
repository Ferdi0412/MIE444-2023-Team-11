from threading import Thread

import sys, os
sys.path.append(os.path.dirname(__file__))

class Client:
    def __init__(self, unique_identifier):
        self.uid = unique_identifier









# class SubClient:
#     """Creates a thread to asynchronously receive and store all values published from the server."""
#     def __init__(self):
#         pass
#         self.thread = Thread(target = _, daemon=True)

#     @property
#     def ultrasonics(self):
#         return self._ultrasonics

#     @property
#     def timestamp_ultrasonics(self):
#         return self._ultrasonic_timestamp

#     @property
#     def progress(self):
#         return self._progress

#     @property
#     def timestamp_progress(self):
#         return self._progress_timestamp

#     @property
#     def in_motion(self):
#         return self._in_motion

#     @property
#     def timestamp_in_motion(self):
#         return self._in_motion_timestamp

