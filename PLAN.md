# Comprehensive Plan: Soil Moisture Sensor YouTube Playlist Analysis

## Objective
Analyze YouTube playlist to understand soil moisture sensor technology (targeting TEROS10-level performance), filter and order videos by relevance, and deliver results in Google Sheets.

---

## Phase 1: Infrastructure Setup

### 1.1 Create Directory Structure
```
soil_moisture_sensor/
├── directives/
│   ├── youtube_playlist_analysis.md
│   └── sheets_export.md
├── execution/
│   ├── fetch_playlist.py
│   ├── analyze_videos.py
│   └── export_to_sheets.py
├── .tmp/
│   ├── playlist_raw.json
│   └── analyzed_videos.json
├── .env
└── credentials.json / token.json
```

### 1.2 Environment Setup
- **YouTube Data API v3**: Required to fetch playlist metadata
- **Google Sheets API**: Required to create/populate spreadsheet
- **API Keys**: Store in `.env` file

**Required `.env` variables:**
```
YOUTUBE_API_KEY=<your_youtube_api_key>
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json
```

---

## Phase 2: Directive Creation

### 2.1 Directive: `directives/youtube_playlist_analysis.md`

**Purpose**: SOP for extracting and analyzing YouTube playlist videos

**Contents:**
- Input: YouTube playlist URL
- Tools: `execution/fetch_playlist.py`, `execution/analyze_videos.py`
- Output: JSON file with filtered, ordered video list
- Edge cases: Private videos, unavailable content, rate limits

**Analysis Criteria for Soil Moisture Sensor Relevance:**
1. **Fundamentals (Priority 1-3)**:
   - Basic electronics (resistors, capacitors, op-amps)
   - Sensor principles (capacitive vs resistive)
   - Soil properties affecting moisture measurement

2. **Intermediate (Priority 4-6)**:
   - PCB design for sensors
   - Signal conditioning circuits
   - Microcontroller integration (ADC, I2C, SPI)

3. **Advanced (Priority 7-10)**:
   - Calibration techniques
   - Frequency domain reflectometry (FDR)
   - Commercial sensor teardowns (TEROS10, EC-5)
   - Professional-grade accuracy optimization

### 2.2 Directive: `directives/sheets_export.md`

**Purpose**: SOP for exporting analyzed data to Google Sheets

**Contents:**
- Input: Analyzed video JSON
- Tools: `execution/export_to_sheets.py`
- Output: Google Sheet with columns:
  - Order (1 = most fundamental)
  - Video Title (hyperlinked)
  - One-Sentence Summary
  - Relevance Category (Fundamental/Intermediate/Advanced)
  - Duration

---

## Phase 3: Execution Scripts

### 3.1 Script: `execution/fetch_playlist.py`

**Function**: Extract all video metadata from playlist

**Implementation:**
```python
# Pseudocode
1. Load YouTube API key from .env
2. Parse playlist ID from URL
3. Call YouTube Data API v3 (playlistItems.list)
4. For each video, fetch:
   - videoId
   - title
   - description
   - duration
   - publishedAt
   - thumbnails
5. Save to .tmp/playlist_raw.json
6. Handle pagination (50 items per page max)
```

**Error Handling:**
- API quota exceeded → Wait and retry with backoff
- Invalid playlist → Clear error message
- Private videos → Skip and log

### 3.2 Script: `execution/analyze_videos.py`

**Function**: Analyze, filter, and order videos by relevance

**Implementation:**
```python
# Pseudocode
1. Load .tmp/playlist_raw.json
2. For each video, score based on:
   - Title keywords (soil, moisture, sensor, capacitive, etc.)
   - Description analysis
   - Duration (longer = potentially more in-depth)
3. Filter out irrelevant videos (score < threshold)
4. Categorize: Fundamental / Intermediate / Advanced
5. Sort by category, then by score within category
6. Generate one-sentence summary from title + description
7. Save to .tmp/analyzed_videos.json
```

**Keyword Scoring Matrix:**
| Category | Keywords | Weight |
|----------|----------|--------|
| Core | soil moisture, sensor, TEROS, capacitive | +10 |
| Electronics | circuit, PCB, op-amp, ADC, microcontroller | +7 |
| Theory | dielectric, permittivity, frequency | +8 |
| Practical | calibration, accuracy, measurement | +6 |
| Negative | unboxing, review only, unrelated | -5 |

### 3.3 Script: `execution/export_to_sheets.py`

**Function**: Create and populate Google Sheet

**Implementation:**
```python
# Pseudocode
1. Load .tmp/analyzed_videos.json
2. Authenticate with Google Sheets API
3. Create new spreadsheet: "Soil Moisture Sensor Learning Path"
4. Format headers (bold, frozen row)
5. Populate rows:
   - Column A: Order number
   - Column B: =HYPERLINK(url, title)
   - Column C: One-sentence summary
   - Column D: Category
   - Column E: Duration
6. Auto-resize columns
7. Return shareable link
```

---

## Phase 4: Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXECUTION FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Setup Environment                                           │
│     └─> Create dirs, validate API keys                         │
│                                                                 │
│  2. Fetch Playlist Data                                         │
│     └─> execution/fetch_playlist.py                            │
│     └─> Output: .tmp/playlist_raw.json                         │
│                                                                 │
│  3. Analyze & Order Videos                                      │
│     └─> execution/analyze_videos.py                            │
│     └─> Output: .tmp/analyzed_videos.json                      │
│                                                                 │
│  4. Export to Google Sheets                                     │
│     └─> execution/export_to_sheets.py                          │
│     └─> Output: Shareable Google Sheet URL                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 5: Deliverables

### Final Google Sheet Structure

| Order | Video Title | Summary | Category | Duration |
|-------|-------------|---------|----------|----------|
| 1 | [Link] Basic Electronics... | Covers fundamental circuit... | Fundamental | 12:34 |
| 2 | [Link] How Capacitive... | Explains capacitive sensing... | Fundamental | 18:22 |
| ... | ... | ... | ... | ... |

### Expected Output
- **Google Sheet URL**: Shareable, organized learning path
- **Video Count**: Filtered list (estimate 60-80% of original playlist)
- **Ordering**: Fundamentals → Intermediate → Advanced

---

## Phase 6: Prerequisites Checklist

Before execution, ensure:

- [ ] YouTube Data API v3 enabled in Google Cloud Console
- [ ] Google Sheets API enabled
- [ ] OAuth 2.0 credentials downloaded as `credentials.json`
- [ ] YouTube API key generated and added to `.env`
- [ ] Python dependencies installed:
  ```
  pip install google-api-python-client google-auth-oauthlib python-dotenv
  ```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API quota exceeded | Implement exponential backoff; cache results |
| Video analysis inaccuracy | Manual review step before final export |
| Private/deleted videos | Skip gracefully, log for reference |
| Large playlist (100+ videos) | Pagination handling in fetch script |

---

## Estimated Workflow

1. **Setup**: Create directories, verify API access
2. **Fetch**: Run fetch_playlist.py
3. **Analyze**: Run analyze_videos.py (may need LLM assistance for summaries)
4. **Review**: Quick manual check of ordering logic
5. **Export**: Run export_to_sheets.py
6. **Deliver**: Share Google Sheet link

---

## Next Steps

1. User to confirm API access / provide credentials
2. Create `directives/` and `execution/` directories
3. Implement scripts in order
4. Test with playlist
5. Deliver final Google Sheet

---

*Plan created following 3-layer architecture (Directive → Orchestration → Execution)*
