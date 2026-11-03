---
name: jira-incident-root-cause
description: Lee incidentes de Jira, los categoriza y agrupa por patrón, identifica sus causas raíz probables y genera un análisis ejecutivo con hallazgos, impacto y acciones priorizadas.
---
# Skill: Jira Incidents -> Root Cause Analysis

## 1) Metadata

- **Skill ID:** jira-incident-root-cause
- **Version:** 0.1.0
- **Purpose:** Convertir un conjunto de incidentes de Jira en un análisis ejecutivo que agrupe los casos por patrón, identifique causas raíz recurrentes y priorice acciones correctivas y preventivas.
- **Audience (roles):** Chapter/PO, Tech Lead, Backend, Frontend, QA, Cyber, Dirección de TI
- **When to use:** Revisión periódica de incidentes (semanal, mensual o trimestral), análisis posterior a una serie de incidentes relacionados o preparación de un informe ejecutivo de estabilidad.
- **When NOT to use:** Gestión en tiempo real de un incidente P1 activo, un único incidente sin relación con otros, o tickets que no sean incidentes (historias, tareas, mejoras).
- **Sensitive inputs:** No incluyas datos reales de clientes, credenciales, secretos, tokens, números de cuenta, correos personales ni URLs internas no autorizadas. Redacta esos valores antes de pegar el contenido.
- **Expected output:** Markdown estructurado mediante la sección Output a continuación.

## 2) Inputs

Proporciona la información en este formato:

- **Período de análisis:** Fecha inicial y final (por ejemplo, 2026-08-01 a 2026-10-31).
- **Fuente:** Proyecto y filtro de Jira usados para obtener los incidentes (por ejemplo, `project = OPS AND issuetype = Incident AND created >= 2026-08-01`), o exportación CSV/JSON.
- **Campos disponibles:** Campos incluidos (clave, resumen, descripción, prioridad, estado, fechas de creación y resolución, componente, etiquetas, asignado, comentarios de causa raíz).
- **Contexto de negocio (brief):** Servicios o procesos afectados y objetivo del análisis.
- **Objetivo ejecutivo:** Decisión que el informe debe apoyar (por ejemplo, priorizar inversión en pruebas de regresión).
- **Taxonomía de categorías (opcional):** Categorías propias del equipo. Si no se entrega, usa la taxonomía por defecto de la sección 4.
- **Restricciones:** Tiempo máximo, nivel de detalle esperado o audiencia.

## 3) Output

Devuelve **solo** un documento Markdown con estas secciones y bullets:

1. **Resumen ejecutivo**
   - Mensaje principal en 3 a 5 líneas: volumen, patrón dominante y causa raíz más relevante.
   - Recomendación central y decisión requerida, si aplica.

2. **Indicadores clave**
   - Total de incidentes analizados y período.
   - Distribución por prioridad y severidad.
   - Distribución por categoría de causa raíz (número y porcentaje).
   - Tiempo medio de resolución (MTTR), solo si las fechas lo permiten; si no, indícalo.

3. **Categorías de incidentes**
   - Tabla con: Categoría, Descripción, Número de incidentes, Porcentaje y Claves de Jira representativas.

4. **Agrupación por causa raíz**
   - Por cada grupo: Causa raíz probable, Incidentes asociados (claves), Evidencia (frase o campo de Jira que la respalda), Nivel de confianza (Alta, Media o Baja) y Servicios afectados.

5. **Impacto**
   - Impacto para clientes, operación o cumplimiento, expresado en términos cualitativos y, cuando existan datos, cuantitativos (tiempo fuera de servicio, número de clientes afectados, reincidencias).

6. **Patrones y tendencias**
   - Recurrencias, incidentes repetidos, componentes con mayor concentración y tendencia respecto al período anterior, si hay datos.

7. **Acciones recomendadas**
   - Acciones correctivas (eliminan la causa raíz) y preventivas (evitan recurrencia).
   - Cada acción con: Prioridad, Responsable sugerido por rol, Resultado esperado y Métrica de seguimiento.

8. **Riesgos y limitaciones del análisis**
   - Calidad de los datos de Jira (campos vacíos, causas raíz no documentadas, incidentes duplicados).
   - Sesgos y supuestos declarados.

9. **Preguntas abiertas**
   - Información faltante que cambiaría las conclusiones.

## 4) Constraints

- Clasifica cada incidente en **una sola** categoría principal. Si un incidente tiene causas secundarias, menciónalas en la descripción del grupo, no como doble conteo.
- Taxonomía por defecto (usa la del equipo si se entrega otra):
  - **Código / defecto de software:** error lógico, excepción no controlada, regresión tras un cambio.
  - **Configuración / despliegue:** variable de entorno incorrecta, despliegue fallido, rollback no ejecutado.
  - **Dependencia externa / integración:** servicio de terceros, API o servicio interno caído o con cambio de contrato.
  - **Datos:** datos corruptos, migración incorrecta, validación de datos insuficiente.
  - **Infraestructura / capacidad:** caída de servidor, saturación de CPU, memoria, red o almacenamiento.
  - **Seguridad:** acceso indebido, exposición de datos, vulnerabilidad explotada o alerta de seguridad.
  - **Proceso / humano:** falta de procedimiento, error operativo, comunicación deficiente o escalamiento tardío.
  - **Sin causa determinada:** la información en Jira no permite clasificar; no lo fuerces.
- Usa solo la información de los incidentes entregados. No inventes causas, cifras, responsables ni fechas.
- Toda causa raíz debe citar al menos una clave de Jira como evidencia.
- Si la causa raíz no está documentada en Jira, indica **"No documentada"** y asigna nivel de confianza Baja.
- No incluyas datos sensibles ni secretos, aunque aparezcan en los tickets; sustitúyelos por `[REDACTADO]`.
- El resumen ejecutivo debe caber en una página y usar lenguaje no técnico cuando sea posible.
- Las acciones deben ser verificables; no escribas "mejorar la estabilidad" sin una métrica de seguimiento.
- Mantén la salida en un máximo de 2 páginas para que siga siendo usable.

## 5) Validation Rules

La salida es válida si:

- Incluye todas las secciones definidas en Output.
- La suma de incidentes por categoría coincide con el total de incidentes analizados.
- Cada grupo de causa raíz tiene al menos una clave de Jira como evidencia.
- Hay al menos 2 acciones recomendadas, cada una con métrica de seguimiento.
- Las causas raíz sin respaldo en Jira aparecen con nivel de confianza Baja o como "No documentada".
- Las limitaciones del análisis están declaradas en la sección 8.
- No contiene datos sensibles, secretos ni cifras que no provengan de la entrada.

## 6) Evidence

Adjunta o referencia estos elementos en la entrega:

- `SKILL.md` versionado.
- `examples/input.sample.md`.
- `examples/output.sample.md`.
- Consulta JQL o exportación utilizada para obtener los incidentes, con fecha de extracción.
- Tabla de conteo que demuestre que la suma por categoría coincide con el total.
- Tag de versión para el Skill, como `skill-jira-incident-rca-v0.1.0`.
