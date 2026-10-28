package com.bcp.workshop.auth;

import io.quarkus.test.junit.QuarkusTest;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.Base64;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.notNullValue;

@QuarkusTest
class AuthResourceTest {
    private static final String TEST_SIGNING_SECRET = "test-only-hmac-key-for-auth-token-0123456789";

    @Test
    void logsInWithWorkshopUserAndReturnsSignedJsonToken() throws Exception {
        var response = given()
                .contentType("application/json")
                .body("{\"username\":\"student\",\"password\":\"Workshop123!\",\"client\":\"angular-workshop\"}")
                .when().post("/auth/login")
                .then()
                .statusCode(200)
                .body("user.username", is("student"))
                .body("token", notNullValue())
                .extract()
                .response();

        String token = response.jsonPath().getString("token");
        JsonNode signedToken = new ObjectMapper().readTree(token);
        JsonNode payload = signedToken.path("payload");
        String signature = signedToken.path("signature").asText();
        byte[] actualSignature = Base64.getUrlDecoder().decode(signature);
        byte[] expectedSignature = sign(payload.toString());
        long expiresAt = payload.path("expiresAt").asLong();
        long expiresIn = response.jsonPath().getLong("expiresIn");
        long now = Instant.now().getEpochSecond();

        assertEquals(2, signedToken.size());
        assertEquals("student", payload.path("username").asText());
        assertEquals("STUDENT", payload.path("role").asText());
        assertFalse(payload.has("secret"));
        assertTrue(Math.abs((expiresAt - now) - expiresIn) <= 1);
        assertArrayEquals(expectedSignature, actualSignature);

        JsonNode alteredPayload = new ObjectMapper().readTree(payload.toString());
        ((com.fasterxml.jackson.databind.node.ObjectNode) alteredPayload).put("role", "ALTERED");
        assertFalse(Arrays.equals(sign(alteredPayload.toString()), actualSignature));
    }

    @Test
    void rejectsBlankSigningSecret() {
        assertThrows(IllegalStateException.class,
                () -> LegacyTokenUtil.create("test-user", "TEST", " "));
    }

    private byte[] sign(String payload) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(TEST_SIGNING_SECRET.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        return mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
    }
}
