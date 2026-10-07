from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List

from app.database import engine, SessionLocal, Base
from app.models import TelemetryEvent, AlertRecord
from app.privacy import stable_device_key, redact_ipv6, format_alert_payload
from app.anomaly import inspect_rotation

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Privacy-Aware IPv6 IoT Security Monitoring",
    description="Detects suspicious IPv6 address rotation while preserving privacy",
    version="1.0.0"
)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# MODELS (Pydantic request/response schemas)
# ============================================================================

from pydantic import BaseModel, Field

class TelemetryEventRequest(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    ipv6_address: str = Field(..., description="IPv6 address of the device")
    network_segment: str = Field("unknown", description="Network segment or zone")
    event_type: str = Field("join", description="Event type: join, leave, heartbeat, etc.")
    protocol: str = Field("udp", description="Protocol used: udp, tcp, coap, etc.")
    port: int = Field(5683, description="Port number")
    status: str = Field("normal", description="Device status: normal, suspicious, offline, etc.")

class AlertResponse(BaseModel):
    id: int
    device_key: str
    severity: str
    title: str
    description: str
    score: float
    created_at: str

    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    total_events: int
    unique_devices: int
    total_alerts: int
    alerts: List[AlertResponse]

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", tags=["Health"])
def read_root():
    """Root endpoint - health check"""
    return {
        "service": "Privacy-Aware IPv6 IoT Security Monitoring",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.query(TelemetryEvent).first()
        return HealthResponse(
            status="healthy",
            message="Service and database are operational",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/api/v1/events", tags=["Telemetry"])
def ingest_event(event: TelemetryEventRequest, db: Session = Depends(get_db)):
    """
    Ingest a telemetry event from an IoT device.
    
    This endpoint:
    1. Accepts device telemetry (device_id, IPv6 address, etc.)
    2. Generates a pseudonymous device_key using HMAC-SHA256
    3. Stores the event in the database
    4. Analyzes recent events for anomalies (IPv6 rotation)
    5. Creates alerts if anomalies are detected
    6. Returns a sanitized response (no raw IDs or addresses exposed)
    """
    try:
        # Generate device pseudonym
        device_key = stable_device_key(event.device_id)
        
        # Create address fingerprint for comparison
        address_fingerprint = stable_device_key(event.ipv6_address)
        
        # Store the raw telemetry event
        db_event = TelemetryEvent(
            device_key=device_key,
            address_fingerprint=address_fingerprint,
            ipv6_address=event.ipv6_address,
            network_segment=event.network_segment,
            event_type=event.event_type,
            protocol=event.protocol,
            port=event.port,
            status=event.status,
            observed_at=datetime.now(timezone.utc)
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Analyze rotation for this device
        # Get last 24 hours of events for this device
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_events = db.query(TelemetryEvent).filter(
            TelemetryEvent.device_key == device_key,
            TelemetryEvent.observed_at >= cutoff_time
        ).order_by(TelemetryEvent.observed_at).all()
        
        # Convert ORM objects to dicts for anomaly inspection
        events_list = [
            {
                "device_id": event.device_key,  # Using device_key as id for anomaly logic
                "ipv6_address": e.ipv6_address,
                "observed_at": e.observed_at
            }
            for e in recent_events
        ]
        
        # Check for anomalies
        if len(events_list) > 1:
            alerts = inspect_rotation(events_list, window_minutes=15, rotation_threshold=2)
            
            # Store alerts in database
            for alert_data in alerts:
                existing_alert = db.query(AlertRecord).filter(
                    AlertRecord.device_key == alert_data["device_key"],
                    AlertRecord.title == alert_data["title"],
                    AlertRecord.created_at >= datetime.now(timezone.utc) - timedelta(minutes=15)
                ).first()
                
                # Avoid duplicate alerts within 15 minutes
                if not existing_alert:
                    db_alert = AlertRecord(
                        device_key=alert_data["device_key"],
                        severity=alert_data["severity"],
                        title=alert_data["title"],
                        description=alert_data["description"],
                        score=alert_data["score"],
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(db_alert)
            
            db.commit()
        
        # Return sanitized response (no raw device_id or full IPv6 exposed)
        return {
            "status": "received",
            "device_key": device_key[:16] + "...",  # Partial key only
            "event_type": event.event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Event processed and analyzed for anomalies"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error processing event: {str(e)}"
        )

@app.get("/api/v1/alerts", response_model=List[AlertResponse], tags=["Alerts"])
def get_alerts(
    limit: int = 50,
    severity: str = None,
    db: Session = Depends(get_db)
):
    """
    Fetch all alerts.
    
    Query parameters:
    - limit: Maximum number of alerts to return (default: 50)
    - severity: Filter by severity level (low, medium, high, critical)
    """
    try:
        query = db.query(AlertRecord).order_by(AlertRecord.created_at.desc())
        
        if severity:
            query = query.filter(AlertRecord.severity == severity)
        
        alerts = query.limit(limit).all()
        
        return [
            AlertResponse(
                id=a.id,
                device_key=a.device_key[:16] + "...",
                severity=a.severity,
                title=a.title,
                description=a.description,
                score=a.score,
                created_at=a.created_at.isoformat()
            )
            for a in alerts
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching alerts: {str(e)}"
        )

@app.get("/api/v1/summary", response_model=SummaryResponse, tags=["Summary"])
def get_summary(db: Session = Depends(get_db)):
    """
    Get a redacted, privacy-aware summary of all telemetry and alerts.
    
    Returns:
    - total_events: Total number of telemetry events processed
    - unique_devices: Count of unique device pseudonyms
    - total_alerts: Total anomalies detected
    - alerts: List of recent alerts (redacted and explainable)
    
    Note: All device identifiers and IPv6 addresses are pseudonymized/redacted.
    """
    try:
        # Count total events
        total_events = db.query(TelemetryEvent).count()
        
        # Count unique devices
        unique_devices = db.query(TelemetryEvent.device_key).distinct().count()
        
        # Get recent alerts (last 24 hours)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        alerts_query = db.query(AlertRecord).filter(
            AlertRecord.created_at >= cutoff_time
        ).order_by(AlertRecord.created_at.desc()).limit(50).all()
        
        # Total alerts ever
        total_alerts = db.query(AlertRecord).count()
        
        # Format alerts (redacted)
        formatted_alerts = [
            AlertResponse(
                id=a.id,
                device_key=a.device_key[:16] + "...",  # Partial pseudonym only
                severity=a.severity,
                title=a.title,
                description=a.description,
                score=a.score,
                created_at=a.created_at.isoformat()
            )
            for a in alerts_query
        ]
        
        return SummaryResponse(
            total_events=total_events,
            unique_devices=unique_devices,
            total_alerts=total_alerts,
            alerts=formatted_alerts
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

@app.get("/api/v1/device-stats/{partial_device_key}", tags=["Device Stats"])
def get_device_stats(partial_device_key: str, db: Session = Depends(get_db)):
    """
    Get statistics for a specific device (by partial pseudonym).
    
    Returns event count, alert count, and last activity timestamp.
    """
    try:
        # Get all events matching this partial key prefix
        events = db.query(TelemetryEvent).filter(
            TelemetryEvent.device_key.like(partial_device_key + "%")
        ).all()
        
        if not events:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device_key = events[0].device_key
        
        # Get alerts for this device
        alerts = db.query(AlertRecord).filter(
            AlertRecord.device_key == device_key
        ).all()
        
        # Get last activity
        last_event = db.query(TelemetryEvent).filter(
            TelemetryEvent.device_key == device_key
        ).order_by(TelemetryEvent.observed_at.desc()).first()
        
        return {
            "device_key": device_key[:16] + "...",
            "total_events": len(events),
            "total_alerts": len(alerts),
            "last_activity": last_event.observed_at.isoformat() if last_event else None,
            "network_segments": list(set([e.network_segment for e in events]))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching device stats: {str(e)}"
        )

@app.delete("/api/v1/alerts/{alert_id}", tags=["Alerts"])
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Acknowledge or delete an alert by ID.
    
    This is useful for marking false positives or handled incidents.
    """
    try:
        alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        db.delete(alert)
        db.commit()
        
        return {
            "status": "deleted",
            "alert_id": alert_id,
            "message": "Alert acknowledged and removed"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting alert: {str(e)}"
        )

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    print("Starting Privacy-Aware IPv6 IoT Security Monitoring Service...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized and ready.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down service...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
