from paddleocr import PaddleOCR
import os

# ========== 配置 ==========
OCR_LANG = 'ch'
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