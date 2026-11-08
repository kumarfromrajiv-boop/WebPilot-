# ==========================================
# FILE NAME: agent_core.py
# WORK DESCRIPTION (यह फाइल कैसे काम करती है):
# 1. Playwright की मदद से बैकग्राउंड में हेडलेस (बिना स्क्रीन वाला) ब्राउज़र खोलती है।
# 2. वेब पेज का लाइव डेटा निकालकर OpenRouter API के पास भेजती है।
# 3. AI से अगला कदम पूछकर वेबसाइट पर काम करवाती है और लूप चलाती है।
# ==========================================

import time
import requests
from playwright.sync_api import sync_playwright

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def query_openrouter_ai(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://webpilot-ai.shop",
        "X-Title": "WebPilot AI"
    }
    
    payload = {
        "model": "YOUR_PREFERRED_MODEL_HERE", # <--- यहाँ आप अपनी पसंद का कोई भी मॉडल नाम लिख सकते हैं
        "messages": [
            {
                "role": "system", 
                "content": (
                    "You are an advanced autonomous web automation AI agent. "
                    "Analyze the provided web page content and user goal, "
                    "then decide the precise next browser action. "
                    "If the goal is fully achieved, reply strictly with 'DONE'."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        res_data = response.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"ERROR: Failed to get AI response - {str(e)}"

def run_web_pilot_agent(session_id: str, url: str, instruction: str, sessions_db: dict):
    session = sessions_db[session_id]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        session["logs"].append(f"Navigating to target URL: {url}")
        page.goto(url)
        
        task_completed = False
        step_count = 0
        max_steps = 15 
        
        while not task_completed and step_count < max_steps:
            step_count += 1
            session["logs"].append(f"Step {step_count}: Analyzing page with AI...")
            
            page_content = page.content()[:4000]
            
            ai_prompt = f"""
            User Goal / Task: {instruction}
            Current Step: {step_count}
            
            Here is the current web page content snippet:
            {page_content}
            
            Based on the goal, what is the exact next step the browser should take? 
            If the task is completely finished, just reply with 'DONE'.
            """
            
            ai_decision = query_openrouter_ai(ai_prompt)
            session["logs"].append(f"AI Decision: {ai_decision}")
            
            if "DONE" in ai_decision.upper():
                task_completed = True
                session["status"] = "COMPLETED"
                session["logs"].append("Task successfully completed by AI!")
                break
            
            time.sleep(2)
            
        browser.close()
        
        if not task_completed:
            session["status"] = "MAX_STEPS_REACHED"
            session["logs"].append("Reached maximum step limit without 'DONE'.")
