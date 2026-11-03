# Testing

## API

Pruebas del componente `api`, derivadas de la sección `api` de [ENDPOINTS.md](ENDPOINTS.md). Código en `api/tests/test_endpoints.py` (nuevo) y `api/tests/test_api.py` (existente, sin cambios).

### Línea base previa (2026-11-02)

| Dato | Valor |
|---|---|
| Fecha | 2026-11-02 |
| Componente / IDs | api / H-API-02, H-API-03, H-API-04 (bugs que los xfail dejan visibles) |
| Directorio | `api/` |
| Intérprete | `api/.venv/Scripts/python.exe` (Python 3.13.15, Windows) |
| Comando | `python -m pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=85` (el mismo que `python tools/lab.py test api`) |
| Código de salida | **0** |
| Resultado | **33 passed, 7 xfailed**, 83 avisos de deprecación (`on_event` de FastAPI, `BlockingPortal` de Starlette) |
| Informe HTML | `api/htmlcov/index.html` |

### Cobertura de la línea base

| Métrica | Numerador / denominador | Resultado |
|---|---|---|
| **Código modificado** | 0 / 0 | No aplica: esta entrega no modificó código de producción (`api/app/`); solo agregó tests. |
| **Global** (`api/app/main.py`), sentencias | 96 / 96 | 100 % |
| **Global**, ramas | 16 / 16 | 100 % |
| **Global**, métrica combinada de coverage.py | 100 % | Umbral `--cov-fail-under=85` alcanzado |
| Línea base previa (solo `test_api.py`, 4 tests) | 89 / 96 sentencias; 3 ramas parciales | 91 %; sin cubrir: líneas 23, 102->95, 103->95, 116-121 |

Método: coverage.py vía `pytest-cov` con `branch = true` y `source = ["app"]` (`api/pyproject.toml`). El 100 % mide que las líneas se ejecutan, no que el comportamiento sea correcto: los 7 tests xfail ejecutan código con bugs conocidos.

### Ejecución H-API-08 (2026-11-03)

| Dato | Valor |
|---|---|
| Componente / IDs | api / H-API-08 |
| Comando de suite | `python tools/lab.py test api` |
| Resultado | Salida 0; **36 passed, 7 xfailed**, 89 avisos de deprecación. |
| Cobertura | 99 / 99 sentencias, 18 / 18 ramas; **100 %**, sobre el umbral requerido de 85 %. |
| Pruebas focalizadas | `Push-Location api; try { & .\.venv\Scripts\python.exe -m pytest -q tests\test_endpoints.py -k size_limit } finally { Pop-Location }` → **3 passed**. |
| Test-first | Antes de implementar, el caso de 101 bytes falló al recibir `201` en vez del `402` acordado. Tras el cambio, los 3 casos de frontera pasan. |
| Informe HTML | `api/htmlcov/index.html` |

Las pruebas nuevas aceptan archivos de 99 y 100 bytes y rechazan uno de 101 bytes con `402` y `{"detail":"File exceeds the 100-byte limit"}`; también verifican que el archivo rechazado no se almacene.

### Casos por endpoint

Tipos: **H** = camino feliz, **B** = caso borde, **E** = error documentado, **S** = seguridad (comportamiento correcto que hoy falla).

| endpoint | caso | tipo | resultado esperado | estado |
|---|---|---|---|---|
| Todos | Sin header `Authorization` (parametrizado en los 5 endpoints) | E | `401`, `detail` empieza con `Invalid token` | pasa |
| `GET /api/tasks` | Token no Base64, expirado, secreto incorrecto, expiración no numérica, esquema `Token` | E | `401`, `detail` empieza con `Invalid token` | pasa |
| `GET /api/tasks` | Usuario `student` con datos iniciales | H | `200`, ids `[1, 2]`, 7 campos exactos, todos de `student` | pasa |
| `GET /api/tasks` | `owner` sin tareas | B | `200`, `[]` | pasa |
| `GET /api/tasks` | `owner=` vacío | B | Usa el usuario del token | pasa |
| `GET /api/tasks` | Token sin prefijo `Bearer` | B | `200` (comportamiento documentado) | pasa |
| `GET /api/tasks` | `student` pide `owner=trainer` | S | No recibe tareas de `trainer` | **xfail** H-API-02 |
| `GET /api/tasks` | `owner` con comilla simple | S | `200` | **xfail** H-API-03 |
| `POST /api/tasks` | Payload completo | H | `201`, 7 campos, `owner` = token, `id` 4, aparece en el listado | pasa |
| `POST /api/tasks` | Objeto vacío `{}` | B | `201` con valores por defecto (`""`, `""`, `TODO`, `MEDIUM`, usuario) | pasa |
| `POST /api/tasks` | Sin cuerpo | E | `422`, tipo `missing` | pasa |
| `POST /api/tasks` | Cuerpo que no es objeto (`[1]`) | E | `422`, tipo `dict_type` | pasa |
| `POST /api/tasks` | `student` asigna `owner=trainer` | S | `403` o `owner` = `student` | **xfail** H-API-02 |
| `POST /api/tasks` | `title` con comilla simple | S | `201`, título almacenado literalmente | **xfail** H-API-03 |
| `GET /api/summary` | `student` con datos iniciales | H | `{"owner":"student","total":2,"byStatus":{"TODO":1,"IN_PROGRESS":1},"highPriorityOpen":1}` | pasa |
| `GET /api/summary` | Propietario sin tareas | B | `total` 0, `byStatus` `{}`, `highPriorityOpen` 0 | pasa |
| `GET /api/summary` | Tareas `HIGH` en `DONE` y `ARCHIVED` | B | No cuentan; una `HIGH` en `TODO` sí (1 → 2) | pasa |
| `GET /api/summary` | `student` pide `owner=trainer` | S | `403` o `owner` = `student` | **xfail** H-API-02 |
| `GET /api/summary` | `owner` con comilla simple | S | `200` | **xfail** H-API-03 |
| `POST /api/requirements` | `requirements.txt` | H | `201`, 4 campos, `size` correcto, bytes guardados | pasa |
| `POST /api/requirements` | Archivo sin extensión (`README`) | B | `201`, archivo guardado | pasa |
| `POST /api/requirements` | Archivo vacío | B | `201`, `size` 0 | pasa |
| `POST /api/requirements` | Archivo de 99 bytes | B | `201`, contenido guardado | pasa H-API-08 |
| `POST /api/requirements` | Archivo de 100 bytes | B | `201`, contenido guardado | pasa H-API-08 |
| `POST /api/requirements` | Archivo de 101 bytes | E | `402`, `detail` estable, no se almacena | pasa H-API-08 |
| `POST /api/requirements` | Mismo nombre dos veces | B | El segundo contenido sobrescribe | pasa |
| `POST /api/requirements` | Sin campo `file` | E | `422`, `loc` `["body","file"]` | pasa |
| `POST /api/requirements` | Nombre `../escape.txt` | S | No se crea fuera del directorio de subidas | **xfail** H-API-04 |
| `GET /api/backend-health` | Servicio local responde `200` | H | `200`, `status` 200 y `body` relayado | pasa |
| `GET /api/backend-health` | Servicio responde `503` | B | `200`, `status` 503, `body` relayado | pasa |
| `GET /api/backend-health` | Servicio inalcanzable | E | `200`, `status` 0, `body` con texto no vacío | pasa |

