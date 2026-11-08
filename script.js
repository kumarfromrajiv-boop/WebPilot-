// ==========================================
// FILE NAME: script.js
// WORK DESCRIPTION (यह फाइल कैसे काम करती है):
// 1. यूज़र द्वारा भरे गए डेटा को main.py के API पर भेजती है।
// 2. हर 2 सेकंड में सर्वर से स्टेटस चेक करती है और स्क्रीन पर लाइव लॉग्स दिखाती है।
// ==========================================

async function startTask() {
    const url = document.getElementById('url').value;
    const instruction = document.getElementById('instruction').value;
    const logsDiv = document.getElementById('logs');

    if (!url || !instruction) {
        alert("Please enter both URL and Instruction!");
        return;
    }

    logsDiv.innerHTML = "Submitting task to WebPilot AI Server...";

    try {
        const res = await fetch('/api/start-task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_url: url, user_instruction: instruction })
        });

        const data = await res.json();
        logsDiv.innerHTML = `Session Started (ID: ${data.session_id})<br>Running background automation...<br>`;
        
        // लाइव अपडेट्स के लिए पोलिंग शुरू करना
        pollStatus(data.session_id);
    } catch (err) {
        logsDiv.innerHTML = "Error connecting to server.";
    }
}

function pollStatus(sessionId) {
    const logsDiv = document.getElementById('logs');
    const interval = setInterval(async () => {
        const res = await fetch(`/api/task-status/${sessionId}`);
        const data = await res.json();
        
        logsDiv.innerHTML = data.logs.join('<br>');
        
        if (data.status === 'COMPLETED' || data.status === 'MAX_STEPS_REACHED') {
            clearInterval(interval);
        }
    }, 2000);
}
