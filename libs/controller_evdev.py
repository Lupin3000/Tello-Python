from logging import getLogger, info, error
from atexit import register
from configparser import ConfigParser
from pathlib import Path
from sys import exit
from threading import Thread, Lock
from typing import Optional
from evdev import InputDevice, list_devices, ecodes
from libs.controller_base import BaseController


logger = getLogger(__name__)


class EvDevController(BaseController):
    """
    Manages a controller connection and provides mechanisms to access and update controller states.

    :ivar _DELAY: The delay between controller reads in seconds.
    """

    _DELAY: float = 0.01

    def __init__(self, file_name: str):
        config = ConfigParser()
        config.read(Path(__file__).parent.parent / "config" / file_name)
        
        self._controller_name = name
        self._controller_path = self._search_device()

        try:
            self._controller = InputDevice(self._controller_path)
            info(f'Connected with "{self._controller.name}" controller.')
        except Exception as err:
            error(f'Failed to connect to controller: "{err}".')
            exit(1)

        # missing implementation
        print('[DEVELOPMENT] Missing implementation application stopping.')
        exit(1)

        section = config[name]

        self._analog_middle = int(section['analog_middle_value'])
        self._analog_threshold = int(section['analog_threshold_value'])

        self._btn = {
            'TAKEOFF': int(section['btn_takeoff_value']),
            'LANDING': int(section['btn_landing_value']),
            'PHOTO': int(section['btn_photo_value'])
        }

        self._btn_status = {
            'TAKEOFF': False,
            'LANDING': False,
            'PHOTO': False
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

    def _search_device(self) -> Optional[str]:
        found_devices = []

        input_paths = list_devices()
        for path in input_paths:
            device = InputDevice(path)
            if self._controller_name.lower() in device.name.lower():
                found_devices.append((device.name, path))

        if found_devices:
            return found_devices[0][1]
        else:
            error('No controller found.')
            return None

    def _close(self) -> None:
        """
        Closes the connection to the controller.

        :return: None
        """
        if self._controller:
            info('Disconnect from controller.')
            self._controller = None

    def _read_controller(self) -> None:
        """
        Reads and processes input data from a connected controller in a continuous loop.

        :return: None
        """
        try:
            for event in self._controller.read_loop():
                if event.type == ecodes.EV_KEY:
                    for btn_name, btn_code in self._btn.items():
                        if event.code == btn_code:
                            if event.value == 1:
                                self._btn_status[btn_name] = True
                            elif event.value == 0:
                                self._btn_status[btn_name] = False
        except Exception as err:
            error(f'Controller event error: {err}')

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
