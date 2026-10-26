# Pruebas - auth

Alcance: endpoints de `auth` documentados en `docs/ENDPOINTS.md`. Los IDs remiten a `prompts/HALLAZGOS.md`. El archivo de tests de este workspace contiene 12 métodos `@Test`. Las salidas compartidas discrepan: 17:16 reporta 12 tests y 17:17 reporta 1. Ninguna incluye `pwd`, así que no se confirma qué corrida corresponde a esta raíz.

## Casos

| endpoint | caso | tipo | resultado esperado | componente / IDs | estado de ejecucion |
|---|---|---|---|---|---|
| `GET /q/health` | Estado agregado sin checks registrados | Camino feliz y borde | HTTP 200; `status=UP`; `checks=[]`, conforme a la respuesta compartida. | auth / contrato, sin ID asociado | Añadido; incluido en la corrida reportada de 12 tests, checkout no confirmado |
| `GET /q/health` | Health check en estado `DOWN` | Error / pendiente de contrato | No hay estado HTTP ni cuerpo esperado documentado para esta instancia; no se inventa una respuesta ni se añade una aserción. | auth / contrato, sin ID asociado | Pendiente; `docs/ENDPOINTS.md` indica que no se observó un check que falle |
| `POST /auth/login` | Usuario ficticio valido y respuesta completa | Camino feliz | HTTP 200; `token` no nulo; `expiresIn=3600`; usuario y `debug` coinciden con el contrato observado. | auth / H-AUTH-02, H-AUTH-03, H-AUTH-06 (caracterizacion, no prueba de seguridad) | Existia prueba parcial; ampliada; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | Omitir `client` | Borde | HTTP 200; usuario autenticado. Caracteriza que el handler no valida ni usa `client`. | auth / contrato, sin ID asociado | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | Body JSON `null` | Error 400 | `{"message":"Request is null"}`. | auth / H-AUTH-06 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | `username` en blanco | Error 400 | `{"message":"Username is required"}`. | auth / H-AUTH-06 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | `username` null | Error 400 | `{"message":"Username is required"}`. | auth / H-AUTH-06 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | `password` en blanco | Error 400 | `{"message":"Password is required"}`. | auth / H-AUTH-06 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | `password` null | Error 400 | `{"message":"Password is required"}`. | auth / H-AUTH-06 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | Password incorrecta no vacia para `student` | Error 401 | `{"message":"Invalid user student or password"}`. | auth / H-AUTH-02 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | Excepcion de persistencia simulada antes de devolver usuario | Error 500; invocacion directa del Resource | HTTP 500; `message` contiene el mensaje de la excepcion simulada y `exception` su nombre de clase. Es prueba de la rama del Resource, no una prueba HTTP integrada. | auth / H-AUTH-05 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | Excepcion sin mensaje | Error 500; invocacion directa del Resource | HTTP 500; `message=Unknown error`; `exception` contiene el nombre de clase. | auth / H-AUTH-05 | Añadido; corrida de 12 tests reportada, checkout no confirmado |
| `POST /auth/login` | Nombre mostrado con etiquetas HTML | Unidad / salida escapada | HTTP 200 desde la invocacion directa; `displayName` contiene `&lt;b&gt;Workshop&lt;/b&gt;`. No depende de SQLite. | auth / sin ID especifico; caracterizacion de salida | Añadido; corrida de 12 tests reportada, checkout no confirmado |

## Codigo de las pruebas

Archivo completo: `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java`.

