# main.py

import yaml
from utils.ffmpeg_utils import extract_frames,remove_subtitles_area
from utils.opencv_utils import process_frames, ImageSimilarityCleaner
from utils.paddleocr_utils import SubtitleOcrProcessor, SubtitleAreaProcessor
from src.similar import SubtitleSimilarityHelper
from utils.translation_utils import translate
import os
from utils.ffmpeg_utils import burn_subtitles
import src.srt_generator as srt_generator

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    # 1. 加载配置
    config = load_config('config/config.yaml')
    paths = config.get('paths', {})
    
    # 2. 设置输入输出路径
    input_video = paths.get('input_video', 'data/input/input_video.mp4')
    output_video = paths.get('output_video', 'data/output/output_video.mp4')
    frames_dir = paths.get('frames_dir', 'data/cache/frames')
    frames_processed_dir = paths.get('frames_processed_dir', 'data/cache/frames_processed')
    output_srt = paths.get('output_srt', 'data/output/output_subtitles.srt')
    input_dir = 'data/cache/frames'#模糊函数要处理的图片目录
    output_dir = 'data/cache/frames_blurred'#模糊函数结果输出目录

    # 3. ffmpeg提取视频帧（原始帧）
    print('提取视频帧...')
    extract_frames(video_file=input_video, output_dir=frames_dir, interval=1)

    # # 4. opencv进行帧去重（原始帧）
    # print('去除重复帧...')
    # cleaner = ImageSimilarityCleaner(dir_path=frames_dir, threshold=0.8)
    # cleaner.remove_similar_images()

    # 5. opencv进行预处理（如缩放、裁剪、二值化等，输出到frames_processed_dir）
    print('预处理帧图片...')
    process_frames(input_dir=frames_dir, output_dir=frames_processed_dir)

    # 5.5 检测并处理字幕区域
    print('检测并处理字幕区域...')
    area_processor = SubtitleAreaProcessor(frames_dir=frames_processed_dir, sample_step=1)
    area = area_processor.detect_subtitle_area()
    print(f'检测到的字幕区域: {area}')
    # 模糊字幕区域
    remove_subtitles_area(
    video_file=input_video,
    output_file=output_video,
    area=area  # 传入你检测到的字幕区域
)
    
    # # 可选：裁剪字幕区域
    # area_processor.crop_subtitle_area(area=area)
    # # 可选：模糊字幕区域
    # SubtitleAreaProcessor.blur_subtitle_area(
    # input_dir=input_dir,
    # output_dir=output_dir,
    # method='gaussian',  # 或 'mosaic'
    # ksize=31
    # )

    # 6. OCR字幕识别与合并（对预处理后的帧）
    print('OCR字幕识别与合并...')
    ocr_processor = SubtitleOcrProcessor(lang='ch')
    ocr_results = ocr_processor.ocr_frames(frames_processed_dir)
    merged_results = SubtitleOcrProcessor.merge_duplicate_subtitles(ocr_results)
    print('合并后的字幕：', merged_results)

    # # 7. 相似度合并、翻译字典构建和SRT保存
    # print('相似度合并、翻译字典构建和SRT保存...')
    # fuzzy_merged = SubtitleSimilarityHelper.merge_duplicate_subtitles_fuzzy(merged_results, threshold=0.8)
    # translation_dict = SubtitleSimilarityHelper.build_translation_dict(fuzzy_merged, translate)
    # # SubtitleSimilarityHelper.save_srt(fuzzy_merged, output_srt, translation_dict) # This line is removed

    # 7. 翻译OCR识别后的字幕并保存为SRT
    print('翻译字幕并保存为SRT...')
    srt_generator.save_srt(merged_results, output_srt)
    print(f"SRT字幕已保存到: {output_srt}")

    # 8. 用ffmpeg外挂字幕到视频
    print('外挂字幕到视频...')
    burn_subtitles(process_file=input_video, srt_file=output_srt, output_file=output_video)
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
