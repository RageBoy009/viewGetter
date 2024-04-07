from googleapiclient.discovery import build
import json
from datetime import datetime

# Replace 'YOUR_API_KEY' with your actual API key
api_key = 'API-KEY-HERE'
youtube = build('youtube', 'v3', developerKey=api_key)

def get_channel_videos(channel_id, max_results=None):
    # Get the list of videos from the channel's upload playlist
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None
    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50, pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None or (max_results is not None and len(videos) >= max_results):
            break
    
    # If a maximum number of results is set, truncate the list of videos
    if max_results is not None:
        videos = videos[:max_results]
    
    return videos

def extract_video_details(videos):
    # Extract video details
    video_details = []
    for video in videos:
        video_id = video['snippet']['resourceId']['videoId']
        video_title = video['snippet']['title']
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        
        # Parse and reformat the published date
        published_at_raw = video['snippet']['publishedAt']
        published_at = datetime.strptime(published_at_raw, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y/%m/%d')
        
        # Get video view count
        video_res = youtube.videos().list(id=video_id, part='statistics').execute()
        view_count = video_res['items'][0]['statistics']['viewCount']
        
        video_details.append({
            'title': video_title,
            'video_link': video_link,
            'published_at': published_at,
            'view_count': view_count
        })
    
    return video_details

# Example usage
channel_id = 'CHANNEL_ID' # Replace with the actual channel ID
max_results = 30  # Limit to the X newest videos
videos = get_channel_videos(channel_id, max_results)
video_details = extract_video_details(videos)

# Print video details
print(json.dumps(video_details, indent=2))
