import os
import sys
import random

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, '..')))

from ImageGenerator.libs.PythonLibrary.enums import Errors
from ImageGenerator.libs.PythonLibrary.arg_manager import Manager as ArgManager
from ImageGenerator.libs.PythonLibrary.utils import TerminalProcess, debug_text
from ImageGenerator.libs.PythonLibrary.files import File;
from ImageGenerator.src.image_modifier import ImageModifier
from ImageGenerator.src.movie_sampler import MovieSampler
from ImageGenerator.src.movie import Movie
from ImageGenerator.src.min_cost_matcher import MinCostMatcher


def main():
    # arg_manager = ArgManager()
    # picture_path = arg_manager.next_arg()
    # debug_text("you've input this: %", picture_path)
    # 1) inputing data
    #   inputing the picture path
    #   inputing the video path
    path = os.path.join('config', 'config.json')
    debug_text('image path is %', path)
    if not File.is_file(path):
        raise Exception(Errors.FileNotFound)

    # 2) reading the config file
    #   box specification: (count_x, count_y)
    config = File.read_json(path)
    # debug_text('config file is: %', config)

    # # 3) optional - turning the image into box-shaped image
    # # 4) evaluating the mean-rgb for each box
    debug_text('building blured image')
    image, mean_rgbs = ImageModifier.get_blured(config['image_path'], {
        'box': config['box'], 
        'ratio': config['ratio']
    })
    # image.show('nice title')
    # image.save('blured.jpg')

    debug_text('retreiving frames')
    if not config['use_frame_directory']:
        movie = Movie(config['movie_path'], {
            'cache_path': config['movie_sampler_path']
        })
        movie_frames = MovieSampler.get_random_frames(movie, {
            'total_frames': config['frame_count_per_box'],
        });
        movie_frames.sort()
        movie.close()
    else:
        movie_frames = File.get_all_files(config["movie_frames_path"], ext=".jpg")
        movie_frames = [os.path.join(config["movie_frames_path"], movie_frames[i]) for i in range(len(movie_frames))]
        random.shuffle(movie_frames)
        movie_frames = movie_frames[:config['frame_count_per_box']]
    
    debug_text('calculating rgbs for frames')
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
    debug_text('running MaxMatcher algorithm')
    max_matcher = MinCostMatcher(mean_rgbs, movie_rgbs, {
        'max_same_picture': config['max_same_picture']
    })
    order = max_matcher.solve()
    # debug_text('oreder is: %', order)
    # order = [random.randint(0, len(movie_rgbs) - 1) for i in range(total_cells)]
    debug_text('constructing final image')
    final_image = ImageModifier.construct_box(image, 
        [movie_frames[order[i]] for i in range(len(order))], {
            'dimensions': {
                'x': dimensions[0],
                'y': dimensions[1]
            },
            'final_box_width': config['final_box_width']
        }
    )
    # final_image.show('final image')
    final_image.save('box_image.jpg')
    # 5) for each box, sample the movie {sample_times} times and find the euclidean
    #   nearest samples, bring {sampler_count} of them 
    # 6) evaluating rgb for each box of the sample movie
    # 7) calculating distance for each box pair from the movie and the picture
    # 8) feed the result into the bipartite-matching algorithm
    # 9) for each box, subtitude the matched box from the movie
    # 10) print the whole image
    pass

if __name__ == '__main__':
    main()
