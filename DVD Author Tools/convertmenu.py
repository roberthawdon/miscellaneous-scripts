#!/usr/bin/env python
import xmltodict
import re
from argparse import ArgumentParser

def ConvertMenu(filein, ntsc):

    with open(filein) as fd:
        docin = xmltodict.parse(fd.read())

    highlight = docin['subpictures']['stream']['spu']['@highlight']
    select = docin['subpictures']['stream']['spu']['@select']

    if ntsc and "pal" in highlight:
        docin['subpictures']['stream']['spu']['@highlight'] = re.sub('pal', 'ntsc', highlight)
    elif not ntsc and "ntsc" in highlight:
        docin['subpictures']['stream']['spu']['@highlight'] = re.sub('ntsc', 'pal', highlight)

    if ntsc and "pal" in select:
        docin['subpictures']['stream']['spu']['@select'] = re.sub('pal', 'ntsc', select)
    elif not ntsc and "ntsc" in select:
        docin['subpictures']['stream']['spu']['@select'] = re.sub('ntsc', 'pal', select)

    buttondefs = docin['subpictures']['stream']['spu']['button']

    count = 0
    for buttons in buttondefs:
        buttonname = docin['subpictures']['stream']['spu']['button'][count]['@name']
        if ntsc:
            y0 = int(round(float(buttons['@y0'])) / 1.2)
            if y0%2 != 0:
                y0 = y0 + 1
            y1 = int(round(float(buttons['@y1'])) / 1.2)
            if y1%2 != 0:
                y1 = y1 + 1
        else:
            y0 = int(round(float(buttons['@y0'])) * 1.2)
            if y0%2 != 0:
                y0 = y0 + 1
            y1 = int(round(float(buttons['@y1'])) * 1.2)
            if y1%2 != 0:
                y1 = y1 + 1
            if y0 > 576 or y1 > 576:
                print "Error, button element \"" + buttonname + "\" is placed below the bottom of the frame. Maybe your source file is already PAL formatted. If you're trying to convert to NTSC, use the -n switch."
                exit(1)
        docin['subpictures']['stream']['spu']['button'][count]['@y0'] = y0
        docin['subpictures']['stream']['spu']['button'][count]['@y1'] = y1
        count = count + 1

    doc = docin

    # print doc # Uncomment this to see the raw dict
    return doc

def parse_args():
    parser = ArgumentParser(description='Converts DVD Author menus between TV formats.')
    parser.add_argument(
        'filein',
        help='file to convert',
        metavar='input.xml'
    )
    parser.add_argument(
        'fileout',
        help='file to write',
        metavar='output.xml'
    )
    parser.add_argument(
        '-n',
        '--ntsc',
        action='store_const',
        const=True,
        default=False,
        help='convert from PAL to NTSC',
        metavar='ntsc'
    )
    return parser.parse_args()

args = parse_args()
doc = ConvertMenu(args.filein, args.ntsc)

outfile = open(args.fileout, 'w')

outfile.write(xmltodict.unparse(doc, pretty=True))
