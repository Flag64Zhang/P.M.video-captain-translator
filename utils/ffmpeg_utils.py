# utils/ffmpeg_utils.py
# 封装 ffmpeg 相关操作
import ffmpeg
import os
# ========== 配置 ==========
VIDEO_FILE = "../data/input/input_video.mp4"
FRAMES_DIR = "frames"
# ========== 1. 提取视频帧 ==========
def extract_frames(video_file, output_dir, interval=1):
    os.makedirs(output_dir, exist_ok=True)
    (
        ffmpeg
        .input(video_file)
        .filter('fps', fps=f'1/{interval}')  # 每 interval 秒采一帧
        .output(f'{output_dir}/frame_%04d.png')
        .run(overwrite_output=True)
    )
    print(f"Frames saved to: {output_dir}")