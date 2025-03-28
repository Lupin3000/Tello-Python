from logging import basicConfig, info
from signal import signal, SIGINT
from sys import exit
from threading import Thread, Event
from time import sleep
from types import FrameType
from typing import Optional
from libs.controller_base import BaseController
from libs.controller_factory import ControllerFactory
from libs.drone import TelloDrone
from libs.stream import VideoStream


CONTROLLER_CONFIG: str = 'stadia_macos.ini'
SPEED: int = 60
STREAM: bool = True
WINDOW_NAME: str = 'DJI Tello Drone HUD'
DELAY: float = 0.008
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

    info(f'Signal: "{sig}" received.')
    raise KeyboardInterrupt


def controller_loop(controller_obj: BaseController, drone_obj: TelloDrone, stream_obj: Optional[VideoStream] = None) -> None:
    """
    Controls the main loop driving the interaction between a game controller and a drone.

    :param controller_obj: The controller object.
    :type controller_obj: Controller
    :param drone_obj: The drone object.
    :type drone_obj: TelloDrone
    :param stream_obj: The video stream object.
    :type stream_obj: Optional[VideoStream]
    :return: None
    """
    photo_triggered = False

    while True:
        drone_obj.reset_rc_speed()

        battery = drone_obj.drone.get_battery()

        if battery < 5:
            info(f'[INFO] Battery is less "{battery}%".')
            break

        btn = controller_obj.get_btn_status()

        if btn['TAKEOFF'] and battery > 10:
            drone_obj.start()

        if btn['LANDING'] or battery < 10:
            drone_obj.land()

        if btn['PHOTO'] and stream_obj is not None and not photo_triggered:
            photo_triggered = True
            stream_obj.capture_photo()
        elif not btn['PHOTO']:
            photo_triggered = False

        stick_right = controller_obj.get_analog_right_stick()

        if stick_right['forward']:
            drone_obj.speed.forward_backward = SPEED

        if stick_right['backward']:
            drone_obj.speed.forward_backward = -SPEED

        if stick_right['left']:
            drone_obj.speed.left_right = -SPEED

        if stick_right['right']:
            drone_obj.speed.left_right = SPEED

        stick_left = controller_obj.get_analog_left_stick()

        if stick_left['up']:
            drone_obj.speed.up_down = SPEED

        if stick_left['down']:
            drone_obj.speed.up_down = -SPEED

        if stick_left['clockwise']:
            drone_obj.speed.clockwise_counterclockwise = -SPEED

        if stick_left['counterclockwise']:
            drone_obj.speed.clockwise_counterclockwise = SPEED

        drone_obj.update_position()
        sleep(DELAY)


if __name__ == "__main__":
    basicConfig(
        level='INFO',
        format='[%(levelname)s] %(message)s'
    )

    signal(SIGINT, signal_handler)

    controller_thread = None
    stream = None

    factory = ControllerFactory()
    controller = factory.create(name=CONTROLLER_CONFIG)
    tello = TelloDrone()

    try:
        if STREAM:
            stream = VideoStream(drone_object=tello.drone, window_name=WINDOW_NAME, shutdown_flag=SHUTDOWN)
            controller_thread = Thread(target=controller_loop, args=(controller, tello, stream), daemon=True)

            controller_thread.start()
            stream.start_stream()
        else:
            controller_loop(controller, tello)
    except KeyboardInterrupt:
        info('Application stopped by user.')
    finally:
        if STREAM:
            SHUTDOWN.set()
            controller_thread.join(timeout=1)
            stream.stop_stream()

        del tello
        del controller
        exit(0)
