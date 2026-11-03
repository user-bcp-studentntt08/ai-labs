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
| H-API-04 | api | El nombre del archivo subido se usa directamente como ruta | Vulnerabilidad | `file.filename` se une al directorio de uploads y se escribe sin normalizar ni limitar el nombre. Una ruta relativa o absoluta manipulada puede escapar del directorio previsto o sobrescribir archivos accesibles al proceso. | api/app/main.py:110, api/app/main.py:117 | alta | Aprobado |  |
| H-API-06 | api | Rutas, persistencia, reglas y serializacion concentradas en un modulo | Refactor | `create_app`, la conexion y el esquema SQLite, las rutas, las consultas y el mapeo de filas estan en `main.py`. Esto dificulta aislar y probar responsabilidades y aumenta el acoplamiento. | api/app/main.py:29, api/app/main.py:35-38, api/app/main.py:67-75, api/app/main.py:77-88, api/app/main.py:90-105, api/app/main.py:107-112 | media | Aprobado |  |
| H-API-05 | api | Dependencias con versiones pendientes de revision SCA | Sugerencia | `urllib3` 2.5.0 y `python-multipart` 0.0.21 figuran en las dependencias. No se consultaron advisories ni se ejecuto un scanner, por lo que no se confirma aqui que esas versiones tengan un CVE aplicable. | api/requirements.txt:4-5 | baja | Aprobado |  |
| H-API-07 | api | Tipado generico, excepciones amplias, anidamiento y logica duplicada | Sugerencia | Se usan `dict[str, Any]` para entrada y respuesta, se capturan `Exception`, `summary` contiene condiciones anidadas y el fallback del propietario se repite en dos rutas. Esto reduce la claridad y hace mas dificil detectar errores y evolucionar el contrato. | api/app/main.py:17, api/app/main.py:25, api/app/main.py:78, api/app/main.py:69, api/app/main.py:92, api/app/main.py:101-104, api/app/main.py:120-121 | baja | Aprobado |  |

### Hallazgos de discovery

#### H-API-08 - Carga de archivos sin limite de tamano
- Estado: Aprobado
- Evidencia inicial: antes del cambio, `api/app/main.py:109-110` leia el archivo completo en memoria antes de escribirlo y no aplicaba un limite de bytes; `api/tests/test_endpoints.py:249-253` comprobaba un archivo vacio, pero no un umbral maximo.
- Impacto: una carga grande puede consumir memoria y espacio en disco del proceso API, degradando o interrumpiendo el servicio.
- Prioridad propuesta: media.
- Contrato potencialmente afectado: `POST /api/requirements` (tamanos de archivo aceptados y respuesta ante cargas excesivas).
- Decision aprobada: limite de 100 bytes para el contenido del archivo; rechazar excesos con HTTP 402 y `{"detail":"File exceeds the 100-byte limit"}`.
- Validacion: `python tools/lab.py test api` paso (36 passed, 7 xfailed, cobertura 100%). Las pruebas nuevas aceptan 99 y 100 bytes y rechazan 101 bytes con HTTP 402 sin almacenar el archivo.

#### H-API-09 - Archivos con el mismo nombre sobrescriben contenido existente
- Estado: CANDIDATO
- Evidencia: `api/app/main.py:110,117` construye la ruta a partir del nombre y escribe en el directorio comun; `api/tests/test_endpoints.py:277-280` verifica que una segunda carga con el mismo nombre reemplaza el contenido anterior.
- Impacto: una persona autenticada puede reemplazar un archivo de otro propietario si ambos usan el mismo nombre; el efecto posterior depende de como otros procesos consuman esos archivos.
- Prioridad propuesta: media.
- Contrato potencialmente afectado: `POST /api/requirements` (propiedad, unicidad y semantica de sobrescritura de archivos).
- Como validarlo: con dos identidades de prueba, cargar el mismo nombre y comprobar si la segunda carga sustituye el archivo de la primera; confirmar con el responsable del contrato si ese comportamiento es intencional.

#### H-API-10 - CORS permite cualquier origen junto con credenciales
- Estado: CANDIDATO
- Evidencia: `api/app/main.py:51-52` configura `allow_origins=["*"]` y `allow_credentials=True`; no se encontraron pruebas CORS en `api/tests/test_endpoints.py`.
- Impacto: la politica amplia puede permitir a sitios de origen no confiable realizar solicitudes cross-origin y leer respuestas cuando el navegador adjunta credenciales autorizadas; el alcance real depende de los clientes y de la autenticacion usada.
- Prioridad propuesta: baja, pendiente de confirmar los origenes confiables y el modo de autenticacion de los clientes.
- Contrato potencialmente afectado: politica de acceso cross-origin de los endpoints `/api/*`.
- Como validarlo: emitir solicitudes preflight y autenticadas con origenes permitidos y no permitidos; contrastar las cabeceras CORS obtenidas con la lista de origenes aprobados para cada despliegue.
