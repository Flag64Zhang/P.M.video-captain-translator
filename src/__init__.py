# src/__init__.py
from utils.opencv_utils import process_frames
import similar
from .similar import is_similar, build_translation_dict, save_srt as save_srt_fuzzy, merge_duplicate_subtitles_fuzzy, get_translation
from .subtitle_translator import save_srt, get_video_resolution, remove_subtitles_area, burn_subtitles