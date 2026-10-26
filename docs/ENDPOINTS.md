# Contratos HTTP - auth

Este documento separa el **contrato observado** en el codigo y la respuesta compartida, de cualquier contrato **acordado** con consumidores. No se encontro un registro de acuerdo; por tanto, todos los comportamientos aqui descritos son observados, no confirmados externamente.

## GET /q/health

### 1. Que hace

Informa si el servicio de autenticacion esta disponible para su comprobacion de salud; no autentica usuarios ni verifica el acceso a la base SQLite de `LegacyDatabase`.

### 2. Autenticacion

No se observa un requisito de autenticacion ni un header `Authorization` configurado para esta ruta. Health lo publica la extension SmallRye Health, declarada en `auth/pom.xml`; no hay un recurso de health propio en el codigo revisado. Confirmar controles de red/autenticacion del despliegue antes de exponer el endpoint fuera del entorno local.

### 3. Request

Metodo y ruta: `GET /q/health`.

| campo | tipo | obligatorio | descripcion |
|---|---|---|---|
| Body | ninguno | no | La ruta GET observada se consulta sin cuerpo JSON. |
| Authorization | header | no observado | El servicio no declara que sea requerido para health. |

Ejemplo de request: `GET http://localhost:8080/q/health`, sin cuerpo.

### 4. Response exitosa

**Estado observado:** `200 OK`, reportado por el usuario al consultar el endpoint.

| campo | tipo | descripcion |
|---|---|---|
| status | string | Estado agregado de los health checks; la respuesta observada fue `UP`. |
| checks | array | Checks individuales. La respuesta observada contiene un array vacio. |

Ejemplo observado:

```json
{
  "status": "UP",
  "checks": []
}
```

### 5. Respuestas de error

- **Estado/cuerpo cuando un health check devuelve DOWN: pendiente de comprobar en esta instancia.** La guia oficial describe el estado agregado y la lista de checks, pero no se capturo aqui una respuesta DOWN ni un codigo/cuerpo de error para este servicio. No se inventa un ejemplo. Pregunta abierta: ¿el despliegue registra checks adicionales y cual es la respuesta HTTP observada cuando uno falla?
- Si el servicio no esta iniciado o no es alcanzable, no hay respuesta HTTP de este endpoint que documentar. No se verifico el cuerpo de errores de red.

