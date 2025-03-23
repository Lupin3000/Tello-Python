from signal import signal, SIGINT
from sys import exit
from time import sleep
from types import FrameType
from typing import Optional
from libs.controller import Controller
from libs.drone import TelloDrone


CONTROLLER: str = 'stadia'
DELAY: float = 0.008
SPEED: int = 60


def signal_handler(sig: int, frame: Optional[FrameType]) -> None:
    """
    Handles incoming system signals and raises always an KeyboardInterrupt.

    :param sig: The signal number.
    :type sig: int
    :param frame: The current stack frame.
    :type frame: Optional[FrameType]
    :return: None
    """
    _ = frame

    print(f'[INFO] Signal "{sig}" received.')
    raise KeyboardInterrupt


if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    controller = Controller(name=CONTROLLER)
    tello = TelloDrone()

    try:
        while True:
            tello.reset_rc_speed()

            battery = tello.drone.get_battery()

            if battery < 5:
                print(f'[INFO] Battery is less {battery} %.')
                break

            btn = controller.get_btn_status()

            if btn['TAKEOFF'] and battery > 10:
                tello.start()

            if btn['LANDING'] or battery < 10:
                tello.land()

            stick_right = controller.get_analog_right_stick()

            if stick_right['forward']:
                tello.speed.forward_backward = SPEED

            if stick_right['backward']:
                tello.speed.forward_backward = -SPEED

            if stick_right['left']:
                tello.speed.left_right = -SPEED

            if stick_right['right']:
                tello.speed.left_right = SPEED

            stick_left = controller.get_analog_left_stick()

            if stick_left['up']:
                tello.speed.up_down = SPEED

            if stick_left['down']:
                tello.speed.up_down = -SPEED

            if stick_left['clockwise']:
                tello.speed.clockwise_counterclockwise = -SPEED

            if stick_left['counterclockwise']:
                tello.speed.clockwise_counterclockwise = SPEED

            tello.update_position()

            sleep(DELAY)
    except KeyboardInterrupt:
        print(f'[INFO] Application stopped by user.')
    finally:
        del tello
        del controller
        exit(0)
