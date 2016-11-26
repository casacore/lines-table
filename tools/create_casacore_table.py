#!/usr/bin/env python3

import argparse
import datetime
import dateutil.parser
import json

from casacore import tables
 
default_version = "1.1"
default_date = "2016-11-26T13:26"

default_input = "lines.json"
default_path = "Lines"

parser = argparse.ArgumentParser(
    usage = 'casacore-update-lines [options]',
    description = 'Update casacore Observatory table from json input')
parser.add_argument('-i', '--input-file',
                    help='JSON oinput file (default: {})'
                    .format(default_input),
                    default=default_input)
parser.add_argument('-o', '--output-path',
                    help='output table path (default: {})'
                    .format(default_path),
                    default=default_path)
parser.add_argument('-v', '--version',
                    help='Set version number in table (default: {})'
                    .format(default_version),
                    default=default_version)
parser.add_argument('-d', '--date',
                    help='Set version date in database (default: {})'
                    .format(default_date),
                    default=default_date)
args = parser.parse_args()

with open(args.input_file) as f:
    linestable = json.load(f)

# Create data table
columns = [
    tables.makescacoldesc('MJD', 0., valuetype='double',
                          keywords={'UNIT':'d'}),
    tables.makescacoldesc('Name', '', valuetype='string'),
    tables.makescacoldesc('Type', '', valuetype='string'),
    tables.makescacoldesc('Freq', 0., valuetype='double',
                          keywords={'UNIT':'GHz'}),
    tables.makescacoldesc('Source', '', valuetype='string'),
    tables.makescacoldesc('Comment', '', valuetype='string'),
]

with tables.table('Lines', tables.tablecreatedesc(columns), len(linestable)) as tbl:
    tbl.putinfo({'type': 'IERS', 'subType': 'lines'})
    tbl.putkeywords({
        'MJD0': 0,
        'dMJD': 0.0,
        'VS_VERSION': '{:04d}.{:04d}'.format(*(int(i)
                                           for i in args.version.split('.'))),
        'VS_CREATE': dateutil.parser.parse(args.date).strftime('%Y/%m/%d/%H:%M'),
        'VS_DATE': dateutil.parser.parse(args.date).strftime('%Y/%m/%d/%H:%M'),
        'VS_TYPE': 'List of spectral line rest frequencies'
    })

    tablerows = tbl.row()
    for i, line in enumerate(linestable):
        tablerows.put(i, {
            'MJD': 0.0,
            'Name': line['name'],
            'Type': 'REST',
            'Freq': line['frequency'],
            'Source': 'WSRT'
        })
