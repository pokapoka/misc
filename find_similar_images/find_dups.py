#! /usr/bin/python
# command line utility for detecting duplicate images
# in current directory
import os
import argparse
import sys
from multiprocessing import Pool
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


class ImageComp:
    def __init__(self, name, hash):
        self.name = name
        self.hash = hash

    def __str__(self):
        return self.name

    def __cmp__(self, other):
        if self.hash == other.hash:
            return 0
        if self.hash > other.hash:
            return 1
        if self.hash < other.hash:
            return -1

    def __hash__(self):
        return hash(self.hash)


def create_img(image_name):
    try:
        im = Image.open(image_name)
    except IOError:
        print "{} is not a valid image".format(image_name)
        return
    im = im.resize((8, 8), Image.ANTIALIAS).convert("L")
    average_color = reduce(lambda a, b: a + b, im.getdata()) / float(64)
    tmp_hash = enumerate(map(lambda i: 1 if i > average_color else 0,
                         im.getdata()), 0)
    img_hash = ""
    for i in tmp_hash:
        img_hash += str(i[1])

    return ImageComp(image_name, img_hash)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="""get rid of visually of identical images,
                        leaving ones with the alphabeticaly greatest name""",
                        action="store_true")
    parser.add_argument("-l", help="list visually identical images",
                        action="store_true")
    parser.add_argument("-c", help="use C number of threads", type=int)
    parser.add_argument("-dev", action="store_true")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    if args.c:
        threads_count = args.c
    else:
        threads_count = 4

    pic_names = os.listdir(".")

    if args.dev:
        print create_img(pic_names[3])
        sys.exit()

    images = []
    pool = Pool(threads_count)
    images = pool.map(create_img, pic_names)
    pool.close()
    pool.join()

    images = filter(lambda x: x is not None and x.hash != "", images)
    result = []

    for image in images:
        result.append(tuple(filter(lambda i: image == i, images)))

    result = filter(lambda x: len(x) > 1, result)

    result = list(set(result))

    if args.l:
        for i in result:
            for item in i:
                print item
            print

    if args.d:
        for group in result:
            for name in group[1:]:
                os.popen("rm {}".format(name))


if __name__ == "__main__":
    main()
