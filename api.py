from app import app, videos, get_video_by_id, current_video
from flask_pydantic import validate
from pydantic import RootModel
from models import Video, video_from_url
from flask import request, jsonify
import os
import yt_dlp


@validate
@app.route('/api/v1/get_next', methods=['GET'])
def api_v1_get_next():
    video = videos[0]
    return RootModel[Video](video).model_dump_json(exclude={'playback_url'})


@validate
@app.route('/api/v1/get_video_list', methods=['GET'])
def api_v1_get_video_list():
    return RootModel[list[Video]](videos).model_dump_json(exclude={'playback_url'})

@validate
@app.route('/api/v1/add', methods=['PUT'])
async def api_v1_add():
    url = request.json['video_url']
    video = await video_from_url(url)
    videos.append(video)
    return RootModel[Video](video).model_dump_json(exclude={'playback_url'})

@validate
@app.route('/api/v1/delete', methods=['DELETE'])
def api_v1_delete():
    video_id = request.json['video_id']
    video = get_video_by_id(video_id)
    videos.remove(video)
    return jsonify({'status': 'ok'})

@validate
@app.route('/api/v1/get_current', methods=['GET'])
def api_v1_get_current():
    return RootModel[Video](current_video[0]).model_dump_json()

@validate
@app.route('/api/v1/get_video_data_by_id', methods=['GET'])
def api_v1_get_video_data_by_id():
    video_id = request.args['video_id']
    video = get_video_by_id(video_id)
    if video.playback_url is None:
        ydl_opts = {'cookiefile': os.getenv('COOKIE_FILE_PATH'), 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video.video_url, download=False)
            video.playback_url = info['url']

    return RootModel[Video](video).model_dump_json()