from atexit import register
from threading import Event
from typing import Tuple
import cv2
import numpy as np
from djitellopy import Tello


class VideoStream:
    """
    This class represents a HUD for the Tello drone's real-time video stream.

    :ivar _MARGIN: Margin (pixels) used for positioning HUD elements.
    :ivar _WHITE_COLOR: Standard color (white) for drawing.
    :ivar _GREEN_COLOR: Status color (green) for safe levels.
    :ivar _YELLOW_COLOR: Warning color (yellow) indicating caution zones.
    :ivar _RED_COLOR: Critical status color (red), used for alerts.
    :ivar _BLACK_COLOR: Color (black) for outlines and contrast-enhancing.
    """

    _MARGIN: int = 20
    _WHITE_COLOR: Tuple[int, int, int] = (255, 255, 255)
    _GREEN_COLOR: Tuple[int, int, int] = (0, 255, 0)
    _YELLOW_COLOR: Tuple[int, int, int] = (0, 255, 255)
    _RED_COLOR: Tuple[int, int, int] = (0, 0, 255)
    _BLACK_COLOR: Tuple[int, int, int] = (0, 0, 0)

    def __init__(self, drone_object: Tello, window_name: str, shutdown_flag: Event):
        """
        Initializes and manages a Tello drone HUD window.

        :param drone_object: A connected Tello drone instance from djitellopy.
        :type drone_object: Tello
        :param window_name: The OpenCV window title for the video stream.
        :type window_name: str
        :param shutdown_flag: Thread-safe flag to coordinate application shutdown.
        :type shutdown_flag: Event
        """
        self._drone = drone_object
        self._window_name = str(window_name)
        self._running = False
        self._shutdown = shutdown_flag
        self._last_frame = None

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
    def _draw_battery(img: np.array, top_left: tuple, bottom_right: tuple, percent: int, radius: int = 10) -> None:
        """
        Draws a graphical representation of drone battery status on the HUD.

        :param img: The image to draw the battery on.
        :type img: np.array
        :param top_left: The top-left corner of the battery (x, y).
        :type top_left: tuple
        :param bottom_right: The bottom-right corner of the battery (x, y).
        :type bottom_right: tuple
        :param percent: The battery percentage.
        :type percent: int
        :param radius: The radius of the battery corners. Default: 10.
        :type radius: int
        :return: None
        """
        x1, y1 = top_left
        x2, y2 = bottom_right

        if percent >= 75:
            color = VideoStream._GREEN_COLOR
        elif percent >= 20:
            color = VideoStream._YELLOW_COLOR
        else:
            color = VideoStream._RED_COLOR

        VideoStream._draw_rounded_rectangle(img, top_left, bottom_right, color, radius)

        pin_width: int = 10
        pin_height = (y2 - y1) // 2
        pin_x1 = x2
        pin_x2 = x2 + pin_width
        pin_y1 = y1 + (y2 - y1 - pin_height) // 2
        pin_y2 = pin_y1 + pin_height

        cv2.rectangle(img, (pin_x1, pin_y1), (pin_x2, pin_y2), color, -1)

        if percent >= 80:
            block_count = 4
        elif percent >= 60:
            block_count = 3
        elif percent >= 40:
            block_count = 2
        elif percent >= 20:
            block_count = 1
        else:
            block_count = 0

        padding: int = 10
        total_blocks: int = 4
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

    @staticmethod
    def _draw_scale_slider(img: np.array, pos_x: int, pos_y: int, color: Tuple[int, int, int]) -> None:
        """
        Draws a slider representing flight height of the drone on the HUD.

        :param img: The image to draw the slider on.
        :type img: np.array
        :param pos_x: The x-coordinate where the slider is to be drawn.
        :type pos_x: int
        :param pos_y: The y-coordinate where the slider is to be drawn.
        :type pos_y: int
        :param color: The color of the slider in a BGR tuple format.
        :type color: Tuple[int, int, int]
        :return: None
        """
        x = pos_x
        y = pos_y

        points = np.array([[x, y], [x - 10, y + 10], [x - 60, y + 10], [x - 60, y - 10], [x - 10, y - 10]])
        cv2.fillPoly(img, [points], color=color)
        cv2.polylines(img, [points], isClosed=True, color=VideoStream._BLACK_COLOR, thickness=1)

    @staticmethod
    def _draw_scale(img: np.array, pos_x: int, height: int) -> None:
        """
        Draws a vertical scale for flight height of the drone on the HUD.

        :param img: The image to draw the scale on.
        :type img: np.array
        :param pos_x: The x-coordinate of the scale's starting position.
        :type pos_x: int
        :param height: The height of the scale.
        :type height: int
        :return: None
        """
        eny_y = int(height)
        start_y = VideoStream._MARGIN

        spacing: int = 4
        short_length: int = 10
        long_length: int = 20

        for y in range(start_y, eny_y + 1, spacing):
            if (y - start_y) % 10 == 0:
                line_length = long_length
            else:
                line_length = short_length

            cv2.line(img, (pos_x - line_length, y), (pos_x, y), VideoStream._WHITE_COLOR, 1)

    def _close(self) -> None:
        """
        Stops the video stream from the Tello drone and closes any OpenCV windows.

        :return: None
        """
        print('[INFO] Force stream stop...')
        self._drone.streamoff()
        cv2.destroyAllWindows()

    def _read_drone_metrics(self) -> Tuple[int, int]:
        """
        Fetches battery and height metrics from Tello drone.

        :return: Returns battery (in %), flight height (in cm).
        :rtype: Tuple[int, int]
        """
        return (
            self._drone.get_battery() or 0,
            self._drone.get_height() or 0
        )

    def _draw_information(self, frame: np.array) -> None:
        """
        Displays drone metrics such as battery status and flight time on current frame.

        :param frame: The current frame to overlay the metrics on.
        :type frame: np.array
        :return: None
        """
        height, width = frame.shape[:2]
        battery, flight_height = self._read_drone_metrics()

        battery_pos_1 = (self._MARGIN, self._MARGIN)
        battery_pos_2 = (self._MARGIN + 100, self._MARGIN + 50)
        scale_pos_x = width - self._MARGIN
        scale_height = height - self._MARGIN

        slider_min_y = self._MARGIN
        slider_max_y = scale_height
        max_flight_height: int = 2000

        current_flight_height = max(0, min(flight_height, max_flight_height))

        if current_flight_height >= 1900:
            slider_color = self._RED_COLOR
        elif current_flight_height >= 1800:
            slider_color = self._YELLOW_COLOR
        else:
            slider_color = self._GREEN_COLOR

        slider_pos_x = scale_pos_x - 25
        slider_pos_y = int(slider_max_y - (current_flight_height / max_flight_height) * (slider_max_y - slider_min_y))

        VideoStream._draw_battery(img=frame, top_left=battery_pos_1, bottom_right=battery_pos_2, percent=battery)
        VideoStream._draw_scale_slider(img=frame, pos_x=slider_pos_x, pos_y=slider_pos_y, color=slider_color)
        VideoStream._draw_scale(img=frame, pos_x=scale_pos_x, height=scale_height)

    def _stream_loop(self) -> None:
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

            self._draw_information(frame=flipped_frame)
            self._last_frame = flipped_frame.copy()

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
            self._stream_loop()

    def stop_stream(self) -> None:
        """
        Stops the active streaming process for the associated object.

        :return: None
        """
        self._running = False

    def capture_photo(self) -> None:
        if self._last_frame is not None:
            print('[INFO] Capture photo from stream.')
        else:
            print('[WARNING] No frame from stream captured.')
