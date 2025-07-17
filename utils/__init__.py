# utils/__init__.py

from .ffmpeg_utils import extract_frames, get_video_resolution, remove_subtitles_area, burn_subtitles
from .opencv_utils import process_frames
from .paddleocr_utils import SubtitleOcrProcessor, SubtitleAreaProcessor
from .translation_utils import translate
