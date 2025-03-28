from logging import getLogger, info, error
from atexit import register
from configparser import ConfigParser
from pathlib import Path
from sys import exit
from threading import Thread, Lock
from time import sleep
from typing import Optional
from hid import device
from libs.controller_base import BaseController


logger = getLogger(__name__)


class HidController(BaseController):
    """
    Manages a controller connection and provides mechanisms to access and update controller states.

    :ivar _DELAY: The delay between controller reads in seconds.
    """

    _DELAY: float = 0.01

    def __init__(self, file_name: str):
        """
        Represents a controller interface for handling configuration, connections, and
        interaction with a controller device via hidapi.

        :param file_name: The configuration file name for the controller.
        :type file_name: str
        """
        self._configuration_file_name = str(file_name)
        self._config = None
        self._controller = None

        self._load_controller_configuration()
        self._connect_to_controller()
        self._initialize_steering()

        register(self._close)

        self._lock = Lock()
        self._thread = Thread(target=self._read_controller, daemon=True)
        self._thread.start()

    def _load_controller_configuration(self) -> None:
        """
        Loads and initializes the controller configuration.

        :raises FileNotFoundError: If the configuration file is not found.
        :raises ValueError: If any required configuration sections are missing.
        :return: None
        """
        info('Loading controller configuration.')
        config_path = (Path(__file__).parent.parent / "config" / self._configuration_file_name)

        if not config_path.exists():
            raise FileNotFoundError(f'Configuration file "{config_path}" not found.')

        config = ConfigParser(strict=True)
        config.read(config_path)

        for section in self._REQUIRED_SECTIONS:
            if section not in config:
                raise ValueError(f'Missing config section: {section}')

        self._config = config

    def _connect_to_controller(self) -> None:
        """
        Attempts to connect to the controller device using configuration values
        for vendor and product IDs, initializes the controller object, and sets
        it to non-blocking mode.

        :raises Exception: If the connection to the controller fails.
        :return: None
        """
        info('Connecting to controller.')
        identification_section = self._config['Identification']
        vendor = int(identification_section['vendor'])
        product = int(identification_section['product'])

        try:
            self._controller = device()
            self._controller.open(vendor, product)
            self._controller.set_nonblocking(True)
            self._name = self._controller.get_product_string()
            info(f'Connected with "{self._name}" controller.')
        except Exception as err:
            error(f'Failed to connect to controller: "{err}".')
            exit(1)

    def _initialize_steering(self) -> None:
        """
        Initializes the steering configuration for various control parameters. This
        method sets up the internal properties such as button statuses, analog stick
        mappings, and other configuration details necessary for steering operations.

        :return: None
        """
        info('Initializing controller steering.')
        identification_section = self._config['Identification']
        self._report_length = int(identification_section['report_length'])

        self._btn_status = {
            'TAKEOFF': False,
            'LANDING': False,
            'PHOTO': False
        }

        btn_section = self._config['Buttons']
        self._btn_byte_index = int(btn_section['btn_byte_index'])

        self._btn = {
            'TAKEOFF': int(btn_section['btn_takeoff_value']),
            'LANDING': int(btn_section['btn_landing_value']),
            'PHOTO': int(btn_section['btn_photo_value'])
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

        analog_section = self._config['AnalogSticks']

        self._analog_middle = int(analog_section['analog_middle_value'])
        self._analog_threshold = int(analog_section['analog_threshold_value'])
        self._axis_left_x = int(analog_section['analog_left_x_index'])
        self._axis_left_y = int(analog_section['analog_left_y_index'])
        self._axis_right_x = int(analog_section['analog_right_x_index'])
        self._axis_right_y = int(analog_section['analog_right_y_index'])


    def _close(self) -> None:
        """
        Closes the connection to the controller.

        :return: None
        """
        if self._controller:
            info('Disconnect from controller.')
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
            data = self._controller.read(self._report_length)

            if data:
                with self._lock:
                    btn_state = data[self._btn_byte_index]

                    for key in self._btn.keys():
                        self._btn_status[key] = btn_state == self._btn[key]

                    right_x = data[self._axis_right_x]
                    right_y = data[self._axis_right_y]

                    if abs(right_x - self._analog_middle) > abs(right_y - self._analog_middle):
                        if right_x + self._analog_threshold < self._analog_middle:
                            self._set_right_stick_active("left")
                        elif right_x - self._analog_threshold > self._analog_middle:
                            self._set_right_stick_active("right")
                        else:
                            self._set_right_stick_active(None)
                    else:
                        if right_y + self._analog_threshold < self._analog_middle:
                            self._set_right_stick_active("forward")
                        elif right_y - self._analog_threshold > self._analog_middle:
                            self._set_right_stick_active("backward")
                        else:
                            self._set_right_stick_active(None)

                    left_x = data[self._axis_left_x]
                    left_y = data[self._axis_left_y]

                    if abs(left_x - self._analog_middle) > abs(left_y - self._analog_middle):
                        if left_x + self._analog_threshold < self._analog_middle:
                            self._set_left_stick_active("counterclockwise")
                        elif left_x - self._analog_threshold > self._analog_middle:
                            self._set_left_stick_active("clockwise")
                        else:
                            self._set_left_stick_active(None)
                    else:
                        if left_y + self._analog_threshold < self._analog_middle:
                            self._set_left_stick_active("up")
                        elif left_y - self._analog_threshold > self._analog_middle:
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
