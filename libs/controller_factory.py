from logging import getLogger, info
from platform import system
from libs.controller_base import BaseController


logger = getLogger(__name__)


class ControllerFactory:
    """
    Factory class that creates controller instances based on the system type.
    """

    def __init__(self):
        """
        Represents a class with system information to provide correct controller instances.
        """
        self._system_name = system()

    def create(self, name: str) -> BaseController:
        """
        Creates and returns a `BaseController` instance based on the operating system.

        :param name: The name of the controller to be created.
        :type name: str
        :return: An instance of `BaseController` initialized with the given name.
        :rtype: BaseController
        """
        if self._system_name == 'Darwin':
            info('Using Python hidapi controller.')
            from libs.controller_hid import HidController
            return HidController(name=name)
        elif self._system_name == 'Linux':
            info('Using Python evdev controller.')
            from libs.controller_evdev import EvDevController
            return EvDevController(name=name)
        else:
            raise OSError(f'Unsupported system: "{self._system_name}".')
