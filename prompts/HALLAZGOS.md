# HALLAZGOS - auth

Discovery del flujo de autenticación. Evidencia confirmada mediante lectura estática; no se ejecutaron pruebas de seguridad ni análisis SCA durante este Discovery.

| id | componente | hallazgo | tipo | explicacion | evidencia (archivo:linea) | severidad | estado |
|---|---|---|---|---|---|---|---|
| H-AUTH-01 | auth | Contraseñas almacenadas en texto plano | Vulnerabilidad | La tabla almacena contraseñas sin hash y la inicialización incluye valores literales; una exposición de la base permitiría leerlas directamente. | auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:22, auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:23 | alta | Pendiente |
| H-AUTH-02 | auth | SQL de credenciales construido por concatenación | Vulnerabilidad | `AuthResource.login` pasa usuario y contraseña del request al repositorio; el repositorio concatena esos valores y ejecuta la consulta con `Statement`. El flujo es alcanzable desde la entrada HTTP; su impacto no se reprodujo con una prueba de seguridad. | auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:35, auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32, auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:35 | alta | Pendiente |
| H-AUTH-03 | auth | Token Base64 con secreto embebido y sin firma criptográfica | Vulnerabilidad | El token codifica usuario, rol, expiración y secreto usando Base64; Base64 no aporta firma ni integridad criptográfica. | auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:8, auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:14, auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:15 | alta | Pendiente |
| H-AUTH-04 | auth | Secreto hardcodeado y CORS con origen amplio | Vulnerabilidad | El secreto está embebido en Java y CORS usa una expresión amplia para orígenes; esto dificulta proteger el secreto y limitar los sitios que pueden llamar al servicio desde el navegador. | auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:8, auth/src/main/resources/application.properties:5 | alta | Pendiente |
| H-AUTH-05 | auth | La respuesta expone detalles internos de excepciones | Vulnerabilidad | La respuesta 500 devuelve el mensaje y el nombre de clase de la excepción, revelando detalles internos al cliente. | auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:56, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:57 | media | Pendiente |
| H-AUTH-06 | auth | El resource concentra validación, persistencia, token y respuesta | Refactor | `login` valida la entrada, consulta el repositorio, genera token y construye la respuesta HTTP; el acoplamiento dificulta mantener y probar cada responsabilidad. | auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:24, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:35, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:39, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:43 | media | Pendiente |
| H-AUTH-07 | auth | Dependencias candidatas a análisis SCA | Sugerencia | Se declaran Quarkus `3.27.4` y Commons Text `1.9`. No se ejecutó análisis SCA ni se verificaron advisories, por lo que no se confirma un CVE aplicable. | auth/pom.xml:13, auth/pom.xml:50 | baja | Pendiente |

## Contrato observado

`POST /auth/login` recibe `username`, `password` y `client`. El código responde 400 ante request nulo o campos requeridos vacíos, 401 ante credenciales no coincidentes y 200 con `token`, `expiresIn`, `user` y `debug`. Este contrato se deriva del código y no se confirmó con los consumidores. `docs/ENDPOINTS.md` no existe; no se crea en este paso.

Evidencia: auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:22, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:23, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:26, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:29, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:32, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:37, auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:41, auth/src/main/java/com/bcp/workshop/auth/LoginRequest.java:4, auth/src/main/java/com/bcp/workshop/auth/LoginRequest.java:5, auth/src/main/java/com/bcp/workshop/auth/LoginRequest.java:6.

## Evidencia de pruebas y límites

El test existente caracteriza un login válido, pero no cubre credenciales incorrectas ni la seguridad de la consulta: auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:12. El health check `UP` reportado por el usuario solo confirma que `/q/health` respondió; no demuestra que login o persistencia funcionen. Maven, Git y análisis SCA no se ejecutaron durante este Discovery.

La nota de aprobación siguiente se conserva como registro proporcionado en el documento. No cambia el estado de los hallazgos ni sustituye evidencia de implementación, pruebas o revisión del diff.

***Aprobación humana verificada
Fecha 26/10/2026
Hallasgos aprobados: H-AUTH-01, H-AUTH-02, H-AUTH-03, H-AUTH-04, H-AUTH-05, H-AUTH-06, H-AUTH-07