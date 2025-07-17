import os
import time
import pysrt
from utils.translation_utils import translate
from utils.paddleocr_utils import SubtitleAreaProcessor
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
paths = config.get('paths', {})

VIDEO_FILE = paths.get('input_video', '../data/input/input_video.mp4')
FRAMES_DIR = paths.get('frames_dir', '../data/cache/frames')
OCR_LANG = 'ch'
OUTPUT_SRT = paths.get('output_srt', '../data/output/output_subtitles.srt')

# ========== 4. 生成 SRT ==========
def save_srt(subs, output_file):
    subs_list = pysrt.SubRipFile()
    for idx, (start, end, text) in enumerate(subs, 1):
        translated = translate(text)
        item = pysrt.SubRipItem(
            index=idx,
            start=pysrt.SubRipTime(seconds=start),
            end=pysrt.SubRipTime(seconds=end),
            text=translated
        )
        subs_list.append(item)
        print(f"[{start}-{end}] {text} -> {translated}")
    subs_list.save(output_file, encoding='utf-8')
    print(f"Subtitles saved to: {output_file}")


