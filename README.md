<div align="center"><img src="https://perseverantmind.top/img/logo.png" style="width:80px; height:auto;" alt="Project Logo"><h1>P.M.video-captain-translator</h1>An automated tool for local video subtitle translation<br><br></div>

Language: [中文](https://github.com/Flag64Zhang/P.M.video-captain-translator/blob/master/README_zh.md) | [EN](https://github.com/Flag64Zhang/P.M.video-captain-translator/blob/master/README.md)

---

An automated tool for extracting, translating, and re-embedding video subtitles. It supports extracting Chinese subtitles from videos, translating them into English, and re-embedding them to achieve localization. This project is still under development, and no release version is available yet. Thank you for your understanding.

## Project Overview

This project aims to automate the process of subtitle extraction, translation, and re-embedding. Key features include:

- Extract Chinese subtitles from video frames
- Translate extracted subtitles into English
- Mask original subtitle areas and embed translated subtitles
- Support multiple OCR and translation services configurable via settings

## Requirements

- Python 3.8+
- Dependencies: See `requirements.txt`
- Additional Tool: ffmpeg (for frame extraction and subtitle embedding)

## Installation Steps

1.Clone the repository

```bash
git clone https://github.com/Flag64Zhang/P.M.video-captain-translator.git
cd P.M.video-captain-translator
```

2.Install dependencies

```bash
pip install -r requirements.txt
```

3.Install ffmpeg

- Download ffmpeg for your system and add it to your PATH
- Verify installation: `ffmpeg -version`

## Directory Structure

```plaintext
P.M.video-captain-translator/
├── config/                 # Configuration files
│   └── config.yaml         # Project settings (paths, parameters)
├── data/                   # Data directory
│   ├── input/              # Input videos
│   ├── output/             # Processed videos
│   └── cache/              # Temporary files (frames, subtitles)
│       ├── frames/         # Extracted frames
│       └── frames_processed/ # Preprocessed frames
├── src/                    # Source code
│   ├── __init__.py
│   ├── similar.py          # Subtitle similarity checker
│   └── subtitle_translator.py # Core translation logic
├── tests/                  # Test suite
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── ffmpeg_utils.py     # ffmpeg wrapper
│   ├── opencv_utils.py     # Image processing
│   └── paddleocr_utils.py  # OCR engine wrapper
├── .gitignore              # Git ignore rules
├── flowchart.vsdx          # Project flowchart
├── main.py                 # Program entry point
├── README.md               # This documentation
└── requirements.txt        # Dependency list
```

## Usage

### 1. Configure the project

Edit `config/config.yaml` to set input/output paths and parameters:

```yaml
paths:
  input_video: "data/input/input_video.mp4"  # Input video path
  output_video: "data/output/output_video.mp4"  # Output video path
  frames_dir: "data/cache/frames"  # Frame cache directory
  frames_processed_dir: "data/cache/frames_processed"  # Processed frames
  srt_chinese: "data/cache/chinese_subtitles.srt"  # Chinese subtitles
  srt_english: "data/cache/english_subtitles.srt"  # English subtitles

ocr:
  lang: "ch"  # OCR language
  threshold: 0.8  # Subtitle similarity threshold

translation:
  api: "baidu"  # Translation API (supports baidu, google, etc.)
  appid: "your_appid"  # API credentials
  secret: "your_secret"  # API credentials
```

### 2. Run the program

```bash
python main.py
```

The program will automatically:

1. Extract and preprocess video frames
2. Recognize and extract Chinese subtitles
3. Translate subtitles to English
4. Mask original subtitle areas
5. Embed translated subtitles and generate output video

## Core Features

### 1. Frame Extraction & Preprocessing

- Extract frames from video using ffmpeg
- Deduplicate frames to retain key moments
- Preprocess frames (grayscale, binarization) for better OCR accuracy

### 2. Subtitle Extraction (OCR)

- Use PaddleOCR to recognize Chinese subtitles
- Localize subtitle regions and extract text
- Deduplicate and merge results into SRT format

### 3. Subtitle Translation

- Support multiple translation APIs (Baidu, Google, etc.)
- Configurable translation service via settings
- Generate English SRT files

### 4. Subtitle Re-embedding

- Mask original subtitle areas using ffmpeg
- Embed translated subtitles while preserving video quality and audio

## Configuration Guide

| Configuration Item | Description                   | Options                                   |
| ------------------ | ----------------------------- | ----------------------------------------- |
| paths.input_video  | Input video path              | Local file path                           |
| paths.output_video | Output video path             | Output file path                          |
| ocr.lang           | OCR language                  | "ch" (Chinese), "en" (English), etc.      |
| ocr.threshold      | Subtitle similarity threshold | 0.0-1.0 (higher = stricter deduplication) |
| translation.api    | Translation API               | "baidu", "google", "deepl", etc.          |
| translation.appid  | API credentials               | App ID for selected service               |
| translation.secret | API credentials               | Secret key for selected service           |

## Translation Service Comparison

| Translation Service   | Accuracy (Reference) | Token Cost (per 100 chars) | Characteristics                    |
| --------------------- | -------------------- | -------------------------- | ---------------------------------- |
| Baidu Translate API   | 92%                  | ~150 tokens                | Strong Chinese context handling    |
| Google Translate API  | 90%                  | ~160 tokens                | Wide language support              |
| DeepL Translate API   | 95%                  | ~200 tokens                | High-quality literary translation  |
| Tencent Translate API | 91%                  | ~140 tokens                | Fast response, ideal for real-time |

*Accuracy based on manual evaluation of 1000 test sentences. Token costs are approximate.*

## Optimization Tips

1. **Subtitle Extraction Optimization**:
   - Use frame interval sampling to reduce redundant processing
   - Apply targeted preprocessing to subtitle regions
   - Correct OCR results using contextual information
2. **Translation Optimization**:
   - Create custom dictionaries for domain-specific terminology
   - Use batch translation to minimize API calls
   - Split long sentences for better translation flow

## FAQs

1. **Q: Extracted subtitles contain garbled text or errors?**
   A: Check OCR model installation, adjust `ocr.threshold`, or enhance frame preprocessing.
2. **Q: Translation results are inaccurate?**
   A: Try switching translation APIs or add custom dictionaries in the config.
3. **Q: Video quality degrades after subtitle embedding?**
   A: Adjust video output parameters in `config.yaml` to increase bitrate.

## Project Flowchart

The complete process from input to output is detailed in `flowchart.vsdx`. Everyone is welcome to join the testing and development!

## License

This project is licensed under the MIT License. See the LICENSE file for details.