import os
import uuid
import threading
import time
import shutil
from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp

app = Flask(__name__)

tasks = {}
tasks_lock = threading.Lock()

DOWNLOAD_DIR = "/tmp/yt2mp3"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 從環境變數寫入 cookies 檔案
COOKIES_PATH = '/tmp/cookies.txt'
yt_cookies = os.environ.get('YT_COOKIES', '')
if yt_cookies:
    with open(COOKIES_PATH, 'w') as f:
        f.write(yt_cookies)
else:
    # 嘗試從 Secret Files 複製
    COOKIES_SRC = '/etc/secrets/cookies.txt'
    if os.path.exists(COOKIES_SRC):
        shutil.copy2(COOKIES_SRC, COOKIES_PATH)


def cleanup_file(path, delay=60):
    def _delete():
        time.sleep(delay)
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    threading.Thread(target=_delete, daemon=True).start()


def download_task(task_id, url, output_path):
    def progress_hook(d):
        with tasks_lock:
            if task_id not in tasks:
                return
            if d['status'] == 'downloading':
                pct = d.get('_percent_str', '0%').strip()
                tasks[task_id]['progress'] = pct
                tasks[task_id]['message'] = f'下載中... {pct}'
            elif d['status'] == 'finished':
                tasks[task_id]['progress'] = '99%'
                tasks[task_id]['message'] = '轉換成 MP3 中...'

    ydl_opts = {
        'format': 'bestaudio/best/worstaudio',
        'outtmpl': output_path + '.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
    }

    if os.path.exists(COOKIES_PATH):
        ydl_opts['cookiefile'] = COOKIES_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')

        mp3_path = output_path + '.mp3'
        if not os.path.exists(mp3_path):
            raise FileNotFoundError("MP3 轉換失敗")

        with tasks_lock:
            tasks[task_id]['status'] = 'done'
            tasks[task_id]['progress'] = '100%'
            tasks[task_id]['message'] = '完成！'
            tasks[task_id]['file'] = mp3_path
            tasks[task_id]['title'] = title

    except Exception as e:
        with tasks_lock:
            tasks[task_id]['status'] = 'error'
            tasks[task_id]['message'] = f'錯誤：{str(e)}'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = (data or {}).get('url', '').strip()

    if not url:
        return jsonify({'error': '請輸入 YouTube 網址'}), 400

    if 'youtube.com' not in url and 'youtu.be' not in url:
        return jsonify({'error': '請輸入有效的 YouTube 網址'}), 400

    task_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, task_id)

    with tasks_lock:
        tasks[task_id] = {
            'status': 'processing',
            'progress': '0%',
            'message': '準備中...',
            'file': None,
            'title': None,
        }

    thread = threading.Thread(
        target=download_task,
        args=(task_id, url, output_path),
        daemon=True
    )
    thread.start()

    return jsonify({'task_id': task_id})


@app.route('/status/<task_id>')
def status(task_id):
    with tasks_lock:
        task = tasks.get(task_id)
    if not task:
        return jsonify({'error': '找不到任務'}), 404
    return jsonify({
        'status': task['status'],
        'progress': task['progress'],
        'message': task['message'],
        'title': task.get('title'),
    })


@app.route('/download/<task_id>')
def download(task_id):
    with tasks_lock:
        task = tasks.get(task_id)

    if not task or task['status'] != 'done':
        return jsonify({'error': '檔案尚未準備好'}), 404

    mp3_path = task['file']
    title = task.get('title', 'audio')

    if not os.path.exists(mp3_path):
        return jsonify({'error': '檔案已過期，請重新轉換'}), 404

    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_title or 'audio'}.mp3"

    cleanup_file(mp3_path, delay=120)

    return send_file(
        mp3_path,
        as_attachment=True,
        download_name=filename,
        mimetype='audio/mpeg'
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
