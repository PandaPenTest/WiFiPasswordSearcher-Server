# -*- coding: utf-8 -*-
def _hex2dec(number):
    return int(number, 16)

def _dec2hex(number):
    return hex(number).split('x')[-1].upper()

def mac2dec(mac):
    mac = mac.replace(':', '')
    return _hex2dec(mac)

def dec2mac(mac):
    mac = _dec2hex(mac)
    mac = mac.zfill(12)
    for pos in range(10, 0, -2):
        mac = mac[:pos] + ':' + mac[pos:]
    return mac

def str2sec(sec):
    security_types = {
        'None': 0,
        'WEP': 1,
        'WPA': 2,
        'WPA2': 3,
        'WPA/WPA2': 4,
        'WPA Enterprise': 5
    }
    return (security_types[sec] if sec in security_types else None)

def sec2str(sec):
    inv_security_types = {
        0: 'None',
        1: 'WEP',
        2: 'WPA',
        3: 'WPA2',
        4: 'WPA/WPA2',
        5: 'WPA Enterprise'
    }
    return (inv_security_types[sec] if sec in inv_security_types else None)

def str2pin(pin):
    return (None if pin == '' else int(pin))

def pin2str(pin):
    return ('' if pin == None else str(pin).zfill(8))