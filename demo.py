#!/usr/bin/env python3
"""
DEMO SCRIPT: Privacy-Aware IPv6 IoT Security Monitoring
=========================================================

This script demonstrates the complete hackathon project workflow:
1. Start the FastAPI server
2. Send normal telemetry events
3. Trigger anomaly detection with rapid IPv6 rotation
4. Fetch summary and alerts (all redacted and privacy-aware)
5. Show the results to judges

Run this from the project root:
    python demo.py
"""

import requests
import time
import json
from datetime import datetime, timedelta
import sys
import subprocess
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
DEMO_DELAY = 2  # seconds between events for readability

# ANSI color codes for terminal output
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 80}{RESET}\n")

def print_step(step_num, text):
    print(f"{BOLD}{GREEN}STEP {step_num}: {text}{RESET}")

def print_info(text):
    print(f"{BLUE}➜ {text}{RESET}")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_json(data):
    print(json.dumps(data, indent=2))

def wait_for_server(max_retries=30):
    """Wait for the FastAPI server to start"""
    print_info("Waiting for FastAPI server to start...")
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print_success("Server is up and ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        if attempt < max_retries - 1:
            print_info(f"Attempt {attempt + 1}/{max_retries}... retrying in 2 seconds")
            time.sleep(2)
    
    print_error("Server failed to start after 60 seconds")
    return False

def send_event(device_id, ipv6_address, event_type="join", network_segment="edge-zone-a"):
    """Send a telemetry event to the API"""
    payload = {
        "device_id": device_id,
        "ipv6_address": ipv6_address,
        "network_segment": network_segment,
        "event_type": event_type,
        "protocol": "coap",
        "port": 5683,
        "status": "normal"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/events",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json(), True
        else:
            return response.json(), False
    except Exception as e:
        print_error(f"Failed to send event: {str(e)}")
        return None, False

def fetch_summary():
    """Fetch the privacy-aware summary"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/summary", timeout=5)
        if response.status_code == 200:
            return response.json(), True
        else:
            return response.json(), False
    except Exception as e:
        print_error(f"Failed to fetch summary: {str(e)}")
        return None, False

def fetch_alerts():
    """Fetch all alerts"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/alerts?limit=10", timeout=5)
        if response.status_code == 200:
            return response.json(), True
        else:
            return response.json(), False
    except Exception as e:
        print_error(f"Failed to fetch alerts: {str(e)}")
        return None, False

def demo_normal_behavior():
    """Demo: Send normal device events"""
    print_step(1, "Normal Device Behavior")
    print_info("Sending 3 normal events from sensor-lab-42 over 10 minutes")
    print()
    
    events = [
        ("sensor-lab-42", "2001:db8:85a3::8a2e:370:7334", "join"),
        ("sensor-lab-42", "2001:db8:85a3::8a2e:370:7334", "heartbeat"),
        ("sensor-lab-42", "2001:db8:85a3::8a2e:370:7334", "heartbeat"),
    ]
    
    for i, (device_id, ipv6, event_type) in enumerate(events, 1):
        print_info(f"Event {i}: {device_id} | IPv6: {ipv6[:30]}... | Type: {event_type}")
        result, success = send_event(device_id, ipv6, event_type)
        
        if success:
            print_success(f"  Device key: {result['device_key']} (pseudonymized)")
        else:
            print_error(f"  Failed: {result}")
        
        time.sleep(DEMO_DELAY)
    
    print()

def demo_rapid_rotation():
    """Demo: Trigger anomaly detection with rapid IPv6 rotation"""
    print_step(2, "Anomaly Trigger: Rapid IPv6 Rotation")
    print_warning("Sending 3 rapid address changes (within 2 minutes) from same device")
    print_info("This simulates an attacker impersonating the device or exploiting rotation")
    print()
    
    events = [
        ("sensor-lab-42", "2001:db8:85a3::9999:1111:1111", "join"),
        ("sensor-lab-42", "2001:db8:85a3::9999:2222:2222", "join"),
        ("sensor-lab-42", "2001:db8:85a3::9999:3333:3333", "join"),
    ]
    
    for i, (device_id, ipv6, event_type) in enumerate(events, 1):
        print_warning(f"Event {i}: {device_id} | IPv6: {ipv6[:30]}... (NEW ADDRESS)")
        result, success = send_event(device_id, ipv6, event_type)
        
        if success:
            print_success(f"  Sent - Device key: {result['device_key']}")
        else:
            print_error(f"  Failed: {result}")
        
        time.sleep(DEMO_DELAY)
    
    print()

def demo_summary():
    """Demo: Show the privacy-aware summary"""
    print_step(3, "Privacy-Aware Summary")
    print_info("Fetching aggregated telemetry summary (all identifiers redacted)")
    print()
    
    time.sleep(2)  # Wait for alerts to be generated
    summary, success = fetch_summary()
    
    if success:
        print_success("Summary received (privacy-preserved):")
        print()
        print_json(summary)
        print()
        
        if summary.get('alerts'):
            print_warning(f"⚠ {len(summary['alerts'])} anomalies detected!")
            print()
    else:
        print_error(f"Failed to fetch summary: {summary}")
    
    print()

def demo_detailed_alerts():
    """Demo: Show detailed alert information"""
    print_step(4, "Detailed Anomaly Alerts")
    print_info("Viewing detailed alert records (redacted and explainable)")
    print()
    
    alerts, success = fetch_alerts()
    
    if success:
        if alerts:
            print_success(f"Found {len(alerts)} alert(s):")
            print()
            for alert in alerts:
                print_json(alert)
                print()
        else:
            print_info("No alerts generated yet")
    else:
        print_error(f"Failed to fetch alerts: {alerts}")
    
    print()

def demo_privacy_explanation():
    """Demo: Explain privacy guarantees"""
    print_step(5, "Privacy Guarantees")
    print_info("This system implements privacy-by-design principles:")
    print()
    
    guarantees = [
        ("Device Pseudonymization", "Device IDs are hashed using HMAC-SHA256 → Irreversible without secret key"),
        ("IPv6 Redaction", "Full addresses stored internally but redacted as 2001:db8:85a3:xxxx:xxxx:xxxx:xxxx"),
        ("No Raw Data Exposure", "Summary and alerts never contain raw device IDs or full addresses"),
        ("Explainable Alerts", "Alert descriptions explain the threat without leaking operational data"),
        ("Time-Series Safe", "Even with access to multiple alerts, individual devices cannot be tracked"),
    ]
    
    for title, description in guarantees:
        print(f"{BOLD}{GREEN}✓ {title}{RESET}")
        print(f"  {description}")
        print()

def demo_api_endpoints():
    """Show available API endpoints"""
    print_step(6, "Available API Endpoints")
    print_info("The complete API for integration with SIEM/monitoring platforms:")
    print()
    
    endpoints = [
        ("GET", "/", "Health check and service info"),
        ("GET", "/health", "Detailed health status"),
        ("POST", "/api/v1/events", "Ingest telemetry events from IoT devices"),
        ("GET", "/api/v1/alerts", "Fetch detected anomalies (paginated)"),
        ("GET", "/api/v1/summary", "Get privacy-aware summary dashboard"),
        ("GET", "/api/v1/device-stats/{device_key}", "Per-device statistics"),
        ("DELETE", "/api/v1/alerts/{alert_id}", "Acknowledge/clear alerts"),
    ]
    
    for method, path, description in endpoints:
        print(f"{BOLD}{BLUE}{method:6} {path:35}{RESET}  {description}")
    
    print()

def run_server_in_background():
    """Start the FastAPI server in a subprocess"""
    print_info("Starting FastAPI server in background...")
    
    # Check if uvicorn is installed
    try:
        import uvicorn
    except ImportError:
        print_error("uvicorn not installed. Install with: pip install -r requirements.txt")
        return None
    
    # Start the server
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    return process

def main():
    """Main demo flow"""
    print_header("🔒 PRIVACY-AWARE IPv6 IoT SECURITY MONITORING")
    print("AIORI-3 Hackathon Submission Demo")
    print("Team: Last Minute Coders")
    print()
    
    # Start server
    print_info("Initializing...")
    server_process = run_server_in_background()
    
    if not server_process:
        print_error("Failed to start server")
        return 1
    
    # Wait for server to be ready
    if not wait_for_server():
        server_process.terminate()
        return 1
    
    print()
    print_header("DEMO SEQUENCE")
    
    try:
        # Run demo scenarios
        demo_normal_behavior()
        demo_rapid_rotation()
        demo_summary()
        demo_detailed_alerts()
        demo_privacy_explanation()
        demo_api_endpoints()
        
        # Final summary
        print_header("DEMO COMPLETE ✓")
        print_success("This demo showcased:")
        print("  • Event ingestion and storage")
        print("  • Anomaly detection (rapid IPv6 rotation)")
        print("  • Privacy-preserving pseudonymization")
        print("  • Redacted alert generation")
        print("  • Explainable security insights")
        print()
        print_info("The system is still running. Test it with:")
        print(f"  • API: {API_BASE_URL}/docs (Swagger UI)")
        print(f"  • Events: POST {API_BASE_URL}/api/v1/events")
        print(f"  • Summary: GET {API_BASE_URL}/api/v1/summary")
        print()
        print_warning("Press Ctrl+C to stop the server")
        print()
        
        # Keep server running
        server_process.wait()
        
    except KeyboardInterrupt:
        print()
        print_info("Shutting down...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print_success("Server stopped cleanly")
        return 0
    except Exception as e:
        print_error(f"Demo error: {str(e)}")
        server_process.terminate()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
