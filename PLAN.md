# Plan

## API

### Alcance y compatibilidad

`docs/ENDPOINTS.md` no existe. Se incluyen H-API-01 y H-API-04 porque se solicitaron expresamente; ambos figuran actualmente como `Aprobado` en `HALLAZGOS.md`, no como `Pendiente`. Las propuestas conservan las rutas y formas de respuesta observadas en `api/app/main.py`. Los cambios que dependen de decisiones externas o de política no documentada quedan señalados como pendientes antes de implementar. Las pruebas se ejecutaran con cwd `api/`.

### Registro de ejecuciones

| fecha | componente | IDs | ejecucion | resultado | alcance |
|---|---|---|---|---|---|
| 2026-11-02 | api | H-API-01, H-API-04 | Interprete seleccionado `api/.venv/Scripts/python.exe`, cwd `api/`, `pytest.main(["-q"])` (equivalente a `python -m pytest -q`) | Salida 0; pasaron las 4 pruebas existentes. Avisos de deprecacion de `on_event` (FastAPI) y `BlockingPortal` (Starlette). | Linea base de la suite existente; no sustituye las caracterizaciones especificas de H-API-01 y H-API-04, que siguen pendientes. |

### H-API-01 - Token Base64 con secreto embebido

- **Hallazgo:** H-API-01 de `HALLAZGOS.md` (estado actual: Aprobado), evidencia en `api/app/main.py:14` y `api/app/main.py:17-24`.
- **Problema:** `legacy_identity` decodifica el Bearer como texto delimitado, compara un secreto fijo y valida expiracion, pero no verifica firma criptografica, emisor ni audiencia. Un token fabricado puede suplantar la identidad si se conoce el secreto.
- **Cambio propuesto:** sustituir la validacion ad hoc por validacion JWT que verifique firma, emisor, audiencia y expiracion. Leer clave, emisor y audiencia desde configuracion externa con nombres claros; no agregar secretos al repositorio. Mantener el requisito de Bearer, la dependencia de identidad y el formato de error 401 observado. Antes de retirar tokens legados, coordinar el formato y claims con el emisor fuera de este alcance; no leer ni modificar otros componentes. Evaluar y justificar una biblioteca JWT mantenida antes de agregarla a `api/requirements.txt`.
- **Archivos a tocar:** `api/app/main.py` o `api/app/security.py` para la validacion; `api` config existente o un modulo `api/app/config.py` si hace falta centralizar configuracion; `api/requirements.txt` solo si se justifica una dependencia; pruebas existentes bajo `api/tests/` o `api/tests/test_api.py` si no hay un modulo equivalente.
- **Prueba de caracterizacion previa:** con `create_app`, base SQLite temporal y un token legado ficticio formado segun el codigo actual, comprobar que una ruta protegida acepta el token, que el usuario y rol se derivan de el, y que un token malformado o expirado produce 401 con la forma de error actual. Registrar primero estos resultados. Despues, probar JWT valido, firma invalida, emisor/audiencia incorrectos y expiracion; mantener ruta, encabezado Bearer y respuesta 401 para tokens no validos. La compatibilidad con el emisor y la fecha de retirada del formato legado quedan pendientes de acuerdo.

### H-API-04 - Nombre de archivo usado directamente como ruta

- **Hallazgo:** H-API-04 de `HALLAZGOS.md` (estado actual: Aprobado), evidencia en `api/app/main.py:107-112`.
- **Problema:** `file.filename` se une directamente al directorio de uploads y se escribe sin comprobar que el destino permanezca dentro de esa raiz, ni limitar extension o tamano. Una ruta manipulada puede escapar del directorio o sobrescribir archivos accesibles al proceso.
- **Cambio propuesto:** normalizar el nombre recibido, resolver el destino y verificar que quede dentro de la raiz de uploads antes de escribir; limitar extension y bytes recibidos usando valores nombrados en configuracion, nunca literales sin nombre. No inventar la allowlist ni el limite: acordarlos como decisiones de producto antes del cambio. Mantener `POST /api/requirements`, el estado 201 y las claves de respuesta observadas (`owner`, `fileName`, `storedAt`, `size`); hacer que `fileName` informe el nombre normalizado y no exponga rutas locales. Rechazar archivo invalido con error controlado sin filtrar detalles internos.
- **Archivos a tocar:** `api/app/main.py` o un modulo de ruta/servicio de carga bajo `api/app/`; configuracion de `api/` para extensiones permitidas y tamano maximo; pruebas existentes bajo `api/tests/` o `api/tests/test_api.py` si no hay un modulo equivalente.
- **Prueba de caracterizacion previa:** con directorio temporal, subir un archivo ficticio pequeno con nombre y extension ordinarios; registrar estado, claves y valores de respuesta y contenido guardado. Comprobar tambien el comportamiento actual ante un nombre con ruta, extension no habitual y archivo grande, sin escribir fuera del directorio temporal. Despues, verificar que la carga ordinaria conserva el contrato observado, que ninguna ruta puede escapar de uploads, que extensiones no permitidas y archivos mayores al limite se rechazan, y que la respuesta no revela la ruta absoluta. Mantener los casos negativos dentro de ubicaciones temporales.
