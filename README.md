# Youtube playlist

## Credentials

Шейко Михаил Андреевич Б05-352

## Description

This is a convenient web tool for creating and controlling youtube playlists with donation alerts integration

## Desired functionality

1) Integrated video player
1) Ability to add videos manually
2) Ability to control video flow
3) Ability to skip to the desired video in queue
4) <s>Integration with donationalerts linked media</s>

Integration with dontaionalerts api was discarded because of extremely poor written API docs.

## Architecture

```python
@dataclass
class Video:
    """
    Dataclass which holds information about video

    Attributes:
        - id: str - Video object uuid
        - title: str | None - Video title
        - thumbnail_url: str | None - Video thumbnail url
        - video_url: str - YouTube video url
        - playback_url: str - Video playback url
    """
    id: str | None
    title: str | None
    thumbnail_url: str | None
    video_url: str | None
    playback_url: str | None
```

`EDIT: Deleted Playlist class as it's not needed`

When addition of the video is requested either by hand or via API exemplar of class Video is created. All of its fields are assigned asynchronously. This guarantees that simultaneous requests can be worked with correctly. Then it's being put into the queue.

When deletion request arrives if video is in the queue it's being deleted. If it's not present, then request is ignored.

If API is given wrong link video it responds with ERROR 400 (Bad Request). No changes to system state are made in this case.

UI elemnts use same API as an external user does.

### Supported api endpoints

<details>
<summary>[GET] /api/v1/get_next</summary>
Get next video from list
</details>
<details>
<summary>[GET] /api/v1/get_current</summary>
Get currently playing video
</details>
<details>
<summary>[PUT] /api/v1/add?video_url=&lt;video_url&gt;</summary>
Add video to the queue by its url
</details>
<details>
<summary>[DELTE] /api/v1/delete?video_id=&lt;video_id&gt;</summary>
Delete video by its id
</details>
<details>
<summary>[GET] /api/v1/get_video_list</summary>
Get list of links and titles to videos in queue
</details>
<details>
<summary>[GET] /api/v1/get_video_data_by_id?video_id=&lt;video_id&gt;</summary>
Get video data, including playback url, by its id
</details>

## Dependencies

- python >= 3.12
- flask
- flask[async]
- turbo-flask
- flask-pydantic
- pydantic
- aiohttp
- yt-dlp
- python-dotenv


## Launching guide
1) Install dependencies either via pip or poetry:
    * In case of pip you need to run `pip install -r requirements.txt`
    * In case of poetry you need to run `poetry install`
2) Create `.env` file in the root of the project with the following content:
    ```
    YOUTUBE_API_KEY=<your_youtube_api_key>
    COOKIE_FILE_PATH=<path_to_cookie_file_with_youtube_auth>
    ```
   * Cookie file can be obtained by following [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)
3) Run the server by executing `python main.py`
