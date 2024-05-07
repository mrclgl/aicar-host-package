
import cv2

from threading import Thread

class Camera():

    def build_gstreamer_pipeline(
        capture_res=(1280, 720), 
        capture_fps=30, 
        flip_method=0, 
        display_res=None, 
        display_fps=None
    ):
        pipeline = (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            % (
                capture_res[0],
                capture_res[1],
                capture_fps,
                flip_method
            ))

        if display_res is not None:
            pipeline += (
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                % (
                    display_res[0],
                    display_res[1]
                ))
        else:
            pipeline += "video/x-raw, format=(string)BGRx ! "

        pipeline += "videoconvert ! video/x-raw, format=(string)BGR ! "

        if display_fps is not None:
            pipeline += (
                "videorate ! video/x-raw,framerate=(fraction)%d/1 ! "
                % (display_fps)
            )

        pipeline += "appsink"

        return pipeline

    def __init__(
        self, 
        capture_res=(1280, 720), 
        capture_fps=30, 
        flip_method=0, 
        display_res=None, 
        display_fps=None
    ):
        self._gstreamer_pipeline = Camera.build_gstreamer_pipeline(
            capture_res,
            capture_fps,
            flip_method,
            display_res,
            display_fps
        )

        self._running = True
        self._image = None

        self._thread = Thread(target=self._update)
        self._thread.setDaemon(True)
        self._thread.start()
        
    def stop(self):
        self._running = False
        self._thread.join()

    def _update(self):
        video = cv2.VideoCapture(self._gstreamer_pipeline, cv2.CAP_GSTREAMER)
        video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while self._running:
            success, image = video.read()

            if success:
                self._image = image

    def get_image(self):
        return self._image
