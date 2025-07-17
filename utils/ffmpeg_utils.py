# utils/ffmpeg_utils.py
# 封装 ffmpeg 相关操作
import ffmpeg
import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
paths = config.get('paths', {})

VIDEO_FILE = paths.get('input_video', '../data/input/input_video.mp4')
OUTPUT_FILE = paths.get('output_video', '../data/output/output_video.mp4')
FRAMES_DIR = paths.get('frames_dir', 'data/cache/frames')
# ========== 1. 提取视频帧 ==========
def extract_frames(video_file=VIDEO_FILE, output_dir=FRAMES_DIR, interval=1):
    os.makedirs(output_dir, exist_ok=True)
    (
        ffmpeg
        .input(video_file)
        .filter('fps', fps=f'1/{interval}')  # 每 interval 秒采一帧
        .output(f'{output_dir}/frame_%04d.png')
        .run(overwrite_output=True)
    )
    print(f"Frames saved to: {output_dir}")

# ========== 5. 处理原视频字幕 ==========
def get_video_resolution(video_file):
    probe = ffmpeg.probe(video_file)
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    return width, height

def remove_subtitles_area(video_file, output_file, area=None):
    width, height = get_video_resolution(video_file)
    print(f"video size: {width}x{height}, area: {area}")
    if area is not None:
        x_min, y_min, x_max, y_max = area
        crop_w = x_max - x_min
        crop_h = y_max - y_min
        crop_x = x_min
        crop_y = y_min
        filter_complex = (
            f"[0:v]split=2[bg][fg];"
            f"[fg]crop={crop_w}:{crop_h}:{crop_x}:{crop_y},boxblur=10:1[blur];"
            f"[bg][blur]overlay={crop_x}:{crop_y}"
        )
        print("ffmpeg filter_complex:", filter_complex)
    else:
        sub_h = height // 6
        sub_y = height - sub_h
        filter_complex = (
            f"[0:v]split=2[bg][fg];"
            f"[fg]crop={width}:{sub_h}:0:{sub_y},boxblur=10:1[blur];"
            f"[bg][blur]overlay=0:{sub_y}"
        )
    (
    ffmpeg
    .input(video_file)
    .output(
        output_file,
        vf=filter_complex,
        vcodec='libx264',
        acodec='copy'
        )
    .run(overwrite_output=True)
    )
    print(f"Video with subtitle area blurred saved to: {output_file}")

# ========== 6. 给视频加字幕（外挂） ==========
def burn_subtitles(process_file=paths.get('process_video', '../data/output/output_video.mp4'), srt_file=paths.get('output_srt', 'data/output/output_subtitles.srt'), output_file=paths.get('output_video', 'data/output/output_video.mp4')):
    (
        ffmpeg
        .input(process_file)
        .output(output_file, vf=f"subtitles={srt_file}")
        .run(overwrite_output=True)
    )
    print(f"Final video saved to: {output_file}")