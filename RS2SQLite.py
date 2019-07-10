# -*- coding: utf-8 -*-
import csv
import sys
import sqlite3

args = sys.argv[1:]
if args:
    filename = args[0]
else:
    print('Ошибка: не передан путь к CSV-файлу\n \
        Синтаксис команды: python {} path/to/file.csv'.format(sys.argv[0]))
    quit()

table_name = 'aps'
conn = sqlite3.connect('APs.db')
cursor = conn.cursor()

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
with open(filename, 'r') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)
    for line in reader:
        bssid = line[8]
        essid = line[9] if line[9] else None
        security = security_types[line[10]]
        key = line[11] if (security and line[11] and not line[11].startswith('<not accessible>')) else None
        wps = line[12] if line[12] else None
        latitude = line[19] if (line[19] and line[19] != 'N/A') else None
        longitude = line[20] if (line[20] and line[20] != 'N/A') else None
        query = 'INSERT INTO {} (bssid,essid,security,key,wps,lat,lon) \
                 VALUES (?,?,?,?,?,?,?)'.format(table_name)
        cursor.execute(query, (bssid, essid, security, key, wps, latitude, longitude))
conn.commit()
conn.close()
