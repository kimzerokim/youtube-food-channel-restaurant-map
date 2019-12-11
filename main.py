import os
import requests

from dotenv import load_dotenv
load_dotenv()

# Get my api key (set in .env file)
API_KEY = os.getenv('GOOGLE_API_KEY')

CHANNEL_IDS = [
    'UCQA89gPDjJ-1M1o9bwdGF-g',
    'UCrpWLg77FZSywF17aDgu_Fw',
]


def get_channel_name_and_upload_playlist_key(channel_id):
    request_url = f'https://www.googleapis.com/youtube/v3/channels' \
                  f'?part=contentDetails,snippet&id={channel_id}&key={API_KEY}'

    resp = requests.get(request_url)
    if resp.status_code == 200:
        data = resp.json()
        # Because we request for one specific channel with ID,
        # ['items'][0] is valid
        upload_playlist_key = (data['items'][0]
                                   ['contentDetails']
                                   ['relatedPlaylists']
                                   ['uploads'])
        channel_title = (data['items'][0]['snippet']['title'])
        return channel_title, upload_playlist_key
    else:
        raise Exception(f'Request Failed with '
                        f'STATUS_CODE = {resp.status_code}')


def get_playlist_video(playlist_key, page_token='', result=[]):
    temp_result = result.copy()
    request_url = f'https://www.googleapis.com/youtube/v3/playlistItems' \
                  f'?part=snippet,contentDetails&maxResults=50' \
                  f'&playlistId={playlist_key}&key={API_KEY}' \
                  f'&pageToken={page_token}'

    resp = requests.get(request_url)
    if resp.status_code == 200:
        data = resp.json()

        items = data['items']
        for item in items:
            temp_result.append({
                'id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
            })

        if 'nextPageToken' in data:
            return get_playlist_video(playlist_key,
                                      page_token=data['nextPageToken'],
                                      result=temp_result)
        else:
            return temp_result
    else:
        raise Exception(f'Request Failed with '
                        f'STATUS_CODE = {resp.status_code}')


def main():
    result = []

    for channel_id in CHANNEL_IDS:
        channel_title, upload_playlist_key = \
            get_channel_name_and_upload_playlist_key(channel_id)
        video_result = get_playlist_video(upload_playlist_key)
        result.append({
            'channel_title': channel_title,
            'videos': video_result,
        })

    return result


result = main()
print(result)
