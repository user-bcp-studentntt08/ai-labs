package com.bcp.workshop.auth;

import io.quarkus.test.junit.QuarkusTest;
import io.restassured.response.ValidatableResponse;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;

@QuarkusTest
class AuthResourceTest {
    private static final String STUDENT_USERNAME = "student";
    private static final String STUDENT_PASSWORD = "Workshop123!";
    private static final String CLIENT = "angular-workshop";
    private static final String INJECTION_PAYLOAD = "' OR '1'='1";

    private static ValidatableResponse postLogin(Map<String, String> body) {
        return given()
                .contentType("application/json")
                .body(body)
                .when().post("/auth/login")
                .then();
    }

    private static ValidatableResponse login(String username, String password) {
        return postLogin(Map.of("username", username, "password", password, "client", CLIENT));
    }

    @Test
    void logsInWithWorkshopUser() {
        given()
                .contentType("application/json")
                .body("{\"username\":\"student\",\"password\":\"Workshop123!\",\"client\":\"angular-workshop\"}")
                .when().post("/auth/login")
                .then()
                .statusCode(200)
                .body("user.username", is("student"))
                .body("token", notNullValue());
    }

    @Test
    @DisplayName("Login válido preservado: formato completo de la respuesta 200")
    void validLoginKeepsResponseFormat() {
        login(STUDENT_USERNAME, STUDENT_PASSWORD)
                .statusCode(200)
                .body("token", notNullValue())
                .body("expiresIn", is(3600))
                .body("user.username", is("student"))
                .body("user.displayName", is("Workshop Student"))
                .body("user.role", is("STUDENT"))
                .body("debug", notNullValue());
    }

    @Test
    @DisplayName("Login válido preservado: contraseña incorrecta responde 401 sin token")
    void wrongPasswordIsRejected() {
        login(STUDENT_USERNAME, "wrong-password")
                .statusCode(401)
                .body("token", nullValue());
    }

    @Test
    @DisplayName("Login válido preservado: usuario inexistente responde 401 sin token")
    void unknownUserIsRejected() {
        login("nobody", STUDENT_PASSWORD)
                .statusCode(401)
                .body("token", nullValue());
    }

    @Test
    @DisplayName("Validación preservada: username vacío responde 400")
    void emptyUsernameIsRejected() {
        login("", STUDENT_PASSWORD)
                .statusCode(400)
                .body("message", is("Username is required"));
    }

    @Test
    @DisplayName("Validación preservada: username ausente responde 400")
    void missingUsernameIsRejected() {
        postLogin(Map.of("password", STUDENT_PASSWORD, "client", CLIENT))
                .statusCode(400)
                .body("message", is("Username is required"));
    }

    @Test
    @DisplayName("Validación preservada: password vacío responde 400")
    void emptyPasswordIsRejected() {
        login(STUDENT_USERNAME, "")
                .statusCode(400)
                .body("message", is("Password is required"));
    }

    @Test
    @DisplayName("Validación preservada: password ausente responde 400")
    void missingPasswordIsRejected() {
        postLogin(Map.of("username", STUDENT_USERNAME, "client", CLIENT))
                .statusCode(400)
                .body("message", is("Password is required"));
    }

    @Test
    @DisplayName("Spec H-AUTH-01: inyección en el usuario responde 401 sin token")
    void injectionInUsernameIsRejected() {
        login(INJECTION_PAYLOAD, "anything")
                .statusCode(401)
                .body("token", nullValue());
    }

    @Test
    @DisplayName("Spec H-AUTH-01: inyección en la contraseña responde 401 sin token")
    void injectionInPasswordIsRejected() {
        login(STUDENT_USERNAME, INJECTION_PAYLOAD)
                .statusCode(401)
                .body("token", nullValue());
    }

    @Test
    @DisplayName("Spec H-AUTH-01: inyección en ambos campos responde 401 sin token")
    void injectionInBothFieldsIsRejected() {
        login(INJECTION_PAYLOAD, INJECTION_PAYLOAD)
                .statusCode(401)
                .body("token", nullValue());
    }

    @Test
    @DisplayName("Spec H-AUTH-01: comentario SQL tras el usuario no omite la contraseña")
    void sqlCommentInUsernameIsRejected() {
        login("student' --", "anything")
                .statusCode(401)
                .body("token", nullValue());
    }

    @Test
    @DisplayName("Spec H-AUTH-01: contraseña legítima con comilla simple responde 401, no 500")
    void passwordWithSingleQuoteIsRejectedWithoutServerError() {
        login(STUDENT_USERNAME, "it's")
                .statusCode(401)
                .body("token", nullValue());
    }
}
