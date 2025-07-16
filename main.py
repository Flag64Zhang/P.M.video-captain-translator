# main.py

import os
import yaml

from src.opencv_processors import process_video  # 假设有此函数
from src.similar import calc_similarity         # 示例：可用于相似度判断
from src.subtitle_area_processor import SubtitleAreaDetector
from src.subtitle_translator import SubtitleTranslator

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    # 1. 加载配置
    config = load_config('config/config.yaml')
    
    # 2. 设置输入输出路径
    input_video = config['input_video'] if 'input_video' in config else 'data/input/input_video.mp4'
    output_video = config['output_video'] if 'output_video' in config else 'data/output/output_video.mp4'
    
    # 3. 处理流程示例
    # 3.1 提取字幕区域
    detector = SubtitleAreaDetector()
    subtitle_area = detector.detect(input_video)
    
    # 3.2 翻译字幕
    translator = SubtitleTranslator()
    translator.process(input_video, subtitle_area, output_video)
    
    print(f"处理完成，输出文件：{output_video}")

if __name__ == "__main__":
    main()
# # ========== 入口 ==========
# if __name__ == "__main__":
#     t0 = time.time()
#     # 先处理帧图片
#     opencv_processors.process_frames(
#         input_dir="frames",
#         output_dir="frames_processed",
#         target_width=640,
#         target_height=360,
#         crop_ratio=1/3
#     )
#     # 后续流程用 frames_processed 作为 OCR 输入
#     extract_frames(VIDEO_FILE, FRAMES_DIR, interval=1)
#     ocr_results = ocr_frames("frames_processed")  # 用处理后的图片
#     merged_results = merge_duplicate_subtitles(ocr_results)
#     save_srt(merged_results, OUTPUT_SRT)
#     remove_subtitles_area(VIDEO_FILE, "../data/output/process_video.mp4")
#     burn_subtitles("../data/output/process_video.mp4", OUTPUT_SRT, "data/output/output_video.mp4")
#     print(f"Done in {time.time() - t0:.2f}s")