```java
package com.bcp.workshop.auth;

import io.quarkus.test.junit.QuarkusTest;
import jakarta.ws.rs.core.Response;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.jupiter.api.Assertions.assertEquals;

@QuarkusTest
class AuthResourceTest {
	@Test
	void logsInWithWorkshopUser() {
		given()
				.contentType("application/json")
				.body("{\"username\":\"student\",\"password\":\"Workshop123!\",\"client\":\"angular-workshop\"}")
				.when().post("/auth/login")
				.then()
				.statusCode(200)
				.body("user.username", is("student"))
				.body("user.displayName", is("Workshop Student"))
				.body("user.role", is("STUDENT"))
				.body("token", notNullValue())
				.body("expiresIn", is(3600))
				.body("debug", is("authenticated-with-legacy-flow"));
	}

	@Test
	void returnsHealthyStatusWithNoChecks() {
		given()
				.when().get("/q/health")
				.then()
				.statusCode(200)
				.body("status", is("UP"))
				.body("checks", empty());
	}

	@Test
	void logsInWhenOptionalClientIsOmitted() {
		given()
				.contentType("application/json")
				.body("{\"username\":\"student\",\"password\":\"Workshop123!\"}")
				.when().post("/auth/login")
				.then()
				.statusCode(200)
				.body("user.username", is("student"))
				.body("token", notNullValue());
	}

	@Test
	void rejectsNullLoginRequest() {
		given()
				.contentType("application/json")
				.body("null")
				.when().post("/auth/login")
				.then()
				.statusCode(400)
				.body("message", is("Request is null"));
	}

	@Test
	void rejectsBlankUsername() {
		given()
				.contentType("application/json")
				.body("{\"username\":\"  \",\"password\":\"Workshop123!\"}")
				.when().post("/auth/login")
				.then()
				.statusCode(400)
				.body("message", is("Username is required"));
	}

	@Test
	void rejectsNullUsername() {
		given()
				.contentType("application/json")
				.body("{\"username\":null,\"password\":\"Workshop123!\"}")
				.when().post("/auth/login")
				.then()
				.statusCode(400)
				.body("message", is("Username is required"));
	}

	@Test
	void rejectsBlankPassword() {
		given()
				.contentType("application/json")
				.body("{\"username\":\"student\",\"password\":\"  \"}")
				.when().post("/auth/login")
				.then()
				.statusCode(400)
				.body("message", is("Password is required"));
	}

	@Test
	void rejectsNullPassword() {
		given()
				.contentType("application/json")
				.body("{\"username\":\"student\",\"password\":null}")
				.when().post("/auth/login")
				.then()
				.statusCode(400)
				.body("message", is("Password is required"));
	}

	@Test
	void rejectsIncorrectCredentials() {
		given()
				.contentType("application/json")
				.body("{\"username\":\"student\",\"password\":\"invalid-test-password\"}")
				.when().post("/auth/login")
				.then()
				.statusCode(401)
				.body("message", is("Invalid user student or password"));
	}

	@Test
	void returnsInternalServerErrorWhenRepositoryThrows() {
		AuthResource resource = new AuthResource();
		resource.database = new LegacyDatabase() {
			@Override
			public UserRecord findByCredentials(String username, String password) {
				throw new IllegalStateException("test persistence failure");
			}
		};
		LoginRequest request = new LoginRequest();
		request.username = "student";
		request.password = "Workshop123!";

		Response response = resource.login(request);
		Map<?, ?> body = (Map<?, ?>) response.getEntity();

		assertEquals(500, response.getStatus());
		assertEquals("test persistence failure", body.get("message"));
		assertEquals(IllegalStateException.class.getName(), body.get("exception"));
	}

	@Test
	void returnsGenericMessageWhenExceptionHasNoMessage() {
		AuthResource resource = new AuthResource();
		resource.database = new LegacyDatabase() {
			@Override
			public UserRecord findByCredentials(String username, String password) {
				throw new IllegalStateException();
			}
		};
		LoginRequest request = new LoginRequest();
		request.username = "student";
		request.password = "Workshop123!";

		Response response = resource.login(request);
		Map<?, ?> body = (Map<?, ?>) response.getEntity();

		assertEquals(500, response.getStatus());
		assertEquals("Unknown error", body.get("message"));
		assertEquals(IllegalStateException.class.getName(), body.get("exception"));
	}

	@Test
	void escapesDisplayNameInLoginResponse() {
		AuthResource resource = new AuthResource();
		resource.database = new LegacyDatabase() {
			@Override
			public UserRecord findByCredentials(String username, String password) {
				return new UserRecord(1L, username, "<b>Workshop</b>", "STUDENT");
			}
		};
		LoginRequest request = new LoginRequest();
		request.username = "student";
		request.password = "test-password";

		Response response = resource.login(request);
		Map<?, ?> body = (Map<?, ?>) response.getEntity();
		Map<?, ?> user = (Map<?, ?>) body.get("user");

		assertEquals(200, response.getStatus());
		assertEquals("&lt;b&gt;Workshop&lt;/b&gt;", user.get("displayName"));
	}
}
```

## Comandos y resultados

