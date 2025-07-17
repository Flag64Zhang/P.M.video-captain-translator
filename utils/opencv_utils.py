import os
import cv2
import numpy as np

def process_frames(
    input_dir="frames",
    output_dir="frames_processed",
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