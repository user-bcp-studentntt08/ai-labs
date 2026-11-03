# Análisis ejecutivo de incidentes: OPS (2026-08-01 a 2026-10-31)

## 1. Resumen ejecutivo

- Se analizaron **10 incidentes**. El 40 % se origina en defectos de software en el flujo de transferencias, que generaron **4 duplicados**.
- Las causas raíz de duplicados son dos: falta de idempotencia en el servicio de transferencias y botón de envío sin bloqueo durante la petición.
- Los **3 incidentes P1** tienen causas de configuración, dependencia externa e infraestructura (certificado vencido). Este último se habría evitado con una alerta preventiva.
- **Recomendación:** invertir en idempotencia de transferencias, bloqueo de envío en la interfaz y alertas de vencimiento de certificados y de saturación de conexiones.

## 2. Indicadores clave

- **Total analizado:** 10 incidentes (período 2026-08-01 a 2026-10-31).
- **Por prioridad:** P1: 3 (30 %) · P2: 5 (50 %) · P3: 2 (20 %).
- **Por categoría:** Código 4 (40 %) · Infraestructura 2 (20 %) · Configuración 1 (10 %) · Dependencia externa 1 (10 %) · Seguridad 1 (10 %) · Sin causa determinada 1 (10 %).
- **MTTR aproximado:** 0,5 días (≈12 h). Las fechas tienen granularidad de día; el cálculo es orientativo.

## 3. Categorías de incidentes

| Categoría | Descripción | Número | % | Claves representativas |
|---|---|---|---|---|
| Código / defecto de software | Lógica que permite duplicados o reintentos inseguros | 4 | 40 % | OPS-101, OPS-160, OPS-118, OPS-190 |
| Infraestructura / capacidad | Saturación de recursos o certificados sin control | 2 | 20 % | OPS-171, OPS-203 |
| Configuración / despliegue | Variable de entorno no actualizada tras despliegue | 1 | 10 % | OPS-134 |
| Dependencia externa | Cambio no anunciado de un proveedor | 1 | 10 % | OPS-185 |
| Seguridad | Datos sensibles en registros | 1 | 10 % | OPS-214 |
| Sin causa determinada | Causa no documentada en Jira | 1 | 10 % | OPS-152 |
| **Total** | | **10** | **100 %** | |

## 4. Agrupación por causa raíz

| Causa raíz probable | Incidentes | Evidencia (Jira) | Confianza | Servicios |
|---|---|---|---|---|
| Transferencias no idempotentes ante reintentos | OPS-101, OPS-160 | "Reintento sin idempotencia en el servicio de transferencias" | Alta | transfers |
| Botón de envío sin bloqueo durante la petición | OPS-118, OPS-190 | "Botón de envío sin deshabilitar durante la petición" | Alta | web |
| Secreto de token no actualizado en producción | OPS-134 | Campo "Causa raíz" | Alta | auth |
| Pool de conexiones saturado en hora pico | OPS-171 | Campo "Causa raíz" | Media | auth |
| Certificado TLS vencido sin alerta | OPS-203 | "Certificado TLS sin alerta de vencimiento" | Alta | auth |
| Cambio de formato del proveedor sin aviso | OPS-185 | Campo "Causa raíz" | Media | payments |
| Datos sensibles registrados en consola | OPS-214 | "Registro de datos sensibles en consola" | Alta | web |
| Timeout en consulta de saldo | OPS-152 | No documentada | Baja | accounts |

## 5. Impacto

- **Clientes:** 4 transferencias duplicadas en el período; la doble ejecución puede generar reclamos y reversiones manuales.
- **Disponibilidad:** 3 eventos P1 con afectación de inicio de sesión (2) y pagos con tarjeta (1).
- **Cumplimiento:** 1 exposición de datos sensibles en registros (OPS-214), que requiere revisión de seguridad.

## 6. Patrones y tendencias

- **Recurrencia:** Dos pares de incidentes idénticos (OPS-101/OPS-160 y OPS-118/OPS-190) indican que las correcciones previas no eliminaron la causa.
- **Concentración:** El componente `auth` concentra 3 incidentes, dos de ellos P1.
- **Tendencia:** No hay datos del período anterior para comparar.

## 7. Acciones recomendadas

| # | Acción | Tipo | Prioridad | Responsable sugerido | Resultado esperado | Métrica de seguimiento |
|---|---|---|---|---|---|---|
| 1 | Implementar clave de idempotencia en transferencias | Correctiva | Alta | Backend / Tech Lead | Ningún reintento genera transferencias duplicadas | 0 duplicados por reintento en 30 días |
| 2 | Deshabilitar el botón de envío durante la petición | Correctiva | Alta | Frontend | Un solo envío por acción del usuario | Quejas por duplicados de transferencia −20 % en un mes |
| 3 | Alerta de vencimiento de certificados TLS con 30 días de anticipación | Preventiva | Alta | Cyber / Infraestructura | Renovación antes del vencimiento | 0 incidentes por certificado vencido |
| 4 | Redactar datos sensibles en registros y revisar logs existentes | Correctiva | Alta | Cyber / Frontend | Ningún dato sensible en registros | 0 hallazgos en la revisión de logs |
| 5 | Checklist de despliegue con verificación de variables de entorno | Preventiva | Media | Tech Lead / QA | Variables validadas antes de producción | 0 incidentes por configuración en el próximo trimestre |
| 6 | Documentar causa raíz obligatoria al cerrar incidentes | Preventiva | Media | Chapter/PO | Causas raíz documentadas en todos los tickets | 100 % de incidentes cerrados con causa raíz |

## 8. Riesgos y limitaciones del análisis

- **Datos:** El incidente OPS-152 no tiene causa documentada; su clasificación es de baja confianza.
- **Granularidad:** Las fechas por día limitan la precisión del MTTR.
- **Muestra:** 10 incidentes son insuficientes para tendencias estadísticas; las conclusiones son orientativas.
- **Supuesto declarado:** Los incidentes OPS-101 y OPS-160 comparten causa según sus descripciones; no se revisó el código.

## 9. Preguntas abiertas

- ¿Cuál fue el resultado del análisis de OPS-152 (timeout en saldo)?
- ¿Existe un análisis previo del período anterior para comparar tendencias?
- ¿Qué proveedor generó el cambio de formato en OPS-185 y existe un canal de notificación?
