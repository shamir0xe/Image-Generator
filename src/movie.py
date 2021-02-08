import cv2
import os

class Movie:
    def __init__(self, movie_path, options={}):
        self.cap = cv2.VideoCapture(movie_path)
        self.capture_path = os.path.join('data', 'captures')
        self._duration = None
        if 'cache_path' in options:
            self.capture_path = options['cache_path']

    def get_frame(self, seconds):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
        hasFrames, image = self.cap.read()
        if hasFrames:
            path = os.path.join(self.capture_path, str(seconds) + ".jpg")
            cv2.imwrite(path, image)
            return path
        return None

    def get_duration(self):
        if not self._duration is None:
            return self._duration
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._duration = frame_count / fps
        return self._duration

    def close(self):
        self.cap.release()
