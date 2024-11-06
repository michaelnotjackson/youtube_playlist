from flask import Flask, render_template, request, abort, redirect, url_for, jsonify
from turbo_flask import Turbo
from flask_pydantic import validate
from models import Video, video_from_url
from threading import Lock
import dotenv
import yt_dlp
import os
from pydantic import RootModel

app = Flask(__name__)
turbo = Turbo(app)

videos: list[Video] = []

current_video: Video | None = None


def get_video_by_id(video_id: int):
    global videos
    video = [video for video in videos if video.id == video_id]
    if len(video) == 0:
        abort(404)
    return video[0]


@app.route('/', methods=['GET', 'POST'])
async def index():
    global current_video, videos, turbo
    if request.method == 'POST':
        url = request.form['video']
        video = await video_from_url(url)
        videos.append(video)
        if turbo.can_stream():
            return turbo.stream([
                turbo.replace(
                    render_template('_video_list.html', videos=videos, current_video=current_video),
                    target='videos'
                ),
                turbo.update(
                    render_template('_video_input.html'), target='form')])
    return render_template('index.html', videos=videos, current_video=current_video)


@validate
@app.route('/force_play/<video_id>', methods=['POST'])
def force_play(video_id: int):
    global turbo, videos, current_video
    video = get_video_by_id(video_id)
    current_video = video

    if current_video.playback_url is None:
        ydl_opts = {'cookiefile': os.getenv('COOKIE_FILE_PATH'), 'format': 'bestvideo[ext=webm]'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(current_video.video_url, download=False)
            current_video.playback_url = info['url']

    if turbo.can_stream():
        videos.remove(current_video)
        return turbo.stream([
            turbo.replace(
                render_template('_player.html', videos=videos, current_video=video),
                target='player'
            ),
            turbo.remove(target=f'video-{current_video.id}')])
    return redirect(url_for('index'))


@validate
@app.route('/delete/<video_id>', methods=['POST'])
def delete(video_id: str):
    global videos, turbo
    video = get_video_by_id(video_id)
    videos.remove(video)
    if turbo.can_stream():
        return turbo.stream(turbo.remove(target=f'video-{video.id}'))
    return redirect(url_for('index'))


setup_once_lock = Lock()
@app.before_request
def app_setup():
    with setup_once_lock:
        try:
            dotenv.load_dotenv('.env')
        finally:
            app.before_request_funcs[None].remove(app_setup)
