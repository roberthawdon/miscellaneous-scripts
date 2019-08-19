#!/usr/bin/env python

import pandas as pd
import zipfile
import requests
import shutil
import tempfile
import glob
import atexit
from argparse import ArgumentParser

maxmindname = "GeoLite2-Country-CSV"
maxmindfile = maxmindname + ".zip"
maxmindlocation = "http://geolite.maxmind.com/download/geoip/database/"
maxmindurl = maxmindlocation + maxmindfile

tmpdir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, tmpdir)

def genZone(mmdir, isocountry):

    outputname = isocountry.lower() + ".zone"

    a = pd.read_csv(mmdir + "/GeoLite2-Country-Blocks-IPv4.csv").astype(object)

    b = pd.read_csv(mmdir + "/GeoLite2-Country-Locations-en.csv").astype(object)

    merged= a.merge(b, on='geoname_id',how='left')

    df = pd.DataFrame(merged)

    results = df.loc[df['country_iso_code'] == isocountry,['network']]

    results.to_csv(outputname, index=False, header=False)


def getGeoLite(maxmindurl, maxmindfile, tmpdir):
    # tmpdir = TempDir(tempfile.mkdtemp())
    response = requests.get(maxmindurl, stream=True, allow_redirects=True)
    with open(tmpdir + "/" + maxmindfile, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    zip_ref = zipfile.ZipFile(tmpdir + "/" + maxmindfile, 'r')
    zip_ref.extractall(tmpdir)
    zip_ref.close()

    for name in glob.glob(tmpdir + "/" + maxmindname + "_*"):
        mmdir = name

    return mmdir

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'country',
        help='Country code in ISO format (e.g. RU).',
        metavar='c',
        nargs='*'
    )
    return parser.parse_args()

args = parse_args()

mmdir = getGeoLite(maxmindurl, maxmindfile, tmpdir)
for c in args.country:
    block = c.upper()
    genZone(mmdir, block)
