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

    @staticmethod
    def _draw_rounded_rectangle(img: np.array, top_left: tuple, bottom_right: tuple, color: tuple, radius: int) -> None:
        """
        Draw a rounded rectangle on an image.

        :param img: The image to draw the rectangle on.
        :type img: np.array
        :param top_left: The top-left corner of the rectangle (x, y).
        :type top_left: tuple
        :param bottom_right: The bottom-right corner of the rectangle (x, y).
        :type bottom_right: tuple
        :param color: The color of the rectangle.
        :type color: tuple
        :param radius: The radius of the rectangle corners.
        :type radius: int
        :return: None
        """
        x1, y1 = top_left
        x2, y2 = bottom_right

        cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, 2)
        cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, 2)
        cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, 2)
        cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, 2)
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, 2)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, 2)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, 2)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, 2)

    @staticmethod
    def _get_battery_color(percent: int) -> Tuple[int, int, int]:
        """
        Determines the RGB color representation for a given battery percentage.

        :param percent: The battery percentage.
        :type percent: int
        :return: Returns the RGB color.
        :rtype: Tuple[int, int, int]
        """
        if percent >= 75:
            return 0, 255, 0
        elif percent >= 20:
            return 0, 255, 255
        else:
            return 0, 0, 255

    @staticmethod
    def _draw_battery(img: np.array, top_left: tuple, bottom_right: tuple, battery_percent: int) -> None:
        """
        Draws a graphical representation of a battery on the given image.

        :param img: The image to draw the battery on.
        :type img: np.array
        :param top_left: The top-left corner of the battery (x, y).
        :type top_left: tuple
        :param bottom_right: The bottom-right corner of the battery (x, y).
        :type bottom_right: tuple
        :param battery_percent: The battery percentage.
        :type battery_percent: int
        :return: None
        """
        radius = 10
        x1, y1 = top_left
        x2, y2 = bottom_right

        color = VideoStream._get_battery_color(battery_percent)
        VideoStream._draw_rounded_rectangle(img, top_left, bottom_right, color, radius)

        pin_width = 10
        pin_height = (y2 - y1) // 2
        pin_x1 = x2
        pin_x2 = x2 + pin_width
        pin_y1 = y1 + (y2 - y1 - pin_height) // 2
        pin_y2 = pin_y1 + pin_height

        cv2.rectangle(img, (pin_x1, pin_y1), (pin_x2, pin_y2), color, -1)

        if battery_percent >= 80:
            block_count = 4
        elif battery_percent >= 60:
            block_count = 3
        elif battery_percent >= 40:
            block_count = 2
        elif battery_percent >= 20:
            block_count = 1
        else:
            block_count = 0

        padding = 10
        total_blocks = 4
        available_width = x2 - x1 - 2 * padding
        available_height = y2 - y1 - 2 * padding
        block_width = (available_width - (total_blocks - 1) * padding) // total_blocks
        block_height = available_height

        for i in range(block_count):
            bx1 = x1 + padding + i * (block_width + padding)
            by1 = y1 + padding
            bx2 = bx1 + block_width
            by2 = by1 + block_height
            cv2.rectangle(img, (bx1, by1), (bx2, by2), color, -1)

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

    def _draw_scale(self, img: np.array, margin: int = 20, spacing: int = 4) -> None:
        """
        Draws a vertical scale on the provided image.

        :param img: The image to draw the scale on.
        :type img: np.array
        :param margin: The margin around the scale. Default: 20.
        :type margin: int
        :param spacing: The spacing between scale lines. Default: 4.
        :type spacing: int
        :return: None
        """
        height, width = img.shape[:2]

        short_length = 10
        long_length = 20

        start_y = margin
        eny_y = height - margin * 3
        pos_x = width - margin

        for y in range(start_y, eny_y + 1, spacing):
            if (y - start_y) % 10 == 0:
                line_length = long_length
            else:
                line_length = short_length

            cv2.line(img, (pos_x - line_length, y), (pos_x, y), self._FG_COLOR, 1)

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

        VideoStream._draw_battery(current_img, (20, 20), (120, 70), battery)
        self._draw_scale(current_img)

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
