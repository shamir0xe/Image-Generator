from ..libs.PythonLibrary.utils import debug_text
import random

class MovieSampler:
    @staticmethod
    def get_random_frames(movie, options={}):
        movie_duration = int(movie.get_duration())
        # debug_text('movie duration is: %', movie_duration)
        res = []
        for i in range(options['total_frames']):
            random_second = random.randint(1, movie_duration)
            frame_path = movie.get_frame(random_second)
            # debug_text('captured  frame %:% from movie', int(random_second / 60), random_second % 60)
            # debug_text('saved in %', frame_path)
            debug_text('frame #%', i)
            res.append(frame_path)
        return res
