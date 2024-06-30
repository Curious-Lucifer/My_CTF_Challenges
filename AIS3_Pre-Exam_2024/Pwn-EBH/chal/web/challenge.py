from pathlib import Path
from base64 import b64encode
from time import time
import shutil
import sqlite3
import subprocess

from .config import *
from .db import *


def user_restart(uid):
    db = get_db()
    db.execute('UPDATE users SET has_result = ? WHERE uid = ?', (0, uid))
    db.commit()


def set_user_running_challenge(uid):
    db = get_db()
    db.execute('UPDATE users SET is_running_challenge = ?, run_until = ? WHERE uid = ?', (1, int(time()) + CHALLENGE_RUNNING_TIME, uid))
    db.commit()


def unset_user_running_challenge(uid, db=None):
    db = db or get_db()
    db.execute('UPDATE users SET is_running_challenge = ?, run_until = ? WHERE uid = ?', (0, 0, uid))
    db.commit()


def set_user_has_result(uid, db=None):
    db = db or get_db()
    db.execute('UPDATE users SET has_result = ? WHERE uid = ?', (1, uid))
    db.commit()


def clean_challenge_upload_path(uid_list):
    for uid in uid_list:
        user_challenge_path = Path(CHALLENGE_UPLOAD_PATH) / str(uid)
        if user_challenge_path.exists():
            shutil.rmtree(user_challenge_path)


def get_result(uid):
    result_path = Path(CHALLENGE_UPLOAD_PATH) / str(uid) / 'result'
    result = result_path.read_bytes()
    return {'result': b64encode(result).decode()}


def run_challenge_daemon(uid):
    db = sqlite3.connect(DATABASE)
    binary_path = Path(CHALLENGE_UPLOAD_PATH) / str(uid) / 'binary'
    result_path = Path(CHALLENGE_UPLOAD_PATH) / str(uid) / 'result'

    # Check
    if not result_path.exists():
        result_path.touch()
    if not binary_path.exists():
        result_path.write_text('Error : No binary to execute')
        unset_user_running_challenge(uid, db)
        return

    # Run challenge
    subprocess.run([CHALLENGE_ENTRY_PATH, str(uid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Release running lock
    unset_user_running_challenge(uid, db)
    set_user_has_result(uid, db)
