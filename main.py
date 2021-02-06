import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, '..')))

from libs.PythonLibrary.arg_manager import Manager as ArgManager
from libs.PythonLibrary.utils import debug_text

def main():
    arg_manager = ArgManager()
    picture_path = arg_manager.next_arg()
    debug_text("you've input this: %", picture_path)
    # 1) inputing data
    #   inputing the picture path
    #   inputing the video path
    # 2) reading the config file
    #   box specification: (count_x, count_y)
    # 3) evaluating the mean-rgb for each box
    # 4) optional - turning the image into box-shaped image
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
