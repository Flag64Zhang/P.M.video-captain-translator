import os
import time
import pysrt

# ========== 配置 ==========
VIDEO_FILE = "../data/input/input_video.mp4"
FRAMES_DIR = "frames"
OCR_LANG = 'ch'
OUTPUT_SRT = "output_subtitles.srt"

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

# ========== 5. 处理原视频字幕 ==========
def get_video_resolution(video_file):
    probe = ffmpeg.probe(video_file)
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    return width, height

def remove_subtitles_area(video_file, process_file='process_video.mp4'):
    width, height = get_video_resolution(video_file)
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
            process_file,
            vf=filter_complex,
            vcodec='libx264',
            acodec='copy'
        )
        .run(overwrite_output=True)
    )
    print(f"Video with subtitle area blurred saved to: {process_file}")

# ========== 6. 给视频加字幕（外挂） ==========
def burn_subtitles(process_file, srt_file, output_file="output_video.mp4"):
    (
        ffmpeg
        .input(process_file)
        .output(output_file, vf=f"subtitles={srt_file}")
        .run(overwrite_output=True)
    )
    print(f"Final video saved to: {output_file}")


# ========== 入口 ==========
if __name__ == "__main__":
    t0 = time.time()
    # 先处理帧图片
    opencv_utils.process_frames(
        input_dir="frames",
        output_dir="frames_processed",
        target_width=640,
        target_height=360,
        crop_ratio=1/3
    )
    # 后续流程用 frames_processed 作为 OCR 输入
    extract_frames(VIDEO_FILE, FRAMES_DIR, interval=1)
    ocr_results = ocr_frames("frames_processed")  # 用处理后的图片
    merged_results = merge_duplicate_subtitles(ocr_results)
    save_srt(merged_results, OUTPUT_SRT)
    remove_subtitles_area(VIDEO_FILE, "../data/output/process_video.mp4")
    burn_subtitles("../data/output/process_video.mp4", OUTPUT_SRT, "data/output/output_video.mp4")
    print(f"Done in {time.time() - t0:.2f}s")
