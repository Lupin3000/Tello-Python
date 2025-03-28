from logging import getLogger, info
from abc import ABC, abstractmethod
from atexit import register
from configparser import ConfigParser
from pathlib import Path
from threading import Thread, Lock
from typing import Dict, Optional


logger = getLogger(__name__)


class BaseController(ABC):
    """
    Abstract base class for all controller implementations.
    Defines the interface that each controller must implement.

    :ivar _REQUIRED_SECTIONS: A list of required sections in the configuration file.
    """

    _REQUIRED_SECTIONS = ['Identification', 'Buttons', 'AnalogSticks']

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

    def get_btn_status(self) -> Dict[str, bool]:
        """
        Retrieves the current digital button status.

        :return: The current digital button status.
        :rtype: Dict[str, bool]
        """
        with self._lock:
            return self._btn_status.copy()

    def get_analog_right_stick(self) -> Dict[str, bool]:
        """
        Retrieves the current state of the analog right stick.

        :return: The current state of the analog right stick.
        :rtype: Dict[str, bool]
        """
        with self._lock:
            return self._analog_right_stick.copy()

    def get_analog_left_stick(self) -> Dict[str, bool]:
        """
        Retrieves the current state of the analog left stick.

        :return: The current state of the analog left stick.
        :rtype: Dict[str, bool]
        """
        with self._lock:
            return self._analog_left_stick.copy()

    def __del__(self):
        """
        Ensures proper cleanup when the controller object is garbage-collected.
        """
        self._close()

    @abstractmethod
    def _connect_to_controller(self) -> None:
        pass

    @abstractmethod
    def _initialize_steering(self) -> None:
        pass

    @abstractmethod
    def _close(self) -> None:
        """
        Closes the connection to the controller and performs necessary cleanup.

        :return: None
        """
        pass

    @abstractmethod
    def _read_controller(self) -> None:
        """
        Reading the controller's state.

        :return: None
        """
        pass
