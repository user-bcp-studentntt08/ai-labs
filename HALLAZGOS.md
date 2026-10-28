# Hallazgos

| Componente | ID | Área | Hallazgo | Evidencia desde la raíz | Estado |
|---|---|---|---|---|---|
| auth | H-AUTH-01 | SQL / login | `username` y `password` se interpolan en la consulta SQLite, que se ejecuta mediante `Statement` sin parámetros enlazados. | `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:35`; `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32`, `:34-35` | CANDIDATO |
| auth | H-AUTH-02 | Token | El token generado es Base64 de campos concatenados que incluyen un secreto constante; el generador no aplica firma criptográfica. | `auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:8`, `:12-15` | CANDIDATO |
| auth | H-AUTH-03 | Login / client | `client` está declarado en el request de login, pero no se pasa al generador ni aparece en el contenido que este construye; confirmar si el contrato requiere propagarlo. | `auth/src/main/java/com/bcp/workshop/auth/LoginRequest.java:6`; `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:35`, `:39`; `auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:14-15` | CANDIDATO |
| auth | H-AUTH-04 | Credenciales / persistencia | La tabla persiste `password` como texto y la inicialización inserta credenciales de práctica sin hashing; la consulta compara directamente el valor recibido. | `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:22-24`, `:32` | CANDIDATO |
| auth | H-AUTH-05 | Errores / login | La respuesta HTTP 500 incluye el mensaje y el nombre de clase de la excepción capturada. | `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:54-58` | CANDIDATO |

## H-AUTH-01 - SQL en login

- **Estado:** CANDIDATO.
- **Evidencia:** `POST /auth/login` pasa ambos campos a `findByCredentials` en `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:22-24`, `:35`. `LegacyDatabase` concatena los valores en SQL en la línea 32, crea un `Statement` en la línea 34 y ejecuta `executeQuery(sql)` en la línea 35.
- **Impacto:** una entrada puede alterar la consulta de autenticación; la integridad del control de acceso depende de la interpretación del SQL resultante.
- **Prioridad propuesta:** Alta.
- **Contrato potencialmente afectado:** solicitud y respuestas de `POST /auth/login`, especialmente autenticación válida/inválida. `docs/ENDPOINTS.md` no existe, así que el contrato de error no está documentado aquí.
- **Cómo validarlo:** con una SQLite temporal local, probar credenciales válidas e inválidas y una cuenta ficticia insertada con parámetros enlazados cuyo usuario/clave incluyan una comilla. Verificar que la cuenta ficticia pueda autenticarse y que entradas inválidas no autentiquen. La prueba existente `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:12-20` solo cubre éxito; no se ejecutó en este Discovery.

## H-AUTH-02 - Token sin firma criptográfica observada

- **Estado:** CANDIDATO.
- **Evidencia:** `LegacyTokenUtil` declara un secreto constante en `auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:8`, concatena usuario, rol, expiración y secreto en la línea 14, y devuelve Base64 del texto en la línea 15.
- **Impacto:** Base64 no aporta integridad ni confidencialidad; un consumidor que confíe en esos campos podría aceptar contenido alterado. La verificación por consumidores queda fuera del código auth revisado.
- **Prioridad propuesta:** Alta.
- **Contrato potencialmente afectado:** formato y semántica del `token` devuelto por `POST /auth/login`; un cambio puede requerir coordinación con consumidores.
- **Cómo validarlo:** generar un token solo con datos ficticios en una prueba local y decodificarlo para comprobar su contenido; revisar/añadir una prueba de verificación que rechace claims alterados. No reutilizar ni publicar tokens reales.

## H-AUTH-03 - `client` no se propaga al token

- **Estado:** CANDIDATO; requiere confirmar el contrato esperado para `client`.
- **Evidencia:** `LoginRequest` declara `client` en `auth/src/main/java/com/bcp/workshop/auth/LoginRequest.java:6`; el recurso consulta credenciales en `AuthResource.java:35` y genera el token usando solo usuario y rol en la línea 39. `LegacyTokenUtil.java:14-15` concatena esos datos, expiración y secreto, sin `client`.
- **Impacto:** el contexto de cliente enviado en el login no queda representado en el token emitido; puede impedir que un consumidor lo use para identificar el cliente.
- **Prioridad propuesta:** Media.
- **Contrato potencialmente afectado:** campo `client` de la solicitud y claims del token de `POST /auth/login`.
- **Cómo validarlo:** acordar primero si `client` debe formar parte del token; después, probar con un valor ficticio que el token contenga el valor validado y que entradas inválidas se rechacen según la regla acordada.

## H-AUTH-04 - Contraseñas almacenadas en texto claro

- **Estado:** CANDIDATO.
- **Evidencia:** el esquema define `password TEXT NOT NULL` y la inicialización inserta credenciales de práctica directamente en `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:22-24`; la consulta compara el password recibido directamente en la línea 32. No se observa hashing en estos tramos.
- **Impacto:** quien obtenga una copia de la base podría leer las contraseñas persistidas.
- **Prioridad propuesta:** Alta.
- **Contrato potencialmente afectado:** persistencia interna y validación de credenciales; se debe conservar el resultado observable de login válido/inválido.
- **Cómo validarlo:** en una base temporal, crear una cuenta de prueba y comprobar que el valor persistido no sea la contraseña original, y que login válido e inválido sigan comportándose conforme al contrato aprobado. No inspeccionar datos reales.

## H-AUTH-05 - Detalle de excepción en respuesta HTTP

- **Estado:** CANDIDATO.
- **Evidencia:** el `catch` de `AuthResource.login` devuelve `error.getMessage()` y `error.getClass().getName()` en el cuerpo de respuesta 500, en `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:54-58`.
- **Impacto:** respuestas de error pueden revelar detalles internos de implementación o persistencia al cliente.
- **Prioridad propuesta:** Media.
- **Contrato potencialmente afectado:** cuerpo y tratamiento de errores de `POST /auth/login`; el contrato documental no está disponible en `docs/ENDPOINTS.md`.
- **Cómo validarlo:** en una prueba local aislada, simular una excepción y verificar que la respuesta conserva el estado/formato aprobado sin incluir el mensaje ni la clase interna; comprobar que el detalle queda solo en el log controlado.

## Validación de Discovery

- No se ejecutaron pruebas ni se hicieron solicitudes a servicios.
- Todos los hallazgos permanecen como CANDIDATO hasta revisión humana.
- `docs/ENDPOINTS.md` no existe; confirmar los contratos de error, `client` y formato/verificación del token.


Aprobacion de usuario
Autor: Luis Aguilar
Fecha 27/10/2026
Puntos aprobados:
  - H-AUTH-01
  - H-AUTH-02, JSON firmado
  - H-AUTH-03
  - H-AUTH-04
  - H-AUTH-05