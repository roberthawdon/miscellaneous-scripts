#!/usr/bin/env python3

# A Hawdon Python script

import pandas as pd
import tempfile
import requests
import shutil
import zipfile
import glob
import atexit
import socket
import struct
import re
import sys
import csv
from argparse import ArgumentParser

# Uncomment and set the line below to disable downloading the current database from MaxMind on each run.
# localGeoLite = ''

maxmindname = "GeoLite2-Country-CSV"
maxmindfile = maxmindname + ".zip"
maxmindlocation = "http://geolite.maxmind.com/download/geoip/database/"
maxmindurl = maxmindlocation + maxmindfile

def floatToInt(dataFrame, key):
    dataFrame[key] = dataFrame[key].fillna('')
    dataFrame[key] = dataFrame[key].astype(str)
    dataFrame[key] = dataFrame[key].str.split('.')
    dataFrame[key] = dataFrame[key].str[0]

def addressInNetwork(ip, net):
    pattern = re.compile("(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
    if not pattern.match(ip):
        ip = '0.0.0.0'
    ipaddr = int(''.join([ '%02x' % int(x) for x in ip.split('.') ]), 16)
    netstr, bits = net.split('/')
    netaddr = int(''.join([ '%02x' % int(x) for x in netstr.split('.') ]), 16)
    mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
    return (ipaddr & mask) == (netaddr & mask)

def loadGeoData(mmdir):
    a = pd.read_csv(mmdir + "/GeoLite2-Country-Blocks-IPv4.csv").astype(object)
    b = pd.read_csv(mmdir + "/GeoLite2-Country-Locations-en.csv").astype(object)
    merged= a.merge(b, on='geoname_id',how='left')
    df = pd.DataFrame(merged)
    floatToInt(df, 'geoname_id')
    floatToInt(df, 'registered_country_geoname_id')
    dataDict = df.to_dict()
    return dataDict

def geoDataByIP(data, ip):
    for index in data['network']:
        if addressInNetwork(ip, data['network'][index]):
            return index
            break

def geoDetail(data, index, key):
    return data.get(key).get(index)

def getGeoLite(maxmindurl, maxmindfile, tmpdir):
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

def processCSV(csvFile, field):
    counter = 0
    outputDict = {}
    ipList = []
    cnList = []
    ciList = []
    inputCSV = pd.read_csv(csvFile).astype(object)
    ipAddrs = inputCSV[field].values.flatten()
    uniqueIP = set(ipAddrs)
    totalIPs = len(uniqueIP)
    for ip in uniqueIP:
        counter += 1
        indexID = geoDataByIP(testData, ip)
        sys.stdout.write("Processing %d of %d unique IP addresses.   \r" % (counter,totalIPs))
        ipList.append(ip)
        cnList.append(geoDetail(testData, indexID, 'country_name'))
        ciList.append(geoDetail(testData, indexID, 'country_iso_code'))
    print('Processing unique IP addresses complete.                          ')
    outputDict[args.field[0]] = ipList
    outputDict["MaxMind Country Name"] = cnList
    outputDict["MaxMind Country ISO Code"] = ciList

    return outputDict

def produceOutput(csvFile, processedDict):

    print('Combining data.')
    origCSV = pd.read_csv(csvFile).astype(object)
    ipResults = pd.DataFrame.from_dict(processedDict)

    merged = origCSV.merge(ipResults, on=args.field, how='left')

    print('Writing file.')
    merged.to_csv(args.output[0], index=False, header=True, quoting=csv.QUOTE_ALL)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'input',
        help='Input CSV file.',
        # metavar='-i',
        nargs=1
    )
    parser.add_argument(
        'output',
        help='Output CSV file.',
        # metavar='-i',
        nargs=1
    )
    parser.add_argument(
        '-f', '--field',
        help='IP Address field name in CSV.',
        # metavar='-f',
        nargs=1,
        type=str,
        default='IP Address'
    )
    return parser.parse_args()

args = parse_args()

print("IP Location Mapping Processor.")
print()

if 'localGeoLite' in globals():
    print('Using specified GeoLite2 location.')
    mmdir = localGeoLite
else:
    print('Downloading GeoLite2 database from MaxMind.')
    tmpdir = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, tmpdir)
    mmdir = getGeoLite(maxmindurl, maxmindfile, tmpdir)

testData = loadGeoData(mmdir)

produceOutput(args.input[0],processCSV(args.input[0], args.field))
print('Complete. Have a nice day.')
