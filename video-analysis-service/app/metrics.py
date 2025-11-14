from prometheus_client import Counter, Histogram, Gauge, REGISTRY
import time

video_processed = Counter(
    'video_analysis_processed_total',
    'Total number of processed videos',
    ['status']
)

video_processing_time = Histogram(
    'video_analysis_processing_time_seconds',
    'Video processing time in seconds',
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)

video_movement_detected = Counter(
    'video_analysis_movement_detected_total',
    'Total number of videos with movement detected'
)

current_processing_videos = Gauge(
    'video_analysis_current_processing',
    'Current number of videos being processed'
)

metrics = REGISTRY

def update_metrics(success: bool, processing_time: float = None):
    status = 'success' if success else 'error'
    video_processed.labels(status=status).inc()

    if processing_time is not None and success:
        video_processing_time.observe(processing_time)