Surefire configura `AUTH_DB_URL=jdbc:sqlite:./target/auth-test.db` para la JVM de pruebas; `mvn clean` elimina esa base de test. El comando de abajo se ejecuto, segun la salida compartida por el usuario, con cwd `C:\Users\Usuario\Documents\T07205-luis-felipe-aguilar-pereda\reqflow-workspace\ai-labs\auth`. Esa ruta difiere de la raiz abierta en esta sesion (`...\T07205-luis-felipe-aguilar-pereda\ai-labs`), por lo que no se atribuye el resultado al checkout abierto.

```bash
mvn clean verify
```

| componente / IDs caracterizados (no implica hallazgo resuelto) | comando | directorio | codigo de salida | resultado |
|---|---|---|---|---|
| auth / IDs no atribuibles: el `.txt` no identifica el metodo ejecutado | `mvn clean verify` | `reqflow-workspace/ai-labs/auth` (ruta informada por el usuario) | No capturado por separado; la salida muestra `BUILD SUCCESS` | Ejecucion reportada 2026-10-26 16:58:30: 1 test, 0 fallos, 0 errores, 0 omitidos. JaCoCo 0.8.12 cargo `jacoco.exec` y analizo 5 clases. El usuario compartio el CSV de esta corrida; metricas calculadas abajo. Checkout externo al abierto. |
| auth / IDs no atribuibles: el `.txt` no identifica el metodo ejecutado | `mvn clean verify` | `reqflow-workspace/ai-labs/auth` (ruta informada por el usuario) | No capturado por separado; la salida muestra `BUILD SUCCESS` | Ejecucion reportada 2026-10-26 17:07:05: 1 test, 0 fallos, 0 errores, 0 omitidos. JaCoCo 0.8.12 cargo `jacoco.exec` y analizo 5 clases. No se compartio un CSV nuevo para esta corrida; no se recalculan porcentajes. Checkout externo al abierto. |
| auth / H-AUTH-02, H-AUTH-03, H-AUTH-05, H-AUTH-06 (caracterizacion; no implica remediacion) | `mvn clean verify` | `auth/` (ruta no incluida) | No capturado por separado; la salida muestra `BUILD SUCCESS` | Ejecucion reportada 2026-10-26 17:16:13: 12 tests, 0 fallos, 0 errores, 0 omitidos. JaCoCo 0.8.12 analizo 5 clases y el usuario compartio el CSV de esta corrida. Checkout no confirmado. |
| auth / IDs no atribuibles: el resumen de Surefire no identifica el metodo | `mvn clean verify` | Ruta no incluida; la terminal previa estaba en `reqflow-workspace/ai-labs/auth` | No capturado por separado; la salida muestra `BUILD SUCCESS` | Ejecucion reportada 2026-10-26 17:17:55: 1 test, 0 fallos, 0 errores, 0 omitidos. CSV compartido; metricas calculadas abajo. No se puede confirmar si es el mismo checkout que la corrida de 12 tests. |

### Medicion de cobertura

Metodo: JaCoCo 0.8.12 (`prepare-agent` + `report` durante `verify`); metricas calculadas sumando las columnas `*_MISSED` y `*_COVERED` de cada CSV. El porcentaje es `covered / (missed + covered)`. Los dos CSV compartidos corresponden a resultados distintos y se muestran por separado.

| corrida | alcance | metrica | cubiertas / total | cobertura |
|---|---|---|---:|---:|
| 17:16, 12 tests | Global, 5 clases | Lineas | 48 / 51 | 94.1% |
| 17:16, 12 tests | Global, 5 clases | Instrucciones | 251 / 257 | 97.7% |
| 17:16, 12 tests | Global, 5 clases | Ramas | 19 / 22 | 86.4% |
| 17:16, 12 tests | Global, 5 clases | Metodos | 9 / 9 | 100% |
| 17:16, 12 tests | Global, 5 clases | Complejidad | 17 / 20 | 85.0% |
| 17:16, 12 tests | `AuthResource` | Lineas / instrucciones / ramas | 25/25, 129/129, 14/14 | 100% / 100% / 100% |
| 17:16, 12 tests | `LegacyDatabase` | Lineas / instrucciones / ramas | 18/21, 88/94, 5/8 | 85.7% / 93.6% / 62.5% |
| 17:17, 1 test | Global, 5 clases | Lineas | 37 / 51 | 72.5% |
| 17:17, 1 test | Global, 5 clases | Instrucciones | 195 / 257 | 75.9% |
| 17:17, 1 test | Global, 5 clases | Ramas | 10 / 22 | 45.5% |
| 17:17, 1 test | `AuthResource` | Lineas / instrucciones / ramas | 16/25, 76/129, 6/14 | 64.0% / 58.9% / 42.9% |
| 17:17, 1 test | `LegacyDatabase` | Lineas / instrucciones / ramas | 16/21, 85/94, 4/8 | 76.2% / 90.4% / 50.0% |

