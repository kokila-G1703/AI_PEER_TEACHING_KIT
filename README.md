# PeerTeach AI — AI Peer Teaching Kit for Weak Topics

A Flask web app that lets learners enter any topic and generates a customizable peer-teaching kit using the Groq API.

## Features
- Open-ended topic input (not limited to predefined topics)
- Beginner / Intermediate / Advanced levels
- Simple English, Tamil + English, or Tamil output preference
- Simple explanation and common misconceptions
- 10-minute lesson plan
- Exactly six slide outlines
- One-page-style handout download
- Five-question multiple-choice quiz with explanations
- Pre-test / post-test labels and SQLite score history
- Verification checklist and teacher tips

## Requirements
- Python 3.10+
- A Groq API key from https://console.groq.com/
- Internet access for API requests

Free-tier access and rate limits can change; check your Groq console before the demo.

## Setup (Windows)
1. Extract the ZIP and open the `ai_peer_teaching_kit` folder in VS Code.
2. Open the VS Code terminal.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to a new file named `.env`.
6. Open `.env` and replace `GROQ_API_KEY` with your own key. Keep the key private; do not upload `.env` to GitHub.
7. Confirm the `GROQ_MODEL` value matches a model available to your account in the Groq console.
8. Start the app:
   ```powershell
   python app.py
   ```
9. Open `http://127.0.0.1:5000` in your browser.

## Setup (macOS / Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key
python app.py
```

## Test checklist
- [ ] Home page loads
- [ ] Empty topic is rejected
- [ ] Try a computing topic and a non-computing topic
- [ ] Check that six slide cards appear
- [ ] Check that five quiz questions appear
- [ ] Submit the quiz and verify the score
- [ ] Check the progress page
- [ ] Download the handout
- [ ] Verify at least three AI-generated claims using trusted course material or a reliable source
- [ ] Try the Tamil + English output setting

## Troubleshooting
- **GROQ_API_KEY missing:** create `.env` from `.env.example`, add your key, and restart.
- **401 / authentication error:** check that the key is correct and active.
- **404 / model not found:** update `GROQ_MODEL` to an available model in your Groq console.
- **429 / rate limit:** wait and retry; free-tier limits vary by model and account.
- **JSON / incomplete output:** retry the request. The app validates the six slides and five quiz questions.
- **Port already in use:** stop the other Flask process or change the port in the final `app.run` line.

## Privacy and safety
- Do not collect passwords or unnecessary personal information.
- Use anonymous student labels for classroom demos.
- The local SQLite database stores topic, optional label, quiz stage, score and timestamp.
- Generated text may contain errors. Verify important claims before teaching.
- The built-in Flask development server is for local demos, not production deployment.

## Capstone deliverables
See `deliverables/` for a draft lesson plan, prompt library, verification report, reflection template, workflow, and before/after analysis template.
