#!/usr/bin/env python3
"""
Fetch YouTube Playlist Metadata

Extracts all video metadata from a YouTube playlist using the YouTube Data API v3.
Output: .tmp/playlist_raw.json

Usage:
    python execution/fetch_playlist.py "PLAYLIST_URL_OR_ID"
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("YOUTUBE_API_KEY")
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp"
OUTPUT_FILE = OUTPUT_DIR / "playlist_raw.json"
SKIPPED_LOG = OUTPUT_DIR / "skipped_videos.log"

# Retry configuration
MAX_RETRIES = 4
BACKOFF_BASE = 2  # seconds


def extract_playlist_id(url_or_id: str) -> str:
    """Extract playlist ID from URL or return as-is if already an ID."""
    # Match playlist ID in URL
    match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url_or_id)
    if match:
        return match.group(1)
    # Assume it's already a playlist ID
    return url_or_id


def fetch_with_retry(request, description: str):
    """Execute API request with exponential backoff retry."""
    for attempt in range(MAX_RETRIES):
        try:
            return request.execute()
        except HttpError as e:
            if e.resp.status in [429, 500, 503]:  # Rate limit or server errors
                wait_time = BACKOFF_BASE ** (attempt + 1)
                print(f"  Retry {attempt + 1}/{MAX_RETRIES}: {description} (waiting {wait_time}s)")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed after {MAX_RETRIES} retries: {description}")


def parse_duration(duration: str) -> str:
    """Convert ISO 8601 duration to human-readable format."""
    # PT1H2M3S -> 1:02:03
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return duration

    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def fetch_playlist(playlist_id: str) -> dict:
    """Fetch all videos from a YouTube playlist."""
    if not API_KEY:
        raise ValueError("YOUTUBE_API_KEY not found in environment. Check .env file.")

    youtube = build('youtube', 'v3', developerKey=API_KEY)

    videos = []
    skipped = []
    next_page_token = None
    page_num = 0

    print(f"Fetching playlist: {playlist_id}")

    # Get playlist metadata
    playlist_request = youtube.playlists().list(
        part="snippet",
        id=playlist_id
    )
    playlist_response = fetch_with_retry(playlist_request, "playlist metadata")

    if not playlist_response.get('items'):
        raise ValueError(f"Playlist not found: {playlist_id}")

    playlist_title = playlist_response['items'][0]['snippet']['title']
    print(f"Playlist title: {playlist_title}")

    # Fetch all playlist items
    while True:
        page_num += 1
        print(f"  Fetching page {page_num}...")

        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = fetch_with_retry(request, f"page {page_num}")

        video_ids = []
        items_map = {}

        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            snippet = item['snippet']

            # Check for unavailable videos
            if snippet.get('title') == 'Private video' or snippet.get('title') == 'Deleted video':
                skipped.append({
                    'video_id': video_id,
                    'reason': snippet.get('title', 'Unknown')
                })
                continue

            video_ids.append(video_id)
            items_map[video_id] = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'published_at': snippet.get('publishedAt', ''),
                'position': snippet.get('position', 0)
            }

        # Fetch video details (duration, etc.) in batch
        if video_ids:
            details_request = youtube.videos().list(
                part="contentDetails,statistics",
                id=','.join(video_ids)
            )
            details_response = fetch_with_retry(details_request, "video details")

            for detail in details_response.get('items', []):
                vid = detail['id']
                if vid in items_map:
                    duration_iso = detail['contentDetails'].get('duration', 'PT0S')
                    items_map[vid]['duration'] = parse_duration(duration_iso)
                    items_map[vid]['duration_seconds'] = iso_to_seconds(duration_iso)
                    items_map[vid]['view_count'] = int(detail.get('statistics', {}).get('viewCount', 0))

        videos.extend(items_map.values())

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    print(f"  Found {len(videos)} videos, skipped {len(skipped)}")

    return {
        'playlist_id': playlist_id,
        'playlist_title': playlist_title,
        'total_videos': len(videos),
        'skipped_count': len(skipped),
        'videos': videos,
        'skipped': skipped
    }


def iso_to_seconds(duration: str) -> int:
    """Convert ISO 8601 duration to seconds."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return 0

    hours, minutes, seconds = match.groups()
    total = 0
    if hours:
        total += int(hours) * 3600
    if minutes:
        total += int(minutes) * 60
    if seconds:
        total += int(seconds)
    return total


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_playlist.py <PLAYLIST_URL_OR_ID>")
        print("Example: python fetch_playlist.py 'https://youtube.com/playlist?list=PLxxx'")
        sys.exit(1)

    playlist_input = sys.argv[1]
    playlist_id = extract_playlist_id(playlist_input)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        data = fetch_playlist(playlist_id)

        # Save main output
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to: {OUTPUT_FILE}")

        # Save skipped videos log
        if data['skipped']:
            with open(SKIPPED_LOG, 'w', encoding='utf-8') as f:
                for item in data['skipped']:
                    f.write(f"{item['video_id']}: {item['reason']}\n")
            print(f"Skipped videos logged to: {SKIPPED_LOG}")

        print(f"\nTotal videos fetched: {data['total_videos']}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except HttpError as e:
        print(f"YouTube API Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
