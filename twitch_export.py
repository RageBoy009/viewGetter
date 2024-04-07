import requests
import json
from datetime import datetime

def get_oauth_token(client_id, client_secret):
    url = "https://id.twitch.tv/oauth2/token"
    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=body)
    return response.json()['access_token']


def get_user_id(client_id, token, user_login):
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    url = f"https://api.twitch.tv/helix/users?login={user_login}"
    response = requests.get(url, headers=headers)
    user_info = response.json()
    return user_info['data'][0]['id'] if user_info['data'] else None


def get_vods_info(client_id, token, user_id, first=20):
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive&first={first}"
    response = requests.get(url, headers=headers)
    vods_data = response.json()
    
    # Print or log the raw response for inspection
    print("VODs API Response:", json.dumps(vods_data, indent=4))
    
    return vods_data


def fetch_game_names(client_id, token, game_ids):
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {token}'
    }
    games = {}
    for game_id in game_ids:
        url = f"https://api.twitch.tv/helix/games?id={game_id}"
        response = requests.get(url, headers=headers)
        game_data = response.json()
        
        # Print or log the raw response for each game ID for inspection
        print(f"Game API Response for ID {game_id}:", json.dumps(game_data, indent=4))
        
        if game_data['data']:
            game_name = game_data['data'][0]['name']
            games[game_id] = game_name
    return games



def extract_vod_details(vods_data):
    vods = vods_data.get('data', [])
    
    vod_details = []
    for vod in vods:
        title = vod['title']
        view_count = vod['view_count']
        
        # Parse the published_at date and reformat it
        published_at_raw = vod['published_at']
        published_at = datetime.strptime(published_at_raw, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")
        
        url = vod['url']
        duration = vod['duration']  # No change needed here
        
        vod_details.append({
            'title': title,
            'view_count': view_count,
            'published_at': published_at,
            'url': url,
            'duration': duration
        })
    return vod_details



def print_vod_details(vod_details):
    print("Title".ljust(50), "View Count".ljust(12), "Published At".ljust(20), "URL")
    print("-" * 100)  # Print a separator line for better readability
    for vod in vod_details:
        title = vod['title'].ljust(50)
        view_count = str(vod['view_count']).ljust(12)
        published_at = vod['published_at'][:10]  # Extract just the date part, if you prefer
        url = vod['url']
        print(f"{title} {view_count} {published_at} {url}")
        
        
def duration_to_hours(duration_str):
    total_seconds = 0
    hours = minutes = seconds = 0
    
    # Extract hours, minutes, and seconds using regular expressions
    import re
    hours_match = re.search(r'(\d+)h', duration_str)
    minutes_match = re.search(r'(\d+)m', duration_str)
    seconds_match = re.search(r'(\d+)s', duration_str)
    
    if hours_match:
        hours = int(hours_match.group(1))
    if minutes_match:
        minutes = int(minutes_match.group(1))
    if seconds_match:
        seconds = int(seconds_match.group(1))
    
    # Convert everything to seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    # Convert seconds to hours
    hours = total_seconds / 3600
    return hours


def calculate_total_hours(vod_details):
    total_hours = sum([duration_to_hours(vod['duration']) for vod in vod_details])
    return total_hours

        

def save_vod_details_to_json(vod_details, filename='vod_details.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(vod_details, file, ensure_ascii=False, indent=4)


client_id = 'CLIENT_ID_HERE'
client_secret = 'CLIENT_SECRET_HERE'
user_login = '' #channel name here like in the example

token = get_oauth_token(client_id, client_secret)
user_id = get_user_id(client_id, token, user_login)
vods_info = get_vods_info(client_id, token, user_id, first=35)
vod_details = extract_vod_details(vods_info)

# Now, instead of printing, save the details to a JSON file
save_vod_details_to_json(vod_details, 'vod_details.json')
total_hours = calculate_total_hours(vod_details)

print(f"VOD details saved to vod_details.json successfully.")
print(f"Total hours of all VODs: {total_hours:.2f} hours")