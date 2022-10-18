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
        contents = file.file.read()
        f = open(file.filename, 'wb')
        f.write(contents)
        # pathSave = os.getcwd() + '\\imagePlate'
        # if (os.path.exists(pathSave)):
        #     imgName = file.filename + '_'+str(time.time())+'.jpg'
        #     shutil.copyfile(file.filename, pathSave+"\\" + imgName)
        # else:
        #     os.mkdir(pathSave)
        #     imgName = file.filename + '_'+str(time.time())+'.jpg'
        #     shutil.copyfile(file.filename, pathSave+"\\" + imgName)
        obj = ReturnInfoLP(file.filename)
        if (obj.status == "successful"):
            return {"textPlate": obj.textPlate, "accPlate": obj.accPlate, "imagePlate": obj.imagePlate, "status": obj.status, "message": obj.message}
        else:
            return {"status": obj.status, "message": obj.message}
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    return {"message": f"Successfuly uploaded {file.filename}"}
