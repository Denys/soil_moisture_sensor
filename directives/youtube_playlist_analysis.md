# Directive: YouTube Playlist Analysis

## Purpose
Extract, analyze, and order videos from a YouTube playlist based on relevance to soil moisture sensor technology and electronic circuitry.

## Inputs
- **Playlist URL**: YouTube playlist URL (e.g., `https://youtube.com/playlist?list=...`)
- **Target Technology**: TEROS10-style soil moisture sensor development

## Tools
1. `execution/fetch_playlist.py` - Fetches all video metadata from playlist
2. `execution/analyze_videos.py` - Scores, filters, and orders videos

## Workflow

### Step 1: Fetch Playlist Data
```bash
python execution/fetch_playlist.py "PLAYLIST_URL"
```
**Output**: `.tmp/playlist_raw.json`

### Step 2: Analyze Videos
```bash
python execution/analyze_videos.py
```
**Output**: `.tmp/analyzed_videos.json`

## Analysis Criteria

### Relevance Categories

**Fundamental (Priority 1-3)**
- Basic electronics principles
- Sensor fundamentals (capacitive vs resistive)
- Soil properties and dielectric constants
- Microcontroller basics (Arduino, ESP32)

**Intermediate (Priority 4-6)**
- PCB design for sensors
- Signal conditioning circuits
- ADC and measurement techniques
- I2C/SPI communication protocols

**Advanced (Priority 7-10)**
- Frequency domain reflectometry (FDR)
- Professional calibration techniques
- Commercial sensor analysis (TEROS10, EC-5)
- High-accuracy measurement optimization
- Environmental compensation

### Keyword Scoring

| Category | Keywords | Weight |
|----------|----------|--------|
| Core Sensor | soil moisture, sensor, TEROS, capacitive, probe | +10 |
| Electronics | circuit, PCB, op-amp, ADC, microcontroller, Arduino | +7 |
| Theory | dielectric, permittivity, frequency, impedance | +8 |
| Practical | calibration, accuracy, measurement, testing | +6 |
| Advanced | FDR, TDR, commercial, professional | +5 |
| Negative | unboxing only, unrelated topic | -5 |

## Edge Cases

1. **Private/Deleted Videos**: Skip and log in `.tmp/skipped_videos.log`
2. **API Rate Limits**: Implement exponential backoff (2s, 4s, 8s, 16s)
3. **Non-English Videos**: Include if technical content visible in title
4. **Very Short Videos (<2 min)**: Lower score unless highly relevant title

## Output Format

```json
{
  "playlist_id": "...",
  "total_videos": 50,
  "analyzed_videos": [
    {
      "order": 1,
      "video_id": "...",
      "title": "...",
      "url": "...",
      "summary": "One sentence summary",
      "category": "Fundamental",
      "relevance_score": 85,
      "duration": "12:34"
    }
  ]
}
```

## Learnings
<!-- Update this section as you discover new patterns -->
- API quota: 10,000 units/day for YouTube Data API v3
- playlistItems.list costs 1 unit per call (50 items max per page)
