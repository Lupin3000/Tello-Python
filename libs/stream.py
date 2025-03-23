from atexit import register
from threading import Event
import cv2


class VideoStream:

    def __init__(self, drone_object, window_name: str, shutdown_flag: Event):
        self._drone = drone_object
        self._window_name = str(window_name)
        self._running = False
        self._shutdown = shutdown_flag

        register(self._close)

    def _close(self) -> None:
        print('[INFO] Force stream stop...')
        self._drone.streamoff()
        cv2.destroyAllWindows()

    def start_stream(self):
        if not self._running:
            self._running = True
            self._loop()

    def stop_stream(self):
        self._running = False

    def _loop(self) -> None:
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
