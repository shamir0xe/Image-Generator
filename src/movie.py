import cv2
import os


class Movie:
    def __init__(self, movie_name: str, movie_path: str, options=None):
        if options is None:
            options = {}
        self.crop_box = None
        self.movie_name = movie_name
        self.cap = cv2.VideoCapture(movie_path)
        self.capture_path = os.path.join("data", "captures")
        self._duration = None
        if "cache_path" in options:
            self.capture_path = options["cache_path"]

    def set_crop_box(self, crop_box: tuple[int, int]):
        self.crop_box = crop_box

    def get_frame(self, seconds):
        self.cap.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
        has_frames, image = self.cap.read()
        if has_frames:
            image = self.crop(image)
            path = os.path.join(self.capture_path, f"{self.movie_name}-{seconds}.jpg")
            cv2.imwrite(path, image)
            return path
        return None

    def crop(self, img: cv2.typing.MatLike) -> cv2.typing.MatLike:
        if self.crop_box:
            dy = (img.shape[0] - self.crop_box[1]) // 2
            dx = (img.shape[1] - self.crop_box[0]) // 2
            img = img[dy: img.shape[0] - dy, dx: img.shape[1] - dx]
        return img

    def get_duration(self):
        if not self._duration is None:
            return self._duration
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._duration = frame_count / fps
        return self._duration

    def close(self):
        self.cap.release()
