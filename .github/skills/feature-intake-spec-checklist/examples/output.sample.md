# Feature Intake -> Spec Checklist

## Summary
- Añadir claims mínimos al token de login, validar `client`, y mantener coherencia entre `expiresIn` y `exp`.
- Evitar que tokens o secretos aparezcan en logs y definir el uso del secreto por defecto.

## Scope (in/out)
- **In:** claims `sub`, `client`, `iat` y `exp`; obtener y validar `client` desde la solicitud; calcular/verificar coherencia de expiración; tratar el secreto por defecto; prevenir registros de tokens y secretos; pruebas de login válido, credenciales inválidas y token expirado.
- **Out:** HU-01 no especifica exclusiones funcionales. No se infieren cambios adicionales al flujo ni al contrato.

## Assumptions
- La HU identifica `POST /auth/login` y la respuesta actual con `token`, `expiresIn` y `user`.
- La HU indica que la implementación usa HMAC y lee `AUTH_TOKEN_SECRET`; no se asume que HMAC deba conservarse.
- No se añaden requisitos ni valores no definidos por la HU.

## Technical decisions to make
- **Pending:** conservar HMAC o adoptar una librería JWT.
- **Pending:** definir los valores/formatos de `client` aceptados y cómo se valida.
- **Pending:** documentar la tolerancia para comprobar `expiresIn` frente a `exp - now`.
- **Pending:** retirar el secreto por defecto fuera del laboratorio o documentarlo como exclusivo de laboratorio; definir qué configuración identifica ese entorno.

## Risks and mitigations
- **Secreto por defecto usado fuera del laboratorio.** Mitigación: retirarlo fuera del laboratorio o documentar y verificar su alcance exclusivo de laboratorio.
- **Token o secreto expuesto en logs.** Mitigación: revisar los logs del flujo de login y comprobar con datos de prueba que ninguno de esos valores aparece.
- **Claim `client` ausente o no validado.** Mitigación: definir la regla de validación antes de emitir el token y cubrir entradas aceptadas y rechazadas con pruebas.
- **Desacuerdo entre expiración declarada y claim `exp`.** Mitigación: documentar la tolerancia antes de validar la relación y probar sus límites.

## Acceptance criteria
- Todo token emitido por un login válido contiene `sub`, `client`, `iat` y `exp`.
- `client` del token corresponde al valor validado recibido en la solicitud.
- `expiresIn` coincide con `exp - now` dentro de una tolerancia documentada.
- Hay pruebas para login válido, credenciales inválidas y token expirado.
- La revisión de logs de los casos de prueba no encuentra tokens, secretos ni valores sensibles.
- La decisión HMAC/JWT está documentada, y el tratamiento del secreto por defecto está configurado o documentado según la decisión acordada.

## Validation plan
- **Unit tests:** verificar presencia y valores de los claims; comprobar cálculo de expiración dentro y fuera de la tolerancia acordada; cubrir validación de `client`.
- **Functional tests:** probar login válido y credenciales inválidas; validar claims y `expiresIn` de la respuesta; comprobar el caso de token expirado.
- **Security checks:** revisar configuración del secreto por defecto y comprobar que logs de pruebas no contienen tokens, secretos ni valores sensibles.
- **Evidence:** resultados de pruebas de claims, expiración y autenticación; documentación de la decisión HMAC/JWT y configuración de `AUTH_TOKEN_SECRET`; evidencia de revisión de logs redactados.

## Suggested tasks by role
- **Chapter/PO:** confirmar los criterios de aceptación; acordar qué se considera `client` válido; resolver qué entornos cuentan como laboratorio.
- **Tech Lead:** decidir HMAC o librería JWT; acordar tolerancia y su documentación; definir la responsabilidad de validación de `client` y de configuración del secreto.
- **Backend:** implementar los claims mínimos; validar `client` y hacer coherente `expiresIn` con `exp`; añadir pruebas unitarias para claims, expiración y entradas de `client`.
- **Frontend:** confirmar el origen del valor `client` que envía el login; si se requiere un cambio en el consumidor, enviarlo conforme a la regla acordada y cubrir ese envío.
- **QA:** preparar casos de login válido, credenciales inválidas y token expirado; verificar claims y coherencia de expiración con la tolerancia aprobada; adjuntar resultados y revisión de logs.
- **Cyber:** revisar el ciclo de vida/configuración del secreto por defecto; comprobar que los logs no exponen tokens ni secretos; revisar los riesgos de la decisión de firma seleccionada.

## Open questions
- ¿Qué valores y formato de `client` son válidos, y qué respuesta corresponde a un valor inválido?
- ¿Cuál es la tolerancia exacta y documentada para comparar `expiresIn` con `exp - now`?
- ¿Se conservará HMAC o se adoptará una librería JWT?
- ¿Qué entornos se consideran exclusivamente de laboratorio y cómo se retirará o documentará allí el secreto por defecto?
- ¿Qué respuesta y contrato aplican al login con credenciales inválidas y al uso de un token expirado?