from fastapi import FastAPI, File, UploadFile
from process import ReturnInfoLP, MessageInfo, ExtractLP
import os
import time
import shutil
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/LicencePlate/upload")
def upload(file: UploadFile = File(...)):
    try:
        pathSave = os.getcwd() + '\\anhtoancanh'
        if (os.path.exists(pathSave)):
            with open(f'anhtoancanh/{file.filename}','wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
        else:
            os.mkdir(pathSave)
            with open(f'anhtoancanh/{file.filename}','wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
        obj = ReturnInfoLP(f'anhtoancanh/{file.filename}')
        if (obj.errorCode ==0):
            return {"errorCode": obj.errorCode, "errorMessage": obj.errorMessage,
            "data": [{"textPlate": obj.textPlate, "accPlate": obj.accPlate, "imagePlate": obj.imagePlate}]
            }
        else:
            return {"errorCode": obj.errorCode, "message": obj.errorMessage, "data": []}
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    return {"message": f"Successfuly uploaded {file.filename}"}
