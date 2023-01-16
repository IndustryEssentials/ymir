from typing import List, Union

import numpy as np
from pycocotools import mask as pct_mask_utils

from mir.protos import mir_command_pb2 as mirpb


def coco_rle_to_ls_rle(mask_or_polygon: Union[str, List[mirpb.IntPoint]], width: int, height: int) -> List[int]:
    """
    Change coco mask or polygon to ls rle encoded mask
    """
    if isinstance(mask_or_polygon, str):
        coco_seg = {'counts': mask_or_polygon, 'size': [height, width]}
    elif isinstance(mask_or_polygon, list):
        polygon = []
        for p in mask_or_polygon:
            polygon.extend([p.x, p.y])
        coco_seg = pct_mask_utils.frPyObjects([polygon], height, width)

    # coco_seg: dict -> mask: np.ndarray (shape: h * w * 1) -> reshape to (h * w) -> ls_rle: List[int]
    mask_np = pct_mask_utils.decode(coco_seg).reshape((height, width))
    # https://labelstud.io/guide/predictions.html#Import-brush-segmentation-pre-annotations-in-RLE-format
    return _mask2rle(mask_np * 255)


def _mask2rle(mask: np.ndarray) -> List[int]:
    """ Convert mask to RLE

    :param mask: uint8 or int np.array mask with len(shape) == 2 like grayscale image
    :return: list of ints in RLE format
    """
    assert len(mask.shape) == 2, 'mask must be 2D np.array'
    assert mask.dtype == np.uint8 or mask.dtype == int, 'mask must be uint8 or int'
    array = mask.ravel()
    array = np.repeat(array, 4)  # must be 4 channels
    rle = _encode_rle(array)
    return rle


def _encode_rle(arr: np.ndarray, wordsize: int = 8, rle_sizes: List[int] = [3, 4, 8, 16]) -> List[int]:
    """ Encode a 1d array to rle
    :param arr: flattened np.array from a 4d image (R, G, B, alpha)
    :type arr: np.array
    :param wordsize: wordsize bits for decoding, default is 8
    :type wordsize: int
    :param rle_sizes:  list of ints which state how long a series is of the same number
    :type rle_sizes: list
        :return rle: run length encoded array
    :type rle: list
    """
    # Set length of array in 32 bits
    num = len(arr)
    numbits = f'{num:032b}'

    # put in the wordsize in bits
    wordsizebits = f'{wordsize - 1:05b}'

    # put rle sizes in the bits
    rle_bits = ''.join([f'{x - 1:04b}' for x in rle_sizes])

    # combine it into base string
    base_str = numbits + wordsizebits + rle_bits

    # start with creating the rle bite string
    out_str = ''
    for length_reeks, p, value in zip(*_base_rle_encode(arr)):
        # TODO: A nice to have but --> this can be optimized but works
        if length_reeks == 1:
            # we state with the first 0 that it has a length of 1
            out_str += '0'
            # We state now the index on the rle sizes
            out_str += '00'

            # the rle size value is 0 for an individual number
            out_str += '000'

            # put the value in a 8 bit string
            out_str += f'{value:08b}'

        elif length_reeks > 1:
            # rle size = 3
            if length_reeks <= 8:
                # Starting with a 1 indicates that we have started a series
                out_str += '1'

                # index in rle size arr
                out_str += '00'

                # length of array to bits
                out_str += f'{length_reeks - 1:03b}'

                out_str += f'{value:08b}'

            # rle size = 4
            elif 8 < length_reeks <= 16:
                # Starting with a 1 indicates that we have started a series
                out_str += '1'
                out_str += '01'

                # length of array to bits
                out_str += f'{length_reeks - 1:04b}'

                out_str += f'{value:08b}'

            # rle size = 8
            elif 16 < length_reeks <= 256:
                # Starting with a 1 indicates that we have started a series
                out_str += '1'

                out_str += '10'

                # length of array to bits
                out_str += f'{length_reeks - 1:08b}'

                out_str += f'{value:08b}'

            # rle size = 16 or longer
            else:

                length_temp = length_reeks
                while length_temp > 2 ** 16:
                    # Starting with a 1 indicates that we have started a series
                    out_str += '1'

                    out_str += '11'
                    out_str += f'{2 ** 16 - 1:016b}'

                    out_str += f'{value:08b}'
                    length_temp -= 2 ** 16

                # Starting with a 1 indicates that we have started a series
                out_str += '1'

                out_str += '11'
                # length of array to bits
                out_str += f'{length_temp - 1:016b}'

                out_str += f'{value:08b}'

    # make sure that we have an 8 fold lenght otherwise add 0's at the end
    nzfill = 8 - len(base_str + out_str) % 8
    total_str = base_str + out_str
    total_str = total_str + nzfill * '0'

    rle = _bits2byte(total_str)

    return rle


def _base_rle_encode(inarray: np.ndarray) -> tuple:
    """ run length encoding. Partial credit to R rle function.
        Multi datatype arrays catered for including non Numpy
        returns: tuple (runlengths, startpositions, values) """
    ia = np.asarray(inarray)                # force numpy
    n = len(ia)
    if n == 0:
        return None, None, None
    else:
        y = ia[1:] != ia[:-1]                # pairwise unequal (string safe)
        i = np.append(np.where(y), n - 1)    # must include last element posi
        z = np.diff(np.append(-1, i))        # run lengths
        p = np.cumsum(np.append(0, z))[:-1]  # positions
        return z, p, ia[i]


def _bits2byte(arr_str: str, n: int = 8) -> List[int]:
    """ Convert bits back to byte
    :param arr_str:  string with the bit array
    :type arr_str: str
    :param n: number of bits to separate the arr string into
    :type n: int
    :return rle:
    :type rle: list
    """
    rle = []
    numbers = [arr_str[i:i + n] for i in range(0, len(arr_str), n)]
    for i in numbers:
        rle.append(int(i, 2))
    return rle
