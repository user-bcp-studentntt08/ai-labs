## Why

El Issue [#23](https://github.com/user-bcp-studentntt08/ai-labs/issues/23) (hallazgo H-AUTH-01, componente `auth`, vulnerabilidad de severidad alta) reporta que `LegacyDatabase.findByCredentials` (`auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32`) construye el SQL concatenando `username` y `password`. Un valor como `' OR '1'='1` altera la consulta y permite iniciar sesión sin conocer la contraseña. Es una inyección SQL en el único punto de autenticación del taller: cualquier cliente puede obtener un token válido, y ese token es el que aceptan los demás componentes.

## What Changes

- Las credenciales recibidas en `POST /auth/login` se tratan siempre como datos y nunca alteran la estructura de la consulta de usuarios.
- Un intento de inyección (`' OR '1'='1` como usuario o contraseña) se rechaza con `401` y sin `token`.
- Se agrega cobertura de pruebas del intento de inyección en `AuthResourceTest` y se verifica que `mvn test` pasa desde `auth/`.

El Issue no cambia el contrato HTTP: no hay cambios incompatibles.

## Scope

### In Scope

- Comportamiento de `POST /auth/login` ante credenciales válidas, inválidas y con intento de inyección.
- Verificación mediante pruebas automatizadas en `auth/` (`AuthResourceTest`).

### Out of Scope

- Código y pruebas de `api/` y `web/`; sus secciones en los documentos generales se conservan.
- Cambios en el contrato de `POST /auth/login`: campos de solicitud, campos de respuesta, códigos de estado y mensajes de validación `400`.
- Formato, firma y expiración del token (`LegacyTokenUtil`), y almacenamiento de contraseñas en texto plano.
- Mensaje `401` que incluye el usuario recibido, campo `debug` de la respuesta y manejo de errores `500`.
- Otros hallazgos de `auth` (H-AUTH-02 en adelante).
- Diseño técnico de la implementación y `tasks.md` (se definen en pasos posteriores).

## Preserved Behavior

`docs/ENDPOINTS.md` solo documenta el componente `api`; no tiene sección de `auth`. El baseline de `POST /auth/login` se toma, por tanto, del Issue #23 y del código actual de `AuthResource`, y debe preservarse:

- `POST /auth/login` con `student` y `Workshop123!` responde `200` con `user.username` igual a `student` y `token` presente.
- La respuesta exitosa conserva `token`, `expiresIn` (`3600`), `user.username`, `user.displayName`, `user.role` y `debug`.
- Cuerpo ausente, `username` vacío o `password` vacío responden `400` con `message` (`Request is null`, `Username is required`, `Password is required`).
- Credenciales inexistentes o incorrectas responden `401` con `message`.
- El token emitido conserva el formato que valida `api` (`legacy_identity` en `docs/ENDPOINTS.md`, convenciones comunes).

## Impact

- Componente afectado: `auth/` (`LegacyDatabase`, `AuthResourceTest`).
- Contrato `POST /auth/login`: sin cambios.
- Componentes `api/` y `web/` y sus secciones en documentos generales: sin cambios.
- Referencias: Issue #23, hallazgo H-AUTH-01, rama actual `feature/h-auth-01`.
