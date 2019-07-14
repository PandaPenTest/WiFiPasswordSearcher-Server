#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import sqlite3
from utils import mac2dec, dec2mac, str2sec, sec2str, str2pin, pin2str
from bottle import Bottle, run, request
import requests
import json
from time import gmtime, strftime, sleep


def createParser():
    parser = argparse.ArgumentParser(
        description='Caching proxy server for 3WiFi Locator.',
        epilog='''The author is not responsible for your
actions with this program.'''
        )
    parser.add_argument(
        '-d',
        '--database',
        type=str, default='APs.db',
        help='path to SQLite database file. Default: APs.db'
        )
    parser.add_argument(
        '-t',
        '--table',
        type=str,
        default='aps',
        help='database table name. Default "aps"'
        )
    parser.add_argument(
        '-f',
        '--offline',
        action='store_const',
        const=True,
        help='work offline: fetch data only from local database'
        )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        type=str,
        help='HTTP server IP. Default: 127.0.0.1'
        )
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=8080,
        help='HTTP server port. Default: 8080'
        )

    return parser


def putAP(cursor, table_name, bssid, essid, sec,
          key=None, wps=None):
    '''Function add new AP record to local database'''
    bssid = mac2dec(bssid)
    sec = str2sec(sec)
    if key and not key.startswith(('<empty>', '<not accessible>')):
        pass
    else:
        key = None
    wps = str2pin(wps)
    query = 'INSERT INTO {} (bssid, essid, sec, key, wps) \
             VALUES (?, ?, ?, ?, ?)'.format(table_name)
    cursor.execute(query, (bssid, essid, sec, key, wps))


def fetchAP(cursor, table_name, bssid, essid=None):
    '''Function returns AP records from local database'''
    bssid = mac2dec(bssid)
    query = 'SELECT bssid, essid, sec, key, wps \
             FROM {} \
             WHERE bssid = ?'.format(table_name)
    if essid:
        query += ' AND essid = ?'
        cursor.execute(query, (bssid, essid))
    else:
        cursor.execute(query, (bssid,))
    r = cursor.fetchall()
    entries = []
    for k in r:
        entry = {
            'time': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            'bssid': dec2mac(k[0]),
            'essid': k[1],
            'sec': sec2str(k[2]),
            'key': k[3] if k[2] else '<empty>',
            'wps': pin2str(k[4])
        }
        entries.append(entry)

    return entries


def callApi(method, request):
    '''Function calls 3WiFi API method and handling errors'''
    url = 'https://3wifi.stascorp.com/api/{}'.format(method)
    r = requests.post(url, json=request).json()
    if r['result']:
        return r
    elif r['error'] == 'cooldown':
        sleep(10)
        return callApi(method, request)
    else:
        return r


err_invalid_request = {'result': False, 'error': 'request is invalid'}

app = Bottle()


@app.route('/api/apiquery', method='POST')
def apiquery():
    data = {}
    try:
        r = request.json
    except json.decoder.JSONDecodeError:
        print('Raw:', request.query_string)
        resp = err_invalid_request
    else:
        bssid_list = r['bssid']
        missing = []
        if 'essid' in r:
            # Fetching by BSSID and ESSID
            essid_list = r['essid']
            for bssid, essid in zip(bssid_list, essid_list):
                bssid = bssid.upper()
                bssess = '{}|{}'.format(bssid, essid)
                results = fetchAP(cursor, table_name, bssid, essid)
                if results:
                    data[bssess] = results
                else:
                    missing.append(bssid)
        else:
            # Fetching by BSSID
            for bssid in bssid_list:
                bssid = bssid.upper()
                results = fetchAP(cursor, table_name, bssid)
                if results:
                    data[bssid] = results
                else:
                    missing.append(bssid)

        if not namespace.offline:
            # Requesting missing AP's from 3WiFi
            n = 100  # Мaximum count of BSSID in a single request
            for i in range(0, len(missing), n):
                sub_missing = missing[i:i+n]
                try:
                    s = callApi(
                        'apiquery',
                        {
                            'key': r['key'],
                            'bssid': sub_missing
                        }
                        )
                except requests.exceptions.RequestException:
                    continue
                if s['result'] and s['data']:
                    server_data = s['data']
                    data.update(server_data)
                    for bssid, values in server_data.items():
                        for entry in values:
                            putAP(cursor, table_name, entry['bssid'],
                                  entry['essid'], entry['sec'], entry['key'],
                                  entry['wps'])
            conn.commit()

        resp = {'result': True, 'data': data}

    return resp


@app.route('/api/apiwps', method='GET')
def apiwps():
    bssid = request.query.bssid.upper()
    if bssid:
        dec_bssid = mac2dec(bssid)
        data = {}
        data[bssid] = {'scores': []}
        query = 'SELECT wps \
                 FROM {} \
                 WHERE bssid = ?'.format(table_name)
        cursor.execute(query, (dec_bssid,))
        r = cursor.fetchall()
        for s in r:
            if s:
                wps_pin = s[0]
                score = {
                    'name': 'Local cached',
                    'value': pin2str(wps_pin),
                    'score': 1,
                    'fromdb': True
                }
                data[bssid]['scores'].append(score)

        if not namespace.offline:
            # Requesting WPS pin's from 3WiFi
            api_key = request.query.key
            try:
                s = callApi('apiwps', {'key': api_key, 'bssid': bssid})
            except requests.exceptions.RequestException:
                pass
            else:
                if s['result'] and s['data']:
                    data[bssid]['scores'].extend(s['data'][bssid]['scores'])

        resp = {'result': True, 'data': data}

    else:
        resp = err_invalid_request

    return resp


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args()
    if namespace.offline:
        print('\n[i] Working offline\n')
    db_name = namespace.database
    table_name = namespace.table
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

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(create_structure)
    conn.commit()

    run(app, host=namespace.host, port=namespace.port)
