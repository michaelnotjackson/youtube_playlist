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
4) Integration with donation alerts linked media

## Architecture

```python
@dataclass
class Video:
"""
Storage for info about queued videos
"""
	video_url: str
	thumbnail_url: str
	title: str
	id: uuid.UUID

class Playlist:
"""
Playlist controller
"""
	queue: collections.dequeue[Video]
	current_idx: int

	def get_current_video(self) -> Video:
		"""
		@return: currently playing video
		"""
		pass

	def add_video(self, video: Video) -> None:
		"""
		Add video to queue to the last place

		@type video: Video
		@param video: Video to add into the queue
		"""
		pass

	def remove_video(self, video_id: uuid.UUID) -> None:
		"""
		Removes specified video from the queue

		@type video_id: uuid.UUID
		@param video_id: ID of video to remove
		"""
		pass
```

When addition of the video is requested either by hand or via API exemplar of class Video is created. All of its fields are assigned asynchronously. This guarantees that simultaneous requests can be worked with correctly. Then it's being put into the queue.

When deletion request arrives if video is in the queue it's being deleted. If it's not present, then request is ignored.

If API is given wrong link video it responds with ERROR 400 (Bad Request). No changes to system state are made in this case.

UI elemnts use same API as an external user does.

### Supported api endpoints

<details>
<summary>[PUT] /api/v1/add/{video_url}</summary>
Add video to the queue by its url
</details>
<details>
<summary>[DELTE] /api/v1/delete/{video_id}</summary>
Delete video by its id
</details>
<details>
<summary>[GET] /api/v1/get_video_list</summary>
Get list of links and titles to videos in queue, including last 5 played videos
</details>

## Dependencies

- python >= 3.12
- flask
- flask[async]
- turbo-flask
- flask-pydantic
- pydantic
- yt-dlp