from fastapi import FastAPI, File, UploadFile
from process import ReturnInfoLP, MessageInfo, ExtractLP,check_type_image
import os
import time
import shutil
from typing import List
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from zipfile import ZipFile
class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_upload_size: int) -> None:
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == 'POST':
            if 'content-length' not in request.headers:
                return Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
            content_length = int(request.headers['content-length'])
            if content_length > self.max_upload_size:
                return Response(status_code=status.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE)
        return await call_next(request)
app = FastAPI()
app.add_middleware(LimitUploadSize, max_upload_size=10000000)  # ~10
@app.get("/")
def read_root():
    return {"Hello": "Tan Dan JSC"}
@app.post("/LicencePlate/UploadingSingleFile")
def UploadingSingleFile(file: UploadFile = File(...)):
    try:
        pathSave = os.getcwd() +'\\'+  'anhtoancanh'
        if (os.path.exists(pathSave)):
            with open(f'anhtoancanh\\{file.filename}','wb') as f:
                f.write(file.file.read())
        else:
            os.mkdir(pathSave)
            with open(f'anhtoancanh\\{file.filename}','wb') as f:
                f.write(file.file.read())
        obj = ReturnInfoLP(f'anhtoancanh\\{file.filename}')
        if (obj.errorCode ==0):
            return {"errorCode": obj.errorCode, "errorMessage": obj.errorMessage,
            "data": [{"textPlate": obj.textPlate, "accPlate": obj.accPlate, "imagePlate": obj.imagePlate}]}
        else:
            return {"errorCode": obj.errorCode, "message": obj.errorMessage, "data": []}
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    return {"message": f"Successfuly uploaded {file.filename}"}
@app.post("/LicencePlate/UploadingMultipleFiles")
def UploadingMultipleFiles(files: List[UploadFile]):
    pathSave = os.getcwd() +'\\'+ 'anhtoancanh'
    if (os.path.exists(pathSave)):
        for file in files:
            with open(f'anhtoancanh\\{file.filename}','wb') as f:
                f.write(file.file.read())
    else:
        os.mkdir(pathSave)
        for file in files:
            with open(f'anhtoancanh\\{file.filename}','wb') as f:
                f.write(file.file.read())
    dict_values = {}
    for file in files:
        obj = ReturnInfoLP(f'anhtoancanh\\{file.filename}')
        if (obj.errorCode ==0):
            dict_values.update({file.filename:{"errorCode": obj.errorCode, "errorMessage": obj.errorMessage,
            "data": [{"textPlate": obj.textPlate, "accPlate": obj.accPlate, "imagePlate": 'anhbienso\\'+obj.imagePlate}]}})
        else:
            dict_values.update({file.filename:{"errorCode": obj.errorCode, "errorMessage": obj.errorMessage,"data": []}})
        file.file.close()
    return dict_values
@app.post("/LicencePlate/UploadingZipFile")
def UploadingZipFile(file: UploadFile = File(...)):
    dict_values = {}
    pathSave = os.getcwd() +'\\'+  'anhtoancanh'
    if(check_type_image(file.filename) != 'zip'):
        return {file.filename:{"errorCode": 1, "errorMessage": "Invalid .zip file! Please try again.", "data": []}}
    else:
        if (os.path.exists(pathSave)):
            with open(f'anhtoancanh\\{file.filename}','wb') as f:
                f.write(file.file.read())
        else:
            os.mkdir(pathSave)
            with open(f'anhtoancanh\\{file.filename}','wb') as f:
                f.write(file.file.read())
        with ZipFile(f'anhtoancanh\\{file.filename}', 'r') as zipObj:
            zipObj.extractall('anhtoancanh')
            # Get list of files names in zip
            listOfiles = zipObj.namelist()
            print(listOfiles)
            for namefile in listOfiles:
                obj = ReturnInfoLP(f'anhtoancanh\\{namefile}')
                if (obj.errorCode ==0):
                    dict_values.update({namefile:{"errorCode": obj.errorCode, "errorMessage": obj.errorMessage,
                    "data": [{"textPlate": obj.textPlate, "accPlate": obj.accPlate, "imagePlate": 'anhbienso\\'+obj.imagePlate}]}})
                else:
                    dict_values.update({namefile:{"errorCode": obj.errorCode, "errorMessage": obj.errorMessage,"data": []}})
            return dict_values