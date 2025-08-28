"""
Background tasks for financial document analysis
This module contains functions that will be executed by RQ workers
"""
import logging
from datetime import datetime
import traceback

# Configure logging for tasks
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_financial_report(query: str, file_path: str, file_hash: str):
    """
    Process financial report analysis - this function will be executed by RQ worker

    Args:
        query: User's query about the financial document
        file_path: Path to the uploaded PDF file
        file_hash: SHA-256 hash of the file (used as job ID)

    Returns:
        str: Analysis result
    """
    try:
        # Import here to avoid circular imports and ensure all modules are available
        from crewai import Crew, Process
        from agents import financial_analyst, verifier
        from task import analyze_financial_document, investment_analysis, risk_assessment
        from redis import Redis

        logger.info(f"🔄 Starting financial analysis for job {file_hash}")
        logger.info(f"📋 Query: {query}")
        logger.info(f"📁 File path: {file_path}")

        # Update Redis to show processing started
        redis = Redis(host="localhost", port=6379, db=0)
        redis.hset(f"finance_result:{file_hash}", mapping={
            "status": "processing",
            "message": "Financial analysis in progress...",
            "processing_started": datetime.now().isoformat(),
            "current_stage": "initializing"
        })

        # Create the crew and run analysis
        logger.info(f"🤖 Creating financial analysis crew for job {file_hash}")
        
        redis.hset(f"finance_result:{file_hash}", mapping={
            "status": "processing",
            "message": "Creating analysis crew...",
            "current_stage": "crew_creation"
        })
        
        crew = Crew(
            agents=[financial_analyst, verifier],
            tasks=[analyze_financial_document, investment_analysis, risk_assessment],
            process=Process.sequential,
        )

        # Update status to show analysis starting
        redis.hset(f"finance_result:{file_hash}", mapping={
            "status": "processing",
            "message": "Running analysis...",
            "current_stage": "analysis_running"
        })

        logger.info(f"🚀 Starting crew analysis for job {file_hash}")
        result = crew.kickoff(inputs={"query": query, "file_path": file_path})
        result_str = str(result)

        logger.info(f"✅ Financial analysis completed for job {file_hash}")
        logger.info(f"📊 Result length: {len(result_str)} characters")

        # Save final result to Redis
        redis.hset(f"finance_result:{file_hash}", mapping={
            "status": "finished",
            "result": result_str,
            "message": "Financial analysis complete.",
            "completed_at": datetime.now().isoformat(),
            "current_stage": "completed"
        })

        logger.info(f"💾 Results saved to Redis for job {file_hash}")
        return result_str

    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error(f"❌ Error processing job {file_hash}: {error_msg}")
        logger.error(f"📋 Full traceback:\n{error_trace}")

        # Save error to Redis
        try:
            from redis import Redis
            redis = Redis(host="localhost", port=6379, db=0)
            redis.hset(f"finance_result:{file_hash}", mapping={
                "status": "failed",
                "result": "",
                "message": f"Error: {error_msg}",
                "error_details": error_trace,
                "failed_at": datetime.now().isoformat()
            })
            logger.info(f"💾 Error status saved to Redis for job {file_hash}")
        except Exception as redis_error:
            logger.error(f"❌ Failed to save error status to Redis: {str(redis_error)}")

        raise e


def test_redis_connection():
    """
    Test function to verify Redis connection - useful for debugging
    """
    try:
        from redis import Redis
        redis = Redis(host="localhost", port=6379, db=0)
        redis.ping()
        logger.info("✅ Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False


def simulate_test_job():
    """
    Simulate a test job for financial document processing
    """
    import time
    
    test_hash = f"finance_debug_test_{int(time.time())}"
    test_query = "Analyze this company's financial performance"
    test_file_path = "data/sample_financial_report.pdf"
    
    logger.info(f"🧪 Simulating test financial job with hash: {test_hash}")
    
    try:
        result = process_financial_report(test_query, test_file_path, test_hash)
        logger.info(f"✅ Test financial job completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Test financial job failed: {e}")
        raise e


# Main execution for testing
if __name__ == "__main__":
    logger.info("🧪 Testing financial tasks module directly...")
    
    if test_redis_connection():
        logger.info("📋 Redis connection OK, proceeding with test financial job...")
        try:
            result = simulate_test_job()
            logger.info("🎉 Direct financial task test completed successfully!")
            logger.info(f"📋 Result preview: {result[:200]}..." if len(result) > 200 else f"📋 Result: {result}")
        except Exception as e:
            logger.error(f"⚠️ Direct financial task test failed: {e}")
    else:
        logger.error("❌ Cannot proceed - Redis connection failed")
