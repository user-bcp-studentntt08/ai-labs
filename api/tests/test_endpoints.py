"""Pruebas de contrato por endpoint (camino feliz, bordes y errores) segun docs/ENDPOINTS.md.

Los tests marcados `xfail(strict=True)` afirman el comportamiento correcto y fallan hoy por un
hallazgo abierto de HALLAZGOS.md; al corregirlo pasan a XPASS, que strict convierte en fallo.
"""
import base64
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

TOKEN_SECRET = "WORKSHOP_SECRET_2026"
TASK_FIELDS = {"id", "title", "description", "status", "owner", "priority", "createdAt"}
INVALID_TOKEN_PREFIX = "Invalid token"
SECONDS_PER_HOUR = 3600
ONE_BYTE_FILE = b"x"
MAX_UPLOAD_BYTES = 100

Headers = dict[str, str]


def bearer(username: str = "student", expires_in: int = SECONDS_PER_HOUR, secret: str = TOKEN_SECRET, expiry: str | None = None) -> Headers:
    expiry_field = expiry if expiry is not None else str(int(time.time()) + expires_in)
    raw = f"{username}|STUDENT|{expiry_field}|{secret}"
    return {"Authorization": "Bearer " + base64.b64encode(raw.encode()).decode()}


@pytest.fixture
def upload_dir(tmp_path: Path) -> Path:
    return tmp_path / "uploads"


@pytest.fixture
def client(tmp_path: Path, upload_dir: Path) -> Iterator[TestClient]:
    app = create_app(str(tmp_path / "workshop.db"), str(upload_dir))
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        down = self.path == "/down"
        body = b'{"status":"DOWN"}' if down else b'{"status":"UP","checks":[]}'
        self.send_response(503 if down else 200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


@pytest.fixture(scope="module")
def health_server() -> Iterator[str]:
    server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def _unused_local_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


PROTECTED_REQUESTS = [
    pytest.param("GET", "/api/tasks", {}, id="GET-tasks"),
    pytest.param("POST", "/api/tasks", {"json": {"title": "x"}}, id="POST-tasks"),
    pytest.param("GET", "/api/summary", {}, id="GET-summary"),
    pytest.param("POST", "/api/requirements", {"files": {"file": ("a.txt", ONE_BYTE_FILE, "text/plain")}}, id="POST-requirements"),
    pytest.param("GET", "/api/backend-health", {}, id="GET-backend-health"),
]


# --- Autenticacion (401) en todos los endpoints -------------------------------------------------

@pytest.mark.parametrize(("method", "path", "options"), PROTECTED_REQUESTS)
def test_every_endpoint_rejects_missing_token(client: TestClient, method: str, path: str, options: dict) -> None:
    response = client.request(method, path, **options)
    assert response.status_code == 401
    assert response.json()["detail"].startswith(INVALID_TOKEN_PREFIX)


@pytest.mark.parametrize(
    "headers",
    [
        pytest.param({"Authorization": "Bearer invalid"}, id="not-base64"),
        pytest.param(bearer(expires_in=-10), id="expired"),
        pytest.param(bearer(secret="wrong"), id="wrong-secret"),
        pytest.param(bearer(expiry="abc"), id="non-numeric-expiry"),
        pytest.param({"Authorization": "Token abc"}, id="other-scheme"),
    ],
)
def test_tasks_rejects_invalid_tokens(client: TestClient, headers: Headers) -> None:
    response = client.get("/api/tasks", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"].startswith(INVALID_TOKEN_PREFIX)


# --- GET /api/tasks -----------------------------------------------------------------------------

def test_list_tasks_returns_own_seeded_tasks_in_id_order(client: TestClient) -> None:
    response = client.get("/api/tasks", headers=bearer())
    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [1, 2]
    assert all(set(task) == TASK_FIELDS and task["owner"] == "student" for task in tasks)


def test_list_tasks_unknown_owner_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/tasks", params={"owner": "nobody"}, headers=bearer("nobody"))
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_empty_owner_falls_back_to_token_user(client: TestClient) -> None:
    response = client.get("/api/tasks", params={"owner": ""}, headers=bearer())
    assert [task["owner"] for task in response.json()] == ["student", "student"]


def test_list_tasks_accepts_token_without_bearer_prefix(client: TestClient) -> None:
    raw_token = bearer()["Authorization"].removeprefix("Bearer ")
    response = client.get("/api/tasks", headers={"Authorization": raw_token})
    assert response.status_code == 200


@pytest.mark.xfail(strict=True, reason="H-API-02: el cliente elige `owner`")
def test_list_tasks_user_cannot_read_other_owner_tasks(client: TestClient) -> None:
    response = client.get("/api/tasks", params={"owner": "trainer"}, headers=bearer("student"))
    leaked = [task for task in response.json() if task["owner"] == "trainer"] if response.status_code == 200 else []
    assert leaked == []


@pytest.mark.xfail(strict=True, reason="H-API-03: `owner` se concatena en el SQL")
def test_list_tasks_owner_with_quote_does_not_fail(client: TestClient) -> None:
    response = client.get("/api/tasks", params={"owner": "a'b"}, headers=bearer())
    assert response.status_code == 200


# --- POST /api/tasks ----------------------------------------------------------------------------

def test_create_task_returns_created_task_and_lists_it(client: TestClient) -> None:
    payload = {"title": "Add tests", "description": "Improve coverage", "status": "IN_PROGRESS", "priority": "HIGH"}
    created = client.post("/api/tasks", json=payload, headers=bearer())
    assert created.status_code == 201
    body = created.json()
    assert set(body) == TASK_FIELDS
    assert {key: body[key] for key in payload} == payload
    assert body["owner"] == "student" and body["id"] == 4
    listed = client.get("/api/tasks", headers=bearer()).json()
    assert body in listed


def test_create_task_with_empty_object_uses_defaults(client: TestClient) -> None:
    response = client.post("/api/tasks", json={}, headers=bearer())
    assert response.status_code == 201
    body = response.json()
    assert (body["title"], body["description"], body["status"], body["priority"], body["owner"]) == ("", "", "TODO", "MEDIUM", "student")


def test_create_task_without_body_returns_422(client: TestClient) -> None:
    response = client.post("/api/tasks", headers=bearer())
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"


def test_create_task_with_non_object_body_returns_422(client: TestClient) -> None:
    response = client.post("/api/tasks", json=[1], headers=bearer())
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "dict_type"


@pytest.mark.xfail(strict=True, reason="H-API-02: el cliente puede asignar `owner`")
def test_create_task_user_cannot_assign_other_owner(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "x", "owner": "trainer"}, headers=bearer("student"))
    assert response.status_code == 403 or response.json()["owner"] == "student"


@pytest.mark.xfail(strict=True, reason="H-API-03: los campos se concatenan en el INSERT")
def test_create_task_stores_title_with_quote_literally(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "it's"}, headers=bearer())
    assert response.status_code == 201
    assert response.json()["title"] == "it's"


