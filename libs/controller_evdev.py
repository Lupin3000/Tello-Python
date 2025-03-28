from logging import getLogger, info, error
from sys import exit
from typing import Optional
from evdev import InputDevice, list_devices, ecodes
from libs.controller_base import BaseController


logger = getLogger(__name__)


class EvDevController(BaseController):
    """
    Manages a controller connection and provides mechanisms to access and update controller states.
    """

    def __init__(self, file_name: str):
        super().__init__(file_name)

        # missing implementation
        print('[DEVELOPMENT] Missing implementation application stopping.')
        exit(1)

    @staticmethod
    def _search_device(name: str) -> Optional[str]:
        """
        Searches for an input device by its name and returns the corresponding device path if found.

        :param name: The name of the device to search for.
        :type name: str
        :return: The path of the first matching input device, if found.
        :rtype: Optional[str]
        """
        found_devices = []
        input_paths = list_devices()

        info(f'Searching for controller "{name}".')
        for path in input_paths:
            device = InputDevice(path)
            if name.lower() in device.name.lower():
                found_devices.append((device.name, path))

        if found_devices:
            return found_devices[0][1]
        else:
            error(f'Controller "{name}" not found.')
            exit(1)

    def _connect_to_controller(self) -> None:
        """
        Attempts to connect to the controller device using the configuration value
        for name, initializes the controller object.

        :raises Exception: If the connection to the controller fails.
        :return: None
        """
        info('Connecting to controller.')
        identification_section = self._config['Identification']
        controller_name = identification_section['name']
        controller_path = EvDevController._search_device(name=controller_name)

        try:
            self._controller = InputDevice(controller_path)
            info(f'Connected with "{self._controller.name}" controller.')
        except Exception as err:
            error(f'Failed to connect to controller: "{err}".')
            exit(1)

    def _initialize_steering(self) -> None:
        """
        Initializes the steering configuration for various control parameters. This
        method sets up the internal properties such as button statuses, analog stick
        mappings, and other configuration details necessary for steering operations.

        :raises ValueError: If any required configuration section values are missing.
        :return: None
        """
        info('Initializing controller steering.')

        btn_section = self._config['Buttons']

        try:
            self._btn = {
                'TAKEOFF': int(btn_section['btn_takeoff_value']),
                'LANDING': int(btn_section['btn_landing_value']),
                'PHOTO': int(btn_section['btn_photo_value'])
            }
        except AttributeError:
            raise ValueError(f'Failed to load correct button configuration.')

        analog_section = self._config['AnalogSticks']

        try:
            self._analog_middle = int(analog_section['analog_middle_value'])
            self._analog_threshold = int(analog_section['analog_threshold_value'])
            self._axis_left_x = getattr(ecodes, analog_section['analog_left_x_index'])
            self._axis_left_y = getattr(ecodes, analog_section['analog_left_y_index'])
            self._axis_right_x = getattr(ecodes, analog_section['analog_right_x_index'])
            self._axis_right_y = getattr(ecodes, analog_section['analog_right_y_index'])
        except AttributeError:
            raise ValueError(f'Failed to load correct analog stick configuration.')

        self._axis_values = {
            'left_x': self._analog_middle,
            'left_y': self._analog_middle,
            'right_x': self._analog_middle,
            'right_y': self._analog_middle
        }

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
                with self._lock:
                    if event.type == ecodes.EV_KEY:
                        for btn_name, btn_code in self._btn.items():
                            if event.code == btn_code:
                                if event.value == 1:
                                    self._btn_status[btn_name] = True
                                elif event.value == 0:
                                    self._btn_status[btn_name] = False

                    elif event.type == ecodes.EV_ABS:
                        if event.code == self._axis_right_x:
                            self._axis_values['right_x'] = event.value
                        elif event.code == self._axis_right_y:
                            self._axis_values['right_y'] = event.value
                        elif event.code == self._axis_left_x:
                            self._axis_values['left_x'] = event.value
                        elif event.code == self._axis_left_y:
                            self._axis_values['left_y'] = event.value

                        self._evaluate_analog_sticks()
        except Exception as err:
            error(f'Controller event error: {err}')
