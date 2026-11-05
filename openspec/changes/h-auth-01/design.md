## Context

Issue #23 (H-AUTH-01): `LegacyDatabase.findByCredentials` concatena `username` y `password` en el SQL, lo que permite inyección SQL en `POST /auth/login`.

Estado observado en `auth/`:

- `AuthResource.login` valida entrada (`400`), llama a `database.findByCredentials(username, password)` y, si devuelve `null`, responde `401`; si no, arma la respuesta con `LegacyTokenUtil.create`.
- `findByCredentials` crea una `Connection` JDBC (SQLite, `AUTH_DB_URL`, por defecto `jdbc:sqlite:./data/workshop.db`), ejecuta el SQL con `Statement` y devuelve `UserRecord` o `null`. Cualquier excepción se imprime y se traduce en `null`, es decir, `401`.
- `initialize()` crea `legacy_users` y siembra `student` y `trainer` con sentencias constantes (sin entrada externa).
- Las pruebas (`AuthResourceTest`, `@QuarkusTest` con RestAssured) usan la misma base `./data/workshop.db`, no una dedicada. Hoy solo cubren el login válido.
- Dependencias de datos: `sqlite-jdbc` 3.50.3.0 (sin ORM); JaCoCo ya configurado en `pom.xml`.

Contrato y alcance están definidos en `proposal.md` y `specs/auth-login/spec.md`.

## Goals / Non-Goals

**Goals**

- Que `username` y `password` nunca alteren la estructura de la consulta de `findByCredentials`.
- Que los intentos de inyección (`' OR '1'='1` en usuario, contraseña o ambos) devuelvan `401` sin `token`.
- Preservar byte a byte el contrato observable de `POST /auth/login` (ver siguiente sección).
- Añadir pruebas que fijen el comportamiento actual y el nuevo, con cobertura del código modificado de 85% o superior.

**Non-Goals**

- Hash o sal de contraseñas, o cualquier cambio en el almacenamiento (`legacy_users.password` sigue en texto plano).
- Formato, firma o expiración del token (`LegacyTokenUtil`), `StringEscapeUtils`, `commons-text`.
- Mensaje `401` que repite el usuario, campo `debug`, manejo de `500`, `printStackTrace`, CORS.
- Refactor por capas (resource/servicio/repositorio), pool de conexiones o migración de `DriverManager`.
- Cambios en `api/`, `web/` o en documentos generales de otros componentes.

## Protected Contracts

Preservados sin cambios, tomados de `specs/auth-login/spec.md` y del código actual (no existe sección `auth` en `docs/ENDPOINTS.md`):

| Contrato | Comportamiento protegido |
|---|---|
| Login válido | `student` / `Workshop123!` responde `200` con `token`, `expiresIn` (`3600`), `user.username`, `user.displayName`, `user.role`, `debug`. |
| Validación | Cuerpo nulo, `username` o `password` vacíos responden `400` con `message` actual. |
| Credenciales no válidas | Usuario inexistente o contraseña incorrecta responden `401` con `message`, sin `token`. |
| Token | Formato `base64(username|role|expiry|secret)` aceptado por `api`. |
| Firma pública | `LegacyDatabase.findByCredentials(String, String)` devuelve `UserRecord` o `null`; `AuthResource` no cambia. |
| Entorno | `AUTH_DB_URL` y el esquema de `legacy_users` no cambian. |

## Affected Components

| Archivo | Cambio previsto |
|---|---|
| `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java` | Solo el método `findByCredentials`. |
| `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java` | Pruebas nuevas de caracterización e inyección. |

Sin cambios: `AuthResource`, `LegacyTokenUtil`, `UserRecord`, `LoginRequest`, `pom.xml` (no se agregan dependencias), `application.properties`.

## Decisions

### D1. `PreparedStatement` con parámetros enlazados

`findByCredentials` usa una consulta con marcadores `?` fija:

```text
SELECT id, username, display_name, role FROM legacy_users WHERE username = ? AND password = ?
```

y enlaza `username` y `password` con `setString`. El texto del SQL deja de depender de la entrada. Es lo que pide el Issue (`PreparedStatement`, sin concatenar valores).

Alternativas consideradas:

- **Escapar comillas manualmente:** frágil, dependiente del dialecto, y no cumple el criterio del Issue. Descartada.
- **Validar o filtrar caracteres en `AuthResource`:** cambia el contrato de validación (`400`) y rechaza contraseñas legítimas con comillas. Descartada.
- **JPA/Panache o jOOQ:** agrega dependencias y rediseña persistencia; excede el alcance. Descartada.
- **Obtener el usuario por `username` y comparar la contraseña en Java:** cambia la semántica de la consulta y adelanta H-AUTH sobre contraseñas; fuera de alcance. Descartada.