# --- GET /api/summary ---------------------------------------------------------------------------

def test_summary_counts_own_tasks(client: TestClient) -> None:
    response = client.get("/api/summary", headers=bearer())
    assert response.status_code == 200
    assert response.json() == {"owner": "student", "total": 2, "byStatus": {"TODO": 1, "IN_PROGRESS": 1}, "highPriorityOpen": 1}


def test_summary_without_tasks_is_empty(client: TestClient) -> None:
    response = client.get("/api/summary", params={"owner": "nobody"}, headers=bearer("nobody"))
    assert response.json() == {"owner": "nobody", "total": 0, "byStatus": {}, "highPriorityOpen": 0}


def test_summary_high_priority_open_ignores_done_and_archived(client: TestClient) -> None:
    for status in ("DONE", "ARCHIVED"):
        client.post("/api/tasks", json={"title": status, "status": status, "priority": "HIGH"}, headers=bearer())
    assert client.get("/api/summary", headers=bearer()).json()["highPriorityOpen"] == 1
    client.post("/api/tasks", json={"title": "open", "status": "TODO", "priority": "HIGH"}, headers=bearer())
    assert client.get("/api/summary", headers=bearer()).json()["highPriorityOpen"] == 2


@pytest.mark.xfail(strict=True, reason="H-API-02: el cliente elige `owner`")
def test_summary_user_cannot_read_other_owner(client: TestClient) -> None:
    response = client.get("/api/summary", params={"owner": "trainer"}, headers=bearer("student"))
    assert response.status_code == 403 or response.json()["owner"] == "student"