La corrida de 12 tests supera el 85% global en lineas, instrucciones y ramas; `AuthResource` queda al 100% en esas metricas. `LegacyDatabase` conserva 3 ramas no cubiertas (62.5%). La corrida posterior de 1 test queda en 72.5% de lineas globales. Debido a la discrepancia de rutas/conteos, no se declara una cobertura validada para un checkout concreto hasta confirmar `pwd` y repetir la ejecucion ahi. No se modifico codigo Java de produccion; JaCoCo no mide las pruebas ni la configuracion Surefire.

## Fallos, pendientes y pruebas propuestas

### Fallos observados

- Las salidas reportadas a las 17:16 y 17:17 indican ambas `BUILD SUCCESS` y cero fallos, pero discrepan en el conteo: 12 frente a 1 test.

### Limitaciones observadas

- La prueba de 500 invoca `AuthResource.login` directamente para simular la excepcion. No verifica el mapeo HTTP integrado de esa rama.

### Pendientes

- Confirmar `pwd` y `grep -c '@Test'` en la misma terminal que ejecuta Maven. Repetir `mvn clean verify` desde esa carpeta `auth/` y conservar juntos el Surefire report y el CSV JaCoCo para resolver por que los resultados difieren.
- Revisar en el HTML de JaCoCo cuales son las 3 ramas no cubiertas de `LegacyDatabase` antes de agregar tests; no caracterizar como comportamiento correcto el manejo silencioso de errores de persistencia.
- El endpoint health en estado `DOWN`, errores de JSON malformado y `Content-Type` no soportado siguen sin contrato de respuesta caracterizado en `docs/ENDPOINTS.md`; no se les asigna resultado esperado aqui.
- El cuerpo de error 500 depende del mensaje y clase concretos de la excepcion. La prueba usa valores simulados y no es una captura del runtime.

### Pruebas propuestas para etapas posteriores

- Capturar el comportamiento HTTP real para JSON malformado y tipos de contenido no admitidos antes de fijar expectativas.
- Capturar un caso `DOWN` solo si el despliegue registra un health check que pueda fallar.
- Tras corregir SQL, anadir una prueba de seguridad que falle ante la consulta original y pase con parametros, sin incluir payloads de explotacion en este documento.
- Tras corregir manejo de errores, actualizar el test de caracterizacion de 500 para verificar respuesta generica y ausencia de detalles internos.

### Referencias de codigo

- `GET /q/health`: test en `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:34`; respuesta observada en `docs/ENDPOINTS.md`.
- Login exitoso: test en `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:18`; handler en `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:24-53`.
- Request null y campos requeridos: tests en `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:56`, `:67`, `:78`, `:89` y `:100`; validaciones en `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:26-34`.
- Credenciales incorrectas: test en `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:111`; ramas HTTP/repositorio en `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:35-37` y `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32,35`.
- Excepcion 500 con y sin mensaje: tests unitarios directos en `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:122` y `:142`; handler en `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:55-57`.
- Escape de `displayName`: test unitario en `auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java:164`; salida en `auth/src/main/java/com/bcp/workshop/auth/AuthResource.java:43-48`.

## Documentos consultados

- `README.md`, `RETO.md`, `docs/GOOD_PRACTICES.md`, `prompts/HALLAZGOS.md`, `PLAN.md`, `docs/ENDPOINTS.md` y la version previa de `docs/TESTING.md`.
- Codigo restringido a `auth/`: `AuthResource.java`, `LegacyDatabase.java`, `LoginRequest.java`, `UserRecord.java`, `LegacyTokenUtil.java`, `AuthResourceTest.java`, `application.properties` y `pom.xml`.
- Salida de Maven y `jacoco.csv` compartidos por el usuario; no se inspeccionaron archivos de otros componentes.