La guia oficial de Quarkus 3.27 describe `/q/health` como agregacion de health checks y el cuerpo general con `status` y `checks`: [SmallRye Health - Quarkus 3.27](https://quarkus.io/version/3.27/guides/smallrye-health). El codigo del servicio solo incluye la extension, no un check de base de datos.

### 6. Notas de seguridad

- `UP` no demuestra que el login, la persistencia o la firma/validez del token funcionen.
- La respuesta observada `checks: []` indica que no se publicaron checks individuales en esa ejecucion.
- La configuracion de `auth/src/main/resources/application.properties` habilita CORS con un patron amplio; esto no convierte health en un endpoint autenticado.

## POST /auth/login

### 1. Que hace

Autentica las credenciales recibidas para el laboratorio y, si coinciden, devuelve un token y los datos basicos del usuario.

### 2. Autenticacion

No requiere un token previo ni un header `Authorization`; es la operacion que inicia la autenticacion. La ruta consume y produce `application/json` segun `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:15-17`.

### 3. Request

Metodo y ruta: `POST /auth/login`.

| campo | tipo | obligatorio | descripcion |
|---|---|---|---|
| username | string o null | si | Nombre de usuario; null, vacio o solo espacios se rechaza con 400. |
| password | string o null | si | Contrasena; null, vacia o solo espacios se rechaza con 400. El valor original se pasa al repositorio. |
| client | string o null | no | Campo aceptado por `LoginRequest`; el handler observado no lo valida ni lo utiliza. |

Ejemplo JSON completo usado por el test existente (credenciales ficticias del laboratorio):

```json
{
  "username": "student",
  "password": "Workshop123!",
  "client": "angular-workshop"
}
```

### 4. Response exitosa

**Estado:** `200 OK` cuando el repositorio devuelve un usuario.

| campo | tipo | descripcion |
|---|---|---|
| token | string | Token generado por `LegacyTokenUtil`. Su contenido depende del usuario, rol y hora de ejecucion. |
| expiresIn | integer | El handler devuelve el numero `3600`. |
| user | object | Datos de usuario expuestos en la respuesta. |
| user.username | string | Nombre de usuario autenticado. |
| user.displayName | string | Nombre mostrado, pasado por `escapeHtml4`. |
| user.role | string | Rol del usuario. |
| debug | string | El handler devuelve literalmente `authenticated-with-legacy-flow`. |

Ejemplo de estructura completa. El valor de `token` se omite intencionalmente porque cambia por ejecucion y no se capturo una respuesta real de login; reemplazarlo por una captura antes de tratar este bloque como ejemplo literal de respuesta:

```json
{
  "token": "<token-capturado-de-una-respuesta-real>",
  "expiresIn": 3600,
  "user": {
    "username": "student",
    "displayName": "Workshop Student",
    "role": "STUDENT"
  },
  "debug": "authenticated-with-legacy-flow"
}
```

**Pendiente de evidencia:** ejecutar el login ficticio y sustituir el placeholder por el token devuelto, o conservar la nota de que es solo una plantilla estructural.

### 5. Respuestas de error

| estado | cuando ocurre segun el codigo | cuerpo observado o ejemplo |
|---|---|---|
| 400 Bad Request | El request se deserializa como null. | `{"message":"Request is null"}` |
| 400 Bad Request | `username` es null, vacio o solo espacios. | `{"message":"Username is required"}` |
| 400 Bad Request | `password` es null, vacia o solo espacios. | `{"message":"Password is required"}` |
| 401 Unauthorized | `findByCredentials` devuelve null. Ocurre con credenciales no coincidentes; el repositorio tambien captura excepciones de persistencia y devuelve null. | Para username `student`: `{"message":"Invalid user student or password"}` |
| 500 Internal Server Error | Una excepcion llega al `catch` de `AuthResource.login`. El cuerpo usa `error.getMessage()` (o `Unknown error` si es null) y `error.getClass().getName()`. | No hay captura de una excepcion real; el cuerpo es dinamico. Plantilla estructural: `{"message":"<mensaje-real-de-la-excepcion-o-Unknown-error>","exception":"<nombre-real-de-clase>"}`. No usar como ejemplo literal hasta capturar valores reales. |

**Errores generados por el framework, pendientes de caracterizacion:** `AuthResource` declara `@Consumes(application/json)`; el codigo no define los cuerpos de error para JSON malformado o un `Content-Type` no soportado. Antes de publicarlos como contrato, capturar su estado y cuerpo con el runtime usado.

### 6. Notas de seguridad

- La comprobacion de password usa la consulta de `LegacyDatabase`; el codigo observado guarda contrasenas en texto plano y concatena los valores del request al SQL (`auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:22-23,32,35`).
- `LegacyTokenUtil` codifica en Base64 usuario, rol, una marca de expiracion y un secreto hardcodeado; Base64 no firma el token. `expiresIn: 3600` es un campo de respuesta y no demuestra que este servicio valide la expiracion (`auth/src/main/java/com/bcp/workshop/auth/LegacyTokenUtil.java:8,13-15`; `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:42`).
- Los errores 500 pueden exponer mensaje y clase de excepcion (`auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:55-57`).
- Las contrasenas y los tokens deben enviarse solo por HTTPS fuera del laboratorio local; no usar credenciales reales.
- El handler HTML-escapa `displayName`, pero los demas campos de la respuesta no se describen como HTML.

## Contrato acordado y preguntas abiertas

- **Contrato acordado:** no se encontro evidencia de acuerdo con consumidores. Los formatos anteriores son contrato observado en el codigo actual y, para health `UP`, la respuesta reportada por el usuario.
- **Preguntas abiertas:** capturar una respuesta real de login para documentar el token dinamico; comprobar los cuerpos de 500 y los errores de deserializacion/Content-Type; confirmar si el despliegue agrega health checks y si sus endpoints requieren controles de acceso.
- No se ejecuto una prueba HTTP desde esta sesion. El login de ejemplo se basa en el test existente y los registros ficticios de inicializacion.

## Fuentes consultadas

- `README.md` y `RETO.md`.
- `docs/GOOD_PRACTICES.md`.
- `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java`, `LoginRequest.java`, `LegacyDatabase.java` y `LegacyTokenUtil.java`.
- `auth/src/main/resources/application.properties` y `auth/pom.xml`.
- `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java`.
- Guia oficial versionada: [SmallRye Health - Quarkus 3.27](https://quarkus.io/version/3.27/guides/smallrye-health).
