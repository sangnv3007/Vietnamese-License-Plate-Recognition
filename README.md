# Vietnamese License Plate Recognition

### Setup
Download folder [model](https://drive.google.com/drive/folders/1V6_qUQH35v6hzVeZ9JCSn50FGAS0DaxA?usp=sharing), unzip and copy to project run directory:
```
model
└───en_dict.txt
│     
└───ch_ppocr_mobile_v2.0_cls_infer
│   └── [...]
│   
└───ch_ppocr_server_v2.0_det_infer
|   └── [...]
│
└───ch_ppocr_server_v2.0_rec_infer
|   └── [...] 
|
└───det
    └── [...] 
```
## Requirements

Python 3.7+

FastAPI stands on the shoulders of giants:

* <a href="https://www.starlette.io/" class="external-link" target="_blank">Starlette</a> for the web parts.
* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a> for the data parts.

## Installation
<div class="termy">

```console
$ pip install -r requirements.txt
```

<div class="termy">

```console
$ pip install fastapi
```

</div>
You will also need an ASGI server, for production such as <a href="https://www.uvicorn.org" class="external-link" target="_blank">Uvicorn</a> or <a href="https://github.com/pgjones/hypercorn" class="external-link" target="_blank">Hypercorn</a>.

<div class="termy">

```console
$ pip install "uvicorn[standard]"
```
### Run it

Run the server with:

<div class="termy">

```console
$ uvicorn main:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

### Interactive API docs

Now go to <a href="http://127.0.0.1:8000/docs" class="external-link" target="_blank">http://127.0.0.1:8000/docs</a>.

You will see the automatic interactive API documentation (provided by <a href="https://github.com/swagger-api/swagger-ui" class="external-link" target="_blank">Swagger UI</a>):

### Alternative API docs

And now, go to <a href="http://127.0.0.1:8000/redoc" class="external-link" target="_blank">http://127.0.0.1:8000/redoc</a>.

You will see the alternative automatic documentation (provided by <a href="https://github.com/Rebilly/ReDoc" class="external-link" target="_blank">ReDoc</a>):
### Check it now 👌

Now go to <a href="http://127.0.0.1:8000/docs" class="external-link" target="_blank">http://127.0.0.1:8000/docs</a>.

* The interactive API documentation will be automatically updated, including the new body:

![Step 1](https://github.com/sangnv3007/Vietnamese-License-Plate-Recognition/blob/main/step1.png)

* Click on the button "Try it out", it allows you to upload file and directly interact with the API:

![Step 2](https://github.com/sangnv3007/Vietnamese-License-Plate-Recognition/blob/main/step2.png)

* Then click on the "Execute" button, the user interface will communicate with your API, get the results and show them on the screen:

Image example

![CCCD Test](https://github.com/sangnv3007/Vietnamese-License-Plate-Recognition/blob/main/BSQD.jpg)

Return results

![Step 3](https://github.com/sangnv3007/Vietnamese-License-Plate-Recognition/blob/main/step3.png)
