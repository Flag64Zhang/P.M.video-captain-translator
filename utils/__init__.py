# utils/__init__.py

from .ffmpeg_utils import extract_frames, get_video_resolution, remove_subtitles_area, burn_subtitles
from .opencv_utils import process_frames, detect_subtitle_area_heuristic
from .paddleocr_utils import SubtitleOcrProcessor, SubtitleAreaProcessor,BigModelOcrProcessor
from .translation_utils import translate
