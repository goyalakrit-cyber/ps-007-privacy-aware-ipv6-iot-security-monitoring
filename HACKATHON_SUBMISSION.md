# AIORI-3 Hackathon Submission

## Project Title
Privacy-Aware IPv6 IoT Security Monitoring Across Address Rotation

---

## Team Information

| Field | Details |
|-------|---------|
| **Team Name** | Last Minute Coders |
| **Team Members** | Akrit Goyal, Vedika Pathak |
| **Faculty Mentor** | Sachin Kumar |
| **Problem Statement** | Privacy-Aware IPv6 IoT Security Monitoring Across Address Rotation |
| **Domain** | Cybersecurity / IoT / IPv6 / Privacy |
| **Submission Date** | October 7, 2026 |

---

## Executive Summary

A privacy-preserving IPv6 IoT security monitoring system that detects suspicious address rotation and reconnect anomalies without exposing raw device identities or sensitive network data.

---

## Project Abstract

The rapid growth of IPv6 adoption in IoT networks introduces new security challenges, particularly when devices frequently rotate addresses due to SLAAC, DHCPv6, network churn, or privacy extensions. These address rotations can be exploited by malicious actors to impersonate trusted devices, evade detection, and bypass conventional monitoring systems. To address this, we propose a privacy-aware IPv6 security monitoring solution that detects suspicious rotation and reconnect patterns without compromising user or device privacy.

Our system ingests IoT telemetry, pseudonymizes device identities using HMAC-based keys, redacts IPv6 addresses in operator-facing summaries, and analyzes abnormal behaviors such as rapid address changes, unexpected reconnect sequences, and suspicious network segment transitions. A lightweight FastAPI backend stores the telemetry and alert records in SQLite, enabling rapid deployment and easy demonstration in a hackathon environment. The solution provides explainable, sanitized alerts and summary endpoints that help security teams identify threats while preserving privacy.

This project demonstrates an effective balance between operational security and privacy protection in modern IoT environments, making it highly relevant for cybersecurity, privacy-preserving monitoring, and next-generation network defense.

---

## Project Impact

1. **Detects Suspicious IPv6 Rotation Behavior**
   - Identifies rapid, anomalous IPv6 address changes that deviate from normal device behavior
   - Flags reconnect patterns indicative of device impersonation or network abuse
   - Provides risk scoring and confidence metrics for each detected anomaly

2. **Preserves Privacy Through Pseudonymization and Redaction**
   - Device identities are transformed into HMAC-SHA256 pseudonyms, preventing raw ID exposure
   - IPv6 addresses are redacted in summaries while maintaining operational visibility
   - Alerts are sanitized to exclude personally identifiable or operationally sensitive information
   - Designed for privacy-aware operational deployment in regulated environments

3. **Provides Explainable, Operator-Friendly Alerts and Summaries**
   - Human-readable alert descriptions that explain *why* a pattern is flagged as anomalous
   - Summary endpoints aggregate device behavior across time windows without leaking raw data
   - Structured JSON responses enable easy integration with SIEM and incident response platforms
   - Transparent heuristics allow security teams to understand and customize detection logic

---

## System Architecture

```
IoT Devices / Telemetry Sources
           |
           v
   FastAPI Event Ingestion (/api/v1/events)
           |
           ├──> Privacy Layer
           |      • HMAC device key generation
           |      • IPv6 redaction
           |      • Safe alert formatting
           |
           ├──> Monitoring Engine
           |      • Rotation heuristics
           |      • Reconnect anomaly detection
           |      • Risk scoring
           |
           ├──> SQLite Database
           |      • Telemetry history (TelemetryEvent)
           |      • Alert records (AlertRecord)
           |
           └──> API Summary Endpoints
                  • /api/v1/summary (redacted overview)
                  • /api/v1/alerts (suspicious activity)
```

---

## Key Features

- **Privacy-First Pseudonymization**: Device IDs are transformed into stable HMAC-SHA256 hashes
- **IPv6 Redaction**: Full addresses are never exposed in summaries or alerts
- **FastAPI-Based Ingestion**: Lightweight, high-performance event collection and processing
- **SQLite Persistence**: Rapid deployment without external database dependencies
- **Anomaly Detection Heuristics**: Detects rapid rotations, reconnect loops, and unusual patterns
- **Explainable Alerts**: Human-readable, sanitized alert payloads for operators
- **Docker-Ready**: Containerized deployment for hackathon and cloud environments
- **Easy Demo Flow**: Designed to showcase privacy and security in under 5 minutes

---

## Technical Implementation

### Technology Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite
- **Containerization**: Docker & Docker Compose

### Core Modules

**`app/privacy.py`**
- `stable_device_key()`: Generates pseudonymous device identifiers using HMAC-SHA256
- `redact_ipv6()`: Redacts IPv6 addresses to prefix notation for safe display
- `format_alert_payload()`: Structures sanitized alert data for operators

**`app/models.py`**
- `TelemetryEvent`: Stores device telemetry with timestamps and network context
- `AlertRecord`: Persists anomaly detections with severity, title, and risk score

**`app/database.py`**
- SQLAlchemy session management
- Automatic schema initialization

**`app/config.py`**
- Environment-based configuration for secrets, database path, and heuristic thresholds

---

## Quick Start

### Prerequisites
- Python 3.9+ or Docker

### Local Deployment

