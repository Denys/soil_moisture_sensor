# Directive: Google Sheets Export

## Purpose
Export analyzed video data to a formatted, shareable Google Sheet.

## Inputs
- **Analyzed Data**: `.tmp/analyzed_videos.json` (from analyze_videos.py)

## Tools
1. `execution/export_to_sheets.py` - Creates and populates Google Sheet

## Workflow

### Step 1: Export to Sheets
```bash
python execution/export_to_sheets.py
```
**Output**: Google Sheet URL (printed to console)

## Prerequisites

1. **Google Cloud Project** with Sheets API enabled
2. **OAuth 2.0 Credentials**: Download as `credentials.json`
3. **First Run**: Will open browser for OAuth consent

## Sheet Structure

### Sheet Name
`Soil Moisture Sensor Learning Path`

### Columns

| Column | Header | Content | Format |
|--------|--------|---------|--------|
| A | Order | Sequential number | Center-aligned |
| B | Video Title | Hyperlink to video | Left-aligned |
| C | Summary | One-sentence description | Wrapped text |
| D | Category | Fundamental/Intermediate/Advanced | Center-aligned |
| E | Duration | Video length | Center-aligned |

### Formatting
- **Header Row**: Bold, frozen, light gray background
- **Category Colors**:
  - Fundamental: Light green (#d9ead3)
  - Intermediate: Light yellow (#fff2cc)
  - Advanced: Light orange (#fce5cd)
- **Column Widths**: Auto-resize to content

## Example Output

| Order | Video Title | Summary | Category | Duration |
|-------|-------------|---------|----------|----------|
| 1 | [Basic Electronics for Sensors](url) | Covers resistors, capacitors, and op-amps for sensor circuits | Fundamental | 15:22 |
| 2 | [How Capacitive Soil Sensors Work](url) | Explains dielectric measurement principles | Fundamental | 12:45 |
| 3 | [Arduino Soil Moisture Tutorial](url) | Step-by-step ADC reading and calibration | Intermediate | 22:10 |

## Edge Cases

1. **Token Expired**: Script will re-authenticate automatically
2. **Quota Exceeded**: Google Sheets API has 300 requests/min limit
3. **Large Dataset**: Batch writes in groups of 100 rows

## Authentication Flow

```
First run:
1. Script reads credentials.json
2. Opens browser for Google OAuth consent
3. User grants access to Google Sheets
4. Token saved to token.json for future use

Subsequent runs:
1. Script loads token.json
2. Refreshes if expired
3. No browser interaction needed
```

## Learnings
<!-- Update this section as you discover new patterns -->
- Batch updates are more efficient than cell-by-cell writes
- HYPERLINK formula format: `=HYPERLINK("url", "display text")`
