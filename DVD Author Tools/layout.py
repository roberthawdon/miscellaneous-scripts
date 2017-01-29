#!/usr/bin/env python
import xmltodict
import re
from datetime import datetime, timedelta
from argparse import ArgumentParser

def ConvertLayout(filein, ntsc):
    with open(filein) as fd:
        docin = xmltodict.parse(fd.read())

    zerotime = datetime.strptime("00:00:00", "%H:%M:%S")

    if ntsc:
        vformat = "ntsc"
        resolution = "720x480"
        speedfactor = "1.04270937604"
    else:
        vformat = "pal"
        resolution = "720x576"
        speedfactor = "0.95904"

    docin['dvdauthor']['vmgm']['menus']['video']['@format'] = vformat
    docin['dvdauthor']['vmgm']['menus']['video']['@resolution'] = resolution

    titlesetsdefs = docin['dvdauthor']['titleset']

    titlesetcounter = 0

    for titlesets in titlesetsdefs:
        pgcdefs = docin['dvdauthor']['titleset'][titlesetcounter]['titles']['pgc']
        pgccounter = 0
        docin['dvdauthor']['titleset'][titlesetcounter]['menus']['video']['@format'] = vformat
        docin['dvdauthor']['titleset'][titlesetcounter]['titles']['video']['@format'] = vformat

        for pgcs in pgcdefs:
            timearray = []
            times = docin['dvdauthor']['titleset'][titlesetcounter]['titles']['pgc'][pgccounter]['vob']['@chapters'].split(', ')
            for chaptertime in times:
                try:
                    timevalue = datetime.strptime(chaptertime, '%H:%M:%S.%f')
                except ValueError:
                    timevalue = datetime.strptime(chaptertime, '%H:%M:%S')
                deltatime = (timevalue-zerotime).seconds * 1000
                fulltime = str(timedelta(seconds=float(speedfactor) * deltatime) / 1000)
                hr, min, sec = map(float, fulltime.split(':'))
                roundsecs = float("{0:.2f}".format(round(sec,2)))
                formattime = str(int(hr)) + ":" + str(int(min)) + ":" + str(roundsecs)
                timearray.append(formattime)
            # print times
            outputtimes = ", ".join(timearray)
            docin['dvdauthor']['titleset'][titlesetcounter]['titles']['pgc'][pgccounter]['vob']['@chapters'] = outputtimes
            pgccounter = pgccounter + 1

        titlesetcounter = titlesetcounter + 1

    # print docin['dvdauthor']['titleset'][0]['menus']['video']['@format']
    # print docin

    doc = docin
    return doc

def parse_args():
    parser = ArgumentParser(description='Converts DVD Author layouts between TV formats.')
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

doc = ConvertLayout(args.filein, args.ntsc)


outfile = open(args.fileout, 'w')
outfile.write(xmltodict.unparse(doc, pretty=True))

# print xmltodict.unparse(doc, pretty=True)
