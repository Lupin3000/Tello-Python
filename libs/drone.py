from atexit import register
from time import sleep
from typing import Optional
from dataclasses import dataclass
from djitellopy import Tello


@dataclass
class SpeedVector:
    """
    Represents a speed vector in a multidirectional space.

    This class is used for storing the components of a speed vector in four
    potential directions, including forward-backward, left-right, up-down, and
    clockwise-counterclockwise.
    """

    forward_backward: int = 0
    left_right: int = 0
    up_down: int = 0
    clockwise_counterclockwise: int = 0


class TelloDrone:
    """
    Manages interactions and operations with a Tello drone.

    :ivar _SPEED: The default speed (cm/s) for the drone.
    :ivar _DELAY: The delay (seconds) for the drone to takeoff/landing.
    """

    _SPEED: int = 10
    _DELAY: float = 0.25

    def __init__(self, speed: Optional[int] = None):
        """
        Initializes the drone instance and performs initial setup.

        :param speed: The speed (cm/s) of the drone [10 - 100] Default: 10.
        :type speed: Optional[int]
        """
        self.drone = Tello()
        self.drone.connect()

        if speed is None:
            self.drone.set_speed(self._SPEED)
        elif 10 <= speed <= 100:
            self.drone.set_speed(speed)
        else:
            raise ValueError(f'Invalid speed value: {speed}')

        register(self._close)

        self.grounded = True
        self.speed = SpeedVector()

    def _close(self) -> None:
        """
        Forces the drone to land if it is not already landed.

        :return: None
        """
        if self.drone:
            if not self.grounded:
                print('[INFO] Force drone landing...')
                self.drone.land()
                self.grounded = True
            self.drone.end()

    def start(self) -> None:
        """
        Start the drone's takeoff if drone is grounded.

        :return: None
        """
        if self.grounded:
            print('[INFO] Takeoff drone...')
            self.drone.takeoff()
            self.grounded = False

            sleep(self._DELAY)
            print('[INFO] Drone is ready to fly.')

    def land(self) -> None:
        """
        Lands the drone if it is currently airborne.

        :return: None
        """
        if not self.grounded:
            print('[INFO] Landing drone...')
            self.drone.land()
            self.grounded = True

            sleep(self._DELAY)
            print('[INFO] Drone is landed.')

    def update_position(self) -> None:
        """
        Updates the drone's position based on current RC control values.

        :return: None
        """
        if not self.grounded:
            self.drone.send_rc_control(self.speed.left_right,
                                       self.speed.forward_backward,
                                       self.speed.up_down,
                                       self.speed.clockwise_counterclockwise)

    def reset_rc_speed(self) -> None:
        """
        Resets the speed values for all RC directions to their default state.

        :return: None
        """
        self.speed = SpeedVector()

    def __del__(self):
        """
        Ensures resources are released properly.
        """
        self._close()
