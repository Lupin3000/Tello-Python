from atexit import register
from threading import Event
from djitellopy import Tello
import cv2


class VideoStream:
    """
    Represents a control interface for managing a Tello drone's video stream and real-time
    operations display.
    """

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

            # frame_width = bgr_frame.shape[1]
            rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            flipped_frame = cv2.flip(rgb_frame, 1)

            cv2.imshow(self._window_name, flipped_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                self._running = False
                raise KeyboardInterrupt

        self._close()
