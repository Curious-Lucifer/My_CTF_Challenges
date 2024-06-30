from time import time

from .config import *
from .db import *
from .challenge import clean_challenge_upload_path


def get_user_status(uid):
    db = get_db()
    res = db.execute('SELECT is_pow_verified, is_running_challenge, run_until, has_result FROM users WHERE uid = ?', (uid,)).fetchone()
    return {
        'is_pow_verified': res[0], 
        'is_running_challenge': res[1], 
        'lefttime': (res[2] - int(time())) if (res[1]) else res[2], 
        'has_result': res[3]
    }


def set_user_pow_verified(uid):
    db = get_db()
    db.execute('UPDATE users SET is_pow_verified = ? WHERE uid = ?', (1, uid))
    db.commit()


def unset_user_pow_verified(uid):
    db = get_db()
    db.execute('UPDATE users SET is_pow_verified = ? WHERE uid = ?', (0, uid))
    db.commit()


def update_user_expired_time(uid):
    db = get_db()
    db.execute('UPDATE users SET valid_until = ? WHERE uid = ?', (int(time()) + USER_EXPIRED_TIME, uid))
    db.commit()


def is_user_valid(uid):
    res = get_db().execute('SELECT valid_until FROM users WHERE uid = ?', (uid,)).fetchone()
    if (res is None) or (res[0] < int(time())):
        return False
    return True


def register_user():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (valid_until) VALUES (?)', (int(time()) + USER_EXPIRED_TIME,))
    db.commit()
    uid = cursor.lastrowid

    if (uid % CLEAN_EXPIRED_USERS_PER) == 0:
        clean_expired_users()
    return uid


def clean_expired_users():
    db = get_db()
    res = db.execute('SELECT uid FROM users WHERE valid_until < strftime("%s", "now")').fetchall()
    clean_challenge_upload_path([uid for (uid,) in res])
    db.execute('DELETE FROM users WHERE valid_until < strftime("%s", "now")')
    db.commit()