```bash
# Clone the repository
git clone https://github.com/goyalakrit-cyber/ps-007-privacy-aware-ipv6-iot-security-monitoring.git
cd ps-007-privacy-aware-ipv6-iot-security-monitoring

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Docker Deployment

```bash
docker-compose up --build
```

The service runs on port 8000 inside the container.

---

## API Usage Examples

### 1. Submit a Telemetry Event

```bash
curl -X POST "http://localhost:8000/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "sensor-lab-42",
    "ipv6_address": "2001:db8:85a3::8a2e:370:7334",
    "network_segment": "edge-zone-a",
    "event_type": "join",
    "protocol": "udp",
    "port": 5683,
    "status": "normal"
  }'
```

**Response:**
```json
{
  "status": "received",
  "device_key": "a1b2c3d4e5f6...",
  "event_type": "join"
}
```

### 2. Submit a Rotation Event (Anomaly Trigger)

```bash
curl -X POST "http://localhost:8000/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "sensor-lab-42",
    "ipv6_address": "2001:db8:85a3::9999:9999:9999",
    "network_segment": "edge-zone-a",
    "event_type": "join",
    "protocol": "udp",
    "port": 5683,
    "status": "normal"
  }'
```

This triggers an anomaly alert due to rapid address change.

### 3. Fetch Summary

```bash
curl http://localhost:8000/api/v1/summary
```

**Response (redacted and pseudonymized):**
```json
{
  "total_events": 5,
  "unique_devices": 2,
  "total_alerts": 1,
  "alerts": [
    {
      "device_key": "a1b2c3d4e5f6...",
      "severity": "medium",
      "title": "Rapid IPv6 Rotation Detected",
      "description": "Device rotated IPv6 address 2 times within 60 seconds.",
      "score": 7.5,
      "created_at": "2026-10-07T11:15:22Z"
    }
  ]
}
```

### 4. Fetch Alerts Only

```bash
curl http://localhost:8000/api/v1/alerts
```

---

## Demo Flow (5-Minute Showcase)

1. **Setup** (1 min): Start the API server and open a terminal.
2. **Normal Behavior** (1 min): Send 2–3 normal telemetry events from a device.
3. **Trigger Anomaly** (1 min): Send a rapid address rotation event.
4. **Show Results** (1 min): Query `/api/v1/summary` to display the alert without exposing device IDs or full IPv6 addresses.
5. **Explain Privacy** (1 min): Highlight the pseudonymized device_key, redacted IPv6, and explainable alert text.

---

## Privacy & Security Design

### Privacy Guarantees
- **No Raw Device IDs**: All device identifiers are hashed using HMAC-SHA256 with a secret key.
- **No Full IPv6 Exposure**: Addresses are stored internally but redacted in all external-facing responses.
- **Minimal Alert Disclosure**: Alerts contain only severity, title, description, and risk score—no raw telemetry.
- **Operator-Safe**: Security teams get actionable insights without access to sensitive data.

### Security Considerations
- HMAC-SHA256 ensures stable pseudonyms while preventing device ID recovery without the secret.
- IPv6 redaction maintains enough structure for clustering analysis while hiding device specifics.
- Risk scoring provides confidence and context for each anomaly.
- Explainability ensures alerts are trustworthy and auditable.

---

## Relevance to AIORI-3 Hackathon

This submission aligns with the hackathon's focus on **Cybersecurity & IoT**:

- **IPv6 Networking**: Directly addresses modern IPv6 challenges in IoT deployments.
- **Privacy-Preserving Design**: Demonstrates how to balance security monitoring with privacy concerns.
- **Practical Prototype**: Fully functional, deployable demo with real-world applicability.
- **Cloud & Edge Ready**: Lightweight architecture suitable for edge gateways, cloud services, and smart city deployments.
- **Explainability**: Alerts and summaries are human-readable and suitable for operators and compliance reviews.

---

## Deliverables

✅ **GitHub Repository**: Fully documented source code with MIT license  
✅ **README.md**: Comprehensive project overview and quick-start guide  
✅ **requirements.txt**: Python dependencies for reproducible deployment  
✅ **Docker & Docker Compose**: Containerized deployment for rapid setup  
✅ **API Documentation**: Inline comments and usage examples  
✅ **Privacy Module**: HMAC and redaction utilities  
✅ **Database Models**: SQLAlchemy ORM for telemetry and alerts  
✅ **Hackathon Submission**: This document with team info, abstract, and impact statement  

---

## Future Enhancements

1. **Dashboard Visualization**: Real-time anomaly heatmap and device cluster view.
2. **Threat Intelligence Integration**: Correlate detected patterns with known attack signatures.
3. **Multi-Device Correlation**: Track coordinated behavior across related IoT devices.
4. **Edge Deployment**: Package as a Kubernetes sidecar or IoT gateway service.
5. **Machine Learning**: Train models on rotation patterns for improved anomaly detection.
6. **Compliance Reporting**: Generate GDPR/HIPAA-compliant audit logs.

---

## Conclusion

**Last Minute Coders** presents a production-ready prototype that solves a critical real-world problem: how to monitor IPv6 IoT security without sacrificing privacy. Our solution is practical, explainable, and immediately deployable, making it an ideal hackathon submission for judges and a strong foundation for future development.

---

## Repository Links

- **GitHub**: https://github.com/goyalakrit-cyber/ps-007-privacy-aware-ipv6-iot-security-monitoring
- **License**: MIT

---

**Submission Status**: ✅ Ready for AIORI-3 Hackathon Online Phase (October 1–31, 2026)
