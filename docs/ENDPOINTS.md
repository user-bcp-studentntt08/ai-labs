# Endpoints

## API

API FastAPI de tareas y requerimientos (`api/app/main.py`).

### Estado del contrato

- **Contrato observado:** todo lo descrito abajo. Se verificó leyendo `api/app/main.py` y ejecutando la API localmente (`create_app` con base SQLite y directorio de subidas temporales, datos ficticios, 2026-11-02). Los cuerpos de ejemplo son salidas reales de esa ejecución, salvo donde se indique lo contrario.
- **Contrato acordado:** no existe un contrato acordado por escrito. Este documento no lo sustituye.
- **Estado del código:** los hallazgos H-API-01 a H-API-07 de `HALLAZGOS.md` siguen sin corregir en este código. Por eso las notas de seguridad describen los riesgos vigentes, no un estado refactorizado.
- **Secciones de otros componentes:** este archivo solo documenta `api`. Las secciones de `auth` y `web` no existían al crearlo.

### Convenciones comunes

- **URL base local:** `http://localhost:8000`. Documentación interactiva generada por FastAPI: `http://localhost:8000/docs`.
- **Formato:** las respuestas JSON usan `application/json`. Los errores 500 no controlados se devuelven como texto plano.
- **CORS:** acepta cualquier origen (`allow_origins=["*"]`), con credenciales, y cualquier método y cabecera (`api/app/main.py`, `add_middleware`).
- **Token:** todos los endpoints exigen el header `Authorization`. Formato del valor del token observado en `legacy_identity`:

  ```text
  base64( <username> | <role> | <expiración en segundos epoch> | <secreto compartido> )
  ```

  El secreto compartido es la constante `LEGACY_SECRET` de `api/app/main.py`; este documento no lo reproduce. Se envía como `Authorization: Bearer <token>`. El prefijo `Bearer ` se elimina con `replace`, y el servidor también aceptó el token sin ese prefijo (`200`). Otros prefijos, como `Token <token>`, devuelven `401`. El token expira cuando su expiración es anterior a la hora actual. El `role` se lee pero ningún endpoint lo usa.
- **Errores de autenticación (`401`) comunes:** cualquier fallo del token devuelve `401` con `{"detail": "Invalid token: <mensaje interno>"}`. El mensaje cambia según la causa. Ejemplos reales:

  | Causa | Cuerpo |
  |---|---|
  | Header `Authorization` ausente, secreto incorrecto o token expirado | `{"detail":"Invalid token: invalid token"}` |
  | Valor que no es Base64 válido (`Bearer invalid`) | `{"detail":"Invalid token: Incorrect padding"}` |
  | Expiración no numérica | `{"detail":"Invalid token: invalid literal for int() with base 10: 'abc'"}` |
  | Token con texto no decodificable como UTF-8 (`Token <token>`) | `{"detail":"Invalid token: 'utf-8' codec can't decode byte 0x89 in position 1: invalid start byte"}` |

- **Datos iniciales:** una base nueva contiene 3 tareas: dos del propietario `student` y una de `trainer`.
- **Tarea (`Task`):** objeto que devuelven los endpoints de tareas.

  | campo | tipo | descripción |
  |---|---|---|
  | `id` | entero | Identificador autoincremental. |
  | `title` | string | Título. |
  | `description` | string | Descripción. |
  | `status` | string | Estado. El código no restringe los valores; los datos iniciales usan `TODO` e `IN_PROGRESS`. El resumen reconoce `DONE` y `ARCHIVED`. |
  | `owner` | string | Propietario de la tarea. |
  | `priority` | string | Prioridad. El código no restringe los valores; los datos iniciales usan `HIGH`, `MEDIUM` y `LOW`. El resumen reconoce `HIGH`. |
  | `createdAt` | string | Fecha de creación en formato `AAAA-MM-DD HH:MM:SS`, generada con `datetime('now')` de SQLite. |

---

### 1. `GET /api/tasks`

**1. Qué hace.** Lista las tareas de un propietario para mostrar su tablero de trabajo.

**2. Autenticación.** Sí. Header exacto: `Authorization: Bearer <token>`.

**3. Request.**

