DONE BY:
NIRANJANA NAYAGI B - 23N233 | SHIRAYA CHANDRA - 23N250 | SWADHITHA SP - 23N258

# Sleep Cycle Tracker (FastAPI + Streamlit + RAG)

A complete, local, sensor-free sleep tracker simulation:
- Backend: FastAPI with endpoints to generate sleep data, compute summaries, and retrieve advice via RAG
- Frontend: Streamlit UI for data input, charts, and advice
- RAG: FAISS + sentence-transformers over a local `data/sleep_tips.json`
- LangChain is used for prompt structuring (no external LLM/API required)

## Requirements
- Python 3.10+
- Windows, macOS, or Linux

## Setup
```powershell
cd D:\projects\SleepTracker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

## Run the Backend (FastAPI)
```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Open docs: `http://127.0.0.1:8000/docs`

## Run the Frontend (Streamlit)
In a second terminal with the same venv:
```powershell
streamlit run streamlit_app.py
```
The app will open in your browser (usually on `http://localhost:8501`).

## Endpoints
- `POST /generate-sleep-data`
  - Body:
    ```json
    { "days": 7, "start_time_range": {"start": "22:00", "end": "00:30"}, "seed": 42 }
    ```
  - Returns: simulated records with date, start_time, wake_time, duration_hours, mood

- `GET /get-sleep-summary`
  - Returns: total hours, average duration, min/max, correlation, trend

- `POST /query-advice`
  - Body:
    ```json
    { "question": "How do I sleep better?" }
    ```
  - Returns: answer text and retrieved sources

## Example Usage
1. Generate 7 days of data in Streamlit and view charts.
2. Ask: "How do I sleep better?" → receive actionable tips.
3. Try invalid inputs (e.g., `days: 0`) to see helpful error messages from the backend.

## Notes
- Data is stored in-memory for simplicity; restarting the backend clears it.
- The RAG index is built in-process on first use from `data/sleep_tips.json`.
- All components run locally without external API keys.


