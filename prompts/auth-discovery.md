# Discovery de auth

## Alcance
- Repositorio `ai-labs`, abierto desde su raíz; inspeccionar código solo en `auth/`.
- Revisar documentación general necesaria y las pruebas/configuración relevantes de `auth/`.
- No modificar código, configuración ni pruebas. No crear issues automáticamente.
- Usar datos ficticios en validaciones locales; no usar servicios remotos ni publicar secretos o credenciales.

## Objetivo
Identificar de tres a cinco riesgos o brechas potenciales del flujo de autenticación con evidencia concreta, impacto, prioridad propuesta, contrato potencialmente afectado y forma de validación.

## Criterios
- Verificar cada afirmación directamente en el código o configuración de `auth/`; no elevar por sí sola una lista de reto o una práctica general a hallazgo.
- Asignar IDs `H-AUTH-NN` sin renumerar los existentes.
- Mantener todos los hallazgos en estado `CANDIDATO` y detenerse para revisión humana.
- Separar evidencia estática de pruebas ejecutadas y propuestas; no afirmar resultados no observados.
- Preservar el contenido y los hallazgos de otros componentes en `HALLAZGOS.md`.

## Hallazgos registrados
- `H-AUTH-01`: concatenación de credenciales en la consulta SQLite.
- `H-AUTH-02`: formato de token generado por Base64 con secreto constante.
- `H-AUTH-03`: campo `client` del request no propagado al token; requiere confirmar el contrato.
- `H-AUTH-04`: contraseñas persistidas y comparadas en texto claro.
- `H-AUTH-05`: mensaje y clase de excepción incluidos en respuesta HTTP 500.

## Pruebas
No ejecutadas en este Discovery. Cada candidato contiene una propuesta de validación local con datos ficticios. `docs/ENDPOINTS.md` no existe; confirmar con revisión humana los contratos potencialmente afectados antes de implementar.
