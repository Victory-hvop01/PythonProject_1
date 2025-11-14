from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
import os
import asyncio
from datetime import datetime

from .database import get_db, init_db
from .models import AnalysisResult
from .video_analyzer import VideoAnalyzer
from .metrics import update_metrics, metrics

app = FastAPI(title="Video Analysis Service", version="1.0.0")



@app.on_event("startup")
async def startup_event():
    await init_db()
    os.makedirs("temp_uploads", exist_ok=True)


@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """
    Анализирует видеофайл на наличие движения
    """
    start_time = datetime.now()

    if not file.content_type.startswith('video/'):
        update_metrics(success=False)
        raise HTTPException(status_code=400, detail="File must be a video")

    try:
        file_id = str(uuid.uuid4())
        file_path = f"temp_uploads/{file_id}_{file.filename}"

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        analyzer = VideoAnalyzer(file_path)
        has_movement, movement_percentage, analysis_time = analyzer.analyze()

        db = next(get_db())
        result = AnalysisResult(
            filename=file.filename,
            file_size=len(content),
            has_movement=has_movement,
            movement_percentage=movement_percentage,
            analysis_time=analysis_time,
            created_at=datetime.now()
        )
        db.add(result)
        db.commit()
        db.refresh(result)

        os.remove(file_path)

        processing_time = (datetime.now() - start_time).total_seconds()
        update_metrics(success=True, processing_time=processing_time)

        return {
            "analysis_id": result.id,
            "filename": file.filename,
            "has_movement": has_movement,
            "movement_percentage": round(movement_percentage, 2),
            "analysis_time_seconds": round(analysis_time, 2),
            "processing_time_seconds": round(processing_time, 2)
        }

    except Exception as e:
        update_metrics(success=False)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


@app.get("/metrics")
async def get_metrics():
    """
    Возвращает метрики в формате Prometheus
    """
    from prometheus_client import generate_latest
    return generate_latest(metrics)


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/results")
async def get_results(limit: int = 10):
    """
    Получает последние результаты анализа
    """
    db = next(get_db())
    results = db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).limit(limit).all()

    return {
        "results": [
            {
                "id": result.id,
                "filename": result.filename,
                "has_movement": result.has_movement,
                "movement_percentage": result.movement_percentage,
                "analysis_time": result.analysis_time,
                "created_at": result.created_at.isoformat()
            }
            for result in results
        ]
    }