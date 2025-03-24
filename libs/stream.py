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
    _FONT_SCALE: float = .6

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

    def _read_drone_metrics(self) -> Tuple[int, float, int, int]:
        """
        Fetches and processes metrics from Tello drone.

        :return: Returns battery (%), temperature (Celsius), flight height (cm), and flight time (s).
        :rtype: Tuple[int, float, int, int]
        """
        return (
            self._drone.get_battery() or 0,
            float(self._drone.get_temperature() or 0.0),
            self._drone.get_height() or 0,
            self._drone.get_flight_time() or 0
        )

    def _draw_information(self, current_img: np.array) -> None:
        """
        Displays various drone metrics such as battery percentage, temperature, flight height,
        and flight time overlaid onto the given current image.

        :param current_img: The current image to overlay the metrics on.
        :type current_img: np.array
        :return: None
        """
        height, width = current_img.shape[:2]
        battery, temperature, flight_height, flight_time = self._read_drone_metrics()
        info_txt = f'{battery} % - {temperature} Celsius - {flight_height} cm - {flight_time} sec'

        rect_height = 40
        cv2.rectangle(current_img, (0, height - rect_height), (width, height), self._BG_COLOR, -1)

        (txt_width, txt_height), baseline = cv2.getTextSize(info_txt, self._FONT_TYPE, self._FONT_SCALE, 1)
        text_x = width // 2 - txt_width // 2
        text_y = height - (rect_height - txt_height) // 2 - baseline

        cv2.putText(current_img, text=info_txt, org=(text_x, text_y + 5), fontFace=self._FONT_TYPE,
                    fontScale=self._FONT_SCALE, color=self._FG_COLOR, thickness=1)

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

            self._draw_information(current_img=flipped_frame)

            cv2.imshow(self._window_name, flipped_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                self._running = False
                raise KeyboardInterrupt

        self._close()

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
