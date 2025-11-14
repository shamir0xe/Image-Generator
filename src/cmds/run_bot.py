import os
import shutil
import random
import re
from typing import Annotated, Any
from dotenv import load_dotenv
import logging
import csv


from pylib_0xe.file.file import File
import typer
from src.image_modifier import ImageModifier, construct_box
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
        "box": int(os.getenv("box", 0)),
        "frame_count_per_box": int(os.getenv("frame_count_per_box", 0)),
        "final_box_height": int(os.getenv("final_box_height", 0)),
        "ratio": float(os.getenv("ratio", 0)),
        "alpha": float(os.getenv("alpha", 0)),
        "beta": float(os.getenv("beta", 0)),
        "crop_box": (int(os.getenv("crop_box_x", 0)), int(os.getenv("crop_box_y", 0))),
    }


app = typer.Typer(help="Image generator")


def movie_standard_name(movie_name: str) -> str:
    return "-".join(movie_name.lower().replace("  ", " ").split())


def our_filename(filename: str, sname: str):
    pattern = rf".*{sname}-.*"
    return re.match(pattern, filename) is not None


@app.command(name="clear-cache")
def clear_cache(
    movie_name: Annotated[
        str, typer.Option(help="Name of the movie you want to remove")
    ],
):
    envs = read_envs()
    sname = movie_standard_name(movie_name)

    frames_path = os.path.join(envs["movie_frames_path"], sname)
    if os.path.isdir(frames_path):
        shutil.rmtree(frames_path)
        logger.info("Removed frames folder")

    filenames = File.get_all_files("assets", ".csv")
    for filename in filenames:
        if our_filename(filename, sname):
            os.remove(os.path.join("assets", filename))
            logger.info(f"Removed {filename}")


@app.command(name="modify")
def post_modification(
    movie_name: Annotated[
        str, typer.Option(help="The movie name available in the path")
    ],
    use_gpu: Annotated[bool, typer.Option(help="Force to use GPU")] = False,
):
    st_name = "-".join(movie_name.lower().split())
    origin_img = ImageModifier.open(f"assets/{st_name}.png")
    gen_img = ImageModifier.open(f"assets/{st_name}-o1.png")

    if use_gpu:
        modified_img = ImageModifier.add_highlights_mac_gpu(gen_img, origin_img)
    else:
        modified_img = ImageModifier.add_highlights(gen_img, origin_img)
    modified_img.save(f"assets/{st_name}-o2.png")


def get_movie_frames(standard_name: str, envs: dict, generate_frames: bool):

    if generate_frames:
        logger.info("Generting frames...")
        # First clear already cache
        clear_cache(standard_name)

        # Create folders
        if not os.path.isdir(envs["movie_frames_path"]):
            os.makedirs(envs["movie_frames_path"])

        # Generates frame
        movie = Movie(
            standard_name,
            envs["movie_path"],
            {"cache_path": envs["movie_frames_path"]},
        )
        movie_frames = MovieSampler.get_random_frames(
            movie,
            {
                "total_frames": envs["frame_count_per_box"],
                "crop_box": envs["crop_box"],
            },
        )
        movie_frames.sort()
        movie.close()
    else:
        logger.info("Already have the frames, retrieving...")
        # Already have the frames
        movie_frames = File.get_all_files(envs["movie_frames_path"], ext=".jpg")
        movie_frames = [
            os.path.join(envs["movie_frames_path"], movie_frames[i])
            for i in range(len(movie_frames))
        ]
        random.shuffle(movie_frames)
        movie_frames = movie_frames[: envs["frame_count_per_box"]]

    return movie_frames


def calculate_movie_rgbs(
    standard_name: str, movie_frames: list[str], envs: dict
) -> list[tuple[int, int, int]]:

    frame_rgbs_file = f"assets/{standard_name}-{envs['frame_count_per_box']}.csv"

    def resolve():
        movie_rgbs = []
        rgbs = {}

        with open(frame_rgbs_file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                time, r, g, b = row
                rgbs[time] = tuple(map(int, (r, g, b)))

        for frame_path in movie_frames:
            pattern = r".*-(\d+).jpg$"
            match = re.search(pattern, frame_path)
            if match:
                time = match.groups()[0]
                movie_rgbs.append(rgbs[time])
            else:
                raise Exception("invalid time!")

        return movie_rgbs

    if not os.path.isfile(frame_rgbs_file):
        logger.info("We dont have any cache for movie rgbs!")

        all_frames = File.get_all_files(envs["movie_frames_path"], ext=".jpg")
        terminal_process = TerminalProcess(len(all_frames))

        with open(frame_rgbs_file, "w") as f:
            writer = csv.writer(f)
            for frame in all_frames:
                if not our_filename(frame, standard_name):
                    continue
                terminal_process.hit()
                rgb = ImageModifier.get_mean_rgb(
                    ImageModifier.open(os.path.join(envs["movie_frames_path"], frame))
                )
                pattern = r"-(\d+).jpg$"
                match = re.search(pattern, frame)
                if not match:
                    raise Exception("invalid frame")
                time = match.groups()[0]
                writer.writerow([time, *rgb])

    return resolve()


@app.command(name="gen")
def main(
    movie_name: Annotated[
        str, typer.Option(help="The movie name available in the path")
    ],
    movie_format: Annotated[str, typer.Option(help="Format of the video")],
    generate_frames: Annotated[
        bool, typer.Option(help="Force to generate frames from the movie")
    ] = False,
):
    logging.info(f"Processing {movie_name}.{movie_format}")

    envs = read_envs()
    envs["movie_path"] += f"{movie_name}.{movie_format}"
    standard_name = movie_standard_name(movie_name)
    envs["movie_frames_path"] = os.path.join(envs["movie_frames_path"], standard_name)

    logger.info("Building blured image...")
    image, mean_rgbs = ImageModifier.get_blured(
        envs["image_path"],
        {
            "box": envs["box"],
        },
    )
    image.show(movie_name)
    image.save(f"assets/{standard_name}.png")

    dimensions = (len(mean_rgbs[0]), len(mean_rgbs))
    logger.info(f"dimensions = {dimensions}")

    logger.info("Retreiving frames")
    movie_frames = get_movie_frames(standard_name, envs, generate_frames)

    logger.info("Calculating rgbs for frames...")
    movie_rgbs = calculate_movie_rgbs(standard_name, movie_frames, envs)

    logger.info("Running MaxMatcher algorithm...")
    max_matcher = MinCostMatcher(mean_rgbs, movie_rgbs)
    order = max_matcher.best_match()
    # order = max_matcher.solve(10)[0]

    logger.info("Constructing final image...")

    final_image = construct_box(
        image,
        [movie_frames[order[i]] for i in range(len(order))],
        mean_rgbs,
        {
            "dimensions": {"x": dimensions[0], "y": dimensions[1]},
            "ratio": envs["ratio"],
            "color_mixtures": {"alpha": envs["alpha"], "beta": envs["beta"]},
            "final_box_height": envs["final_box_height"],
        },
    )
    final_image.save(f"assets/{standard_name}-o1.png")