| parámetro | ubicación | tipo | obligatorio | descripción |
|---|---|---|---|---|
| `owner` | query | string | No | Propietario cuyas tareas se listan. Si se omite o es una cadena vacía, se usa el `username` del token. |

Ejemplo:

```http
GET /api/tasks?owner=trainer HTTP/1.1
Host: localhost:8000
Authorization: Bearer <token>
```

**4. Respuesta exitosa.** `200 OK`, `application/json`. Arreglo de `Task` ordenado por `id`; vacío si no hay coincidencias.

| campo | tipo | descripción |
|---|---|---|
| (elemento del arreglo) | `Task` | Ver tabla de `Task` en convenciones comunes. |

Ejemplo, con `owner=trainer`:

```json
[
  {
    "id": 3,
    "title": "Trainer notes",
    "description": "Preparar retrospectiva",
    "status": "TODO",
    "owner": "trainer",
    "priority": "LOW",
    "createdAt": "2026-11-02 22:09:21"
  }
]
```

Sin `owner`, con un token de `student`, devuelve las tareas con `id` 1 y 2. Con un propietario inexistente (`owner=zzz`) devuelve `[]`.

**5. Errores.**

| código | cuándo | cuerpo de ejemplo |
|---|---|---|
| `401` | Token ausente, inválido o expirado. | `{"detail":"Invalid token: invalid token"}` |
| `500` | El valor de `owner` contiene una comilla simple (`a'b`). | `Internal Server Error` (`text/plain`) |

**6. Notas de seguridad.**
- La autorización no está ligada a la identidad: cualquier usuario autenticado puede enviar `owner=trainer` y recibir sus tareas (comprobado: un token de `student` obtuvo la tarea de `trainer`). Corresponde a H-API-02.
- `owner` se concatena en el SQL (`api/app/main.py`, `list_tasks`); una comilla provoca un `500`. Corresponde a H-API-03.
- El token no tiene firma criptográfica (H-API-01).

---

### 2. `POST /api/tasks`

**1. Qué hace.** Crea una tarea nueva en el tablero.

**2. Autenticación.** Sí. Header exacto: `Authorization: Bearer <token>`.

**3. Request.** `Content-Type: application/json`. El cuerpo debe ser un objeto JSON. Todos sus campos son opcionales y el servidor convierte cada valor con `str()`.

| campo | tipo | obligatorio | descripción |
|---|---|---|---|
| `title` | string | No | Título. Por defecto `""`. |
| `description` | string | No | Descripción. Por defecto `""`. |
| `status` | string | No | Estado. Por defecto `"TODO"`. |
| `priority` | string | No | Prioridad. Por defecto `"MEDIUM"`. |
| `owner` | string | No | Propietario. Por defecto el `username` del token; si se envía, se respeta. |

Ejemplo:

```http
POST /api/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer <token>
Content-Type: application/json

{"title": "Add tests", "description": "Improve coverage", "status": "TODO", "priority": "HIGH"}
```

**4. Respuesta exitosa.** `201 Created`, `application/json`. Devuelve la `Task` creada.

| campo | tipo | descripción |
|---|---|---|
| `id` | entero | Identificador asignado. |
| `title`, `description`, `status`, `owner`, `priority`, `createdAt` | string | Ver tabla de `Task`. |

Ejemplo:

```json
{
  "id": 4,
  "title": "Add tests",
  "description": "Improve coverage",
  "status": "TODO",
  "owner": "student",
  "priority": "HIGH",
  "createdAt": "2026-11-02 22:09:21"
}
```

Con el cuerpo `{}` crea una tarea con `title` y `description` vacíos, `status` `TODO` y `priority` `MEDIUM`.

**5. Errores.**

| código | cuándo | cuerpo de ejemplo |
|---|---|---|
| `401` | Token ausente, inválido o expirado. | `{"detail":"Invalid token: invalid token"}` |
| `422` | No se envía cuerpo. | `{"detail":[{"type":"missing","loc":["body"],"msg":"Field required","input":null}]}` |
| `422` | El cuerpo no es un objeto JSON (por ejemplo `[1]`). | `{"detail":[{"type":"dict_type","loc":["body"],"msg":"Input should be a valid dictionary","input":[1]}]}` |
| `500` | Un campo de texto contiene una comilla simple (por ejemplo `title` igual a `it's`). | `Internal Server Error` (`text/plain`) |

