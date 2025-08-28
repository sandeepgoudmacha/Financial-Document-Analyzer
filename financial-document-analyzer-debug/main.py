from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from rq import Queue
from crewai import Crew, Process
from agents import financial_analyst,investment_advisor,risk_assessor,verifier
from task import analyze_financial_document
import hashlib
import os
import logging
from datetime import datetime

# ===============================
# Logging Setup
# ===============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================
# FastAPI App
# ===============================
app = FastAPI(title="Financial Document Analyzer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, restrict domains
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Redis + RQ Setup
# ===============================
redis_conn = Redis(host="localhost", port=6379, db=0)
queue = Queue(connection=redis_conn)

# ===============================
# Utility Functions
# ===============================
def compute_file_hash(content: bytes) -> str:
    """Compute unique SHA256 hash for uploaded file."""
    return hashlib.sha256(content).hexdigest()

def run_crew(query: str, file_path: str):
    """Run the CrewAI financial analyst pipeline synchronously."""
    crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document],
        process=Process.sequential,
    )
    return crew.kickoff({"query": query, "file_path": file_path})

# Background worker task
def process_financial_document(query: str, file_path: str, job_id: str):
    """Process financial document in background worker."""
    redis_key = f"finance_result:{job_id}"
    try:
        logger.info(f"🔎 Starting analysis for job {job_id}")

        result = run_crew(query, file_path)

        # Save result to Redis
        redis_conn.hset(redis_key, mapping={
            "status": "finished",
            "result": str(result),
            "completed_at": datetime.now().isoformat()
        })

        logger.info(f"✅ Job {job_id} finished successfully")

    except Exception as e:
        logger.error(f"❌ Job {job_id} failed: {e}")
        redis_conn.hset(redis_key, mapping={
            "status": "failed",
            "result": "",
            "message": str(e),
            "failed_at": datetime.now().isoformat()
        })

# ===============================
# Endpoints
# ===============================

@app.post("/upload")
async def upload_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Upload a financial PDF and start background analysis."""

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    file_hash = compute_file_hash(content)
    redis_key = f"finance_result:{file_hash}"

    # Check cache
    if redis_conn.exists(redis_key):
        status = redis_conn.hget(redis_key, "status").decode()
        logger.info(f"Cache hit: Job {file_hash} already exists with status {status}")

        if status == "finished":
            result = redis_conn.hget(redis_key, "result").decode()
            return JSONResponse(content={
                "status": "success",
                "message": "Result found in cache.",
                "result": result,
                "job_id": file_hash
            })
        elif status == "processing":
            return JSONResponse(content={
                "status": "processing",
                "message": "Job is still processing.",
                "job_id": file_hash
            })
        elif status == "failed":
            error_message = redis_conn.hget(redis_key, "message").decode()
            return JSONResponse(content={
                "status": "failed",
                "message": error_message,
                "job_id": file_hash
            })

    # Save file to disk
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", f"{file_hash}.pdf")
    with open(file_path, "wb") as f:
        f.write(content)

    # Mark job as processing in Redis
    redis_conn.hset(redis_key, mapping={
        "status": "processing",
        "result": "",
        "message": "Job is being processed.",
        "started_at": datetime.now().isoformat(),
        "file_name": file.filename
    })

    # Enqueue background job
    try:
        job = queue.enqueue(
            process_financial_document,
            query.strip(),
            file_path,
            file_hash,
            job_timeout="15m"
        )
        logger.info(f"📌 Job {file_hash} enqueued successfully (RQ id: {job.id})")
    except Exception as e:
        redis_conn.hset(redis_key, mapping={
            "status": "failed",
            "result": "",
            "message": f"Failed to enqueue job: {str(e)}",
            "failed_at": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")

    return JSONResponse(content={
        "status": "processing",
        "message": "Job enqueued for analysis.",
        "job_id": file_hash
    })


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Check the status/result of a job."""
    redis_key = f"finance_result:{job_id}"
    if not redis_conn.exists(redis_key):
        return JSONResponse(content={
            "status": "not_found",
            "message": "Job not found."
        })
    data = redis_conn.hgetall(redis_key)
    decoded = {k.decode(): v.decode() for k, v in data.items()}

    # Try to parse result JSON if present
    if "result" in decoded and decoded["result"]:
        try:
            decoded["result"] = json.loads(decoded["result"])
        except Exception:
            pass  # fallback: leave as string

    return JSONResponse(content=decoded)


@app.get("/queue/stats")
async def queue_stats():
    """Queue statistics."""
    try:
        return JSONResponse(content={
            "queue_length": len(queue),
            "failed_jobs": queue.failed_job_registry.count,
            "finished_jobs": queue.finished_job_registry.count,
            "status": "healthy"
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.get("/health")
async def health_check():
    """Health check for API + Redis + Queue."""
    try:
        redis_conn.ping()
        return JSONResponse(content={
            "status": "healthy",
            "redis": "connected",
            "queue_length": len(queue),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "unhealthy",
            "error": str(e)
        }, status_code=500)


@app.get("/")
async def root():
    return JSONResponse(content={
        "message": "📊 Financial Document Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload - POST - Upload financial PDF",
            "status": "/status/{job_id} - GET - Check job status",
            "queue_stats": "/queue/stats - GET - Queue statistics",
            "health": "/health - GET - Health check"
        }
    })


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Financial Document Analyzer API")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
