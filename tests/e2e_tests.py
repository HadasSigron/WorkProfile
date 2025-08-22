import requests
import time
import sys
import os

NGINX_URL = os.environ.get("NGINX_URL", "http://localhost:8080")


def get(path="/", timeout=10):
    return requests.get(f"{NGINX_URL}{path}", timeout=timeout)


def wait_for_stack(max_retries=60, delay=2):
    print("Waiting for 3-tier stack (nginx -> app -> database) to be ready...")
    for attempt in range(max_retries):
        try:
            r = get("/health")
            if r.status_code == 200:
                data = r.json()
                if (
                    data.get("status") == "healthy"
                    and data.get("components", {}).get("application") == "running"
                ):
                    print(f"✓ stack ready after {attempt*delay} seconds")
                    return True
        except requests.RequestException:
            pass
        print(f"Attempt {attempt+1}/{max_retries} - waiting {delay} seconds...")
        time.sleep(delay)
    print("✗ stack did not become ready in time")
    return False


def test_nginx_proxy():
    print("🔎 Testing NGINX reverse proxy...")
    r = get("/")
    assert r.status_code == 200


def test_health_endpoint():
    print("🔎 Testing /health endpoint (JSON)...")
    r = get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"
    assert data.get("components", {}).get("application") == "running"


def test_main_page():
    print("🔎 Testing main page...")
    r = get("/")
    assert r.status_code == 200
    txt = r.text.lower()
    assert "workprofile" in txt or "people" in txt


def test_3tier_architecture():
    print("🔎 Testing 3-tier architecture (nginx -> app -> mysql via app health)...")
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

    tests = [
        test_nginx_proxy,
        test_health_endpoint,
        test_main_page,
        test_3tier_architecture,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"✗ {t.__name__} failed: {e}")

    print(f"\n=== E2E Test Results: {passed}/{len(tests)} passed ===")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    run_all_tests()

