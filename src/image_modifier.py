from PIL import Image
import operator
import math

from src.utils.terminal_process import TerminalProcess


class ImageModifier:
    @staticmethod
    def rgb_to_monochromatic(rgb):
        return (0.2125 * rgb[0]) + (0.7154 * rgb[1]) + (0.0721 * rgb[2])

    @staticmethod
    def open(image_path):
        return Image.open(image_path)

    @staticmethod
    def construct_box(image, images, properties):
        final_image_width = (
            properties["final_box_width"] * properties["dimensions"]["x"]
        )
        image = image.resize(
            (final_image_width, int(final_image_width * image.size[1] / image.size[0]))
        )
        x_len, y_len = image.size
        data = image.load()
        box = {
            "x": x_len / properties["dimensions"]["x"],
            "y": y_len / properties["dimensions"]["y"],
        }
        count = (properties["dimensions"]["x"], properties["dimensions"]["y"])
        terminal_process = TerminalProcess(count[0] * count[1])
        for i in range(count[0]):
            for j in range(count[1]):
                index = count[0] * j + i
                # debug_text('going to open % of images with path = %', index, images[index])
                # debug_text('images index: %', index)
                terminal_process.hit()
                temp_image = Image.open(images[index])
                temp_image = temp_image.resize(
                    (math.ceil(box["x"]), math.ceil(box["y"]))
                )
                temp_data = temp_image.load()
                if temp_data is not None:
                    ii = 0
                    while ii < box["x"] and i * box["x"] + ii < x_len:
                        jj = 0
                        while jj < box["y"] and j * box["y"] + jj < y_len:
                            data[
                                math.floor(i * box["x"] + ii),
                                math.floor(j * box["y"] + jj),
                            ] = temp_data[ii, jj]
                            jj += 1
                        ii += 1
                else:
                    raise Exception("something wiered happened!")
        return image

    @staticmethod
    def get_blured(image_path, properties):
        image = Image.open(image_path)
        x_len, y_len = image.size
        res_image = Image.new("RGB", image.size)
        box = {
            "x": math.ceil(x_len / properties["box"]),
            "y": math.ceil(y_len / properties["box"]),
        }
        box["x"] = max(box["y"], box["x"])
        box["y"] = math.ceil(box["x"] / properties["ratio"])
        count = (math.ceil(x_len / box["x"]), math.ceil(y_len / box["y"]))
        mean_rgbs = [[(0, 0, 0) for _ in range(count[0])] for _ in range(count[1])]
        data = list(image.getdata())  # pyright: ignore
        res_data = res_image.load()
        if res_data is None:
            raise Exception("result data is None!")
        # res_data = np.ndarray((image.size[1], image.size[0]))
        # debug_text(res_data)
        terminal_process = TerminalProcess(count[0] * count[1])
        for i in range(count[0]):
            for j in range(count[1]):
                terminal_process.hit()
                rgb = (0, 0, 0)
                total = 0
                ii = 0
                while ii < box["x"] and i * box["x"] + ii < x_len:
                    jj = 0
                    while jj < box["y"] and j * box["y"] + jj < y_len:
                        rgb = tuple(
                            map(
                                operator.add,
                                rgb,
                                data[(j * box["y"] + jj) * x_len + i * box["x"] + ii],
                            )
                        )
                        jj += 1
                        total += 1
                    ii += 1
                rgb = tuple(map(operator.mul, rgb, (1 / total, 1 / total, 1 / total)))
                rgb = tuple(map(math.floor, rgb))
                mean_rgbs[j][i] = rgb
                ii = 0
                while ii < box["x"] and i * box["x"] + ii < x_len:
                    jj = 0
                    while jj < box["y"] and j * box["y"] + jj < y_len:
                        res_data[i * box["x"] + ii, j * box["y"] + jj] = rgb
                        jj += 1
                    ii += 1
        return res_image, mean_rgbs

    @staticmethod
    def get_mean_rgb(image):
        data = list(image.resize((100, 100)).getdata())
        rgb = (0, 0, 0)
        for i in range(len(data)):
            rgb = tuple(map(operator.add, rgb, data[i]))
        total = len(data)
        rgb = tuple(map(operator.mul, rgb, (1 / total, 1 / total, 1 / total)))
        rgb = tuple(map(math.floor, rgb))
        return rgb
