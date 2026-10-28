package com.bcp.workshop.auth;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.microprofile.config.ConfigProvider;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.time.Instant;
import java.util.Base64;

public final class LegacyTokenUtil {
    private static final long TOKEN_LIFETIME_SECONDS = 3600;
    private static final String SIGNATURE_ALGORITHM = "HmacSHA256";
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private LegacyTokenUtil() {}

    public static String create(String username, String role) {
        String secret = ConfigProvider.getConfig().getValue("auth.token.secret", String.class);
        return create(username, role, secret);
    }

    static String create(String username, String role, String secret) {
        if (secret.isBlank()) {
            throw new IllegalStateException("Token signing key is not configured");
        }

        TokenPayload payload = new TokenPayload(
                username,
                role,
                Instant.now().plusSeconds(TOKEN_LIFETIME_SECONDS).getEpochSecond()
        );

        try {
            byte[] payloadBytes = OBJECT_MAPPER.writeValueAsBytes(payload);
            String signature = Base64.getUrlEncoder().withoutPadding()
                    .encodeToString(sign(payloadBytes, secret));
            return OBJECT_MAPPER.writeValueAsString(new SignedToken(payload, signature));
        } catch (GeneralSecurityException | JsonProcessingException error) {
            throw new IllegalStateException("Unable to create signed token", error);
        }
    }

    private static byte[] sign(byte[] payload, String secret) throws GeneralSecurityException {
        Mac mac = Mac.getInstance(SIGNATURE_ALGORITHM);
        mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), SIGNATURE_ALGORITHM));
        return mac.doFinal(payload);
    }

    @JsonPropertyOrder({"username", "role", "expiresAt"})
    private record TokenPayload(String username, String role, long expiresAt) {}

    @JsonPropertyOrder({"payload", "signature"})
    private record SignedToken(TokenPayload payload, String signature) {}
}