**6. Notas de seguridad.**
- El cliente puede crear tareas asignadas a otro usuario enviando `owner` (comprobado con `"owner": "trainer"`). Corresponde a H-API-02.
- Los campos se concatenan en el `INSERT` (H-API-03); una comilla produce `500`.
- No se valida el valor de `status` ni de `priority`, ni la longitud de los textos.

---

### 3. `GET /api/summary`

**1. Qué hace.** Resume cuántas tareas tiene un propietario, cómo se reparten por estado y cuántas de prioridad alta siguen abiertas.

**2. Autenticación.** Sí. Header exacto: `Authorization: Bearer <token>`.

**3. Request.**

| parámetro | ubicación | tipo | obligatorio | descripción |
|---|---|---|---|---|
| `owner` | query | string | No | Propietario a resumir. Si se omite o es una cadena vacía, se usa el `username` del token. |

Ejemplo:

```http
GET /api/summary HTTP/1.1
Host: localhost:8000
Authorization: Bearer <token con username student>
```

**4. Respuesta exitosa.** `200 OK`, `application/json`.

| campo | tipo | descripción |
|---|---|---|
| `owner` | string | Propietario resumido. |
| `total` | entero | Cantidad de tareas del propietario. |
| `byStatus` | objeto (string → entero) | Cantidad de tareas por cada valor de `status` presente. Vacío si no hay tareas. |
| `highPriorityOpen` | entero | Tareas con `priority` `HIGH` cuyo `status` no es `DONE` ni `ARCHIVED`. |

Ejemplo, con la base inicial y un token de `student` (derivado de las dos tareas iniciales de `student`; con propietario `trainer` se observó `{"owner":"trainer","total":2,"byStatus":{"TODO":2},"highPriorityOpen":0}` tras crear una tarea adicional):

```json
{
  "owner": "student",
  "total": 2,
  "byStatus": {"TODO": 1, "IN_PROGRESS": 1},
  "highPriorityOpen": 1
}
```

Un propietario sin tareas devuelve `total` 0, `byStatus` `{}` y `highPriorityOpen` 0.

**5. Errores.**

| código | cuándo | cuerpo de ejemplo |
|---|---|---|
| `401` | Token ausente, inválido o expirado. | `{"detail":"Invalid token: invalid token"}` |
| `500` | El valor de `owner` contiene una comilla simple (`a'b`). | `Internal Server Error` (`text/plain`) |

**6. Notas de seguridad.**
- Igual que `GET /api/tasks`: cualquier usuario autenticado puede resumir a otro propietario con `owner` (comprobado con `owner=trainer`). H-API-02.
- `owner` se concatena en el SQL (H-API-03).

---

### 4. `POST /api/requirements`

**1. Qué hace.** Sube un archivo de requerimientos y lo guarda en el servidor.

**2. Autenticación.** Sí. Header exacto: `Authorization: Bearer <token>`.

**3. Request.** `Content-Type: multipart/form-data`.

| campo | tipo | obligatorio | descripción |
|---|---|---|---|
| `file` | archivo | Sí | Archivo a guardar. Se almacena en el directorio de subidas con el nombre que envía el cliente. |

Ejemplo:

```http
POST /api/requirements HTTP/1.1
Host: localhost:8000
Authorization: Bearer <token>
Content-Type: multipart/form-data; boundary=----b

------b
Content-Disposition: form-data; name="file"; filename="requirements.txt"
Content-Type: text/plain

Login must be accessible
------b--
```

**4. Respuesta exitosa.** `201 Created`, `application/json`.

| campo | tipo | descripción |
|---|---|---|
| `owner` | string | `username` del token. |
| `fileName` | string | Nombre recibido en la subida, sin cambios. |
| `storedAt` | string | Ruta donde se guardó el archivo en el servidor. Es relativa al directorio de subidas configurado. |
| `size` | entero | Tamaño en bytes del contenido guardado. |

Ejemplo, con el directorio por defecto (`./uploads`, configurable con `WORKSHOP_UPLOAD_DIR`). En la ejecución local con directorio temporal en Windows, `storedAt` fue una ruta absoluta de ese directorio; en Linux el valor sería el siguiente:

