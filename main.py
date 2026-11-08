# ==========================================
# FILE NAME: main.py
# WORK DESCRIPTION (यह फाइल कैसे काम करती है):
# 1. यह FastAPI सर्वर चालू रखता है और /api/start-task पर रिक्वेस्ट रिसीव करता है।
# 2. यह बिना लॉगिन के हर यूज़र को एक गुप्त Session ID और Token देता है।
# 3. यह BackgroundTasks का उपयोग करके agent_core.py को पीछे चला देता है, 
#    ताकि यूज़र का मोबाइल या ब्राउज़र बंद होने पर भी सर्वर काम करता रहे।
# ==========================================

import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent_core import run_web_pilot_agent

app = FastAPI(title="WebPilot AI Server")

# स्टैटिक फाइल्स (HTML, CSS, JS) को सर्व करने के लिए
app.mount("/static", StaticFiles(directory="."), name="static")

class TaskRequest(BaseModel):
    target_url: str
    user_instruction: str

active_sessions = {}

@app.get("/")
async def serve_index():
    # फ्रंटएंड पेज सर्व करता है
    return FileResponse("index.html")

@app.post("/api/start-task")
async def start_task(request: TaskRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    session_token = str(uuid.uuid4())
    
    active_sessions[session_id] = {
        "status": "RUNNING",
        "logs": ["Session created. Launching browser automation..."],
        "token": session_token
    }
    
    # बैकग्राउंड में Playwright + OpenRouter लूप शुरू करना
    background_tasks.add_task(
        run_web_pilot_agent, 
        session_id=session_id, 
        url=request.target_url, 
        instruction=request.user_instruction,
        sessions_db=active_sessions
    )
    
    return {
        "status": "success",
        "session_id": session_id,
        "session_token": session_token
    }

@app.get("/api/task-status/{session_id}")
async def get_task_status(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return active_sessions[session_id]
