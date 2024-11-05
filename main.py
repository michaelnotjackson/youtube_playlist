from flask import Flask, render_template, request
from turbo_flask import Turbo
from flask_pydantic import validate
from models import Video, video_from_url
from threading import Lock
import dotenv

app = Flask(__name__)
turbo = Turbo(app)

videos: list[Video] = []
@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        url = request.form['video']
        video = await video_from_url(url)
        videos.append(video)
        if turbo.can_stream():
            return turbo.stream([
                turbo.append(
                    render_template('_video.html', video=video), target='videos'),
                turbo.update(
                    render_template('_video_input.html'), target='form')])
    return render_template('index.html')


@app.route('/force_play/<uuid>', methods=['POST'])
# @validate
def force_play(uuid: str):
    pass

@app.route('/delete/<uuid>', methods=['POST'])
# @validate
def delete(uuid: str):
    pass

setup_once_lock = Lock()

@app.before_request
def app_setup():
    with setup_once_lock:
        try:
            dotenv.load_dotenv('.env')
        finally:
            app.before_request_funcs[None].remove(app_setup)


if __name__ == '__main__':
    app.run()