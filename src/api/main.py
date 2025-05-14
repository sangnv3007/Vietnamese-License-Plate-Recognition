from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import shutil
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
    def save_upload_file(upload_file: UploadFile, save_path: str) -> str:
        """Lưu file upload vào thư mục"""
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, upload_file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return file_path

    @staticmethod
    def process_image_file(file_path: str) -> Dict[str, Any]:
        """Xử lý một file ảnh"""
        result = detector.process_image(file_path)
        
        if result.error_code == 0:
            return {
                "errorCode": result.error_code,
                "errorMessage": result.error_message,
                "data": [{
                    "textPlate": result.text_plate,
                    "accPlate": result.confidence,
                    "imagePlate": f"anhbienso/{result.image_name}"
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

@app.post("/api/v1/license-plate/single")
async def process_single_image(file: UploadFile = File(...)):
    """API xử lý một ảnh đơn"""
    try:
        save_path = os.path.join(os.getcwd(), 'anhtoancanh')
        file_path = FileProcessor.save_upload_file(file, save_path)
        return FileProcessor.process_image_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

@app.post("/api/v1/license-plate/multiple")
async def process_multiple_images(files: List[UploadFile] = File(...)):
    """API xử lý nhiều ảnh"""
    try:
        save_path = os.path.join(os.getcwd(), 'anhtoancanh')
        results = {}
        
        for file in files:
            file_path = FileProcessor.save_upload_file(file, save_path)
            results[file.filename] = FileProcessor.process_image_file(file_path)
            file.file.close()
            
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
        save_path = os.path.join(os.getcwd(), 'anhtoancanh')
        zip_path = FileProcessor.save_upload_file(file, save_path)
        results = {}

        with ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(save_path)
            
            for image_name in zip_file.namelist():
                image_path = os.path.join(save_path, image_name)
                results[image_name] = FileProcessor.process_image_file(image_path)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="192.168.2.167",
        port=8001,
        reload=True
    ) 