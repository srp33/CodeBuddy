# From https://raw.githubusercontent.com/datenhahn/imgcompare/master/imgcompare/imgcompare.py
# Slightly modified from the original.

# MIT License
#
# Copyright (c) 2016 Jonas Hahn <jonas.hahn@datenhahn.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import io
from PIL import Image
from PIL import ImageChops

class ImageCompareException(Exception):
    pass

def diff_jpg(expected_image_string, answer_image_string):
    expected_bytes = decode_image_string(expected_image_string)
    answer_bytes = decode_image_string(answer_image_string)

    expected_image = Image.open(io.BytesIO(expected_bytes))
    answer_image = Image.open(io.BytesIO(answer_bytes))
    expected_image = expected_image.convert("L")
    answer_image = answer_image.convert("L")

    diff_image = pixel_diff(expected_image, answer_image)
    diff_percent = image_diff_percent(expected_image.size, diff_image)

    expected_image.close()
    answer_image.close()

    return diff_image, diff_percent

def decode_image_string(s):
    return base64.b64decode(s)

def does_image_pass(diff_percent):
    return diff_percent < 0.1

def convert_image_to_bytes(the_image):
    with io.BytesIO() as output:
        the_image.save(output, format="JPEG")
        return output.getvalue()

def pixel_diff(image_a, image_b):
    if image_a.size != image_b.size:
        raise ImageCompareException("Different image sizes, can only compare same size images: A=" + str(image_a.size) + " B=" + str(image_b.size))

    if image_a.mode != image_b.mode:
        raise ImageCompareException("Different image mode, can only compare same mode images: A=" + str(image_a.mode) + " B=" + str(image_b.mode))

    diff = ImageChops.difference(image_a, image_b)
    diff = diff.convert('L')

    return diff

def total_histogram_diff(pixel_diff):
    return sum(i * n for i, n in enumerate(pixel_diff.histogram()))

def image_diff_percent(image_a_size, image_pixel_diff):
    histogram_diff = total_histogram_diff(image_pixel_diff)

    # Get the worst possible difference use a black and a white image of the same size and diff them
    black_reference_image = Image.new('RGB', image_a_size, (0, 0, 0))
    white_reference_image = Image.new('RGB', image_a_size, (255, 255, 255))

    worst_bw_diff = total_histogram_diff(pixel_diff(black_reference_image, white_reference_image))

    percentage_diff = (histogram_diff / float(worst_bw_diff)) * 100

    return percentage_diff
