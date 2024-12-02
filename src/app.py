from flask import Flask, render_template, request, abort, redirect, url_for, jsonify, Response
from turbo_flask import Turbo
from flask_pydantic import validate
from .models import Video, video_from_url
import yt_dlp
import os

app = Flask(__name__, template_folder='../templates')
turbo = Turbo(app)

videos: list[Video] = []

current_video: list[Video] = []


def get_video_by_id(video_id: str) -> Video:
    global videos
    video = [video for video in videos if video.id == video_id]
    if len(video) == 0:
        abort(404)
    return video[0]


@app.route('/', methods=["GET", "POST"])
async def index() -> Response:
    """
    On GET request, render index.html template with videos list and current video.
    On POST request, add video to the list and rerender corresponding turbo frames.
    """
    global current_video, videos, turbo
    cur_vid = current_video[0] if len(current_video) else None
    if request.method == "POST":
        url = request.form['video']
        video = await video_from_url(url)
        videos.append(video)
        if turbo.can_stream():
            return turbo.stream([
                turbo.replace(
                    render_template('_video_list.html', videos=videos, current_video=cur_vid),
                    target='videos'
                ),
                turbo.update(
                    render_template('_video_input.html'), target='form')])
    return render_template('index.html', videos=videos, current_video=cur_vid)


@validate
@app.route('/force_play/<video_id>', methods=["POST"])
def force_play(video_id: int) -> Response:
    """
    Forcefully play selected video
    :param video_id: str - Video object uuid
    """
    global turbo, videos, current_video
    video = get_video_by_id(video_id)
    videos.remove(video)
    current_video.clear()
    current_video.append(video)

    if current_video[0].playback_url is None:
        ydl_opts = {'cookiefile': os.getenv('COOKIE_FILE_PATH'), 'format': 'best',
                    'extractor_args': {'youtube': {'player_client': ['default', '-ios']}}}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(current_video[0].video_url, download=False)
            current_video[0].playback_url = info['url']
            current_video[0].playback_ext = info['ext']

    return jsonify({'status': 'ok'})


@validate
@app.route('/delete/<video_id>', methods=["POST"])
def delete(video_id: str) -> Response:
    """
    Delete video from the list
    :param video_id: str - Video object uuid
    """
    global videos, turbo
    video = get_video_by_id(video_id)
    videos.remove(video)
    if turbo.can_stream():
        return turbo.stream(turbo.remove(target=f'video-{video.id}'))
    return redirect(url_for('index'))


@validate
@app.route('/reload_data', methods=["POST"])
def reload_data() -> Response:
    """
    Reload video list and player data
    """
    global videos, turbo, current_video
    cur_vid = current_video[0] if len(current_video) else None
    turbo.push(turbo.replace(
        render_template('_video_list.html', videos=videos, current_video=cur_vid),
        target='videos'
    ))
    turbo.push(turbo.replace(
        render_template('_player.html', videos=videos, current_video=cur_vid),
        target='player'
    ))
    return jsonify({'status': 'ok'})
