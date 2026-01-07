#!/usr/bin/env python3
"""
Export Analyzed Videos to Google Sheets

Creates a formatted Google Sheet with the analyzed video learning path.
Input: .tmp/analyzed_videos.json
Output: Google Sheet URL

Usage:
    python execution/export_to_sheets.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / ".tmp" / "analyzed_videos.json"
CREDENTIALS_FILE = BASE_DIR / os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")
TOKEN_FILE = BASE_DIR / "token.json"

# Google Sheets API scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Sheet formatting
SHEET_TITLE = "Soil Moisture Sensor Learning Path"
CATEGORY_COLORS = {
    'Fundamental': {'red': 0.85, 'green': 0.92, 'blue': 0.83},   # Light green
    'Intermediate': {'red': 1.0, 'green': 0.95, 'blue': 0.8},     # Light yellow
    'Advanced': {'red': 0.99, 'green': 0.9, 'blue': 0.8}          # Light orange
}


def get_credentials():
    """Get or refresh Google API credentials."""
    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing credentials...")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {CREDENTIALS_FILE}\n"
                    "Download OAuth 2.0 credentials from Google Cloud Console."
                )
            print("Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"Credentials saved to: {TOKEN_FILE}")

    return creds


def create_spreadsheet(service, title: str) -> str:
    """Create a new spreadsheet and return its ID."""
    spreadsheet = {
        'properties': {'title': title}
    }
    result = service.spreadsheets().create(body=spreadsheet).execute()
    return result['spreadsheetId']


def format_sheet(service, spreadsheet_id: str, videos: list):
    """Apply formatting to the sheet."""
    requests = []

    # Header formatting (bold, frozen, gray background)
    requests.append({
        'repeatCell': {
            'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                    'textFormat': {'bold': True},
                    'horizontalAlignment': 'CENTER'
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
        }
    })

    # Freeze header row
    requests.append({
        'updateSheetProperties': {
            'properties': {'sheetId': 0, 'gridProperties': {'frozenRowCount': 1}},
            'fields': 'gridProperties.frozenRowCount'
        }
    })

    # Category-based row coloring
    for i, video in enumerate(videos):
        category = video.get('category', 'Intermediate')
        color = CATEGORY_COLORS.get(category, CATEGORY_COLORS['Intermediate'])

        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': i + 1,
                    'endRowIndex': i + 2,
                    'startColumnIndex': 3,  # Only category column
                    'endColumnIndex': 4
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': color,
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment)'
            }
        })

    # Column widths
    column_widths = [60, 400, 350, 120, 80]  # Order, Title, Summary, Category, Duration
    for i, width in enumerate(column_widths):
        requests.append({
            'updateDimensionProperties': {
                'range': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': i,
                    'endIndex': i + 1
                },
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        })

    # Center align Order and Duration columns
    for col_index in [0, 4]:  # Order and Duration
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 1,
                    'startColumnIndex': col_index,
                    'endColumnIndex': col_index + 1
                },
                'cell': {
                    'userEnteredFormat': {'horizontalAlignment': 'CENTER'}
                },
                'fields': 'userEnteredFormat.horizontalAlignment'
            }
        })

    # Wrap text in Summary column
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': 0,
                'startRowIndex': 1,
                'startColumnIndex': 2,
                'endColumnIndex': 3
            },
            'cell': {
                'userEnteredFormat': {'wrapStrategy': 'WRAP'}
            },
            'fields': 'userEnteredFormat.wrapStrategy'
        }
    })

    # Execute all formatting requests
    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()


def populate_sheet(service, spreadsheet_id: str, videos: list):
    """Populate the sheet with video data."""
    # Prepare data
    rows = [['Order', 'Video Title', 'Summary', 'Category', 'Duration']]

    for video in videos:
        # Create hyperlink formula
        title = video['title'].replace('"', '""')  # Escape quotes
        hyperlink = f'=HYPERLINK("{video["url"]}", "{title}")'

        rows.append([
            video['order'],
            hyperlink,
            video['summary'],
            video['category'],
            video['duration']
        ])

    # Write data
    range_name = 'A1:E' + str(len(rows))
    body = {
        'values': rows,
        'majorDimension': 'ROWS'
    }

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',  # Allows formulas
        body=body
    ).execute()

    print(f"  Written {len(rows)} rows")


def main():
    # Load analyzed videos
    if not INPUT_FILE.exists():
        print(f"Error: Input file not found: {INPUT_FILE}")
        print("Run analyze_videos.py first.")
        return 1

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    videos = data.get('videos', [])
    if not videos:
        print("No videos to export.")
        return 1

    print(f"Exporting {len(videos)} videos to Google Sheets...")

    try:
        # Authenticate
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)

        # Create spreadsheet
        playlist_title = data.get('playlist_title', 'YouTube Playlist')
        sheet_title = f"{SHEET_TITLE} - {playlist_title[:30]}"
        spreadsheet_id = create_spreadsheet(service, sheet_title)
        print(f"  Created spreadsheet: {sheet_title}")

        # Populate data
        populate_sheet(service, spreadsheet_id, videos)

        # Apply formatting
        print("  Applying formatting...")
        format_sheet(service, spreadsheet_id, videos)

        # Generate URL
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

        print(f"\n{'='*60}")
        print("SUCCESS! Google Sheet created:")
        print(f"\n{sheet_url}")
        print(f"\n{'='*60}")
        print(f"\nTotal videos: {len(videos)}")
        print(f"Categories: {data.get('category_counts', {})}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except HttpError as e:
        print(f"Google API Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
