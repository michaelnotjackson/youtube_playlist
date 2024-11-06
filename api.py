from crypt import methods

from app import app, turbo, videos, get_video_by_id
from flask_pydantic import validate
from pydantic import RootModel
from models import Video, video_from_url
from flask import request

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
    return {'status': 'ok'}