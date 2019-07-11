#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import csv
import sqlite3


parser = argparse.ArgumentParser(
    description = '''This script converts Scan Router CSV tables to SQLite DB
file for 3WiFi Locator caching server.''',
    epilog = '''The author is not responsible for your 
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
    bssid TEXT NOT NULL,
    essid TEXT,
    security INTEGER,
    key TEXT,
    wps INTEGER,
    lat REAL,
    lon REAL
)
""".format(table_name)
cursor.execute(create_structure)
conn.commit()

security_types = {
    'None': 0,
    'WEP': 1,
    'WPA': 2,
    'WPA2': 3,
    'WPA/WPA2': 4,
    'WPA Enterprise': 5
}

reader = csv.reader(namespace.input, delimiter=';')
next(reader)  # Skip header
for line in reader:
    bssid = line[8]
    essid = line[9]
    security = security_types[line[10]] if line[10] else None
    key = line[11] if security else None
    wps = line[12] if line[12] else None
    latitude = line[19] if (line[19] and line[19] != 'N/A') else None
    longitude = line[20] if (line[20] and line[20] != 'N/A') else None
    if bssid and essid:
        query = 'INSERT INTO {} (bssid,essid,security,key,wps,lat,lon) \
                 VALUES (?,?,?,?,?,?,?)'.format(table_name)
        cursor.execute(query, (
            bssid, essid, security,
            key, wps, latitude, longitude))
conn.commit()
conn.close()
