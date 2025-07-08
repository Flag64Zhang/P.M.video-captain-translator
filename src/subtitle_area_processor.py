import os
import cv2
import numpy as np
from paddleocr import PaddleOCR

def detect_subtitle_area(frames_dir, sample_step=1):
    """
    用OCR自动检测所有帧的字幕区域，返回最大包围矩形 (x_min, y_min, x_max, y_max)
    """
    ocr = PaddleOCR(use_textline_orientation=True, lang='ch')
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    all_boxes = []
    for idx, frame in enumerate(frames):
        if idx % sample_step != 0:
            continue  # 采样加速
        img_path = os.path.join(frames_dir, frame)
        ocr_result = ocr.predict(img_path)
        if ocr_result and isinstance(ocr_result, list):
            result_dict = ocr_result[0]
            rec_boxes = result_dict.get('rec_boxes', [])
            for box in rec_boxes:
                # box: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
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

def crop_subtitle_area(frames_dir, output_dir, area):
    """
    批量裁剪字幕区域
    """
    os.makedirs(output_dir, exist_ok=True)
    x_min, y_min, x_max, y_max = area
    for fname in sorted(os.listdir(frames_dir)):
        if not fname.endswith('.png'):
            continue
        img_path = os.path.join(frames_dir, fname)
        img = cv2.imread(img_path)
        crop_img = img[y_min:y_max, x_min:x_max]
        out_path = os.path.join(output_dir, fname)
        cv2.imwrite(out_path, crop_img)
        print(f"Cropped and saved: {out_path}")

def blur_subtitle_area(frames_dir, output_dir, area, method='gaussian', ksize=31):
    """
    只对字幕区域做模糊/马赛克，叠加回原图
    method: 'gaussian' or 'mosaic'
    ksize: 模糊核大小或马赛克块大小
    """
    os.makedirs(output_dir, exist_ok=True)
    x_min, y_min, x_max, y_max = area
    for fname in sorted(os.listdir(frames_dir)):
        if not fname.endswith('.png'):
            continue
        img_path = os.path.join(frames_dir, fname)
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

if __name__ == "__main__":
    # 配置参数
    FRAMES_DIR = "frames"  # 原始帧目录
    CROPPED_DIR = "frames_cropped"  # 裁剪后帧目录
    BLURRED_DIR = "frames_blurred"  # 模糊后帧目录

    # 步骤1：自动检测字幕区域
    area = detect_subtitle_area(FRAMES_DIR, sample_step=1)  # 可调大sample_step加速

    # 步骤2：批量裁剪字幕区域
    crop_subtitle_area(FRAMES_DIR, CROPPED_DIR, area)

    # 步骤3：只对字幕区域做模糊/马赛克
    blur_subtitle_area(FRAMES_DIR, BLURRED_DIR, area, method='gaussian', ksize=31)
    # 或用马赛克
    # blur_subtitle_area(FRAMES_DIR, BLURRED_DIR, area, method='mosaic', ksize=20)