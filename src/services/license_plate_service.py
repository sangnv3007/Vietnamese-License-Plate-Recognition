import cv2
import numpy as np
import re
import os
import time
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from paddleocr import PaddleOCR
from src.utils.image_utils import ImageUtils

@dataclass
class LicensePlateResult:
    text_plate: str
    confidence: float
    image_name: str
    error_code: int
    error_message: str

class LicensePlateDetector:
    def __init__(self, weights_path: str, config_path: str, paddle_model_dir: str):
        """Khởi tạo model nhận diện biển số xe"""
        self.net = cv2.dnn.readNet(weights_path, config_path)
        self.ocr = PaddleOCR(
            det_model_dir=f'{paddle_model_dir}/ch_PP-OCRv3_det_infer/',
            rec_model_dir=f'{paddle_model_dir}/ch_ppocr_server_v2.0_rec_infer/',
            rec_char_dict_path=f'{paddle_model_dir}/en_dict.txt',
            use_angle_cls=False
        )
        self.conf_threshold = 0.8
        self.nms_threshold = 0.4
        self.input_size = (416, 416)

    def _detect_license_plate(self, image: np.ndarray) -> Tuple[List, List, np.ndarray]:
        """Phát hiện vị trí biển số xe trong ảnh"""
        height, width = image.shape[:2]
        blob = cv2.dnn.blobFromImage(
            image, 1/255.0, self.input_size, (0, 0, 0), True, crop=False)
        
        self.net.setInput(blob)
        outs = self.net.forward(ImageUtils.get_output_layers(self.net))
        
        boxes = []
        confidences = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.conf_threshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = center_x - w // 2
                    y = center_y - h // 2
                    
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
        
        indices = cv2.dnn.NMSBoxes(
            boxes, confidences, self.conf_threshold, self.nms_threshold)
            
        return indices, boxes, image

    def _is_valid_plate_number(self, text: str) -> bool:
        """Kiểm tra định dạng biển số xe"""
        patterns = [
            r"^[A-Z0-9]{2}-?[A-Z0-9]{1,3}-?[A-Z0-9]{1,2}$",
            r"^[A-Z0-9]{2,5}$",
            r"^[0-9]{2,3}-[0,9]{2}$",
            r"^[A-Z0-9]{2,3}-?[0-9]{4,5}$",
            r"^[A-Z]{2}-?[0-9]{0,4}$",
            r"^[0-9]{2}-?[A-Z0-9]{2,3}-?[A-Z0-9]{2,3}-?[0-9]{2}$",
            r"^[A-Z]{2}-?[0-9]{2}-?[0-9]{2}$",
            r"^[0-9]{3}-?[A-Z0-9]{2}$"
        ]
        return any(re.fullmatch(pattern, text) for pattern in patterns)

    def process_image(self, image_path: str) -> LicensePlateResult:
        """Xử lý ảnh và trả về kết quả nhận diện biển số"""
        # Kiểm tra định dạng ảnh
        image_type = ImageUtils.check_image_type(image_path)
        if image_type not in ['png', 'jpeg', 'jpg', 'bmp']:
            return LicensePlateResult('', 0, '', 1, 'Invalid image file! Please try again.')

        # Đọc và xử lý ảnh
        image = cv2.imread(image_path)
        indices, boxes, image = self._detect_license_plate(image)

        if not len(indices):
            return LicensePlateResult('', 0, '', 4, 'Error! License Plate not found!')

        best_result = LicensePlateResult('', 0, '', 2, 
            'The photo license plate is low. Please try the image again!')

        for i in indices:
            box = boxes[i]
            x, y, w, h = [int(v) for v in box]
            
            # Cắt vùng biển số
            plate_region = image[y:y+h, x:x+w]
            
            # Lưu ảnh biển số
            save_path = os.path.join(os.getcwd(), 'anhbienso')
            os.makedirs(save_path, exist_ok=True)
            
            image_name = f"bienso_{time.time()}.jpg"
            cv2.imwrite(os.path.join(save_path, image_name), plate_region)

            # Nhận dạng text
            plate_region = ImageUtils.resize_image(plate_region, width=250)
            ocr_result = self.ocr.ocr(plate_region, cls=False)
            
            if not ocr_result[0]:
                continue

            text_blocks = [line[1][0] for line in ocr_result[0]]
            confidences = [line[1][1] for line in ocr_result[0]]
            
            # Xử lý text nhận dạng được
            valid_plates = []
            for text in text_blocks:
                cleaned_text = re.sub("[^A-Z0-9\-]|^-|-$", "", text)
                if self._is_valid_plate_number(cleaned_text):
                    valid_plates.append(cleaned_text)

            if valid_plates:
                plate_text = "-".join(valid_plates)
                confidence = min(confidences)
                
                if len(plate_text) > len(best_result.text_plate):
                    best_result = LicensePlateResult(
                        plate_text, confidence, image_name, 0, "")

        return best_result 