# Flask app with HTTP /api/recognize and WebSocket (flask-socketio) live transcription.
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import tempfile, subprocess, os, time, threading, shutil
from recognizer_core import RecognizerCore
from utils import match_command, handle_command
from auth import require_api_key

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['SECRET_KEY'] = 'change-me'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
rc = RecognizerCore()

def convert_webm_to_wav(webm_path, wav_path):
    cmd = ['ffmpeg', '-y', '-i', webm_path, '-ar', '16000', '-ac', '1', '-acodec', 'pcm_s16le', wav_path]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0 or not os.path.exists(wav_path):
        raise RuntimeError('ffmpeg failed: ' + proc.stderr.decode('utf8', errors='ignore'))

@app.route('/api/recognize', methods=['POST'])
@require_api_key
def recognize():
    if 'file' not in request.files:
        return jsonify({'error':'no file uploaded'}), 400
    f = request.files['file']
    tmpdir = tempfile.mkdtemp(prefix='audio_')
    webm_path = os.path.join(tmpdir, 'in.webm')
    wav_path = os.path.join(tmpdir, 'out.wav')
    with open(webm_path, 'wb') as wf:
        wf.write(f.read())
    try:
        convert_webm_to_wav(webm_path, wav_path)
        text = rc.transcribe_wav_file(wav_path)
        key, args = match_command(text)
        ok, info = handle_command(key, args)
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify({'error': str(e)}), 500
    shutil.rmtree(tmpdir, ignore_errors=True)
    return jsonify({'text': text, 'command': key, 'args': args, 'action_result': info})

# WebSocket live: clients send binary chunks (webm) with session id; server appends to file and periodically converts+transcribes and emits 'partial' events.
SESS_DIR = {}

@socketio.on('start_session')
def on_start(data):
    sid = request.sid
    tmpdir = tempfile.mkdtemp(prefix='sess_')
    SESS_DIR[sid] = {'tmpdir': tmpdir, 'webm': os.path.join(tmpdir, 'stream.webm'), 'last_emit':0}
    # create empty file
    open(SESS_DIR[sid]['webm'], 'wb').close()
    emit('session_started', {'status':'ok'})
    print('Session started', sid)

@socketio.on('audio_chunk')
def on_chunk(data):
    sid = request.sid
    if sid not in SESS_DIR:
        return
    path = SESS_DIR[sid]['webm']
    # append binary bytes
    with open(path, 'ab') as f:
        f.write(data)
    now = time.time()
    if now - SESS_DIR[sid]['last_emit'] > 1.5:
        SESS_DIR[sid]['last_emit'] = now
        threading.Thread(target=do_partial_transcribe, args=(sid,)).start()

def do_partial_transcribe(sid):
    info = SESS_DIR.get(sid)
    if not info: return
    webm = info['webm']
    tmpwav = os.path.join(info['tmpdir'],'partial.wav')
    try:
        convert_webm_to_wav(webm, tmpwav)
        text = rc.transcribe_wav_file(tmpwav)
        socketio.emit('partial', {'text': text}, room=sid)
    except Exception as e:
        socketio.emit('partial_error', {'error': str(e)}, room=sid)
    finally:
        try:
            if os.path.exists(tmpwav): os.remove(tmpwav)
        except: pass

@socketio.on('stop_session')
def on_stop(data):
    sid = request.sid
    info = SESS_DIR.get(sid)
    if not info:
        emit('stopped', {'status':'no_session'})
        return
    webm = info['webm']
    tmpwav = os.path.join(info['tmpdir'],'final.wav')
    try:
        convert_webm_to_wav(webm, tmpwav)
        text = rc.transcribe_wav_file(tmpwav)
        key, args = match_command(text)
        ok, act = handle_command(key, args)
        emit('final', {'text': text, 'command': key, 'action_result': act})
    except Exception as e:
        emit('final_error', {'error': str(e)})
    finally:
        shutil.rmtree(info['tmpdir'], ignore_errors=True)
        SESS_DIR.pop(sid, None)

# serve frontend static
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
