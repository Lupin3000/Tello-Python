from atexit import register
from configparser import ConfigParser
from pathlib import Path
from sys import exit
from threading import Thread, Lock
from time import sleep
from typing import Optional
from hid import device


class Controller:
    """
    Manages a controller connection and provides mechanisms to access and update controller states.

    :ivar _THRESHOLD: The threshold value for determining the direction of the analog sticks.
    :ivar _MIDDLE: The middle value for determining the direction of the analog sticks.
    :ivar _DELAY: The delay between controller reads in seconds.
    """

    _THRESHOLD: int = 50
    _MIDDLE: int = 128
    _DELAY: float = 0.01

    def __init__(self, name: str):
        """
        Initialize a controller connection and set up attributes to manage controller states,
        button statuses, and analog stick movements. This method attempts to connect to the
        specified controller using the provided vendor and product IDs.

        :param name: The configuration name of the controller.
        :type name: str
        """
        config = ConfigParser()
        config.read(Path(__file__).parent.parent / "config" / "configuration.ini")

        section = config[name]
        vendor = int(section['vendor'])
        product = int(section['product'])

        try:
            self._controller = device()
            self._controller.open(vendor, product)
            self._controller.set_nonblocking(True)
            self._name = self._controller.get_product_string()
            print(f'[INFO] Connected with "{self._name}" controller.')
        except Exception as err:
            print(f'[ERROR] Failed to connect to controller: {err}')
            exit(1)

        self._btn = {
            'TAKEOFF': int(section['btn_takeoff']),
            'LANDING': int(section['btn_landing'])
        }

        self._axis_left_x = int(section['analog_left_x'])
        self._axis_left_y = int(section['analog_left_y'])
        self._axis_right_x = int(section['analog_right_x'])
        self._axis_right_y = int(section['analog_right_y'])

        self._btn_status = {
            'TAKEOFF': False,
            'LANDING': False
        }

        self._analog_right_stick = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False
        }

        self._analog_left_stick = {
            "up": False,
            "down": False,
            "clockwise": False,
            "counterclockwise": False
        }

        register(self._close)

        self._lock = Lock()
        self._thread = Thread(target=self._read_controller, daemon=True)
        self._thread.start()

    def _close(self) -> None:
        """
        Closes the connection to the controller.

        :return: None
        """
        if self._controller:
            print('[INFO] Disconnect from controller.')
            self._controller.close()

    def _set_right_stick_active(self, direction: Optional[str]) -> None:
        """
        Sets the state of the right stick to be active in the specified direction.

        :param direction: The direction to set the right analog stick to be active.
        :type direction: Optional[str]
        :return: None
        """
        for key in self._analog_right_stick.keys():
            self._analog_right_stick[key] = False

        if direction is not None:
            self._analog_right_stick[direction] = True

    def _set_left_stick_active(self, direction: Optional[str]) -> None:
        """
        Sets the state of the left stick to be active in the specified direction.

        :param direction: The direction to set the left analog stick to be active.
        :type direction: Optional[str]
        :return: None
        """
        for key in self._analog_left_stick.keys():
            self._analog_left_stick[key] = False

        if direction is not None:
            self._analog_left_stick[direction] = True

    def _read_controller(self) -> None:
        """
        Reads and processes input data from a connected controller in a continuous loop.

        :return: None
        """
        while True:
            data = self._controller.read(64)

            if data:
                with self._lock:
                    btn_state = data[3]

                    for key in self._btn.keys():
                        self._btn_status[key] = btn_state == self._btn[key]

                    right_x = data[self._axis_right_x]
                    right_y = data[self._axis_right_y]

                    if abs(right_x - self._MIDDLE) > abs(right_y - self._MIDDLE):
                        if right_x + self._THRESHOLD < self._MIDDLE:
                            self._set_right_stick_active("left")
                        elif right_x - self._THRESHOLD > self._MIDDLE:
                            self._set_right_stick_active("right")
                        else:
                            self._set_right_stick_active(None)
                    else:
                        if right_y + self._THRESHOLD < self._MIDDLE:
                            self._set_right_stick_active("forward")
                        elif right_y - self._THRESHOLD > self._MIDDLE:
                            self._set_right_stick_active("backward")
                        else:
                            self._set_right_stick_active(None)

                    left_x = data[self._axis_left_x]
                    left_y = data[self._axis_left_y]

                    if abs(left_x - self._MIDDLE) > abs(left_y - self._MIDDLE):
                        if left_x + self._THRESHOLD < self._MIDDLE:
                            self._set_left_stick_active("counterclockwise")
                        elif left_x - self._THRESHOLD > self._MIDDLE:
                            self._set_left_stick_active("clockwise")
                        else:
                            self._set_left_stick_active(None)
                    else:
                        if left_y + self._THRESHOLD < self._MIDDLE:
                            self._set_left_stick_active("up")
                        elif left_y - self._THRESHOLD > self._MIDDLE:
                            self._set_left_stick_active("down")
                        else:
                            self._set_left_stick_active(None)

            sleep(self._DELAY)

    def get_btn_status(self) -> dict:
        """
        Retrieves the current digital button status.

        :return: The current digital button status.
        :rtype: dict
        """
        with self._lock:
            return self._btn_status.copy()

    def get_analog_right_stick(self) -> dict:
        """
        Retrieves the current state of the analog right stick.

        :return: The current state of the analog right stick.
        :rtype: dict
        """
        with self._lock:
            return self._analog_right_stick.copy()

    def get_analog_left_stick(self) -> dict:
        """
        Retrieves the current state of the analog left stick.

        :return: The current state of the analog left stick.
        :rtype: dict
        """
        with self._lock:
            return self._analog_left_stick.copy()

    def __del__(self):
        """
        Ensures resources are released properly.
        """
        self._close()
