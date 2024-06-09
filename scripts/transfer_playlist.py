import os
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import google.auth
import google_auth_oauthlib.flow
import googleapiclient.discovery

# Absolute path to the credentials file
CREDENTIALS_PATH = os.path.abspath('./credentials\youtube_credentials.json')
SPOTIPY_CLIENT_ID = '19c18b1a551d41afa19a4f93fd61e2e6'
SPOTIPY_CLIENT_SECRET = '223ced6438d64241af190b187304e141'
SPOTIPY_PLAYLIST_ID = 'https://open.spotify.com/playlist/0CBqB1ybR2nx19xVZAHuyV?si=5b7b88733e3143ea'

# Spotify API authentication
def get_spotify_tracks(playlist_id):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    track_list = []
    for item in tracks:
        track = item['track']
        track_info = f"{track['name']} {track['artists'][0]['name']}"
        track_list.append(track_info)
    return track_list

# YouTube API authentication
def get_youtube_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, ["https://www.googleapis.com/auth/youtube.force-ssl"])
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
    return youtube

# Search for a video on YouTube
def search_youtube(youtube, query):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    return response['items'][0]['id']['videoId'] if response['items'] else None

# Create a new YouTube playlist
def create_youtube_playlist(youtube, title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Spotify", "Music", "Playlist"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    return response['id']

# Add a video to the YouTube playlist
def add_video_to_youtube_playlist(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    request.execute()

def main():
    # Get Spotify tracks
    tracks = get_spotify_tracks(SPOTIPY_PLAYLIST_ID)
    print(f"Fetched {len(tracks)} tracks from Spotify")

    # Authenticate YouTube service
    youtube = get_youtube_service()
    print("Authenticated with YouTube")

    # Create YouTube playlist
    playlist_title = "My Spotify Playlist on YouTube"
    playlist_description = "This playlist was converted from Spotify to YouTube using Python."
    youtube_playlist_id = create_youtube_playlist(youtube, playlist_title, playlist_description)
    print(f"Created YouTube playlist with ID: {youtube_playlist_id}")

    # Search and add tracks to YouTube playlist
    for track in tracks:
        print(f"Searching for: {track}")
        video_id = search_youtube(youtube, track)
        if video_id:
            print(f"Found YouTube video ID: {video_id}, adding to playlist")
            add_video_to_youtube_playlist(youtube, youtube_playlist_id, video_id)
        else:
            print(f"Could not find video for: {track}")

if __name__ == "__main__":
    main()
