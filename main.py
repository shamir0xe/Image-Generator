import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, '..')))

from ImageGenerator.libs.PythonLibrary.enums import Errors
from ImageGenerator.libs.PythonLibrary.arg_manager import Manager as ArgManager
from ImageGenerator.libs.PythonLibrary.utils import debug_text
from ImageGenerator.libs.PythonLibrary.files import File;
from ImageGenerator.src.image_modifier import ImageModifier

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
    debug_text('read file is: %', config)
    # 3) optional - turning the image into box-shaped image
    # 4) evaluating the mean-rgb for each box
    image, mean_rgbs = ImageModifier.get_blured(config['image_path'], {
        'box': config['box'], 
        'ratio': config['ratio']
    })
    image.show('nice title')
    image.save('blured.jpg')
    # debug_text('mean_rgb array is: %', mean_rgbs)
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
