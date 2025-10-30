import random
import logging

from src.movie import Movie
from src.utils.terminal_process import TerminalProcess

logger = logging.getLogger(__name__)


class MovieSampler:
    @staticmethod
    def get_random_frames(movie: Movie, options={}):
        movie_duration = int(movie.get_duration())
        res = []
        if options["crop_box"] and options["crop_box"][0] > 0:
            movie.set_crop_box(options["crop_box"])

        tp = TerminalProcess(movie_duration)
        for i in range(movie_duration):
            tp.hit()
            frame_path = movie.get_frame(i + 1)
            res.append(frame_path)

        random.shuffle(res)
        return res[:options["total_frames"]]
