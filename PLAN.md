# Plan

## API

### Alcance y compatibilidad

El contrato de los endpoints está documentado en `docs/ENDPOINTS.md`. Las propuestas conservan las rutas y formas de respuesta observadas en `api/app/main.py`; los cambios que dependen de decisiones externas o de política no documentada quedan señalados como pendientes antes de implementar. Las pruebas se ejecutaran con cwd `api/`.

### Registro de ejecuciones

| fecha | componente | IDs | ejecucion | resultado | alcance |
|---|---|---|---|---|---|
| 2026-11-02 | api | H-API-01, H-API-04 | Interprete seleccionado `api/.venv/Scripts/python.exe`, cwd `api/`, `pytest.main(["-q"])` (equivalente a `python -m pytest -q`) | Salida 0; pasaron las 4 pruebas existentes. Avisos de deprecacion de `on_event` (FastAPI) y `BlockingPortal` (Starlette). | Linea base de la suite existente; no sustituye las caracterizaciones especificas de H-API-01 y H-API-04, que siguen pendientes. |
| 2026-11-03 | api | H-API-08 | `python tools/lab.py test api` | Salida 0; 36 passed, 7 xfailed, 89 avisos; cobertura 100% (supera el umbral 85%). | Limite de 100 bytes en `POST /api/requirements`; pruebas de frontera y contrato documentado. |

### H-API-01 - Token Base64 con secreto embebido

- **Hallazgo:** H-API-01 de `HALLAZGOS.md` (estado actual: Aprobado), evidencia en `api/app/main.py:14` y `api/app/main.py:17-24`.
- **Problema:** `legacy_identity` decodifica el Bearer como texto delimitado, compara un secreto fijo y valida expiracion, pero no verifica firma criptografica, emisor ni audiencia. Un token fabricado puede suplantar la identidad si se conoce el secreto.
- **Cambio propuesto:** sustituir la validacion ad hoc por validacion JWT que verifique firma, emisor, audiencia y expiracion. Leer clave, emisor y audiencia desde configuracion externa con nombres claros; no agregar secretos al repositorio. Mantener el requisito de Bearer, la dependencia de identidad y el formato de error 401 observado. Antes de retirar tokens legados, coordinar el formato y claims con el emisor fuera de este alcance; no leer ni modificar otros componentes. Evaluar y justificar una biblioteca JWT mantenida antes de agregarla a `api/requirements.txt`.
- **Archivos a tocar:** `api/app/main.py` o `api/app/security.py` para la validacion; `api` config existente o un modulo `api/app/config.py` si hace falta centralizar configuracion; `api/requirements.txt` solo si se justifica una dependencia; pruebas existentes bajo `api/tests/` o `api/tests/test_api.py` si no hay un modulo equivalente.
- **Prueba de caracterizacion previa:** con `create_app`, base SQLite temporal y un token legado ficticio formado segun el codigo actual, comprobar que una ruta protegida acepta el token, que el usuario y rol se derivan de el, y que un token malformado o expirado produce 401 con la forma de error actual. Registrar primero estos resultados. Despues, probar JWT valido, firma invalida, emisor/audiencia incorrectos y expiracion; mantener ruta, encabezado Bearer y respuesta 401 para tokens no validos. La compatibilidad con el emisor y la fecha de retirada del formato legado quedan pendientes de acuerdo.

### H-API-04 - Nombre de archivo usado directamente como ruta

- **Hallazgo:** H-API-04 de `HALLAZGOS.md` (estado actual: Aprobado), evidencia en `api/app/main.py:107-112`.
- **Problema:** `file.filename` se une directamente al directorio de uploads y se escribe sin comprobar que el destino permanezca dentro de esa raiz. Una ruta manipulada puede escapar del directorio o sobrescribir archivos accesibles al proceso. El limite de tamano se rastrea en H-API-08.
- **Cambio propuesto:** normalizar el nombre recibido, resolver el destino y verificar que quede dentro de la raiz de uploads antes de escribir; acordar una allowlist de extensiones. Mantener `POST /api/requirements`, el estado 201 y las claves de respuesta observadas (`owner`, `fileName`, `storedAt`, `size`); hacer que `fileName` informe el nombre normalizado y no exponga rutas locales. Rechazar archivo invalido con error controlado sin filtrar detalles internos.
- **Archivos a tocar:** `api/app/main.py` o un modulo de ruta/servicio de carga bajo `api/app/`; configuracion de `api/` para extensiones permitidas; pruebas existentes bajo `api/tests/` o `api/tests/test_api.py` si no hay un modulo equivalente.
- **Prueba de caracterizacion previa:** con directorio temporal, subir un archivo ficticio pequeno con nombre y extension ordinarios; registrar estado, claves y valores de respuesta y contenido guardado. Comprobar tambien el comportamiento ante un nombre con ruta y una extension no habitual, sin escribir fuera del directorio temporal. Despues, verificar que ninguna ruta puede escapar de uploads, que extensiones no permitidas se rechazan y que la respuesta no revela la ruta absoluta. Mantener los casos negativos dentro de ubicaciones temporales.

### H-API-08 - Limite de tamaño en la carga de requisitos

- **Hallazgo aprobado:** H-API-08 de `HALLAZGOS.md`; el handler leía el archivo completo sin limite y no cubría un umbral máximo.
- **Decisiones aprobadas:** máximo 100 bytes para el contenido del archivo; rechazar excesos con HTTP 402 y `{"detail":"File exceeds the 100-byte limit"}`.
- **Cambio implementado:** `POST /api/requirements` lee como máximo 101 bytes y rechaza el exceso antes de escribirlo. Se conservan autenticación, éxito `201`, campos de respuesta y aceptación de archivo vacío.
- **Archivos modificados:** `api/app/main.py`, `api/tests/test_endpoints.py`, `docs/ENDPOINTS.md`, `docs/TESTING.md`.
- **Validación real:** primero, las pruebas nuevas detectaron que 101 bytes recibían `201`; tras el cambio, `Push-Location api; try { & .\.venv\Scripts\python.exe -m pytest -q tests\test_endpoints.py -k size_limit } finally { Pop-Location }` pasó (3 tests). La suite `python tools/lab.py test api` pasó (36 passed, 7 xfailed, 100% de cobertura, salida 0).
- **Riesgo residual:** el límite acota los bytes que el handler lee y guarda, pero el parser multipart puede recibir o almacenar temporalmente el cuerpo antes de ejecutar la ruta. Un límite de ingreso a nivel de servidor o infraestructura queda fuera de este cambio.
