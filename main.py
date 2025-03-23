from signal import signal, SIGINT
from sys import exit
from threading import Thread, Event
from time import sleep
from types import FrameType
from typing import Optional
from libs.controller import Controller
from libs.drone import TelloDrone
from libs.stream import VideoStream


CONTROLLER: str = 'stadia'
DELAY: float = 0.008
SPEED: int = 60
STREAM: bool = True
WINDOW_NAME: str = 'DJI Tello'
SHUTDOWN: Event = Event()


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


def controller_loop(controller_object: Controller, drone_object: TelloDrone) -> None:
    while True:
        drone_object.reset_rc_speed()

        battery = drone_object.drone.get_battery()

        if battery < 5:
            print(f'[INFO] Battery is less {battery} %.')
            break

        btn = controller_object.get_btn_status()

        if btn['TAKEOFF'] and battery > 10:
            drone_object.start()

        if btn['LANDING'] or battery < 10:
            drone_object.land()

        stick_right = controller_object.get_analog_right_stick()

        if stick_right['forward']:
            drone_object.speed.forward_backward = SPEED

        if stick_right['backward']:
            drone_object.speed.forward_backward = -SPEED

        if stick_right['left']:
            drone_object.speed.left_right = -SPEED

        if stick_right['right']:
            drone_object.speed.left_right = SPEED

        stick_left = controller_object.get_analog_left_stick()

        if stick_left['up']:
            drone_object.speed.up_down = SPEED

        if stick_left['down']:
            drone_object.speed.up_down = -SPEED

        if stick_left['clockwise']:
            drone_object.speed.clockwise_counterclockwise = -SPEED

        if stick_left['counterclockwise']:
            drone_object.speed.clockwise_counterclockwise = SPEED

        drone_object.update_position()

        sleep(DELAY)


if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    controller_thread = None
    stream = None

    controller = Controller(name=CONTROLLER)
    tello = TelloDrone()

    try:
        controller_thread = Thread(target=controller_loop, args=(controller, tello), daemon=True)
        controller_thread.start()

        if STREAM:
            stream = VideoStream(drone_object=tello.drone, window_name=WINDOW_NAME, shutdown_flag=SHUTDOWN)
            stream.start_stream()
        else:
            while True:
                sleep(1)
    except KeyboardInterrupt:
        print('[INFO] Application stopped by user.')
    finally:
        SHUTDOWN.set()
        controller_thread.join(timeout=1)

        if STREAM:
            stream.stop_stream()

        del tello
        del controller
        exit(0)
