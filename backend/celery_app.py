from celery import Celery
from datetime import datetime
from config import settings

celery_app = Celery(
    "securestack",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task
def run_scheduled_scan(scan_id: int):
    from database import SessionLocal
    from routers.scheduled_scans import ScheduledScan
    from modules.dependencies import DependencyAnalyzer
    from modules.container_scanner import ContainerScanner
    from modules.infrastructure_scanner import InfrastructureScanner
    
    db = SessionLocal()
    try:
        scan = db.query(ScheduledScan).filter(ScheduledScan.id == scan_id).first()
        if not scan or not scan.enabled:
            return
        
        scan_type = scan.scan_type
        config = scan.config or {}
        
        if scan_type == "dependency":
            analyzer = DependencyAnalyzer()
            result = analyzer.analyze_package(
                package_name=config.get("package_name"),
                version=config.get("version", "latest"),
                ecosystem=config.get("ecosystem", "npm")
            )
        elif scan_type == "container":
            scanner = ContainerScanner()
            result = scanner.scan_image(
                image_name=config.get("image_name"),
                image_tag=config.get("image_tag", "latest")
            )
        elif scan_type == "infrastructure":
            scanner = InfrastructureScanner()
            result = scanner.scan(
                scan_type=config.get("scan_type"),
                target=config.get("target"),
                config=config
            )
        
        scan.last_run = datetime.utcnow()
        from croniter import croniter
        cron = croniter(scan.schedule, datetime.utcnow())
        scan.next_run = cron.get_next(datetime)
        db.commit()
        
        return {"status": "completed", "result": result}
    finally:
        db.close()

