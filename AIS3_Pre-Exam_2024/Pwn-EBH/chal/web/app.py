from flask import Flask, session, g, render_template, request, send_file

import os
import logging
import threading

from .config import *
from .user import *
from .pow import *
from .challenge import *

app = Flask(__name__)
app.secret_key = os.urandom(0x20)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/')
def index_view():
    if (not 'uid' in session) or (not is_user_valid(session['uid'])):
        uid = register_user()
    else:
        uid = session['uid']
        update_user_expired_time(uid)

    session['uid'] = uid
    return render_template('index.html')


@app.route('/usage')
def usage_view():
    return render_template('usage.html')


@app.route('/example.c')
def example_view():
    return send_file(os.path.join(BASEDIR, 'source', 'example.c'))


@app.route('/api/user/restart')
def user_restart_api():
    if (not 'uid' in session) or (not is_user_valid(session['uid'])):
        return {'status': 'error', 'error': 'Incorrect uid'}
    uid = session['uid']
    if not get_user_status(uid)['has_result']:
        return {'status': 'error', 'error': 'User do not need to restart'}

    user_restart(uid)
    return {'status': 'success'}


@app.route('/api/user/status')
def get_user_status_api():
    if (not 'uid' in session) or (not is_user_valid(session['uid'])):
        return {'status': 'error', 'error': 'Incorrect uid'}

    res = get_user_status(session['uid'])
    res['status'] = 'success'
    return res


@app.route('/api/challenge/get_result')
def get_result_api():
    if (not 'uid' in session) or (not is_user_valid(session['uid'])):
        return {'status': 'error', 'error': 'Incorrect uid'}
    uid = session['uid']
    if not get_user_status(uid)['has_result']:
        return {'status': 'error', 'error': 'User has no result'}

    res = get_result(uid)
    res['status'] = 'success'
    return res


@app.route('/api/challenge/upload_binary', methods=['POST'])
def upload_challenge_binary_api():
    if (not 'uid' in session) or (not is_user_valid(session['uid'])):
        return {'status': 'error', 'error': 'Incorrect uid'}
    uid = session['uid']
    if not 'file' in request.files:
        return {'status': 'error', 'error': 'No file uploaded'}

    user_status = get_user_status(uid)
    if not user_status['is_pow_verified']:
        return {'status': 'error', 'error': 'Need to finish PoW'}
    unset_user_pow_verified(uid)
    if user_status['is_running_challenge']:
        return {'status': 'error', 'error': 'User is already running challenge'}
    set_user_running_challenge(uid)

    upload_folder_path = Path(CHALLENGE_UPLOAD_PATH) / str(uid)
    if not upload_folder_path.exists():
        upload_folder_path.mkdir()
    upload_binary = request.files['file']
    upload_binary_path = upload_folder_path / 'binary'
    upload_binary.save(upload_binary_path)

    run_challenge_thread = threading.Thread(
        target = run_challenge_daemon, 
        args   = (uid,), 
        daemon = True
    )
    run_challenge_thread.start()

    return {'status': 'success', 'lefttime': CHALLENGE_RUNNING_TIME}


@app.route('/api/pow/verify', methods=['POST'])
def verify_pow_api():
    if (not 'uid' in session) or (not is_user_valid(session['uid'])):
        return {'status': 'error', 'error': 'Incorrect uid'}

    if not 'answer' in request.json:
        return {'status': 'error', 'error': 'No answer in request'}

    uid = session['uid']
    res = verify_pow(uid, request.json['answer'])
    if res == 1:
        set_user_pow_verified(uid)
        return {'status': 'success', 'result': 'verified'}
    elif res == 0:
        return {'status': 'success', 'result': 'wrong'}
    elif res == -1:
        return {'status': 'success', 'result': 'error'}


@app.route('/api/pow/get')
def get_pow_api():
    if (not 'uid' in session) or (not is_user_valid(session['uid'])):
        return {'status': 'error', 'error': 'Incorrect uid'}

    prefix, lefttime = get_pow(session['uid'])
    return {
        'status': 'success', 
        'prefix': prefix, 
        'lefttime': lefttime, 
        'difficulty': POW_DIFFICULTY
    }


@app.teardown_appcontext
def close_connection(e):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
