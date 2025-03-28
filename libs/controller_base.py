from abc import ABC, abstractmethod
from typing import Dict


class BaseController(ABC):
    """
    Abstract base class for all controller implementations.
    Defines the interface that each controller must implement.

    :ivar _REQUIRED_SECTIONS: A list of required sections in the configuration file.
    """

    _REQUIRED_SECTIONS = ['Identification', 'Buttons', 'AnalogSticks']

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

    @abstractmethod
    def get_btn_status(self) -> Dict[str, bool]:
        """
        Returns the current status of the mapped controller buttons.

        :return: A dictionary indicating the pressed state of each button.
        :rtype: Dict[str, bool]
        """
        pass

    @abstractmethod
    def get_analog_right_stick(self) -> Dict[str, bool]:
        """
        Returns the current directional state of the right analog stick.

        :return: A dictionary with directional booleans (e.g., 'forward', 'left', etc.).
        :rtype: Dict[str, bool]
        """
        pass

    @abstractmethod
    def get_analog_left_stick(self) -> Dict[str, bool]:
        """
        Returns the current directional state of the left analog stick.

        :return: A dictionary with directional booleans (e.g., 'up', 'counterclockwise', etc.).
        :rtype: Dict[str, bool]
        """
        pass

    @abstractmethod
    def __del__(self):
        """
        Ensures proper cleanup when the controller object is garbage-collected.
        """
        pass
