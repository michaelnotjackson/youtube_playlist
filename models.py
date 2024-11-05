from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from uuid import uuid4
from aiohttp import ClientSession
from re import match
from isodate import parse_duration
from os import getenv

@dataclass
class Video:
    """
    Dataclass which holds information about video

    Attributes:
        - uuid: str - Video object uuid
        - title: str | None - Video title
        - thumbnail_url: str | None - Video thumbnail url
        - duration: int - Video duration in seconds
        - playback_url: str - Video playback url
        - video_id: str - YouTube video id
    """
    uuid: str
    title: str | None
    thumbnail_url: str | None
    duration: int
    playback_url: str


video_id_regex: str = r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
youtube_api_url: str = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails'

async def video_from_url(video_url: str, client_session: ClientSession | None = None):
    if client_session is None:
        client_session = ClientSession()

    video_id = match(video_id_regex, video_url).group(7)
    response = await client_session.get(f'{youtube_api_url}&id={video_id}&key={getenv('YOUTUBE_API_KEY')}')
    data = await response.json()

    return Video(
        uuid4().hex,
        data['items'][0]['snippet']['title'],
        data['items'][0]['snippet']['thumbnails']['default']['url'],
        parse_duration(data['items'][0]['contentDetails']['duration']).total_seconds(),
        '',
    )

