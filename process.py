import cv2
import numpy as np
from PIL import Image
import time
import os
import re
from paddleocr import PaddleOCR
# Funtions
# Ham check dinh dang dau vao cua anh
def check_type_image(path):
    imgName = str(path)
    imgName = imgName[imgName.rindex('.')+1:]
    imgName = imgName.lower()
    return imgName
# Ham ve cac boxes len anh


def draw_prediction(img, classes, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes)
    color = (0, 0, 255)
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x-5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1)
# Ham resize anh aspect ratio


def resize_image(imageOriginal, width=0, height=0):
    w, h = imageOriginal.shape[1], imageOriginal.shape[0]
    new_w = 0
    new_h = 0
    if (width == 0 and height == 0):
        return imageOriginal
    if (width == 0):
        r = height / float(h)
        new_w = int(w * r)
        new_h = height
    else:
        r = width / float(w)
        new_w = width
        new_h = int(h * r)
    new_img = cv2.resize(imageOriginal, (new_w, new_h),
                         interpolation=cv2.INTER_CUBIC)
    return new_img
# Ham get output_layer


def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1]
                     for i in net.getUnconnectedOutLayers()]
    return output_layers
# Ham check valid regex License Plate


def isValidPlatesNumber(inputBlock):
    strRegex = "(^[0-9]{2}-?[0-9A-Z]{1,3}$)|(^[A-Z0-9]{2,5}$)|(^[0-9]{2,3}-[0,9]{2}$)|(^[A-Z0-9]{2,3}-?[0-9]{4,5}$)|(^[A-Z]{2}-?[0-9]{0,4}$)|(^[0-9]{2}-?[A-Z0-9]{2,3}-?[A-Z0-9]{2,3}-?[0-9]{2}$)|(^[A-Z]{2}-?[0-9]{2}-?[0-9]{2}$)|(^[0-9]{3}-?[A-Z0-9]{2}$)"
    pat = re.compile(strRegex)
    if (re.fullmatch(pat, inputBlock)):
        return True
    else:
        return False
# Ham load model yolo


def load_model():
    net = cv2.dnn.readNet('./model/det/yolov4-tiny-custom_det.weights',
                          './model/det/yolov4-tiny-custom_det.cfg')
    ocr = PaddleOCR(det_model_dir='./model/ch_ppocr_server_v2.0_det_infer/', rec_model_dir='./model/ch_ppocr_server_v2.0_rec_infer/',
                    rec_char_dict_path='./model/en_dict.txt', use_angle_cls=False)
    #classes = ['LP']
    # return net, classes
    return net, ocr
# Ham getIndices


def getIndices(image, net):
    #image = cv2.imread(path_to_image)
    #net = load_model('model/rec/yolov4-custom_rec.weights','model/rec/yolov4-custom_rec.cfg')
    (Width, Height) = (image.shape[1], image.shape[0])
    boxes = []
    class_ids = []
    confidences = []
    conf_threshold = 0.8
    nms_threshold = 0.4
    scale = 0.00392
    # print(classes)
    # (416,416) img target size, swapRB=True,  # BGR -> RGB, center crop = False
    blob = cv2.dnn.blobFromImage(
        image, scale, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(get_output_layers(net))
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    # Loai bo cac boxes dư thua
    indices = cv2.dnn.NMSBoxes(
        boxes, confidences, conf_threshold, nms_threshold)
    return indices, boxes, image
# Crop image tu cac boxes


def ReturnInfoLP(path):
    typeimage = check_type_image(path) 
    if(typeimage!='png' and typeimage!='jpeg' and typeimage!='jpg' and typeimage != 'bmp'):
        obj = MessageInfo(1, 'Invalid image file! Please try again.')
        return obj
    else:
        image = cv2.imread(path)
        indices, boxes, image = getIndices(image, net)
        # print(indices)
        list_image = []
        label = []
        if (len(indices) > 0):
            tempOCRResult = ''
            acc = 0
            obj = None
            for i in indices:
                i = i[0]
                box = boxes[i]
                x = box[0]
                y = box[1]
                w = box[2]
                h = box[3]
                src = image[round(y): round(y + h), round(x):round(x + w)]
                #Luu lai anh bien so
                pathSave = os.getcwd() + '\\anhbienso\\'
                stringImage = "bienso" + '_' + str(time.time()) + ".jpg"
                if (os.path.exists(pathSave)):
                    cv2.imwrite(pathSave + stringImage, src)
                else:
                    os.mkdir(pathSave)
                    cv2.imwrite(pathSave + stringImage, src)
                #Resize anh de recognition
                imageCrop = resize_image(src, 900)
                #Check ket qua nhan dang
                ocrResult = ocr.ocr(imageCrop, cls=False)
                textBlocks = [line[1][0] for line in ocrResult]
                scores = [line[1][1] for line in ocrResult]
                txts = "".join(textBlocks)
                arrayResult = []
                
                if (len(txts) > len(tempOCRResult) and len(txts) > 0 and len(txts) <= 12):
                    tempOCRResult = txts
                    for textBlock in textBlocks:
                        textBlockPlate = re.sub("[^A-Z0-9\-]|^-|-$", "", textBlock)
                        if (isValidPlatesNumber(textBlockPlate)):
                            arrayResult.append(textBlockPlate)
                    if (len(arrayResult) != 0):
                        errorCode = 0
                        message = ""
                        textPlates = "-".join(arrayResult)
                        obj = ExtractLP(textPlates, min(scores), stringImage, errorCode, message)
                    else:
                        obj = ExtractLP('', 0, stringImage, 2, 'The photo license plate is low. Please try the image again!')
            if(obj != None): return obj
            else: 
                obj = MessageInfo(3, "The photo quality is low. Please try the image again!")
                return obj
        else:
            obj = MessageInfo(4, "Error! License Plate not found !")
            return obj


net, ocr = load_model()


class ExtractLP:
    def __init__(self, textPlate, accPlate, imagePlate, errorCode, errorMessage):
        self.textPlate = textPlate
        self.accPlate = accPlate
        self.imagePlate = imagePlate
        self.errorCode = errorCode
        self.errorMessage = errorMessage
class MessageInfo:
    def __init__(self, errorCode, errorMessage):
        self.errorCode = errorCode
        self.errorMessage = errorMessage