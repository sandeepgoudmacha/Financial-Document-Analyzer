Financial Document Analyzer --- AI-Powered Financial Report Analysis
==================================================================

A complete, production-minded README for the **Financial Document Analyzer** repository:

GitHub: [https://github.com/sandeepgoudmacha/Financial-Document-Analyzer](https://github.com/sandeepgoudmacha/Financial-Document-Analyzer?utm_source=chatgpt.com)

This project analyzes uploaded financial PDF documents (earnings reports, 10-Q/10-K extracts, investor presentations) using CrewAI agents and returns structured, human-readable analysis. It consists of:

-   **Backend** --- FastAPI + RQ (Redis) worker running CrewAI agents that read PDFs and produce analysis.

-   **Worker** --- `worker.py` runs RQ worker that executes background jobs.

-   **Frontend** --- React UI (Vite) for uploading PDFs and polling job status.

* * * * *

Table of Contents
-----------------

-   [Features](#features)

-   [Prerequisites](#prerequisites)

-   [Repository layout](#repository-layout)

-   [Quick start (short)](#quick-start-short)

-   [Full installation & setup (detailed)](#full-installation--setup-detailed)

    -   Backend setup

    -   Redis setup

    -   Worker setup

    -   Frontend setup (Node/npm issues and fixes)

-   [How it works (flow)](#how-it-works-flow)

-   [API documentation (endpoints + examples)](#api-documentation-endpoints--examples)

-   [Frontend integration notes and examples](#frontend-integration-notes-and-examples)

-   [Bugs found & how they were fixed (detailed)](#bugs-found--how-they-were-fixed-detailed)

-   [Troubleshooting & common errors](#troubleshooting--common-errors)

-   [Expected output examples (sample JSON)](#expected-output-examples-sample-json)

-   [Security & production notes](#security--production-notes)

-   [Contributing](#contributing)

-   [License](#license)

* * * * *

Features
--------

-   Upload a PDF financial report and start asynchronous analysis.

-   Background processing with RQ + Redis.

-   Multi-agent analysis (Financial Analyst, Investment Advisor, Risk Assessor, Verifier).

-   Cached results in Redis by file SHA-256 (prevents duplicate processing).

-   Simple React frontend to upload files, receive a `job_id`, and poll status/result.

-   Logs each agent activity in terminal (useful for debugging) and saves final output to Redis.

* * * * *

Prerequisites
-------------

-   **Python 3.8+**

-   **pip**

-   **Node.js 16+** (use `nvm` recommended)

-   **npm** (or yarn)

-   **Redis server** running locally or accessible

-   **Google AI API Key** (or your preferred LLM provider) --- `GOOGLE_API_KEY` in `.env`

-   **Serper API Key** (if search functionality is used) --- `SERPER_API_KEY` in `.env`

* * * * *

Repository layout (relevant files)
----------------------------------

`Financial-Document-Analyzer/
├── financial-document-analyzer-debug/    # Backend code
│   ├── agents.py
│   ├── main.py          # FastAPI API used by frontend
│   ├── task.py
│   ├── tasks.py         # worker-side tasks for RQ
│   ├── tools.py
│   ├── worker.py        # starts RQ worker
│   ├── requirements.txt
│   ├── .env             # not checked in
│   └── data/            # uploaded files (created at runtime)
├── frontend/           # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx
│   └── package.json
└── README.md`

> **Note:** Your repo path may differ slightly --- adjust commands accordingly.

* * * * *

Quick start (short)
-------------------

1.  Start Redis server.

2.  Start backend API:

    `cd financial-document-analyzer-debug
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

3.  Start worker (new terminal):

    `cd financial-document-analyzer-debug
    python worker.py`

4.  Start frontend (new terminal):

    `cd frontend
    npm install
    npm run dev`

5.  Open `http://localhost:5173` (or `http://localhost:3000` if configured) and upload PDF.

* * * * *

Full installation & setup (detailed)
------------------------------------

### 1) Clone repository

`git clone https://github.com/sandeepgoudmacha/Financial-Document-Analyzer.git
cd Financial-Document-Analyzer`

### 2) Backend (Python) setup

`cd financial-document-analyzer-debug

# create venv
python3 -m venv venv
source venv/bin/activate    # windows: venv\Scripts\activate

# install python deps
pip install -r requirements.txt`

Create `.env` file in the backend folder:

`GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0`

> Keep keys secret and **never** commit `.env` to GitHub.

### 3) Redis

**Ubuntu / Debian**

`sudo apt update
sudo apt install redis-server
sudo systemctl enable --now redis
redis-cli ping   # should output: PONG`

**macOS (Homebrew)**

`brew install redis
brew services start redis
redis-cli ping`

**Windows**

Use WSL to run Redis or use a Docker container:

`# using Docker
docker run -p 6379:6379 --name redis -d redis:7`

### 4) Run the backend API

`# from financial-document-analyzer-debug
uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

Visit API docs: `http://localhost:8000/docs`

### 5) Start worker (RQ)

Open a second terminal, activate venv and start worker:

`cd financial-document-analyzer-debug
source venv/bin/activate
python worker.py`

The worker picks up jobs queued into Redis.

### 6) Frontend (React) setup & Node troubleshooting

If you encounter Node errors while creating / installing the frontend (e.g. `SyntaxError: Unexpected token '?'`, or `node: command not found`), these are usually caused by:

-   Old Node.js version

-   Using an incompatible global `create-vite` scaffold

**Install Node using nvm (recommended)**

`# Install nvm (if not installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
# Restart shell, then
nvm install 20
nvm use 20
node -v   # should be 20.x
npm -v`

**Install frontend dependencies and run**

`cd frontend
npm install
npm run dev
# Vite will print local URL (e.g. http://localhost:5173)`

* * * * *

How it works (flow)
-------------------

1.  User uploads a PDF and enters a "query" on the frontend.

2.  Frontend `POST /upload` (or `/analyze` depending on your frontend/backend wiring) --- API stores file and enqueues a job (RQ) with `process_financial_document(job_id, file_path, query)`.

3.  RQ worker (running `worker.py`) picks job, runs CrewAI pipeline (`run_crew`) that invokes agents and tools to read PDF and produce analysis.

4.  Worker stores result into Redis under a stable key (e.g. `finance_result:{file_hash}`).

5.  Frontend polls `/status/{job_id}` periodically and receives `processing` → `finished` along with `result`.

**Important:** the `job_id` returned to the frontend should be the file SHA-256 (the key used by your backend to store results), not the internal RQ job id --- there are two ids in the system (RQ job id vs file hash). Use consistent `job_id` across upload response and status check.

* * * * *

API documentation (endpoints & examples)
----------------------------------------

> Replace `localhost:8000` with your host if different.

### 1) Upload / start analysis

**POST** `/upload`

-   Content type: `multipart/form-data`

-   Fields:

    -   `file`: PDF (required)

    -   `query`: string (optional)

**Response (processing)**:

`{
  "status": "processing",
  "message": "Job enqueued for analysis.",
  "job_id": "<file_hash>"
}`

**cURL example**

`curl -X POST "http://localhost:8000/upload"\
  -F "file=@sample.pdf"\
  -F "query=profit shares"`

> If your frontend uses `/analyze` endpoint, either change the frontend to call `/upload` or add an alias endpoint.

* * * * *

### 2) Check status / result

**GET** `/status/{job_id}`

**Responses**

-   Not found:

`{ "status": "not_found", "message": "Job not found." }`

-   Processing:

`{
  "status": "processing",
  "message": "Job is being processed.",
  "started_at": "...",
  "file_name": "sample.pdf"
}`

-   Finished (example):

`{
  "status": "finished",
  "result": "Long textual or structured result stored by worker",
  "completed_at": "2025-08-28T17:20:31.000000"
}`

**cURL example**

`curl -X GET "http://localhost:8000/status/<file_hash>" -H "accept: application/json"`

* * * * *

### 3) Health & queue stats

**GET** `/health` --- returns Redis connectivity & queue length.\
**GET** `/queue/stats` --- queue length, failed/finished counts.

* * * * *

Frontend integration notes & examples
-------------------------------------

Your React app must:

1.  `POST /upload` and read `job_id` from response.

2.  Poll `/status/{job_id}` until `status` is `finished` or `failed`.

3.  Display `result`.

Example React pseudo-code (the project already contains `App.jsx` with these patterns). **Important fixes**:

-   Ensure the frontend calls the same endpoint (`/upload`) as the backend.

-   The backend returns `job_id = file_hash`. Use that to poll `/status/{job_id}`.

-   If your frontend posts to `/analyze` but backend listens on `/upload`, you will get 404. Fix by changing frontend endpoint to `/upload` or adding `/analyze` in backend.

* * * * *

Bugs found & how you fixed them (detailed)
------------------------------------------

During development we found several bugs. Below is a clear list (what was wrong, why it caused the frontend to not receive results, and how to fix it). You can copy these fixes into your repo.

### 1) Endpoint mismatch: `/analyze` vs `/upload`

-   **Problem:** Frontend was POSTing to `/analyze` while backend exposed `/upload`. This produced `404` or unexpected responses.

-   **Fix:** Make frontend call `/upload` (or add a duplicate `/analyze` endpoint on backend that forwards to the same logic). Example fix in `App.jsx`:

`// old
const res = await axios.post("http://localhost:8000/analyze", formData);

// new
const res = await axios.post("http://localhost:8000/upload", formData);`

### 2) Job ID mismatch: using RQ job.id vs file hash

-   **Problem:** Worker saved result under Redis key `finance_result:{file_hash}`, but frontend was polling using the RQ job ID (or vice versa).

-   **Fix:** Standardize on using the file hash as `job_id`. Backend `POST /upload` must return the file hash; frontend uses that in `/status/{job_id}`.

### 3) Redis key name mismatch across modules

-   **Problem:** Some code used `financial_result:{id}` while others used `finance_result:{id}`; hence API couldn't find worker results.

-   **Fix:** Choose one consistent key prefix (the code above uses `finance_result:{job_id}`). Ensure `tasks.py` and `main.py` / `app.py` use the exact same key string.

### 4) Worker produced results but frontend still returned `pending`

-   **Cause(s):**

    -   Frontend polled different job id or different redis key prefix.

    -   Worker stored result as Python object/string that wasn't JSON-serializable and your `/status` tried to parse JSON incorrectly.

-   **Fix:**

    -   Ensure worker writes `redis_conn.hset(key, mapping={ "status": "finished", "result": str(result), ... })`.

    -   `/status` should fetch `redis_conn.hgetall(key)` and decode bytes to str and (optionally) `json.loads` result if it's JSON.

### 5) Node / Vite errors when creating or running frontend

-   **Problem:** `node` not found or syntax errors due to old Node version.

-   **Fix:** Install Node via `nvm` and use Node 18/20. Example:

`nvm install 20
nvm use 20`

### 6) Agents/tools misconfigured (python-side)

-   **Problem:** Agents used method references rather than registered tool objects; or `llm` wasn't properly initialized.

-   **Fix:** In `agents.py`, ensure `llm` is properly instantiated and the tools list includes the tool objects (not bare methods). Also ensure `task.py` uses tasks bound to appropriate agents (verifier, analyst, etc.). (This readme lists the fixes; if you want, I can patch files in your repo to implement these changes.)

* * * * *

Troubleshooting & common errors
-------------------------------

### `404` on POST request from frontend

-   Likely endpoint mismatch (`/analyze` vs `/upload`). Confirm both frontend and backend use same route.

### `Result not ready yet` while worker finished in terminal

-   Confirm job_id used in status check is file hash returned by upload response.

-   Confirm worker saved result under the same Redis key prefix (`finance_result:{file_hash}`).

-   Check Redis directly:

    `redis-cli HGETALL finance_result:<file_hash>`

### `node` or `npm` errors

-   Use `nvm` to install a compatible Node version (>= 16, preferably 18 or 20).

-   Re-run `npm install` after Node upgrade.

### `ModuleNotFoundError` or Pydantic errors

-   Run `pip install -r requirements.txt` inside the venv.

-   For pydantic v2 warnings, consider updating related libraries that depend on pydantic.

### Worker errors complaining about Agent/Tool validation

-   Ensure agent tools are proper `BaseTool` instances and not raw methods. Register tools using the `crewai_tools` pattern shown in `tools.py`.

* * * * *

Expected output examples (sample JSON)
--------------------------------------

**When job is finished** --- `/status/{job_id}` returns:

`{
  "status": "finished",
  "result": "Final analysis text (or JSON) returned by CrewAI agents",
  "completed_at": "2025-08-28T18:14:46.123456"
}`

**If you return structured JSON from agents**, a more helpful response could be:

`{
  "status": "finished",
  "result": {
    "summary": "Tesla Q2 2025: revenues down 12% YoY; operating income down 42%...",
    "key_metrics": {
      "total_revenues": 22496000000,
      "operating_income": 923000000
    },
    "recommendations": [
      "Monitor new affordable model launch.",
      "Consider capital allocation reprioritization."
    ]
  },
  "completed_at": "2025-08-28T18:14:46.123456"
}`

* * * * *

Security & production notes
---------------------------

-   **Do not commit `.env`** --- API keys must stay secret.

-   **CORS:** Current config allows all origins. Restrict this in production.

-   **Rate limits / LLM cost:** LLM calls are expensive --- add limits and cost accounting.

-   **Timeouts:** Add timeouts and cancellation for long-running LLM calls.

-   **Access control:** Add authentication for public deployment.

-   **Data retention:** Securely manage uploaded files in `data/` and implement retention policy.

* * * * *

Contributing
------------

1.  Fork repository.

2.  Create a branch `fix/some-bug` or `feature/new-agent`.

3.  Make changes and add tests where possible.

4.  Submit a pull request with a clear description of changes and rationale.

* * * * *

License
-------

(Choose an appropriate license --- not provided in this repository by default.)

* * * * *

Final notes & checklist for you (copy-apply)
--------------------------------------------

1.  **Standardize Redis key prefix.** Make sure `main.py`, `tasks.py`, and `worker.py` all use the same key prefix (e.g. `finance_result:{file_hash}`).

2.  **Frontend → Backend endpoint parity.** Update `App.jsx` to call `/upload` (or update backend to also accept `/analyze`).

3.  **Return file_hash to frontend** in `/upload` response, and **poll `/status/{file_hash}`**.

4.  **Start services in this order:**

    -   Redis

    -   Backend (`uvicorn main:app --reload`)

    -   Worker (`python worker.py`)

    -   Frontend (`npm run dev`)

5.  **Check Redis manually** to confirm worker saved output:

    `redis-cli HGETALL finance_result:<file_hash>`
