"""
Automated Test Suite for Student API (FastAPI)
Tests all routes: Root, Health, Student CRUD operations, and Error Handling.
Supports both in-process testing via FastAPI TestClient and live testing via requests.
"""

import sys
import os
import argparse
import warnings
from typing import Optional

# Suppress library deprecation warnings for cleaner test reports
warnings.filterwarnings("ignore")

def run_tests(base_url: Optional[str] = None):
    print("=" * 70)
    print("  STUDENT API AUTOMATED TEST SUITE")
    print("=" * 70)

    use_live_server = False
    client = None

    if base_url:
        import requests
        use_live_server = True
        base_url = base_url.rstrip("/")
        print(f"[INFO] Running tests against live server: {base_url}")
    else:
        try:
            from fastapi.testclient import TestClient
            from main import app
            client = TestClient(app)
            print("[INFO] Running in-process tests using FastAPI TestClient")
        except Exception as e:
            print(f"[WARN] TestClient initialization failed: {e}. Falling back to live request on http://127.0.0.1:8000")
            import requests
            use_live_server = True
            base_url = "http://127.0.0.1:8000"

    passed = 0
    failed = 0

    def request(method: str, path: str, json_data: dict = None):
        if use_live_server:
            import requests
            url = f"{base_url}{path}"
            return requests.request(method=method, url=url, json=json_data)
        else:
            return client.request(method=method, url=path, json=json_data)

    testcases = []

    # 1. Test Root Endpoint
    def test_root():
        res = request("GET", "/")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data.get("application") == "Student API", f"Unexpected application: {data}"
        assert data.get("status") == "running", f"Unexpected status: {data}"

    testcases.append(("GET /", "Root endpoint returns application metadata", test_root))

    # 2. Test Health Check Endpoint
    def test_health():
        res = request("GET", "/health")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data.get("status") == "healthy", f"Expected healthy status, got {data}"

    testcases.append(("GET /health", "Health check endpoint returns healthy status", test_health))

    # 3. Test CI/CD Demo Route
    def test_new_route():
        res = request("GET", "/new")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert "message" in data, "Expected message in /new response"

    testcases.append(("GET /new", "CI/CD verification route returns expected message", test_new_route))

    # 4. Test List Students
    def test_list_students():
        res = request("GET", "/students")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert isinstance(data, list), "Expected list of students"
        assert len(data) >= 2, f"Expected at least 2 initial students, found {len(data)}"

    testcases.append(("GET /students", "List all students returns student array", test_list_students))

    # 5. Test Get Student By Valid ID
    def test_get_student_by_id():
        res = request("GET", "/students/1")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["id"] == 1, f"Expected id 1, got {data.get('id')}"
        assert data["name"] == "Aarav", f"Expected name 'Aarav', got {data.get('name')}"

    testcases.append(("GET /students/1", "Get student by valid ID returns student details", test_get_student_by_id))

    # 6. Test Create New Student
    created_id = {"id": None}
    def test_create_student():
        payload = {"name": "Kanishka", "course": "Cloud Computing & DevOps"}
        res = request("POST", "/students", json_data=payload)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}"
        data = res.json()
        assert data["name"] == "Kanishka", f"Expected name 'Kanishka', got {data.get('name')}"
        assert data["course"] == "Cloud Computing & DevOps", f"Expected course match, got {data.get('course')}"
        assert "id" in data, "Expected generated student id"
        created_id["id"] = data["id"]

    testcases.append(("POST /students", "Create new student with valid payload returns 201", test_create_student))

    # 7. Test Retrieve Created Student
    def test_retrieve_created_student():
        new_id = created_id["id"]
        assert new_id is not None, "Previous student creation did not yield an ID"
        res = request("GET", f"/students/{new_id}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["id"] == new_id, f"Expected ID {new_id}, got {data.get('id')}"
        assert data["name"] == "Kanishka"

    testcases.append(("GET /students/{id}", "Retrieve newly created student by ID", test_retrieve_created_student))

    # 8. Test Delete Created Student
    def test_delete_student():
        new_id = created_id["id"]
        assert new_id is not None
        res = request("DELETE", f"/students/{new_id}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"

    testcases.append(("DELETE /students/{id}", "Delete created student returns 200", test_delete_student))

    # 9. Test Non-existent Student Returns 404
    def test_not_found():
        res = request("GET", "/students/99999")
        assert res.status_code == 404, f"Expected 404 for missing student, got {res.status_code}"

    testcases.append(("GET /students/99999 (404)", "Non-existent student ID returns 404 Not Found", test_not_found))

    # 10. Test Validation Error on Invalid Creation Payload
    def test_validation_error():
        res = request("POST", "/students", json_data={})
        assert res.status_code == 422, f"Expected 422 for invalid payload, got {res.status_code}"

    testcases.append(("POST /students (Invalid)", "Empty payload returns 422 Unprocessable Entity", test_validation_error))

    # Execute all test cases
    for endpoint, description, test_fn in testcases:
        try:
            test_fn()
            print(f"[PASS] {endpoint:<25} - {description}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {endpoint:<25} - {description}")
            print(f"       Error: {e}")
            failed += 1

    print("-" * 70)
    print(f"Test Summary: Total={len(testcases)} | Passed={passed} | Failed={failed}")
    print("=" * 70)

    if failed > 0:
        print("[RESULT] TESTS FAILED")
        sys.exit(1)
    else:
        print("[RESULT] ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated API Tests for Student API")
    parser.add_argument("--url", default=os.getenv("API_URL"), help="Live server base URL (e.g., http://localhost:8000)")
    args = parser.parse_args()

    run_tests(base_url=args.url)
