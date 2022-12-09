from getpass import getpass
from argparse import ArgumentParser, Namespace
from typing import Union

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_apikey_service(api_key: str):
	return build(API_SERVICE_NAME, API_VERSION, developerKey=api_key)

def youtube_search(options: Union[dict, Namespace], api_key: str):
	youtube = get_apikey_service(api_key)
	print(type(options))
	search_args = dict(part='id,snippet', order='date')

	if type(options) is Namespace:
		options = vars(options)
	search_args.update(options)

	search_response = youtube.search().list(**search_args).execute()

	videos = []
	channels = []
	playlists = []
	
	for search_result in search_response.get('items', []):
		if search_result['id']['kind'] == 'youtube#video':
			videos.append({
				'title': search_result['snippet']['title'],
				'video_id':search_result['id']['videoId']
			})
		elif search_result['id']['kind'] == 'youtube#channel':
			channels.append({
				'title': search_result['snippet']['title'],
				'channel_id': search_result['id']['channelId']
			})
		elif search_result['id']['kind'] == 'youtube#playlist':
			playlists.append({
				'title': search_result['snippet']['title'],
				'playlist_id': search_result['id']['playlistId']
			})

	return {
		'videos': videos,
		'channels': channels,
		'playlists': playlists
	}

def get_channel_videos(api_key: str, channel_id: int, max_results: int = 20):
	args = {"channelId": channel_id, "maxResults": max_results}
	res = youtube_search(args, api_key)
	return res

def get_channel_videos_cli():
	parser = ArgumentParser()
	parser.add_argument("--channelId", help="Channel ID", required=True)
	parser.add_argument("--maxResults", help="Max no. results to show.", default=20)

	args = parser.parse_args()
	api_key = getpass("Google API key: ")
	
	try:
		res = youtube_search(args, api_key)
		print(res)
	except HttpError as err:
		print(f'An HTTP error {err.resp.status} occurred:\n{err.content}')

if __name__ == "__main__":
	get_channel_videos_cli()
	