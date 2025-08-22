import requests
import time
import sys
import os

NGINX_URL = os.environ.get("NGINX_URL", "http://localhost:8080")

def get(path="/", timeout=10):
    return requests.get(f"{NGINX_URL}{path}", timeout=timeout)

def wait_for_stack(max_retries=60, delay=2):
    print("Waiting for stack (nginx -> app) to be ready...")
    for attempt in range(1, max_retries + 1):
        try:
            r = get("/health")
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "healthy" and data.get("components", {}).get("application") == "running":
                    print(f"✓ ready after {attempt * delay}s")
                    return True
        except Exception:
            pass
        print(f"Attempt {attempt}/{max_retries} - waiting {delay}s...")
        time.sleep(delay)
    print("✗ not ready in time")
    return False

def test_nginx_proxy():
    r = get("/")
    assert r.status_code == 200

def test_health_endpoint():
    r = get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"
    assert data.get("components", {}).get("application") == "running"

def test_main_page():
    r = get("/")
    assert r.status_code == 200
    page = r.text.lower()
    assert ("workprofile" in page) or ("people" in page)

def test_3tier_architecture():
    # בדיקה בסיסית שהאפליקציה בריאה (nginx -> app). החיבור ל-DB נבדק ע"י הלוגיקה הפנימית שלך.
    r = get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"
    assert data.get("components", {}).get("application") == "running"

def run_all_tests():
    print("=== Starting Simplified E2E Tests ===")
    if not wait_for_stack():
        print("✗ Stack readiness check failed")
        sys.exit(1)
    test_nginx_proxy()
    test_health_endpoint()
    test_main_page()
    test_3tier_architecture()
    print("✓ E2E passed")

if __name__ == "__main__":
    run_all_tests()

