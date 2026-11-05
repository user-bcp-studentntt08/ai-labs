# Hallazgos

## API

### Contrato observado

`docs/ENDPOINTS.md` no existe. Lo siguiente se deriva del codigo de `api/app/main.py`; no se ha ejecutado ni se considera contrato acordado:

- `GET /api/tasks`: requiere la dependencia `legacy_identity`; acepta `owner` opcional y devuelve las tareas que coincidan.
- `POST /api/tasks`: requiere `legacy_identity`, acepta un objeto JSON y declara respuesta `201`.
- `GET /api/summary`: requiere `legacy_identity`, acepta `owner` opcional y devuelve un resumen.
- `POST /api/requirements`: requiere `legacy_identity`, acepta un archivo y declara respuesta `201`.
- `GET /api/backend-health`: requiere `legacy_identity` y consulta la URL configurada en `AUTH_HEALTH_URL`.

### Matriz de seguimiento

| id | componente | hallazgo | tipo | explicacion | evidencia (archivo:linea) | severidad | estado |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-API-01 |  | api | Token Base64 con secreto embebido y sin verificacion de firma | Vulnerabilidad | La identidad y el rol se leen de un token decodificado como texto; el validador compara un secreto fijo incluido en el codigo y comprueba la expiracion, pero no verifica una firma criptografica. Si se conoce el secreto, se puede falsificar la identidad del token. | api/app/main.py:14, api/app/main.py:17, api/app/main.py:19, api/app/main.py:22-24 | Aprobado |  |
| H-API-02 | api | El cliente puede consultar o asignar tareas a otro `owner` | Vulnerabilidad | `GET /api/tasks` y `GET /api/summary` priorizan el `owner` enviado por el cliente sobre la identidad; `POST /api/tasks` permite elegir el `owner` en el cuerpo. Esto puede exponer tareas ajenas o asignar una tarea a otro propietario. | api/app/main.py:68-70, api/app/main.py:83, api/app/main.py:92-93 | alta | Aprobado |  |
| H-API-03 | api | Filtros e inserts concatenan entradas en SQL | Vulnerabilidad | El propietario de los filtros y los campos del cuerpo usados en el insert se concatenan en las consultas. Una entrada con comillas puede alterar la sintaxis o el significado de SQL. Las consultas de estas rutas no pasan parametros separados a `execute`. | api/app/main.py:70-71, api/app/main.py:84-85, api/app/main.py:93 | alta | Aprobado |  |
| H-API-04 | api | El nombre del archivo subido se usa directamente como ruta | Vulnerabilidad | `file.filename` se une al directorio de uploads y se escribe sin normalizar ni limitar el nombre. Una ruta relativa o absoluta manipulada puede escapar del directorio previsto o sobrescribir archivos accesibles al proceso. | api/app/main.py:109-111 | alta | Aprobado |  |
| H-API-06 | api | Rutas, persistencia, reglas y serializacion concentradas en un modulo | Refactor | `create_app`, la conexion y el esquema SQLite, las rutas, las consultas y el mapeo de filas estan en `main.py`. Esto dificulta aislar y probar responsabilidades y aumenta el acoplamiento. | api/app/main.py:29, api/app/main.py:35-38, api/app/main.py:67-75, api/app/main.py:77-88, api/app/main.py:90-105, api/app/main.py:107-112 | media | Aprobado |  |
| H-API-05 | api | Dependencias con versiones pendientes de revision SCA | Sugerencia | `urllib3` 2.5.0 y `python-multipart` 0.0.21 figuran en las dependencias. No se consultaron advisories ni se ejecuto un scanner, por lo que no se confirma aqui que esas versiones tengan un CVE aplicable. | api/requirements.txt:4-5 | baja | Aprobado |  |
| H-API-07 | api | Tipado generico, excepciones amplias, anidamiento y logica duplicada | Sugerencia | Se usan `dict[str, Any]` para entrada y respuesta, se capturan `Exception`, `summary` contiene condiciones anidadas y el fallback del propietario se repite en dos rutas. Esto reduce la claridad y hace mas dificil detectar errores y evolucionar el contrato. | api/app/main.py:17, api/app/main.py:25, api/app/main.py:78, api/app/main.py:69, api/app/main.py:92, api/app/main.py:101-104, api/app/main.py:120-121 | baja | Aprobado |  |

## auth

### Contrato observado

`docs/ENDPOINTS.md` no tiene sección `auth`. Lo siguiente se deriva de `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java`; no se ha ejecutado ni se considera contrato acordado:

- `POST /auth/login`: acepta `username`, `password` y `client`.
- Respuestas: `400` si falta el cuerpo, `username` o `password`; `401` si las credenciales no coinciden; `200` con `token`, `expiresIn` (3600), `user` (`username`, `displayName`, `role`) y `debug`; `500` con `message` y `exception` ante una excepción.

### Matriz de seguimiento

| id | componente | hallazgo | tipo | explicacion | evidencia (archivo:linea) | severidad | estado | issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-AUTH-01 | auth | Consulta de login concatena credenciales en SQL | Vulnerabilidad | `findByCredentials` arma el SQL con `username` y `password` sin parametrizar. Un valor con comillas puede alterar la consulta y permitir iniciar sesion sin conocer la contrasena. | auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32 | alta | Aprobado | #23 |
| H-AUTH-02 | auth | Token Base64 con secreto embebido y sin firma | Vulnerabilidad | El token es `username|role|expiry|SECRET` en Base64, con `SECRET` fijo en el codigo y sin firma criptografica. Quien conozca el secreto puede fabricar tokens con cualquier usuario y rol. Coincide con H-API-01, que valida este formato. | auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:8, auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:13-15 | alta | Aprobado |  |
| H-AUTH-03 | auth | Contrasenas en texto plano y credenciales sembradas | Vulnerabilidad | `legacy_users.password` guarda el valor sin hash y el login lo compara directamente. El arranque siembra `student` y `trainer` con contrasenas literales. | auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:21, auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:23-24, auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32 | media | Aprobado |  |
| H-AUTH-04 | auth | Errores exponen detalle interno y reflejan entrada | Vulnerabilidad | El `500` devuelve `getMessage()` y el nombre de la clase de la excepcion; el `401` incluye el `username` recibido; la respuesta `200` incluye `debug`. `findByCredentials` imprime la traza y convierte cualquier fallo de base de datos en `null`, que se ve como `401`. | auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:37, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:48, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:55-58, auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:40-42 | media | Aprobado |  |
| H-AUTH-05 | auth | CORS abierto y dependencias con versiones antiguas | Sugerencia | CORS acepta cualquier origen. `pom.xml` fija Quarkus 3.27.4, `commons-text` 1.9 y `sqlite-jdbc` 3.50.3.0, con PR de Dependabot abiertos. No se consultaron advisories ni se ejecuto un scanner: no se confirma aqui un CVE aplicable. | auth/src/main/resources/application.properties:5, auth/pom.xml:13, auth/pom.xml:45, auth/pom.xml:50 | baja | Aprobado |  |
