# app.py
from fastapi import FastAPI, File, UploadFile, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketState
from .connmanager import ConnectionManager

import os
import json

manager = ConnectionManager()
app = FastAPI()
templates = Jinja2Templates(directory="static")

UPLOAD_FOLDER = 'uploads'
HISTORY_FILE = 'text_history.json'

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to load the last 10 text entries from the history file
def load_text_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            history = json.load(file)
    else:
        history = []
    return history[-10:][::-1]  # Last 10 entries in reverse order

# Route to render the main page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    files = os.listdir(UPLOAD_FOLDER)
    text_history = load_text_history()
    latest_text = text_history[0] if text_history else ""
    return templates.TemplateResponse("index.html", {
        'request': request,
        'files': files,
        'latest_text': latest_text,
        'text_history': text_history
    })

# Route to upload files and text
@app.post("/upload")
async def upload_file(file: UploadFile = File(None), shared_text: str = Form(None)):
    if file:
        with open(os.path.join(UPLOAD_FOLDER, file.filename), 'wb') as f:
            f.write(await file.read())
    
    if shared_text:
        history = load_text_history()
        history.append(shared_text)
        with open(HISTORY_FILE, 'w') as file:
            json.dump(history, file)
    
    return RedirectResponse(url="/", status_code=303)

# Route to delete files
@app.post("/delete_file")
async def delete_file(filename: str = Form(...)):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return JSONResponse({'success': True})

# Route to get specific text entry from history
@app.post("/get_text_history")
async def get_text_history(index: int = Form(...)):
    text_history = load_text_history()
    if 0 <= index < len(text_history):
        return JSONResponse({'text': text_history[index]})
    return JSONResponse({'text': ''})


@app.websocket("/ws/shared_text")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Serve static files (like HTML templates)
app.mount("/static", StaticFiles(directory="static"), name="static")
