from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import io
import cv2
import numpy as np
from zipfile import ZipFile
import uvicorn
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.services.license_plate_service import LicensePlateDetector

# Khởi tạo FastAPI app
app = FastAPI(
    title="License Plate Recognition API",
    description="API để nhận diện biển số xe từ ảnh",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo detector
detector = LicensePlateDetector(
    weights_path='src/model/yolov4-tiny-custom_final.weights',
    config_path='src/model/yolov4-tiny-custom.cfg',
    paddle_model_dir='src/model/inference'
)

class FileProcessor:
    @staticmethod
    async def read_image_file(file: UploadFile) -> np.ndarray:
        """Đọc file ảnh từ UploadFile thành numpy array"""
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def process_image_array(image: np.ndarray, filename: str) -> Dict[str, Any]:
        """Xử lý ảnh dạng numpy array"""
        result = detector.process_image_array(image, filename)
        
        if result.error_code == 0:
            return {
                "errorCode": result.error_code,
                "errorMessage": result.error_message,
                "data": [{
                    "textPlate": result.text_plate,
                    "accPlate": result.confidence,
                    "imagePlate": result.image_base64 # Trả về ảnh dạng base64 string
                }]
            }
        else:
            return {
                "errorCode": result.error_code,
                "errorMessage": result.error_message,
                "data": []
            }

@app.get("/")
def read_root():
    """API endpoint chính"""
    return {"message": "Welcome to License Plate Recognition API"}

@app.post("/LicencePlate/UploadingSingleFile")
async def process_single_image(file: UploadFile = File(...)):
    """API xử lý một ảnh đơn"""
    try:
        image = await FileProcessor.read_image_file(file)
        if image is None:
            raise HTTPException(status_code=400, detail="Could not read image file")
        return FileProcessor.process_image_array(image, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@app.post("/api/v1/license-plate/multiple")
async def process_multiple_images(files: List[UploadFile] = File(...)):
    """API xử lý nhiều ảnh"""
    try:
        results = {}
        for file in files:
            image = await FileProcessor.read_image_file(file)
            if image is not None:
                results[file.filename] = FileProcessor.process_image_array(image, file.filename)
            await file.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/license-plate/zip")
async def process_zip_file(file: UploadFile = File(...)):
    """API xử lý file zip chứa nhiều ảnh"""
    if not file.filename.lower().endswith('.zip'):
        return {
            file.filename: {
                "errorCode": 1,
                "errorMessage": "Invalid .zip file! Please try again.",
                "data": []
            }
        }

    try:
        contents = await file.read()
        zip_buffer = io.BytesIO(contents)
        results = {}

        with ZipFile(zip_buffer, 'r') as zip_file:
            for filename in zip_file.namelist():
                with zip_file.open(filename) as image_file:
                    contents = image_file.read()
                    nparr = np.frombuffer(contents, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if image is not None:
                        results[filename] = FileProcessor.process_image_array(image, filename)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="192.168.2.167",
        port=8001,
        reload=True
    ) 