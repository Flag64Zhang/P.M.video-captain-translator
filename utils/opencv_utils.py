import os
import cv2
import numpy as np
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
paths = config.get('paths', {})

#去除重复图片帧
class ImageSimilarityCleaner:
    def __init__(self, dir_path=None, threshold=0.99):
        if dir_path is None:
            dir_path = paths.get('frames_processed_dir', 'data/cache/frames_processed')
        self.dir_path = dir_path
        self.threshold = threshold

    @staticmethod
    def calc_image_similarity(img1, img2):
        hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()
        similarity = np.dot(hist1, hist2) / (np.linalg.norm(hist1) * np.linalg.norm(hist2))
        return similarity

    def remove_similar_images(self):
        files = sorted([f for f in os.listdir(self.dir_path) if f.endswith('.png')])
        prev_img = None
        prev_fname = None
        for fname in files:
            img_path = os.path.join(self.dir_path, fname)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if prev_img is not None:
                sim = self.calc_image_similarity(prev_img, img)
                if sim >= self.threshold:
                    os.remove(img_path)
                    print(f"Removed similar image: {img_path} (similarity={sim:.2f})")
                    continue
            prev_img = img
            prev_fname = fname           

#对图片帧进行预处理
def process_frames(
    input_dir=paths.get('frames_dir', 'data/cache/frames'),
    output_dir=paths.get('frames_processed_dir', 'data/cache/frames_processed'),
    target_width=640,
    target_height=360,
    crop_ratio=1/3
):
    os.makedirs(output_dir, exist_ok=True)
    for fname in sorted(os.listdir(input_dir)):
        if not fname.endswith('.png'):
            continue
        img_path = os.path.join(input_dir, fname)
        img = cv2.imread(img_path)

        # 1. 缩小分辨率
        img = cv2.resize(img, (target_width, target_height))

        # 2. 裁剪字幕区域（如底部 crop_ratio 区域）
        h, w = img.shape[:2]
        crop_top = int(h * (1 - crop_ratio))
        crop_img = img[crop_top:h, 0:w]

        # 3. 转灰度
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

        # 4. 提升对比度（CLAHE）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        # 5. 二值化（Otsu）
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # # 5. 自适应阈值二值化
        #     binary = cv2.adaptiveThreshold(
        #         enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #         cv2.THRESH_BINARY, 15, 10
        #     )

        #     # 6. 形态学操作去除小噪点
        #     kernel = np.ones((3, 3), np.uint8)
        #     clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

        #     # 7. 可选：只保留最大连通域（字幕块）
        #     contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #     mask = np.zeros_like(clean)
        #     if contours:
        #         c = max(contours, key=cv2.contourArea)
        #         cv2.drawContours(mask, [c], -1, 255, -1)
        #         clean = cv2.bitwise_and(clean, mask)

        # 6. 保存
        out_path = os.path.join(output_dir, fname)
        cv2.imwrite(out_path, binary)
        print(f"Processed and saved: {out_path}")

# 启发式检测（底部高亮区域）
def detect_subtitle_area_heuristic(frames_dir, sample_step=1, crop_ratio=1/6, min_area=500):
    """
    启发式检测视频帧图片中的字幕区域（底部高亮区域法）。
    返回最大包围矩形 (x_min, y_min, x_max, y_max)，若未检测到返回None。
    """
    print("尝试启发式检测字幕区域...")
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    all_boxes = []
    for idx, frame in enumerate(frames):
        if idx % sample_step != 0:
            continue
        img_path = os.path.join(frames_dir, frame)
        img = cv2.imread(img_path)
        h, w = img.shape[:2]
        crop_top = int(h * (1 - crop_ratio))
        roi = img[crop_top:h, 0:w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > min_area]
        if boxes:
            x, y, bw, bh = max(boxes, key=lambda b: b[2]*b[3])
            all_boxes.append([x, crop_top + y, x + bw, crop_top + y + bh])
    if all_boxes:
        all_boxes = np.array(all_boxes)
        x_min, y_min = np.min(all_boxes[:, 0]), np.min(all_boxes[:, 1])
        x_max, y_max = np.max(all_boxes[:, 2]), np.max(all_boxes[:, 3])
        print(f"[启发式] Detected subtitle area: x={x_min}, y={y_min}, w={x_max-x_min}, h={y_max-y_min}")
        return int(x_min), int(y_min), int(x_max), int(y_max)
    else:
        print("[启发式] 未检测到字幕区域")
        return None