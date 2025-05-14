import cv2
import numpy as np
from typing import Tuple, Optional, List

class ImageUtils:
    @staticmethod
    def check_image_type(path: str) -> str:
        """Kiểm tra định dạng file ảnh"""
        image_extension = path.split('.')[-1].lower()
        return image_extension

    @staticmethod
    def draw_bounding_box(
        img: np.ndarray,
        label: str,
        confidence: float,
        x: int,
        y: int,
        x_plus_w: int,
        y_plus_h: int,
        color: Tuple[int, int, int] = (0, 0, 255)
    ) -> None:
        """Vẽ bounding box và label lên ảnh"""
        cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
        cv2.putText(img, label, (x-5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1)

    @staticmethod
    def resize_image(
        image: np.ndarray,
        width: Optional[int] = None,
        height: Optional[int] = None,
        interpolation: int = cv2.INTER_AREA
    ) -> np.ndarray:
        """Resize ảnh giữ nguyên tỷ lệ"""
        if width is None and height is None:
            return image

        h, w = image.shape[:2]
        if width is None:
            aspect_ratio = height / float(h)
            new_width = int(w * aspect_ratio)
            new_height = height
        else:
            aspect_ratio = width / float(w)
            new_width = width
            new_height = int(h * aspect_ratio)

        return cv2.resize(image, (new_width, new_height), interpolation=interpolation)

    @staticmethod
    def get_output_layers(net) -> List[str]:
        """Lấy tên các layer output của mạng neural"""
        layer_names = net.getLayerNames()
        return [layer_names[i - 1] for i in net.getUnconnectedOutLayers()] 