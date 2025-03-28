from logging import getLogger, info, error
from sys import exit
from time import sleep
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
        super().__init__(file_name)

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

        :raises ValueError: If any required configuration section values are missing.
        :return: None
        """
        info('Initializing controller steering.')
        identification_section = self._config['Identification']
        self._report_length = int(identification_section['report_length'])

        btn_section = self._config['Buttons']
        self._btn_byte_index = int(btn_section['btn_byte_index'])

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
            self._axis_left_x = int(analog_section['analog_left_x_index'])
            self._axis_left_y = int(analog_section['analog_left_y_index'])
            self._axis_right_x = int(analog_section['analog_right_x_index'])
            self._axis_right_y = int(analog_section['analog_right_y_index'])
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
            self._controller.close()

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

                    self._axis_values['right_x'] = data[self._axis_right_x]
                    self._axis_values['right_y'] = data[self._axis_right_y]
                    self._axis_values['left_x'] = data[self._axis_left_x]
                    self._axis_values['left_y'] = data[self._axis_left_y]
                    self._evaluate_analog_sticks()

            sleep(self._DELAY)
