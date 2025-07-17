# utils/paddleocr_utils.py
from paddleocr import PaddleOCR
import os
import os
import cv2
import numpy as np
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
paths = config.get('paths', {})

# ========== 配置 ==========
OCR_LANG = 'ch'
FRAMES_DIR = "frames"  # 原始帧目录
CROPPED_DIR = "frames_cropped"  # 裁剪后帧目录
BLURRED_DIR = "frames_blurred"  # 模糊后帧目录
# ========== 2. 对帧做 OCR ==========
class SubtitleOcrProcessor:
    def __init__(self, lang='ch'):
        self.ocr = PaddleOCR(use_textline_orientation=True, lang=lang)

    def ocr_frames(self, frames_dir):
        results = []
        frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
        for idx, frame in enumerate(frames):
            img_path = os.path.join(frames_dir, frame)
            ocr_result = self.ocr.predict(img_path)
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

    @staticmethod
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

#对视频帧图片中的字幕区域进行自动检测、裁剪和模糊处理
class SubtitleAreaProcessor:
    def __init__(self, frames_dir, sample_step=1):
        self.frames_dir = frames_dir
        self.sample_step = sample_step
        self.ocr = PaddleOCR(use_textline_orientation=True, lang='ch')

    def detect_subtitle_area(self):
        """
        用OCR自动检测所有帧的字幕区域，返回最大包围矩形 (x_min, y_min, x_max, y_max)
        """
        frames = sorted([f for f in os.listdir(self.frames_dir) if f.endswith('.png')])
        all_boxes = []
        for idx, frame in enumerate(frames):
            if idx % self.sample_step != 0:
                continue  # 采样加速
            img_path = os.path.join(self.frames_dir, frame)
            ocr_result = self.ocr.predict(img_path)
            if ocr_result and isinstance(ocr_result, list):
                result_dict = ocr_result[0]
                rec_boxes = result_dict.get('rec_boxes', [])
                for box in rec_boxes:
                    xs = [pt[0] for pt in box]
                    ys = [pt[1] for pt in box]
                    all_boxes.append([min(xs), min(ys), max(xs), max(ys)])
        if not all_boxes:
            raise ValueError("No subtitle boxes detected!")
        all_boxes = np.array(all_boxes)
        x_min, y_min = np.min(all_boxes[:, 0]), np.min(all_boxes[:, 1])
        x_max, y_max = np.max(all_boxes[:, 2]), np.max(all_boxes[:, 3])
        print(f"Detected subtitle area: x={x_min}, y={y_min}, w={x_max-x_min}, h={y_max-y_min}")
        return int(x_min), int(y_min), int(x_max), int(y_max)

    def crop_subtitle_area(self, output_dir=None, area=None):
        if output_dir is None:
            output_dir = paths.get('frames_cropped_dir', 'data/cache/frames_cropped')
        os.makedirs(output_dir, exist_ok=True)
        x_min, y_min, x_max, y_max = area
        for fname in sorted(os.listdir(self.frames_dir)):
            if not fname.endswith('.png'):
                continue
            img_path = os.path.join(self.frames_dir, fname)
            img = cv2.imread(img_path)
            crop_img = img[y_min:y_max, x_min:x_max]
            out_path = os.path.join(output_dir, fname)
            cv2.imwrite(out_path, crop_img)
            print(f"Cropped and saved: {out_path}")

    def blur_subtitle_area(self, output_dir=None, area=None, method='gaussian', ksize=31):
        if output_dir is None:
            output_dir = paths.get('frames_blurred_dir', 'data/cache/frames_blurred')
        os.makedirs(output_dir, exist_ok=True)
        x_min, y_min, x_max, y_max = area
        for fname in sorted(os.listdir(self.frames_dir)):
            if not fname.endswith('.png'):
                continue
            img_path = os.path.join(self.frames_dir, fname)
            img = cv2.imread(img_path)
            roi = img[y_min:y_max, x_min:x_max]
            if method == 'gaussian':
                blur = cv2.GaussianBlur(roi, (ksize|1, ksize|1), 0)
            elif method == 'mosaic':
                h, w = roi.shape[:2]
                blur = cv2.resize(roi, (max(1, w//ksize), max(1, h//ksize)), interpolation=cv2.INTER_LINEAR)
                blur = cv2.resize(blur, (w, h), interpolation=cv2.INTER_NEAREST)
            else:
                raise ValueError("method must be 'gaussian' or 'mosaic'")
            img[y_min:y_max, x_min:x_max] = blur
            out_path = os.path.join(output_dir, fname)
            cv2.imwrite(out_path, img)
            print(f"Blurred and saved: {out_path}")

    @staticmethod
    def get_default_processor(frames_dir, sample_step=1):
        """
        获取默认参数的SubtitleAreaProcessor实例，便于跨模块调用。
        """
        return SubtitleAreaProcessor(frames_dir, sample_step)