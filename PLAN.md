# Plan de correccion - auth

## Alcance y seleccion

Fuente: `prompts/HALLAZGOS.md`. Se seleccionan solo hallazgos que estan en estado `Pendiente`:

- **H-AUTH-02**, SQL de credenciales concatenado: severidad alta y entrada del request trazada hasta la ejecucion de la consulta. Es el riesgo prioritario.
- **H-AUTH-04**, secreto hardcodeado y CORS de origen amplio: severidad alta y correccion acotada a la configuracion y la utilidad de token, sin cambiar el contrato HTTP.

No se modifica codigo en este paso. No hay `HALLAZGOS.md` ni `ENDPOINTS.md` en la raiz; la matriz disponible esta en `prompts/HALLAZGOS.md`. No se inspeccionan ni modifican otros componentes.

## Contrato que se preserva

El contrato observado en `auth/` es `POST /auth/login` con `username`, `password` y `client`; responde 400 para request nulo o campos requeridos vacios, 401 para credenciales no coincidentes y 200 con las claves `token`, `expiresIn`, `user` y `debug`. No existe `docs/ENDPOINTS.md`, por lo que este comportamiento del codigo es la referencia. No cambiar ruta, campos, codigos ni forma de respuesta sin acuerdo documentado con consumidores.

## H-AUTH-02 - SQL de credenciales concatenado

**Hallazgo y problema.** `AuthResource.login` pasa usuario y contrasena del request a `LegacyDatabase.findByCredentials`; el repositorio concatena ambas entradas en SQL y ejecuta la cadena con `Statement`. Evidencia registrada: `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:35`, `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32` y `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:35`.

**Cambio propuesto.** Sustituir la concatenacion por `PreparedStatement` con parametros enlazados. Mantener el contrato 401 para credenciales no coincidentes y preservar la respuesta de login exitoso. No anadir dependencias.

**Archivos previstos.**
- `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java`
- `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java`

**Pruebas previas al cambio.**
1. Caracterizar credenciales presentes pero incorrectas: verificar 401 y el mensaje observado.
2. Anadir una prueba de seguridad a traves de `POST /auth/login` que verifique que entradas destinadas a alterar la consulta no autentican ni cambian el resultado esperado; esta prueba debe fallar con el SQL original y pasar con parametros enlazados.
3. Ejecutar las pruebas con una base temporal/aislada, configurada antes de inicializar `LegacyDatabase`; no usar ni borrar `auth/data/workshop.db`.

## H-AUTH-04 - Secreto hardcodeado y CORS amplio

**Hallazgo y problema.** `LegacyTokenUtil` contiene un secreto en codigo y `application.properties` acepta un patron amplio de origenes CORS. Evidencia: `auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:8` y `auth/src/main/resources/application.properties:5`.

**Cambio propuesto.** Leer el secreto desde una variable de entorno o configuracion externa de Quarkus, usando solo un valor ficticio/aislado en pruebas. Configurar explicitamente los origenes acordados en lugar del patron abierto. Conservar la forma de la respuesta HTTP. Esta correccion no reemplaza H-AUTH-03: el token Base64 seguira pendiente de firma criptografica y expiracion validada.

**Archivos previstos.**
- `auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java`
- `auth/src/main/resources/application.properties`
- `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java`

**Pruebas previas al cambio.**
1. Caracterizar que un login valido responde 200 y conserva las claves `token`, `expiresIn`, `user` y `debug`.
2. Caracterizar preflight CORS para el origen local documentado `http://localhost:4200`; registrar el header observado antes de restringir origenes.
3. Tras el cambio, comprobar que el origen permitido sigue respondiendo como se acordo y que un origen no permitido no recibe autorizacion CORS. Configurar el secreto de prueba fuera del codigo y sin reutilizar valores reales.

## Secuencia y validacion

1. Revisar y aprobar este alcance antes de editar codigo; la nota de aprobacion en la matriz se conserva como registro, pero no se infiere aprobacion adicional para cambios no especificados.
2. Escribir primero las pruebas de caracterizacion y seguridad, y ejecutarlas para registrar el baseline antes de modificar produccion.
3. Corregir H-AUTH-02 y H-AUTH-04 en cambios separados y ejecutar las pruebas afectadas despues de cada cambio.
4. Ejecutar `mvn verify` con cwd `auth/`; registrar comando, salida y codigo de retorno reales. Revisar el reporte JaCoCo generado en `auth/target/site/jacoco/`.
5. Desde la raiz, revisar `git diff main -- auth/` y `git status --short`. No marcar hallazgos resueltos sin pruebas, diff revisado y aprobacion humana verificable.

## Cobertura y limites

La meta es al menos 85% del codigo modificado, sin reducir gates. Informar cobertura global de JaCoCo por separado de la cobertura de las clases modificadas, indicando numerador, denominador, tipo de metrica y metodo usado para seleccionar esas clases. JaCoCo no calcula por si solo cobertura del diff; si no se puede aislar, declarar el limite y el siguiente paso. No hay resultados de pruebas, SCA ni cobertura registrados por este plan.

## Dependencia externa pendiente

Confirmar con los consumidores que esperan el token el impacto de cambios futuros de formato o validacion. Esta coordinacion no amplifica el alcance a `api/` ni `web/`; mientras no haya acuerdo, preservar `token` y el resto de la respuesta observada.

## Dependencia externa relacionada: H-WEB-01

`RETO.md` identifica para web el token en `localStorage` como candidato de seguridad. Se registra aqui solo como dependencia de coordinacion; no es un hallazgo de auth, no cambia su ID y su confirmacion/evidencia corresponde al alcance web. No se inspecciono ni modifico `web/`.

Antes de cambiar la estrategia de token de auth, coordinar con responsables de auth, api y web una decision compartida. Evaluar cookie `HttpOnly`, `Secure` y `SameSite`, incluyendo soporte para emitirla en auth, aceptarla en api, enviarla desde web y cubrir CSRF/CORS. Una cookie agregada mientras el token sigue disponible en el cuerpo JSON no elimina por si sola la exposicion a JavaScript. Quitar o cambiar `token` del cuerpo puede modificar el contrato observado de `POST /auth/login` y requiere acuerdo explicito.

Hasta tener acuerdo, mantener el contrato y el mecanismo actuales; H-WEB-01 queda pendiente en su propio seguimiento. El almacenamiento solo en memoria puede reducir persistencia, pero no se debe presentar como proteccion completa frente a XSS. El cierre requiere pruebas y evidencia de cada componente por sus responsables, sin ampliar este cambio de auth.
