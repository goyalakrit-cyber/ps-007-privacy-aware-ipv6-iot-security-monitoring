# AIORI-3 Presentation Notes

Use with [`assets/AIORI-3-Hackathon-Presentation.pptx`](assets/AIORI-3-Hackathon-Presentation.pptx).
Suggested delivery time: 4–5 minutes, plus questions.

## Presenter flow

1. **Title (20 sec):** Introduce Last Minute Coders, the project, and problem statement A3-PS007-TC236.
2. **Monitoring gap (35 sec):** Explain that rotating IPv6 addresses can make event correlation harder; distinguish legitimate privacy rotation from suspicious repeated changes.
3. **Prototype approach (40 sec):** Walk through telemetry ingestion, HMAC pseudonymization, address fingerprints, and the two-change / 15-minute alert threshold.
4. **Architecture (35 sec):** Show the FastAPI, privacy/heuristics, SQLite, and summary/alerts flow.
5. **Live demo (60–90 sec):** Start the API, submit three events for one demo device using `2001:db8:1::1`, `::2`, and `::3`, then display `/api/v1/summary`.
6. **Privacy boundaries (45 sec):** State clearly that raw IPv6 addresses remain in the local database, while summary and alert responses omit full addresses. Current detection is a heuristic; reconnect and segment checks are not implemented.
7. **Impact and close (30 sec):** Summarize the prototype's value and describe production hardening as future work. Invite questions.

## Claims to keep precise

- The current signal is two or more consecutive address-fingerprint changes within 15 minutes.
- HMAC-based pseudonyms are used for the submitted device identifier and address fingerprint.
- Raw IPv6 addresses are stored internally; do not claim end-to-end encryption or that raw telemetry is never retained.
- Reconnect anomalies, network-segment anomalies, machine learning, and production readiness are not current capabilities.
- Use documentation-only IPv6 samples, never real device or production network data.

## Demo fallback

If the API is unavailable, show the local silent explainer at
`assets/aiori-3-demo-explainer.mp4` and explain that it is an architectural
overview, not a recording of live API output.
