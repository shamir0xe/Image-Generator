from PIL import Image
import operator
import math
from ..libs.PythonLibrary.utils import debug_text

class ImageModifier:
    @staticmethod
    def get_blured(image_path, properties):
        image = Image.open(image_path)
        y_len, x_len = image.size
        debug_text('image size: %', image.size)
        res_image = Image.new('RGB', image.size)
        box = properties['box']
        count = (math.ceil(x_len / box['x']), math.ceil(y_len / box['y']))
        debug_text('count is: %', count)
        mean_rgbs = [[(0, 0, 0) for j in range(count[1])]
                    for i in range(count[0])]
        data = list(image.getdata())
        res_data = [(0, 0, 0) for _ in range(len(data))]
        for i in range(count[0]):
            for j in range(count[1]):
                rgb = (0, 0, 0)
                total = 0
                ii = 0
                while ii < box['x'] and i + ii < x_len:
                    jj = 0
                    while jj < box['y'] and j + jj < y_len:
                        rgb = tuple(map(operator.add, rgb, data[(i + ii) * y_len + j + jj]))
                        jj += 1
                        total += 1
                    ii += 1
                rgb = tuple(map(operator.mul, rgb, (1 / total, 1 / total, 1 / total)))
                mean_rgbs[i][j] = rgb
                debug_text('generated rgb is: %', rgb)
                debug_text('total cells are: %', total)
                ii = 0
                while i + ii < x_len:
                    jj = 0
                    while j + jj < y_len:
                        res_data[(i + ii) * y_len + j + jj] = rgb
                        jj += 1
                    ii += 1


        res_image = Image.fromarray(res_data, 'RGB')
        return res_image, mean_rgbs

    @staticmethod
    def get_mean_rgb(image):
        pass