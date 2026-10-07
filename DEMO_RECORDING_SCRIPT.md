# AIORI-3 Demo Recording Script

Target length: 2–3 minutes. Record the running project with a terminal and browser
visible. Use the documentation-only IPv6 prefix `2001:db8::/32`; do not expose
real device identifiers, production addresses, or secrets.

## Generated explainer asset

A silent, captioned explainer video is provided at
`assets/aiori-3-demo-explainer.mp4`. It is a visual overview, not a recording of
a live API session. To regenerate it, install the optional video-rendering tools
and run:

```powershell
python -m pip install Pillow imageio-ffmpeg
python tools\generate_explainer_video.py
```

Use the shot list below to record the live API behavior separately or add a
spoken narration to the generated explainer before uploading.

## Before recording

1. Install the requirements and start the service with a dedicated demo database
   in PowerShell. Use a new filename after a previous demo if you want an empty database:

   ```powershell
   $env:DATABASE_URL = "sqlite:///./data/hackathon-demo.db"
   $env:SECRET_KEY = "demo-only-change-before-use"
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. Open `http://localhost:8000/health` to verify the service, then
   `http://localhost:8000/docs` to use the interactive API.
3. Submit three `/api/v1/events` requests for the same demo device, changing
   only the IPv6 address. Then open `/api/v1/summary` and `/api/v1/alerts`.

## Shot list and narration

| Time | Show | Narration |
|------|------|-----------|
| 0:00–0:20 | Title card or repository README | “We are Last Minute Coders. Our AIORI-3 project monitors IPv6 IoT address changes while limiting what operators need to see.” |
| 0:20–0:45 | README architecture diagram | “Telemetry enters a FastAPI service. Device identifiers and address fingerprints are HMAC-pseudonymized for correlation, and SQLite stores the demo history.” |
| 0:45–1:20 | Swagger UI `/docs`; submit three events for one demo device with different documentation IPv6 addresses | “I’m simulating one device appearing with several IPv6 addresses. These sample addresses are reserved for documentation and are not real device data.” |
| 1:20–1:55 | `/api/v1/summary` or `/api/v1/alerts` response | “The monitor flags repeated address changes within its configured time window. The response provides a pseudonymous device key and an explainable alert, not the submitted device ID or full IPv6 address.” |
| 1:55–2:20 | `app/privacy.py`, `app/anomaly.py`, and the returned JSON | “The prototype combines HMAC-based pseudonyms, rotation heuristics, and a local database. This is a hackathon prototype, not a production security guarantee; deployments need protected secrets, access controls, and operational testing.” |
| 2:20–2:30 | Project title and repository URL | “This is Privacy-Aware IPv6 IoT Security Monitoring Across Address Rotation, by Last Minute Coders.” |

## Sample event body

Use the same `device_id` for all three submissions and change the address each
time. For example:

```json
{
  "device_id": "demo-sensor-01",
  "ipv6_address": "2001:db8:1::1",
  "network_segment": "demo-zone",
  "event_type": "join",
  "protocol": "udp",
  "port": 5683,
  "status": "normal"
}
```

Use `2001:db8:1::2` and `2001:db8:1::3` for the next two submissions. Do not
promise a particular score or alert count; show the response produced by the
recorded run.

## Publishing checklist

- Trim dead time and confirm the API output is readable in the recording.
- Upload the finished recording to YouTube using a visibility setting accepted
  by the hackathon.
- Replace the pending YouTube URL in `README.md` and `HACKATHON_SUBMISSION.md`
  with the final link, then verify that reviewers can access it.
