from .app import app, videos, get_video_by_id, current_video
from flask_pydantic import validate
from pydantic import RootModel
from .models import Video, video_from_url
from flask import request, jsonify, abort
import os
import yt_dlp


@validate
@app.route('/api/v1/get_next', methods=['GET'])
def api_v1_get_next():
    """
    Get next video from the list
    """
    video = videos[0]
    return jsonify(RootModel[Video](video).model_dump_json(exclude={'playback_url'}))


@validate
@app.route('/api/v1/get_video_list', methods=['GET'])
def api_v1_get_video_list():
    """
    Get list of videos
    """
    return jsonify(RootModel[list[Video]](videos).model_dump_json(exclude={'playback_url'}))

@validate
@app.route('/api/v1/add', methods=['PUT'])
async def api_v1_add():
    """
    Add video to the list.
    :param: video_url: str - YouTube video url
    """
    url = request.json['video_url']
    video: Video | None = None
    try:
        video = await video_from_url(url)
        if video.thumbnail_url == '':
            abort(400)
    except ():
        abort(400)
    videos.append(video)
    return jsonify(RootModel[Video](video).model_dump_json(exclude={'playback_url'}))

@validate
@app.route('/api/v1/delete', methods=['DELETE'])
def api_v1_delete():
    """
    Delete video from the list
    :param: video_id: str - Video object uuid
    """
    video_id = request.json['video_id']
    video = get_video_by_id(video_id)
    videos.remove(video)
    return ''

@validate
@app.route('/api/v1/get_current', methods=['GET'])
def api_v1_get_current():
    """
    Get currently playing video
    """
    return jsonify(RootModel[Video](current_video[0]).model_dump_json())

@validate
@app.route('/api/v1/get_video_data_by_id', methods=['GET'])
def api_v1_get_video_data_by_id():
    """
    Get video data by given id
    """
    video_id = request.args['video_id']
    video = get_video_by_id(video_id)
    if video.playback_url is None:
        ydl_opts = {'cookiefile': os.getenv('COOKIE_FILE_PATH'), 'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video.video_url, download=False)
            video.playback_url = info['url']

    return jsonify(RootModel[Video](video).model_dump_json())
