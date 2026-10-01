# Privacy-Aware IPv6 IoT Security Monitoring Across Address Rotation

A hackathon-ready prototype for detecting suspicious IPv6 address rotation in IoT networks while preserving privacy.

## Problem

IoT devices often rotate IPv6 addresses because of SLAAC, DHCPv6, privacy extensions, or network churn. Attackers can abuse these rotations to impersonate trusted devices or evade detection. The project monitors address churn while preserving privacy.

## Features

- Privacy-first device pseudonymization
- FastAPI service for telemetry ingestion
- SQLite database for easy demo deployment
- IPv6 rotation and reconnect anomaly detection
- Redacted alerts and summary endpoint
- Docker-ready deployment

## Architecture

```text
IoT Telemetry
    |
    v
FastAPI service
    |
    +--> Privacy layer (HMAC + redaction)
    |
    +--> Monitoring engine (rotation heuristics)
    |
    +--> SQLite persistence
    |
    +--> Alerts + Summary API
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API examples

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

```bash
curl http://localhost:8000/api/v1/summary
```

## Privacy controls

- Device IDs are stored as HMAC-SHA256 pseudonyms
- IPv6 addresses are not retained in raw form in summaries
- Alerts are sanitized and explainable to operators
- Monitoring is designed for privacy-aware operational use

## License

MIT