### Fallos, bugs y pendientes

**Fallos reales:** ninguno en la ejecución oficial.

**Bugs encontrados (7 tests xfail, reportados aparte, no ocultos):** cada test afirma el comportamiento correcto y está marcado `xfail(strict=True)` con el ID del hallazgo. No se modificó ninguna aserción para que pase. Sin la marca, los 7 fallan por aserción, no por un error del propio test (`--runxfail`, código de salida 1):

| test | hallazgo | evidencia observada |
|---|---|---|
| `test_list_tasks_user_cannot_read_other_owner_tasks` | H-API-02 | `student` recibe la tarea de `trainer` (id 3) |
| `test_create_task_user_cannot_assign_other_owner` | H-API-02 | `201` con `owner` = `trainer` |
| `test_summary_user_cannot_read_other_owner` | H-API-02 | `200` con `owner` = `trainer` |
| `test_list_tasks_owner_with_quote_does_not_fail` | H-API-03 | `500` en lugar de `200` |
| `test_create_task_stores_title_with_quote_literally` | H-API-03 | `500` en lugar de `201` |
| `test_summary_owner_with_quote_does_not_fail` | H-API-03 | `500` en lugar de `200` |
| `test_upload_requirement_cannot_escape_upload_dir` | H-API-04 | `escape.txt` existe fuera del directorio de subidas (dentro del directorio temporal de la prueba) |

`strict=True` hace que, al corregir un hallazgo, el test pase a XPASS y falle hasta quitar la marca; así no queda un xfail obsoleto.

**Desviación respecto a ENDPOINTS.md:** el documento lista `500` como respuesta de error para comillas en `owner` y en los campos. No hay un test que fije ese `500` como esperado, porque eso consolidaría el bug. Esos casos quedan cubiertos por los xfail H-API-03.

**Pendientes y pruebas propuestas (no implementadas):**

| propuesta | motivo |
|---|---|
| Extensiones permitidas en `POST /api/requirements` | No existe una allowlist; depende de una decisión pendiente en PLAN.md (H-API-04). El límite de 100 bytes se implementó en H-API-08. |
| `detail` del 401 y `body` de `backend-health` no deben filtrar texto de excepciones | Hoy exponen mensajes internos (H-API-07); no es un contrato documentado, es una propuesta de seguridad. |
| JSON malformado en `POST /api/tasks` | Respuesta no verificada (pregunta abierta en ENDPOINTS.md). |
| Nombre de archivo con subdirectorios inexistentes | Respuesta no verificada (pregunta abierta en ENDPOINTS.md). |
| Valores no válidos de `status` y `priority` | El código no los restringe; falta definir el contrato. |
| Token con firma JWT, emisor y audiencia | Requiere implementar H-API-01. |

### Notas de ejecución

- Cada test usa base SQLite y directorio de subidas bajo `tmp_path`. `backend-health` usa un servidor HTTP local en `127.0.0.1` con puerto efímero; no hay llamadas a servicios remotos.
- Al importar `app.main` se ejecuta `create_app()` con las rutas por defecto, lo que crea `api/data` y `api/uploads`. Los `.gitignore` de `api` excluyen sus contenidos (`*.db`, `uploads/*`).
- Las pruebas fijan el comportamiento observado del token (formato Base64 con secreto compartido). Cambiarán cuando se resuelva H-API-01.
- `api/tests/test_api.py` (4 tests de la plantilla) se conserva; sus casos de camino feliz se solapan con los de `test_endpoints.py`.

### Código de los tests

Archivo canónico: [api/tests/test_endpoints.py](../api/tests/test_endpoints.py). Copia de la versión ejecutada:

```python
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
```

### Documentos consultados

[ENDPOINTS.md](ENDPOINTS.md), [HALLAZGOS.md](../HALLAZGOS.md), [PLAN.md](../PLAN.md), [GOOD_PRACTICES.md](GOOD_PRACTICES.md), README.md, `tools/lab.py` (comando oficial de pruebas de `api`), `api/pyproject.toml`, `api/requirements-dev.txt` y `api/.gitignore`.