```json
{
  "owner": "student",
  "fileName": "requirements.txt",
  "storedAt": "uploads/requirements.txt",
  "size": 24
}
```

**5. Errores.**

| código | cuándo | cuerpo de ejemplo |
|---|---|---|
| `401` | Token ausente, inválido o expirado. | `{"detail":"Invalid token: invalid token"}` |
| `422` | No se envía el campo `file`. | `{"detail":[{"type":"missing","loc":["body","file"],"msg":"Field required","input":null}]}` |

**6. Notas de seguridad.**
- El nombre del archivo se usa tal cual para construir la ruta de destino, sin normalizarlo ni comprobar que quede dentro del directorio de subidas. Corresponde a H-API-04.
- No hay límite de extensión ni de tamaño; el contenido completo se lee en memoria.
- Subir un archivo con el mismo nombre sobrescribe el anterior.

---

### 5. `GET /api/backend-health`

**1. Qué hace.** Consulta el estado del servicio de autenticación desde la API y devuelve su respuesta.

**2. Autenticación.** Sí. Header exacto: `Authorization: Bearer <token>`.

**3. Request.** Sin parámetros, cuerpo ni query. La URL consultada se toma de la variable de entorno `AUTH_HEALTH_URL` (por defecto `http://localhost:8080/q/health`), con un tiempo máximo de 3 segundos.

```http
GET /api/backend-health HTTP/1.1
Host: localhost:8000
Authorization: Bearer <token>
```

**4. Respuesta exitosa.** `200 OK`, `application/json`. Se devuelve `200` tanto si el servicio consultado responde como si no es alcanzable.

| campo | tipo | descripción |
|---|---|---|
| `requestedBy` | string | `username` del token. |
| `status` | entero | Código HTTP del servicio consultado; `0` si la consulta falló. |
| `body` | string | Cuerpo de la respuesta del servicio consultado, o el texto de la excepción si la consulta falló. |

Ejemplo con servicio disponible (probado contra un servidor local de prueba que respondía `{"status":"UP","checks":[]}`):

```json
{
  "requestedBy": "student",
  "status": 200,
  "body": "{\"status\":\"UP\",\"checks\":[]}"
}
```

Ejemplo con servicio no disponible (cuerpo abreviado; el texto exacto depende del sistema):

```json
{
  "requestedBy": "student",
  "status": 0,
  "body": "HTTPConnectionPool(host='127.0.0.1', port=1): Max retries exceeded with url: /q/health (Caused by NewConnectionError(...))"
}
```

**5. Errores.**

| código | cuándo | cuerpo de ejemplo |
|---|---|---|
| `401` | Token ausente, inválido o expirado. | `{"detail":"Invalid token: invalid token"}` |

Un fallo al consultar el servicio no produce un código de error: se devuelve `200` con `status` `0`.

**6. Notas de seguridad.**
- En caso de fallo, `body` expone el texto de la excepción, que puede incluir host, puerto y detalles de red internos.
- El servidor consulta la URL de `AUTH_HEALTH_URL`; la URL no se recibe del cliente.

---

### Preguntas abiertas

- ¿El token emitido por el servicio de autenticación tiene este formato? Se documentó el formato que valida la API; no se leyó el código de `auth`.
- ¿Qué valores de `status` y `priority` son válidos? El código no los restringe.
- Respuesta ante un cuerpo JSON malformado en `POST /api/tasks`, o un nombre de archivo con subdirectorios inexistentes en `POST /api/requirements`: no se probaron.
- ¿La zona horaria de `createdAt` debe documentarse como UTC? Es el comportamiento documentado de `datetime('now')` en SQLite, no se verificó contra la configuración del servidor.

### Riesgos pendientes

Hallazgos de `HALLAZGOS.md` que afectan al contrato y siguen sin corregir en el código revisado: H-API-01 (token sin firma), H-API-02 (`owner` elegido por el cliente), H-API-03 (SQL concatenado), H-API-04 (nombre de archivo sin validar), H-API-05 (dependencias sin revisión SCA) y H-API-07 (errores y tipos). Si se corrigen, este documento debe actualizarse: cambiarían, como mínimo, el comportamiento de `owner`, los códigos de error y el formato del token.