@pytest.mark.xfail(strict=True, reason="H-API-03: `owner` se concatena en el SQL")
def test_summary_owner_with_quote_does_not_fail(client: TestClient) -> None:
    response = client.get("/api/summary", params={"owner": "a'b"}, headers=bearer())
    assert response.status_code == 200


# --- POST /api/requirements ---------------------------------------------------------------------

def upload(client: TestClient, filename: str, content: bytes):
    return client.post("/api/requirements", files={"file": (filename, content, "text/plain")}, headers=bearer())


def test_upload_requirement_stores_file_and_reports_it(client: TestClient, upload_dir: Path) -> None:
    content = b"Login must be accessible"
    response = upload(client, "requirements.txt", content)
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"owner", "fileName", "storedAt", "size"}
    assert (body["owner"], body["fileName"], body["size"]) == ("student", "requirements.txt", len(content))
    assert (upload_dir / "requirements.txt").read_bytes() == content


def test_upload_requirement_without_extension(client: TestClient, upload_dir: Path) -> None:
    response = upload(client, "README", b"no extension")
    assert response.status_code == 201
    assert (upload_dir / "README").read_bytes() == b"no extension"


def test_upload_requirement_empty_file_reports_zero_size(client: TestClient, upload_dir: Path) -> None:
    response = upload(client, "empty.txt", b"")
    assert response.status_code == 201
    assert response.json()["size"] == 0
    assert (upload_dir / "empty.txt").read_bytes() == b""


@pytest.mark.parametrize("size", [MAX_UPLOAD_BYTES - 1, MAX_UPLOAD_BYTES])
def test_upload_requirement_accepts_files_at_or_below_size_limit(
    client: TestClient, upload_dir: Path, size: int
) -> None:
    content = b"x" * size
    response = upload(client, "within-limit.txt", content)

    assert response.status_code == 201
    assert response.json()["size"] == size
    assert (upload_dir / "within-limit.txt").read_bytes() == content


def test_upload_requirement_rejects_file_above_size_limit(client: TestClient, upload_dir: Path) -> None:
    response = upload(client, "too-large.txt", b"x" * (MAX_UPLOAD_BYTES + 1))

    assert response.status_code == 402
    assert response.json() == {"detail": "File exceeds the 100-byte limit"}
    assert not (upload_dir / "too-large.txt").exists()


def test_upload_requirement_same_name_overwrites_previous_file(client: TestClient, upload_dir: Path) -> None:
    upload(client, "requirements.txt", b"first")
    upload(client, "requirements.txt", b"second")
    assert (upload_dir / "requirements.txt").read_bytes() == b"second"


def test_upload_requirement_without_file_returns_422(client: TestClient) -> None:
    response = client.post("/api/requirements", headers=bearer())
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "file"]


@pytest.mark.xfail(strict=True, reason="H-API-04: el nombre del archivo se usa como ruta")
def test_upload_requirement_cannot_escape_upload_dir(client: TestClient, tmp_path: Path) -> None:
    upload(client, "../escape.txt", b"outside")
    assert not (tmp_path / "escape.txt").exists()


# --- GET /api/backend-health --------------------------------------------------------------------

def test_backend_health_relays_service_response(client: TestClient, health_server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_HEALTH_URL", health_server + "/q/health")
    response = client.get("/api/backend-health", headers=bearer())
    assert response.status_code == 200
    assert response.json() == {"requestedBy": "student", "status": 200, "body": '{"status":"UP","checks":[]}'}


def test_backend_health_relays_non_200_status_from_service(client: TestClient, health_server: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_HEALTH_URL", health_server + "/down")
    response = client.get("/api/backend-health", headers=bearer())
    assert response.status_code == 200
    assert (response.json()["status"], response.json()["body"]) == (503, '{"status":"DOWN"}')


def test_backend_health_unreachable_service_returns_status_zero(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_HEALTH_URL", f"http://127.0.0.1:{_unused_local_port()}/q/health")
    response = client.get("/api/backend-health", headers=bearer())
    assert response.status_code == 200
    body = response.json()
    assert (body["requestedBy"], body["status"]) == ("student", 0)
    assert isinstance(body["body"], str) and body["body"]
