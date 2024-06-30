from time import time
import secrets
import hashlib

from .config import *
from .db import *


def verify_pow(uid, answer):
    db = get_db()

    res = db.execute('SELECT prefix, valid_until FROM pow WHERE uid = ?', (uid,)).fetchone()
    if (res is None) or (res[1] < int(time())):
        return -1

    prefix = res[0]
    digest = hashlib.sha256((prefix + answer).encode()).digest()
    bits = ''.join(bin(byte)[2:].zfill(8) for byte in digest)
    if not bits.startswith('0' * POW_DIFFICULTY):
        return 0

    expire_pow(uid)
    return 1


def expire_pow(uid):
    db = get_db()
    db.execute('UPDATE pow SET valid_until = ? WHERE uid = ?', (int(time()) - 1, uid))
    db.commit()


def get_pow(uid):
    db = get_db()
    res = db.execute('SELECT prefix, valid_until FROM pow WHERE uid = ?', (uid,)).fetchone()
    if (res is None) or (res[1] < int(time())):
        return new_pow(uid)
    return res[0], res[1] - int(time())


def new_pow(uid):
    db = get_db()

    prefix = secrets.token_urlsafe(POW_PREFIX_LENGTH)[:POW_PREFIX_LENGTH].replace('-', 'B').replace('_', 'A')
    valid_until = int(time()) + POW_EXPIRED_TIME

    res = db.execute('SELECT * FROM pow WHERE uid = ?', (uid,)).fetchall()
    if len(res) != 0:
        db.execute('UPDATE pow SET valid_until = ?, prefix = ? WHERE uid = ?', (valid_until, prefix, uid))
        db.commit()
    else:
        cursor = db.cursor()
        cursor.execute('INSERT INTO pow (uid, valid_until, prefix) VALUES (?, ?, ?)', (uid, valid_until, prefix))
        db.commit()
        id = cursor.lastrowid

        if (id % CLEAN_EXPIRED_POW_PER) == 0:
            clean_expired_pow()

    return prefix, POW_EXPIRED_TIME


def clean_expired_pow():
    db = get_db()
    db.execute('DELETE FROM pow WHERE valid_until < strftime("%s", "now")')
    db.commit()

