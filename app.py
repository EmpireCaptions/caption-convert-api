import pycaption
import os
from fastapi import FastAPI, UploadFile, Form, HTTPException
from pycaption import CaptionConverter, detect_format

app = FastAPI()

ALLOWED_EXTENSIONS = {'srt', 'dfxp', 'sami', 'vtt', 'scc'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/convert")
async def convert_caption(file: UploadFile = Form(...), output_format: str = Form(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
import pycaption
from fastapi import FastAPI, UploadFile, Form, HTTPException, Request

app = FastAPI()

ALLOWED_EXTENSIONS = {'srt', 'dfxp', 'sami', 'vtt', 'scc'}
ALLOWED_IPS = {"123.45.67.89", "98.76.54.32", "75.183.118.168"}  # Add your app's IP addresses and localhost for testing

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.middleware("http")
async def check_allowed_ip(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Access denied")
    return await call_next(request)

@app.post("/convert")
async def convert_caption(file: UploadFile = Form(...), output_format: str = Form(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()

    detected_format = detect_format(content.decode())
    if not detected_format:
        raise HTTPException(status_code=400, detail="Unsupported caption format")

    converter = CaptionConverter()
    converter.read(content.decode(), detected_format())

    writer_mapping = {
        'srt': 'SRTWriter',
        'dfxp': 'DFXPWriter',
        'sami': 'SAMIWriter',
        'vtt': 'WebVTTWriter',
        'scc': 'SCCWriter',
        'txt': 'TranscriptWriter'
    }

    writer_class = writer_mapping.get(output_format.lower())
    if not writer_class:
        raise HTTPException(status_code=400, detail="Unsupported output format")

    output_content = converter.write(getattr(pycaption, writer_class)())

    return {"converted_content": output_content}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
