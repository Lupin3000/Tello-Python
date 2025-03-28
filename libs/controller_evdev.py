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

    def _search_device(self) -> Optional[str]:
        #found_devices = []
        #
        #input_paths = list_devices()
        #for path in input_paths:
        #    device = InputDevice(path)
        #    if self._controller_name.lower() in device.name.lower():
        #        found_devices.append((device.name, path))
        #
        #if found_devices:
        #    return found_devices[0][1]
        #else:
        #    error('No controller found.')
        #    return None
        pass

    def _connect_to_controller(self) -> None:
        #self._controller_name = file_name
        #self._controller_path = self._search_device()
        #
        #try:
        #    self._controller = InputDevice(self._controller_path)
        #    info(f'Connected with "{self._controller.name}" controller.')
        #except Exception as err:
        #    error(f'Failed to connect to controller: "{err}".')
        #    exit(1)
        pass

    def _initialize_steering(self) -> None:
        info('Initializing controller steering.')

        btn_section = self._config['Buttons']
        self._btn = {
            'TAKEOFF': int(btn_section['btn_takeoff_value']),
            'LANDING': int(btn_section['btn_landing_value']),
            'PHOTO': int(btn_section['btn_photo_value'])
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
                if event.type == ecodes.EV_KEY:
                    for btn_name, btn_code in self._btn.items():
                        if event.code == btn_code:
                            if event.value == 1:
                                self._btn_status[btn_name] = True
                            elif event.value == 0:
                                self._btn_status[btn_name] = False
        except Exception as err:
            error(f'Controller event error: {err}')
