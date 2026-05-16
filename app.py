from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
import zipfile
import shutil
import threading
import time
from pathlib import Path
from detect_similarities import collect_documents
import re
from io import StringIO, BytesIO
import csv

# Setup paths
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Global processing state
class ProcessingState:
    def __init__(self):
        self.status = "idle"
        self.stage = ""
        self.percent = 0
        self.current_file = ""
        self.total_files = 0
        self.results = []
        self.cancel_flag = False
        self.pause_flag = False
        self.error_message = ""
        self.lock = threading.Lock()

state = ProcessingState()

def get_ngrams(text, n=3):
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    words = text.split()
    shingles = set()
    if len(words) < n:
        shingles.add(" ".join(words))
    else:
        for i in range(len(words) - n + 1):
            shingles.add(" ".join(words[i:i+n]))
    return shingles

def jaccard_similarity(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    return len(intersection) / len(union) if union else 0.0

def process_zip_file(zip_path):
    try:
        with state.lock:
            state.status = "processing"
            state.stage = "extracting"
            state.percent = 0
            state.cancel_flag = False
            state.pause_flag = False
            state.error_message = ""

        extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path)

        if state.cancel_flag:
            with state.lock:
                state.status = "cancelled"
            return

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        except Exception as e:
            with state.lock:
                state.status = "error"
                state.error_message = "Invalid ZIP file"
            return

        while state.pause_flag and not state.cancel_flag:
            time.sleep(0.5)

        if state.cancel_flag:
            with state.lock:
                state.status = "cancelled"
            return

        with state.lock:
            state.stage = "reading_documents"
            state.percent = 25

        try:
            paths, docs = collect_documents(extract_path)
        except Exception as e:
            with state.lock:
                state.status = "error"
                state.error_message = "Error reading documents"
            return

        if len(docs) < 2:
            with state.lock:
                state.status = "error"
                state.error_message = "Need at least 2 documents"
            return

        with state.lock:
            state.total_files = len(docs)

        while state.pause_flag and not state.cancel_flag:
            time.sleep(0.5)

        if state.cancel_flag:
            with state.lock:
                state.status = "cancelled"
            return

        with state.lock:
            state.stage = "comparing"
            state.percent = 45

        doc_shingles = [get_ngrams(doc) for doc in docs]
        results = []
        n = len(paths)

        for i in range(n):
            while state.pause_flag and not state.cancel_flag:
                time.sleep(0.5)

            if state.cancel_flag:
                with state.lock:
                    state.status = "cancelled"
                return

            for j in range(i + 1, n):
                score = jaccard_similarity(doc_shingles[i], doc_shingles[j])
                if score >= 0.20:
                    file_a = paths[i].name
                    file_b = paths[j].name
                    results.append((file_a, file_b, round(score, 3)))

            with state.lock:
                state.current_file = paths[i].name if i < len(paths) else ""
                state.percent = 45 + int((i / max(n, 1)) * 35)

        while state.pause_flag and not state.cancel_flag:
            time.sleep(0.5)

        if state.cancel_flag:
            with state.lock:
                state.status = "cancelled"
            return

        with state.lock:
            state.stage = "complete"
            state.percent = 100

        if results:
            results.sort(key=lambda x: x[2], reverse=True)

        with state.lock:
            state.results = results
            state.status = "completed"

        shutil.rmtree(extract_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    except Exception as e:
        with state.lock:
            state.status = "error"
            state.error_message = "Processing error"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    try:
        if not file.filename or not file.filename.lower().endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files allowed")

        zip_path = os.path.join(UPLOAD_FOLDER, "input.zip")
        with open(zip_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        thread = threading.Thread(target=process_zip_file, args=(zip_path,), daemon=True)
        thread.start()

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/progress")
async def get_progress():
    with state.lock:
        return {
            "status": state.status,
            "stage": state.stage,
            "percent": state.percent,
            "current_file": state.current_file,
            "total_files": state.total_files,
            "error": state.error_message
        }

@app.post("/api/pause")
async def pause():
    with state.lock:
        if state.status == "processing":
            state.pause_flag = True
            state.status = "paused"
    return {"ok": True}

@app.post("/api/resume")
async def resume():
    with state.lock:
        if state.status == "paused":
            state.pause_flag = False
            state.status = "processing"
    return {"ok": True}

@app.post("/api/cancel")
async def cancel():
    with state.lock:
        state.cancel_flag = True
        state.status = "cancelled"
    return {"ok": True}

@app.get("/api/results")
async def get_results():
    with state.lock:
        results = state.results.copy()

    if not results:
        return {"rows": []}

    return {"rows": [{"file_a": r[0], "file_b": r[1], "score": r[2]} for r in results]}

@app.post("/api/reset")
async def reset():
    with state.lock:
        state.status = "idle"
        state.stage = ""
        state.percent = 0
        state.current_file = ""
        state.total_files = 0
        state.results = []
        state.cancel_flag = False
        state.pause_flag = False
        state.error_message = ""
    return {"ok": True}

@app.get("/api/csv")
async def download_csv():
    with state.lock:
        results = state.results.copy()

    if not results:
        raise HTTPException(status_code=400, detail="No results")

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["File A", "File B", "Similarity Score"])
    writer.writerows(results)

    csv_str = output.getvalue()
    csv_bytes = csv_str.encode()

    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=results.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
