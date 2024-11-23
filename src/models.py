import os
import re

from pydantic.dataclasses import dataclass
from uuid import uuid4
from os import getenv
from aiohttp import ClientSession


@dataclass
class Video:
    """
    Dataclass which holds information about video

    Attributes:
        - id: str | None - Video object uuid
        - title: str | None - Video title
        - thumbnail_url: str | None - Video thumbnail url
        - video_url: str | None - YouTube video url
        - playback_url: str | None - Video playback url
    """
    id: str | None = None
    title: str | None = None
    thumbnail_url: str | None = None
    video_url: str | None = None
    playback_url: str | None = None


async def video_from_url(video_url: str, client_session: ClientSession | None = None) -> Video:
    """
    Video object factory function. Constructs video from url
    :param video_url:
    :param client_session:
    :return:
    """
    should_close: bool = False
    if client_session is None:
        should_close = True
        client_session = ClientSession()

    id_regexp = r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
    api_url = (f'https://www.googleapis.com/youtube/v3/videos'
               f'?key={os.getenv('YOUTUBE_API_KEY')}'
               f'&id={re.match(id_regexp, video_url)[7]}'
               f'&part=snippet')

    response = await client_session.get(api_url)

    await response.raise_for_status()

    data = await response.json()

    if should_close:
        await client_session.close()

    return Video(
        uuid4().hex,
        data['items'][0]['snippet']['title'],
        data['items'][0]['snippet']['thumbnails']['default']['url'],
        video_url,
        None
    )
