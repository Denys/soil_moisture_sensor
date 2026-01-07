#!/usr/bin/env python3
"""
Analyze and Order YouTube Videos

Scores, filters, and orders videos by relevance to soil moisture sensor technology.
Input: .tmp/playlist_raw.json
Output: .tmp/analyzed_videos.json

Usage:
    python execution/analyze_videos.py
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Paths
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / ".tmp" / "playlist_raw.json"
OUTPUT_FILE = BASE_DIR / ".tmp" / "analyzed_videos.json"

# Minimum score to include video (filters out irrelevant content)
MIN_RELEVANCE_SCORE = 5

# Keyword scoring configuration
KEYWORD_SCORES = {
    # Core sensor terms (highest priority)
    'soil moisture': 15,
    'moisture sensor': 15,
    'soil sensor': 15,
    'teros': 20,
    'ec-5': 15,
    'capacitive sensor': 12,
    'capacitive soil': 15,

    # Sensor principles
    'dielectric': 10,
    'permittivity': 10,
    'volumetric water': 12,
    'water content': 10,
    'fdr': 12,  # Frequency Domain Reflectometry
    'tdr': 12,  # Time Domain Reflectometry

    # Electronics fundamentals
    'arduino': 6,
    'esp32': 7,
    'esp8266': 6,
    'microcontroller': 5,
    'circuit': 4,
    'pcb': 7,
    'op-amp': 8,
    'opamp': 8,
    'operational amplifier': 8,
    'adc': 7,
    'analog to digital': 7,
    'signal conditioning': 9,

    # Practical implementation
    'calibration': 8,
    'accuracy': 6,
    'measurement': 4,
    'tutorial': 3,
    'diy': 4,
    'homemade': 4,
    'build': 3,

    # Communication protocols
    'i2c': 5,
    'spi': 5,
    'uart': 4,
    'modbus': 6,
    'sdi-12': 8,

    # Negative keywords (reduce score)
    'unboxing': -8,
    'review only': -5,
    'watering system': -3,  # Often focuses on pumps, not sensors
    'plant watering': -2,
}

# Category thresholds
CATEGORY_THRESHOLDS = {
    'Fundamental': (0, 30),      # Basic concepts
    'Intermediate': (31, 60),    # Applied knowledge
    'Advanced': (61, 100),       # Expert level
}

# Fundamental topic indicators (for ordering within categories)
FUNDAMENTAL_INDICATORS = [
    'basics', 'basic', 'introduction', 'intro', 'beginner',
    'getting started', 'what is', 'how does', 'explained',
    'fundamentals', 'principle', '101', 'for beginners'
]

ADVANCED_INDICATORS = [
    'advanced', 'professional', 'commercial', 'precision',
    'high accuracy', 'industrial', 'research', 'teardown',
    'reverse engineer', 'optimization', 'calibration curve'
]


def calculate_score(video: Dict) -> Tuple[int, List[str]]:
    """Calculate relevance score for a video based on title and description."""
    title = video.get('title', '').lower()
    description = video.get('description', '').lower()[:1000]  # First 1000 chars

    combined_text = f"{title} {description}"
    score = 0
    matched_keywords = []

    for keyword, points in KEYWORD_SCORES.items():
        # Count occurrences (title matches worth more)
        title_matches = len(re.findall(re.escape(keyword), title))
        desc_matches = len(re.findall(re.escape(keyword), description))

        if title_matches > 0:
            score += points * 2 * title_matches  # Double points for title
            matched_keywords.append(f"{keyword} (title)")
        if desc_matches > 0:
            score += points * desc_matches
            if title_matches == 0:
                matched_keywords.append(keyword)

    # Bonus for longer videos (more in-depth content)
    duration_seconds = video.get('duration_seconds', 0)
    if duration_seconds > 600:  # > 10 minutes
        score += 5
    if duration_seconds > 1200:  # > 20 minutes
        score += 5

    # Slight bonus for popular videos (social proof)
    view_count = video.get('view_count', 0)
    if view_count > 100000:
        score += 3
    elif view_count > 10000:
        score += 2

    return max(0, score), matched_keywords


def determine_category(score: int) -> str:
    """Determine video category based on score."""
    for category, (low, high) in CATEGORY_THRESHOLDS.items():
        if low <= score <= high:
            return category
    return 'Advanced' if score > 100 else 'Fundamental'


def calculate_complexity_order(video: Dict) -> int:
    """Calculate complexity order within category (lower = more fundamental)."""
    title = video.get('title', '').lower()
    description = video.get('description', '').lower()[:500]
    combined = f"{title} {description}"

    order_score = 50  # Base score

    # Decrease for fundamental indicators
    for indicator in FUNDAMENTAL_INDICATORS:
        if indicator in combined:
            order_score -= 10

    # Increase for advanced indicators
    for indicator in ADVANCED_INDICATORS:
        if indicator in combined:
            order_score += 10

    # Longer videos tend to be more advanced
    duration = video.get('duration_seconds', 0)
    order_score += min(20, duration // 300)  # +1 per 5 minutes, max +20

    return order_score


def generate_summary(video: Dict) -> str:
    """Generate a one-sentence summary from title and description."""
    title = video.get('title', '')
    description = video.get('description', '')

    # Clean title
    title = re.sub(r'\s*[\|\-\#]\s*.*$', '', title)  # Remove channel name suffixes
    title = title.strip()

    # Try to extract first meaningful sentence from description
    if description:
        # Get first sentence
        sentences = re.split(r'[.!?]', description)
        first_sentence = sentences[0].strip() if sentences else ''

        # Clean up
        first_sentence = re.sub(r'^(in this video,?|today,?|hey guys,?|welcome,?)\s*', '',
                               first_sentence, flags=re.IGNORECASE)
        first_sentence = first_sentence.strip()

        if 20 < len(first_sentence) < 200:
            # Capitalize first letter
            return first_sentence[0].upper() + first_sentence[1:] if first_sentence else title

    # Fallback: use cleaned title
    return f"Covers {title.lower()}" if title else "Video content"


def analyze_videos(data: Dict) -> Dict:
    """Analyze all videos and return ordered results."""
    videos = data.get('videos', [])
    analyzed = []

    print(f"Analyzing {len(videos)} videos...")

    for video in videos:
        score, keywords = calculate_score(video)

        # Skip low-relevance videos
        if score < MIN_RELEVANCE_SCORE:
            continue

        category = determine_category(score)
        complexity = calculate_complexity_order(video)
        summary = generate_summary(video)

        analyzed.append({
            'video_id': video['video_id'],
            'title': video['title'],
            'url': video['url'],
            'summary': summary,
            'category': category,
            'relevance_score': score,
            'complexity_order': complexity,
            'duration': video.get('duration', 'N/A'),
            'duration_seconds': video.get('duration_seconds', 0),
            'matched_keywords': keywords,
            'view_count': video.get('view_count', 0)
        })

    # Sort by category order, then complexity within category
    category_order = {'Fundamental': 0, 'Intermediate': 1, 'Advanced': 2}
    analyzed.sort(key=lambda x: (
        category_order.get(x['category'], 1),
        x['complexity_order'],
        -x['relevance_score']  # Higher score first within same complexity
    ))

    # Assign final order numbers
    for i, video in enumerate(analyzed, 1):
        video['order'] = i

    # Count by category
    category_counts = {}
    for video in analyzed:
        cat = video['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print(f"\nAnalysis complete:")
    print(f"  Total relevant videos: {len(analyzed)}")
    for cat, count in sorted(category_counts.items(),
                             key=lambda x: category_order.get(x[0], 1)):
        print(f"  - {cat}: {count}")

    return {
        'playlist_id': data.get('playlist_id', ''),
        'playlist_title': data.get('playlist_title', ''),
        'original_count': len(videos),
        'filtered_count': len(analyzed),
        'category_counts': category_counts,
        'videos': analyzed
    }


def main():
    if not INPUT_FILE.exists():
        print(f"Error: Input file not found: {INPUT_FILE}")
        print("Run fetch_playlist.py first.")
        return 1

    # Load raw playlist data
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Analyze videos
    result = analyze_videos(data)

    # Save output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {OUTPUT_FILE}")

    # Print top 5 videos
    print("\nTop 5 recommended videos:")
    for video in result['videos'][:5]:
        print(f"  {video['order']}. [{video['category']}] {video['title'][:60]}")

    return 0


if __name__ == "__main__":
    exit(main())
