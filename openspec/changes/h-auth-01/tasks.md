## 1. Pruebas de caracterización (sin tocar `LegacyDatabase.java`)

- [x] 1.1 En `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java`, agregar prueba del login válido `student` / `Workshop123!` que verifique `200`, `expiresIn` igual a `3600`, `user.displayName`, `user.role` igual a `STUDENT` y `debug` presente (la prueba actual ya cubre `user.username` y `token`).
- [x] 1.2 Agregar prueba de contraseña incorrecta para `student`: `401` y cuerpo sin `token`.
- [x] 1.3 Agregar prueba de usuario inexistente: `401` y cuerpo sin `token`.
- [x] 1.4 Agregar pruebas de validación: `username` vacío o ausente responde `400` con `Username is required`; `password` vacío o ausente responde `400` con `Password is required`.
- [x] 1.5 Agregar prueba de inyección en el usuario (`' OR '1'='1` como `username`, contraseña cualquiera): `401` y sin `token`.
- [x] 1.6 Agregar prueba de inyección en la contraseña (`student` y `' OR '1'='1`): `401` y sin `token`.
- [x] 1.7 Agregar prueba de inyección en ambos campos (`' OR '1'='1` en `username` y `password`): `401` y sin `token`.
- [x] 1.8 Agregar prueba con `student' --` como usuario: `401` y sin `token`.
- [x] 1.9 Agregar prueba de contraseña legítima con comilla simple (por ejemplo `it's`) para `student`: `401`, no `500`.
- [x] 1.10 Ejecutar `mvn test` desde `auth/` antes del cambio funcional y registrar el resultado: las pruebas de contrato deben pasar; las de inyección que fallen se anotan como evidencia del hallazgo H-AUTH-01, sin desactivarlas ni excluirlas.
  - Comando: `mvn test "-Dquarkus.http.test-port=0"` desde `auth/` (el puerto 8081 por defecto estaba ocupado por un proceso ajeno).
  - Resultado: 13 pruebas, 10 pasan, 3 fallan (`BUILD FAILURE`, código de salida 1).
  - Evidencia de H-AUTH-01 (`Expected status code <401> but was <200>`): `injectionInPasswordIsRejected`, `injectionInBothFieldsIsRejected` y `sqlCommentInUsernameIsRejected`.
  - Las pruebas 1.1 a 1.4, 1.5 y 1.9 pasan; 1.5 y 1.9 pasan por la precedencia de `AND`/`OR` y por la excepción capturada, no por una consulta correcta (riesgo ya anotado en `design.md`).
- [x] 1.11 Confirmar con `git status` que solo cambió `AuthResourceTest.java`.

## 2. Corrección en `LegacyDatabase`

- [x] 2.1 En `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java`, reemplazar en `findByCredentials` la concatenación por una consulta fija con marcadores `?` para `username` y `password`, ejecutada con `PreparedStatement` y `setString`.
- [x] 2.2 Mantener la firma `findByCredentials(String, String)`, el retorno `UserRecord` o `null`, el `try-with-resources` y el `catch` existentes (decisión D2 del diseño).
- [x] 2.3 Verificar que `findByCredentials` ya no concatena valores en el SQL y que `AuthResource`, `LegacyTokenUtil`, `pom.xml` y `application.properties` no cambiaron.

## 3. Validación

- [x] 3.1 Ejecutar `mvn test` desde `auth/`: todas las pruebas pasan, incluidas las de inyección de 1.5 a 1.9.
  - Comando: `mvn test "-Dquarkus.http.test-port=0"` desde `auth/`. Resultado: 13 pruebas, 0 fallos, 0 errores, `BUILD SUCCESS`.
  - Las 3 pruebas que fallaban antes del cambio (`injectionInPasswordIsRejected`, `injectionInBothFieldsIsRejected`, `sqlCommentInUsernameIsRejected`) ahora pasan. Los reportes de surefire no contienen `SQLException` ni errores de sintaxis SQL, por lo que `passwordWithSingleQuoteIsRejectedWithoutServerError` ya no pasa por una excepción capturada.
- [x] 3.2 Ejecutar la verificación de cobertura de JaCoCo desde `auth/` (por ejemplo `mvn verify`, porque el reporte está ligado a `verify`) y comprobar que el código modificado de `findByCredentials` alcanza 85% o más.
  - Comando: `mvn verify "-Dquarkus.http.test-port=0"` desde `auth/`. Resultado: 13 pruebas, 0 fallos, `BUILD SUCCESS`. Reporte: `auth/target/site/jacoco/jacoco.xml`.
  - `findByCredentials`: líneas 12/13 (92,3%), instrucciones 56/59 (94,9%), ramas 5/8 (62,5%).
  - La única línea sin cubrir es `error.printStackTrace()` del `catch`; las ramas sin cubrir son las que genera el `try-with-resources` y ese mismo `catch`. Ejercitar el `catch` por HTTP exige una `AUTH_DB_URL` inválida, que `DB_URL` fija al cargar la clase.
  - Cumple 85% por líneas e instrucciones; por ramas queda por debajo. Pendiente de decisión qué métrica rige para 3.3.
- [x] 3.3 Si la cobertura de `findByCredentials` queda por debajo de 85%, agregar solo las pruebas HTTP necesarias para las ramas faltantes.
  - No se agregaron pruebas: por líneas (92,3%) e instrucciones (94,9%) la cobertura no queda por debajo de 85%. Las ramas sin cubrir (62,5%) son las del `try-with-resources` y del `catch`, que no se pueden ejercitar por HTTP sin cambiar código o configuración fuera de alcance.
- [x] 3.4 Revisar el diff: solo `LegacyDatabase.java` y `AuthResourceTest.java` modificados; sin cambios en `api/`, `web/` ni documentos generales.
  - Diff de `auth/`: solo `LegacyDatabase.java` (+9/-5) y `AuthResourceTest.java` (+123); sin cambios en `api/` ni `web/`.
  - Desviación aprobada por el responsable: el PR incluye además `HALLAZGOS.md` (sección `auth`, conservando la de `api`), `openspec/changes/h-auth-01/` y los archivos de agentes, prompts, skills y `.vscode/mcp.json` que estaban sin seguimiento. Se revisó que no contienen secretos.
- [x] 3.5 Contrastar los criterios de aceptación del Issue #23 y los escenarios de `specs/auth-login/spec.md` con los resultados de las pruebas, y registrar el resultado como evidencia de H-AUTH-01.
  - Issue #23, criterio 1 (`PreparedStatement` sin concatenar): `findByCredentials` usa marcadores `?` con `setString`; búsqueda de concatenaciones en `LegacyDatabase.java` sin resultados.
  - Issue #23, criterio 2 (login `student` responde 200 con `user.username` y `token`): `logsInWithWorkshopUser` y `validLoginKeepsResponseFormat` pasan.
  - Issue #23, criterio 3 (`' OR '1'='1` como usuario o contraseña responde 401 sin `token`): `injectionInUsernameIsRejected`, `injectionInPasswordIsRejected` e `injectionInBothFieldsIsRejected` pasan.
  - Issue #23, criterio 4 (prueba de inyección en `AuthResourceTest` y `mvn test` pasa desde `auth/`): cumplido, 13/13.
  - Spec: los escenarios de inyección, login válido, contraseña incorrecta y validación de entrada tienen prueba y pasan. `student' --` y la contraseña con comilla simple (1.8 y 1.9) también.
