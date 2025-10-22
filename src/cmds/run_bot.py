import os
import random
from typing import Any
from dotenv import load_dotenv
import logging


from pylib_0xe.file.file import File
from src.image_modifier import ImageModifier
from src.movie_sampler import MovieSampler
from src.movie import Movie
from src.min_cost_matcher import MinCostMatcher
from src.utils.terminal_process import TerminalProcess


load_dotenv()
logger = logging.getLogger(__name__)


def read_envs() -> dict[str, Any]:
    return {
        "movie_path": os.getenv("movie_path"),
        "image_path": os.getenv("image_path"),
        "movie_frames_path": os.getenv("movie_frames_path"),
        "use_frame_directory": os.getenv("use_frame_directory"),
        "movie_sampler_path": os.getenv("movie_sampler_path"),
        "box": os.getenv("box"),
        "ratio": os.getenv("ratio"),
        "frame_count_per_box": os.getenv("frame_count_per_box"),
        "final_box_width": os.getenv("final_box_width"),
        "max_same_picture": os.getenv("max_same_picture"),
    }


def main():
    # arg_manager = ArgManager()
    # picture_path = arg_manager.next_arg()
    # debug_text("you've input this: %", picture_path)
    # 1) inputing data
    #   inputing the picture path
    #   inputing the video path
    envs = read_envs()

    # 2) reading the config file
    #   box specification: (count_x, count_y)
    # debug_text('config file is: %', config)

    # # 3) optional - turning the image into box-shaped image
    # # 4) evaluating the mean-rgb for each box
    logger.info("Building blured image...")
    image, mean_rgbs = ImageModifier.get_blured(
        envs["image_path"], {"box": envs["box"], "ratio": envs["ratio"]}
    )
    image.show('nice title')
    image.save('blured.jpg')

    logger.info("Retreiving frames")
    if not envs["use_frame_directory"]:
        movie = Movie(envs["movie_path"], {"cache_path": envs["movie_sampler_path"]})
        movie_frames = MovieSampler.get_random_frames(
            movie,
            {
                "total_frames": envs["frame_count_per_box"],
            },
        )
        movie_frames.sort()
        movie.close()
    else:
        movie_frames = File.get_all_files(envs["movie_frames_path"], ext=".jpg")
        movie_frames = [
            os.path.join(envs["movie_frames_path"], movie_frames[i])
            for i in range(len(movie_frames))
        ]
        random.shuffle(movie_frames)
        movie_frames = movie_frames[: envs["frame_count_per_box"]]

    logger.info("Calculating rgbs for frames...")
    terminal_process = TerminalProcess(len(movie_frames))
    movie_rgbs = []
    for frame_path in movie_frames:
        terminal_process.hit()
        rgb = ImageModifier.get_mean_rgb(ImageModifier.open(frame_path))
        movie_rgbs.append(rgb)
    # debug_text('rgb for sorted pictures: %', movie_rgbs)
    dimensions = (len(mean_rgbs[0]), len(mean_rgbs))
    # total_cells = dimensions[0] * dimensions[1]
    # debug_text('total_cells: %', total_cells)
    # it sould be max-mathcing order
    logger.info("Running MaxMatcher algorithm...")
    max_matcher = MinCostMatcher(
        mean_rgbs, movie_rgbs, {"max_same_picture": envs["max_same_picture"]}
    )
    order = max_matcher.solve()
    # debug_text('oreder is: %', order)
    # order = [random.randint(0, len(movie_rgbs) - 1) for i in range(total_cells)]
    logger.info("Constructing final image...")
    final_image = ImageModifier.construct_box(
        image,
        [movie_frames[order[i]] for i in range(len(order))],
        {
            "dimensions": {"x": dimensions[0], "y": dimensions[1]},
            "final_box_width": envs["final_box_width"],
        },
    )
    # final_image.show('final image')
    final_image.save("box_image.jpg")
    # 5) for each box, sample the movie {sample_times} times and find the euclidean
    #   nearest samples, bring {sampler_count} of them
    # 6) evaluating rgb for each box of the sample movie
    # 7) calculating distance for each box pair from the movie and the picture
    # 8) feed the result into the bipartite-matching algorithm
    # 9) for each box, subtitude the matched box from the movie
    # 10) print the whole image
