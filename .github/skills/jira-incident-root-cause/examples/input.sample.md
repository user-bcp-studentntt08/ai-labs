# Input de ejemplo: incidentes de Jira

- **Período de análisis:** 2026-08-01 a 2026-10-31
- **Fuente:** `project = OPS AND issuetype = Incident AND created >= "2026-08-01" AND created <= "2026-10-31"` (extraído el 2026-11-02)
- **Campos disponibles:** clave, resumen, descripción, prioridad, estado, creado, resuelto, componente, etiquetas, asignado, campo "Causa raíz" y comentarios.
- **Contexto de negocio:** Incidentes en el flujo de transferencias y en el inicio de sesión de la banca web.
- **Objetivo ejecutivo:** Decidir la inversión del próximo trimestre en estabilidad.
- **Taxonomía de categorías:** Por defecto.
- **Restricciones:** Máximo 2 páginas; audiencia de dirección de TI.

## Incidentes (resumidos y redactados)

| Clave | Resumen | Prioridad | Creado | Resuelto | Componente | Causa raíz (Jira) |
|---|---|---|---|---|---|---|
| OPS-101 | Transferencias duplicadas tras reintento de red | P2 | 2026-08-04 | 2026-08-05 | transfers | Reintento sin idempotencia en el servicio de transferencias |
| OPS-118 | Duplicado de transferencia por doble clic | P3 | 2026-08-12 | 2026-08-12 | web | Botón de envío sin deshabilitar durante la petición |
| OPS-134 | Login falla tras despliegue | P1 | 2026-08-20 | 2026-08-20 | auth | Variable de entorno del secreto de token no actualizada en producción |
| OPS-152 | Timeout al consultar saldo | P2 | 2026-09-03 | 2026-09-04 | accounts | Sin causa documentada |
| OPS-160 | Transferencias duplicadas con monto alto | P2 | 2026-09-10 | 2026-09-11 | transfers | Reintento sin idempotencia en el servicio de transferencias |
| OPS-171 | Login lento en horario pico | P2 | 2026-09-18 | 2026-09-19 | auth | Pool de conexiones a base de datos saturado |
| OPS-185 | Error 500 en pagos con tarjeta | P1 | 2026-10-02 | 2026-10-02 | payments | Proveedor externo cambió el formato de respuesta sin aviso |
| OPS-190 | Duplicado de transferencia por reintento de usuario | P3 | 2026-10-08 | 2026-10-08 | web | Botón de envío sin deshabilitar durante la petición |
| OPS-203 | Login falla por certificado expirado | P1 | 2026-10-21 | 2026-10-21 | auth | Certificado TLS sin alerta de vencimiento |
| OPS-214 | Cliente expone número de cuenta en el log | P2 | 2026-10-27 | 2026-10-28 | web | Registro de datos sensibles en consola (`[REDACTADO]`) |

- **Comentarios relevantes:** OPS-160 menciona que el usuario reenvió la transferencia tras un error de red.