### D2. Mantener el manejo de errores existente

El `try-with-resources` y el `catch (Exception)` que devuelven `null` se mantienen, de modo que una falla de base de datos sigue produciendo `401` como hoy. Los recursos (`Connection`, `PreparedStatement`, `ResultSet`) se cierran con `try-with-resources`. Cambiarlo a `500` alteraría el contrato.

### D3. Las comillas dejan de ser caso especial

Hoy una comilla simple rompe el SQL, lanza una excepción y se traduce en `401` por el `catch`. Con parámetros, la comilla es un valor y no coincide con ningún usuario: el resultado observable sigue siendo `401`. Por eso no hay cambio de contrato.

### D4. Pruebas con RestAssured sobre el endpoint real

Las pruebas se escriben en `AuthResourceTest`, a nivel HTTP, igual que la prueba existente. Verifican el contrato público y no la implementación, así que sirven antes y después del cambio.

## Incremental Strategy

1. **Caracterización (sin tocar `LegacyDatabase`):** agregar las pruebas de contrato listadas abajo y ejecutarlas desde `auth/` con `mvn test`. Las de comportamiento actual deben pasar. Las de inyección con `OR '1'='1'` pueden fallar por la vulnerabilidad: esa falla confirma el hallazgo y se registra como evidencia.
2. **Corrección:** cambiar solo `findByCredentials` a `PreparedStatement` (D1, D2).
3. **Verificación:** `mvn test` desde `auth/`; todas las pruebas pasan, incluidas las de inyección. Revisar la cobertura de JaCoCo del método modificado (meta: 85% o superior).
4. **Cierre:** confirmar que el diff solo toca `LegacyDatabase.java` y `AuthResourceTest.java`.

Los pasos 1 y 2 son commits separables para facilitar la revisión.

## Characterization Tests

Necesarias antes de modificar `findByCredentials`, todas a nivel HTTP en `AuthResourceTest`:

| Prueba | Fija |
|---|---|
| Login válido `student` / `Workshop123!` (ya existe) | `200`, `user.username`, `token`. |
| Login válido: campos de respuesta | `expiresIn` igual a `3600`, `user.displayName`, `user.role` igual a `STUDENT`, `debug` presente. |
| Contraseña incorrecta | `401`, sin `token`. |
| Usuario inexistente | `401`, sin `token`. |
| Cuerpo sin `username` / `password` vacío | `400` con `Username is required` / `Password is required`. |
| Inyección en usuario, contraseña y ambos (`' OR '1'='1`) | `401`, sin `token` (escenarios de la spec). |
| Variante `student' --` como usuario | `401`, sin `token`. |
| Contraseña legítima con comilla simple | `401` (no es error `500`). |

Datos de prueba: solo usuarios ficticios del taller sembrados por `initialize()`; no se agregan secretos.

## Risks / Trade-offs

- **Base de datos compartida en pruebas:** las pruebas usan `./data/workshop.db`. Son solo de lectura sobre usuarios sembrados, por lo que no se contaminan entre sí. Mitigación: no escribir datos desde las pruebas; el aislamiento con `AUTH_DB_URL` temporal queda como mejora fuera de alcance.
- **Enmascaramiento por el `catch`:** un error de SQL sigue devolviendo `401`, por lo que una prueba de inyección podría pasar por la razón equivocada (excepción en lugar de consulta correcta). Mitigación: incluir en las pruebas el login válido y el caso `OR '1'='1'` con usuario existente, y revisar que el SQL ya no se concatena (inspección del diff).
- **Prueba de caracterización fallando en el paso 1:** es esperado para los casos de inyección y se documenta, no se desactiva ni se excluye.
- **Vulnerabilidades residuales:** contraseñas en texto plano, token sin firma y mensaje `401` con el usuario no se corrigen aquí; quedan para otros hallazgos y se mantienen fuera de alcance.
- **Cobertura:** el cambio es pequeño, pero las ramas de `catch` y de `result.next()` falso deben ejercitarse para llegar a 85%.

## Rollback

Cambio local y reversible: `git revert` del commit de `LegacyDatabase.java` restaura la consulta anterior sin migraciones, sin cambios de esquema ni de datos y sin impacto en `api/` o `web/`. Las pruebas de caracterización pueden permanecer tras el revert, salvo las de inyección, que volverían a fallar.

## Open Questions

- Ninguna que bloquee el diseño. Confirmar durante la implementación que `mvn test` genera el reporte de JaCoCo requerido (el `report` está ligado a `verify`, no a `test`).
