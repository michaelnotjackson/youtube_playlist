import pytest
from dotenv import load_dotenv
from src.api import app, videos, current_video
from src.models import Video, video_from_url
from json import loads
from unittest.mock import AsyncMock

@pytest.fixture
def client():
    load_dotenv()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    videos.clear()
    current_video.clear()

def test_api_v1_get_next(client, mocker):
    video = Video(id='1', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', thumbnail_url='http://test.com/thumb.jpg')
    videos.append(video)
    rv = client.get('/api/v1/get_next')
    assert rv.status_code == 200
    json = loads(rv.json)
    assert json['id'] == '1'

def test_api_v1_get_video_list(client, mocker):
    video = Video(id='1', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', thumbnail_url='http://test.com/thumb.jpg')
    videos.append(video)
    rv = client.get('/api/v1/get_video_list')
    assert rv.status_code == 200
    json = loads(rv.json)
    assert json[0]['id'] == '1'

def test_api_v1_add(client, mocker):
    mocker.patch('src.api.video_from_url', return_value=Video(id='1', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', thumbnail_url='http://test.com/thumb.jpg'))
    rv = client.put('/api/v1/add', json={'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'})
    assert rv.status_code == 200
    json = loads(rv.json)
    assert json['id'] == '1'
    assert len(videos) == 1

def test_api_v1_delete(client, mocker):
    video = Video(id='1', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', thumbnail_url='http://test.com/thumb.jpg')
    videos.append(video)
    mocker.patch('src.api.get_video_by_id', return_value=video)
    rv = client.delete('/api/v1/delete', json={'video_id': '1'})
    assert rv.status_code == 200
    assert len(videos) == 0

def test_api_v1_get_current(client, mocker):
    video = Video(id='1', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', thumbnail_url='http://test.com/thumb.jpg')
    current_video.append(video)
    rv = client.get('/api/v1/get_current')
    assert rv.status_code == 200
    json = loads(rv.json)
    assert json['id'] == '1'

def test_api_v1_get_video_data_by_id(client, mocker):
    load_dotenv()
    video = Video(id='1', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', thumbnail_url='http://test.com/thumb.jpg')
    videos.append(video)
    mocker.patch('src.api.get_video_by_id', return_value=video)
    rv = client.get('/api/v1/get_video_data_by_id', query_string={'video_id': '1'})
    assert rv.status_code == 200
    json = loads(rv.json)
    assert json['id'] == '1'

@pytest.mark.asyncio
async def test_video_from_url(mocker):
    mock_response = {
        'items': [{
            'snippet': {
                'title': 'Test Video',
                'thumbnails': {
                    'default': {
                        'url': 'http://test.com/thumb.jpg'
                    }
                }
            }
        }]
    }

    mocker.patch('aiohttp.ClientSession.get', new_callable=AsyncMock, return_value=AsyncMock(json=AsyncMock(return_value=mock_response), status=200))

    video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    video = await video_from_url(video_url)

    assert isinstance(video, Video)
    assert video.title == 'Test Video'
    assert video.thumbnail_url == 'http://test.com/thumb.jpg'
    assert video.video_url == video_url