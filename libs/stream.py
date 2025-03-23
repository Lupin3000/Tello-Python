from atexit import register
from threading import Event
from typing import Tuple
import cv2
import numpy as np
from djitellopy import Tello


class VideoStream:
    """
    Represents a control interface for managing a Tello drone's video stream and real-time
    operations display.

    :ivar _BG_COLOR: The background color for the OpenCV window.
    :ivar _FG_COLOR: The foreground color for the OpenCV window.
    :ivar _FONT_TYPE: The font type for the OpenCV window.
    :ivar _FONT_SCALE: The font scale for the OpenCV window.
    """

    _BG_COLOR: Tuple[int, int, int] = (0, 0, 0)
    _FG_COLOR: Tuple[int, int, int] = (255, 255, 255)
    _FONT_TYPE: int = cv2.FONT_HERSHEY_SIMPLEX
    _FONT_SCALE: float = .5

    def __init__(self, drone_object: Tello, window_name: str, shutdown_flag: Event):
        """
        Represents a control interface for managing a Tello drone's operations.

        :param drone_object: The Tello drone object.
        :type drone_object: Tello
        :param window_name: The name of the OpenCV window.
        :type window_name: str
        :param shutdown_flag: The shutdown event flag.
        :type shutdown_flag: Event
        """
        self._drone = drone_object
        self._window_name = str(window_name)
        self._running = False
        self._shutdown = shutdown_flag

        register(self._close)

    def _close(self) -> None:
        """
        Stops the video stream from the drone and closes any OpenCV windows.

        :return: None
        """
        print('[INFO] Force stream stop...')
        self._drone.streamoff()
        cv2.destroyAllWindows()

    def start_stream(self) -> None:
        """
        Starts the streaming process if it is not already running.

        :return: None
        """
        if not self._running:
            self._running = True
            self._loop()

    def stop_stream(self) -> None:
        """
        Stops the active streaming process for the associated object.

        :return: None
        """
        self._running = False

    def _read_drone_metrics(self) -> Tuple[int, int, int, int]:
        """
        Fetches and processes metrics from Tello drone.

        :return: Returns battery (%), temperature (Celsius), height (cm), and flight time (s).
        :rtype: Tuple[int, int, int, int]
        """
        battery = self._drone.get_battery()
        temperature = self._drone.get_temperature()
        height = self._drone.get_height()
        flight_time = self._drone.get_flight_time()

        val_battery = battery if battery is not None else 0
        val_temperature = temperature if temperature is not None else 0
        val_height = height if height is not None else 0
        val_flight_time = flight_time if flight_time is not None else 0

        return val_battery, val_temperature, val_height, val_flight_time

    def _draw_information(self, current_frame) -> None:
        # height, width = current_frame.shape[:2]
        # battery, temperature, height, flight_time = self._read_drone_metrics()
        pass

    def _loop(self) -> None:
        """
        Executes the main loop to process video frames from the drone, allowing real-time
        display of the stream, and handles user input for terminating the stream.

        :return: None
        """
        self._drone.streamon()

        cv2.namedWindow(self._window_name, cv2.WINDOW_AUTOSIZE)
        frame_reader = self._drone.get_frame_read()

        while self._running and not self._shutdown.is_set():
            bgr_frame = frame_reader.frame

            if bgr_frame is None:
                print('[WARNING] No frame received.')
                continue

            if bgr_frame.dtype != np.uint8:
                bgr_frame = bgr_frame.astype(np.uint8)

            rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            flipped_frame = cv2.flip(rgb_frame, 1)

            cv2.imshow(self._window_name, flipped_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                self._running = False
                raise KeyboardInterrupt

        self._close()
