#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import csv
from utils import mac2dec, str2sec, str2pin
import sqlite3


parser = argparse.ArgumentParser(
    description='''This script converts Scan Router CSV tables to SQLite DB
file for 3WiFi Locator caching server.''',
    epilog='''The author is not responsible for your
actions with this script.'''
    )
parser.add_argument(
    '-i',
    '--input',
    type=argparse.FileType(
        mode='r'
        ),
    required=True,
    help='path to Router Scan CSV "Good Results" table'
)
parser.add_argument(
    '-o',
    '--output',
    default='APs.db',
    type=str,
    help='output SQLite DB file'
)
namespace = parser.parse_args()

conn = sqlite3.connect(namespace.output)
cursor = conn.cursor()

table_name = 'aps'
create_structure = """
CREATE TABLE IF NOT EXISTS {} (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    bssid INTEGER NOT NULL,
    essid TEXT,
    sec INTEGER NOT NULL,
    key TEXT,
    wps INTEGER
)
""".format(table_name)
cursor.execute(create_structure)
conn.commit()


reader = csv.reader(namespace.input, delimiter=';')
next(reader)  # Skip header
for line in reader:
    bssid = mac2dec(line[8])
    essid = line[9]
    sec = str2sec(line[10])
    key = line[11] if sec else None
    wps = str2pin(line[12])
    if bssid and essid and sec:
        query = 'INSERT INTO {} (bssid,essid,sec,key,wps) \
                 VALUES (?,?,?,?,?)'.format(table_name)
        cursor.execute(query, (
            bssid, essid, sec,
            key, wps))
conn.commit()
conn.close()
