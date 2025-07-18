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
import sys
import glob

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def clean_dir(dir_path):
    for f in glob.glob(os.path.join(dir_path, '*')):
        try:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                import shutil
                shutil.rmtree(f)
        except Exception as e:
            print(f"清理文件失败: {f}，原因: {e}")

def run_pipeline(input_video, output_video, ocr_method, log_callback=print):
    """
    主处理流程，支持不同 OCR 方式。
    ocr_method: 'paddleocr' 或 'bigmodel'
    log_callback: 日志输出函数，默认为 print
    """
     # 自动清理输出目录
    clean_dir('data/output')
    log_callback('输出目录已清理。')

    # 自动补全输出文件名后缀
    if not output_video.lower().endswith('.mp4'):
        output_video += '.mp4'
    config = load_config('config/config.yaml')
    paths = config.get('paths', {})
    frames_dir = paths.get('frames_dir', 'data/cache/frames')
    frames_processed_dir = paths.get('frames_processed_dir', 'data/cache/frames_processed')
    output_srt = paths.get('output_srt', 'data/output/output_subtitles.srt')
    input_dir = 'data/cache/frames'
    output_dir = 'data/cache/frames_blurred'

    # 3. ffmpeg提取视频帧（原始帧）
    log_callback('提取视频帧...')
    extract_frames(video_file=input_video, output_dir=frames_dir, interval=1)

    # 5. opencv进行预处理（如缩放、裁剪、二值化等，输出到frames_processed_dir）
    log_callback('预处理帧图片...')
    process_frames(input_dir=frames_dir, output_dir=frames_processed_dir)

    # 5.5 检测并处理字幕区域
    log_callback('检测并处理字幕区域...')
    area_processor = SubtitleAreaProcessor(frames_dir=frames_processed_dir, sample_step=1)
    area = area_processor.detect_subtitle_area()
    log_callback(f'检测到的字幕区域: {area}')
    remove_subtitles_area(
        video_file=input_video,
        output_file=output_video,
        area=area
    )

    # 6. OCR字幕识别与合并（对预处理后的帧）
    log_callback('OCR字幕识别与合并...')
    if ocr_method == 'paddleocr':
        ocr_processor = SubtitleOcrProcessor(lang='ch')
        ocr_results = ocr_processor.ocr_frames(frames_processed_dir)
        merged_results = SubtitleOcrProcessor.merge_duplicate_subtitles(ocr_results)
    elif ocr_method == 'bigmodel':
        try:
            from utils.paddleocr_utils import BigModelOcrProcessor
            ocr_processor = BigModelOcrProcessor()
            ocr_results = ocr_processor.ocr_frames(frames_processed_dir)
            merged_results = ocr_processor.merge_duplicate_subtitles(ocr_results)
        except ImportError:
            log_callback('大模型 OCR 错误！')
            raise NotImplementedError('大模型 OCR 错误')
    else:
        log_callback(f'OCR方式 {ocr_method} 不支持')
        raise ValueError(f'不支持的OCR方式: {ocr_method}')
    log_callback(f'合并后的字幕：{merged_results}')

    # 7. 翻译OCR识别后的字幕并保存为SRT
    log_callback('翻译字幕并保存为SRT...')
    srt_generator.save_srt(merged_results, output_srt)
    log_callback(f"SRT字幕已保存到: {output_srt}")

    # 8. 用ffmpeg外挂字幕到视频
    log_callback('外挂字幕到视频...')
    temp_output = output_video.replace('.mp4', '_temp.mp4')
    burn_subtitles(process_file=output_video, srt_file=output_srt, output_file=temp_output)
    os.replace(temp_output, output_video)
    log_callback(f"处理完成，输出文件：{output_video}")

    # 9. 自动清理缓存目录
    clean_dir('data/cache/frames')
    clean_dir('data/cache/frames_processed')
    log_callback('缓存目录已清理。')

def main():
    # 1. 加载配置
    config = load_config('config/config.yaml')
    paths = config.get('paths', {})
    input_video = paths.get('input_video', 'data/input/input_video.mp4')
    output_video = paths.get('output_video', 'data/output/output_video.mp4')
    ocr_method = 'paddleocr'  # 命令行默认用 paddleocr
    run_pipeline(input_video, output_video, ocr_method)

if __name__ == "__main__":
    main()
