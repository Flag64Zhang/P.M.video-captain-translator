import os
import ffmpeg
import time
from paddleocr import PaddleOCR
from openai import OpenAI
import pysrt
import opencv_processors

# ========== 配置 ==========
VIDEO_FILE = "input_video.mp4"
FRAMES_DIR = "frames"
OCR_LANG = 'ch'
OUTPUT_SRT = "output_subtitles.srt"
client = OpenAI(
    api_key="HIDE",
    base_url="https://api.deepseek.com/v1"
)

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

# ========== 2. 对帧做 OCR ==========
def ocr_frames(frames_dir):
    ocr = PaddleOCR(use_textline_orientation=True, lang='ch')
    results = []
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    for idx, frame in enumerate(frames):
        img_path = os.path.join(frames_dir, frame)
        ocr_result = ocr.predict(img_path)
        text = ""
        if ocr_result and isinstance(ocr_result, list):
            result_dict = ocr_result[0]
            rec_texts = result_dict.get('rec_texts', [])
            text = " ".join(rec_texts).strip()
        if text:
            start_time = idx
            end_time = idx + 1
            results.append((start_time, end_time, text))
        print(f"OCR result: {text}")
    return results
    """
    合并连续重复的字幕
    subs: List of (start, end, text)
    返回：合并后的 List
    """
def merge_duplicate_subtitles(subs):
    if not subs:
        return []
    merged = []
    last_start, last_end, last_text = subs[0]
    for start, end, text in subs[1:]:
        if text == last_text:
            # 连续相同，延长结束时间
            last_end = end
        else:
            merged.append((last_start, last_end, last_text))
            last_start, last_end, last_text = start, end, text
    merged.append((last_start, last_end, last_text))
    return merged

# ========== 3. 翻译 ==========
def translate(text):
    prompt = (
        f"Translate the following Chinese subtitle into fluent, concise English suitable for video subtitles. "
        f"Only output the English translation itself, with no explanation, notes, or extra content:\n{text}"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

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
    opencv_processors.process_frames(
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
    remove_subtitles_area(VIDEO_FILE, "process_video.mp4")
    burn_subtitles("process_video.mp4", OUTPUT_SRT, "output_video.mp4")
    print(f"Done in {time.time() - t0:.2f}s")
