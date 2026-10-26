# Plan de implementacion de auth

## Objetivo y alcance

Resolver los hallazgos H-AUTH-01 a H-AUTH-07 documentados en `prompts/HALLAZGOS.md`, preservando el contrato observado de `POST /auth/login`. Los cambios de codigo, configuracion y pruebas se limitan a `auth/`. La coordinacion con consumidores externos no autoriza leer ni modificar otros componentes.

El registro fuente mantiene los hallazgos en estado `Pendiente`. Aunque incluye una nota de aprobacion, este plan no la toma como evidencia verificable ni como aprobacion de cada cambio. Confirmar con la persona revisora el alcance concreto antes de implementar cada fase.

## Contrato que se preserva

- Request de `POST /auth/login`: `username`, `password` y `client`.
- `400` para request nulo o campos requeridos vacios.
- `401` para credenciales no coincidentes.
- `200` con las claves observadas `token`, `expiresIn`, `user` y `debug`.
- No cambiar rutas, codigos ni forma de la respuesta sin acuerdo documentado con los consumidores. El formato interno del token requiere coordinacion externa antes de cambiarlo.

Este contrato se derivo del codigo; `docs/ENDPOINTS.md` no existe y aun no hay evidencia de confirmacion por los consumidores.

## Fases

| Fase | Hallazgos | Trabajo | Criterio de salida |
|---|---|---|---|
| 1. Caracterizacion y aislamiento | H-AUTH-01 a H-AUTH-06 | Ampliar `AuthResourceTest` para registrar login exitoso, request nulo, username/password vacios, credenciales incorrectas y error de persistencia. Aislar la base de pruebas para no usar `auth/data/workshop.db` ni datos persistentes. Ejecutar baseline antes de refactorizar persistencia o token. | Pruebas que describen el comportamiento actual pasan y su salida/codigo de retorno quedan registrados. Ninguna prueba depende de datos de desarrollador o secretos reales. |
| 2. Separacion de capas | H-AUTH-06 | Separar Resource (HTTP), Service (reglas de login), Repository (persistencia) y Security (hash/token) en cambios revisables. Mantener el contrato HTTP y repetir caracterizacion en cada cambio. | Responsabilidades separadas; pruebas de contrato pasan; diff revisable y limitado a `auth/`. |
| 3. Consulta SQL parametrizada | H-AUTH-02 | Sustituir concatenacion y `Statement` por consulta parametrizada. Anadir una prueba de seguridad a traves de `POST /auth/login` que verifique rechazo de entradas que intenten alterar la consulta; debe fallar ante el comportamiento original. | La entrada del request no puede modificar la estructura de la consulta; casos valido e invalido mantienen el contrato observado. |
| 4. Hash de contrasenas | H-AUTH-01 | Reemplazar almacenamiento/comparacion en texto plano por hash lento con salt. Definir migracion o estrategia de datos del laboratorio y fixtures aislados; no registrar contrasenas en logs. | Pruebas demuestran autenticacion con contrasena valida, rechazo de invalida y almacenamiento no reversible. La base de pruebas es desechable y aislada. |
| 5. Token y secreto | H-AUTH-03, H-AUTH-04 | Cambiar Base64 casero por token firmado con expiracion y claims explicitos. Cargar el secreto desde configuracion de entorno o `application.properties`; no incluir secretos reales ni valores de produccion. | Pruebas cubren token valido, expirado y alterado. La respuesta mantiene la clave `token`; cambio del formato solo despues de confirmar compatibilidad con los consumidores. |
| 6. CORS y manejo de errores | H-AUTH-04, H-AUTH-05 | Restringir origenes CORS a los acordados y parametrizar la configuracion. Devolver mensajes genericos al cliente y enviar detalles tecnicos solo al log controlado. | Pruebas/configuracion verifican origen permitido y rechazo de no permitido; la respuesta 500 no filtra mensaje ni clase de excepcion. No se debilitan quality gates. |
| 7. Analisis SCA | H-AUTH-07 | Analizar Quarkus `3.27.4` y Commons Text `1.9` con los scanners disponibles. Evaluar advisories y compatibilidad; actualizar o retirar dependencias solo con evidencia. | Evidencia del analisis y decision por dependencia. No silenciar CodeQL ni Dependency Review. |
| 8. Regresion, cobertura y revision | Todos | Ejecutar pruebas y `mvn verify` con cwd `auth/`; revisar `auth/target/site/jacoco/`. Desde la raiz, revisar `git diff main -- auth/` y `git status --short`. Registrar comandos, salida y codigos de retorno reales. | Contrato y pruebas de seguridad pasan; riesgos externos se conservan como pendientes; diff revisado y aprobacion humana real registrada antes de cerrar hallazgos. |

## Estrategia de cobertura

- **Cobertura global:** reportar las metricas del modulo completo tal como aparecen en JaCoCo, indicando numerador, denominador y si se informa cobertura de lineas, instrucciones o ramas.
- **Cobertura del cambio:** identificar las clases de produccion modificadas a partir del diff y calcular sus metricas JaCoCo por separado; reportar numerador, denominador, tipo de cobertura y metodo de seleccion de clases. No presentar la cobertura global como cobertura del diff.
- **Meta:** al menos 85% del codigo modificado, sin reducir umbrales existentes. Si el reporte no permite aislar el cambio o falta una prueba/integracion, declarar el limite y el siguiente paso; no inferir cobertura.

## Dependencias y riesgos pendientes

- Confirmar con responsables de consumidores que aceptan el nuevo formato de token antes de cambiarlo. Esta coordinacion no incluye inspeccionar o editar `api/` ni `web/`.
- Confirmar el contrato observado con los consumidores; hasta entonces mantener ruta, request, codigos y forma de respuesta.
- Definir como se aisla/migra la base del laboratorio antes de probar hashes; las credenciales de fixture deben ser ficticias.
- Verificar las versiones con SCA; las versiones declaradas no prueban por si solas una vulnerabilidad aplicable.
- `/q/health` reportado `UP` solo confirma el health endpoint; no demuestra que login, persistencia, token o CORS funcionen.
- No registrar pruebas, cobertura, escaneos, revision humana ni aprobaciones hasta ejecutarlos y obtener evidencia.
