---
name: feature-intake-spec-checklist
description: Estandariza la definición de funcionalidades antes de la implementación generando un paquete mínimo trazable que cubra alcance, decisiones, riesgos, criterios de aceptación y planes de validación.
---
# Skill: Feature Intake -&gt; Spec Checklist

## 1) Metadata

- **Skill ID:** feature-intake-spec-checklist
- **Version:** 0.1.0
- **Purpose:** Estandarizar la definición de funcionalidades antes de la implementación generando un paquete mínimo trazable que cubra alcance, decisiones, riesgos, aceptación y validación.
- **Audience (roles):** Chapter/PO, Tech Lead, Backend, Frontend, QA, Cyber
- **When to use:** Antes de crear tareas de implementación o abrir un PR significativo.
- **When NOT to use:** Incidentes P1 de producción, cambios triviales como typos o tareas sin impacto funcional.
- **Sensitive inputs:** No incluyas datos reales de clientes, credenciales, secretos, tokens ni URLs internas no autorizadas.
- **Expected output:** Markdown estructurado mediante la sección Output a continuación.

## 2) Inputs

Proporciona la información en este formato:

- **Business context (brief):** Reduce complaints caused by duplicate transfers.

- **Feature request / user story:** As a user, I want to confirm a transfer before sending it so that I can avoid duplicates.

- **Expected impact (metric or outcome):** Reduce duplicate-transfer complaints by 20% in one month.

- **Scope (in/out):** In: pre-send confirmation, summary message, data validation. Out: infrastructure changes and a complete UI redesign.

- **Known technical constraints:** Existing REST API, web frontend, standardized logging.

- **Known risks:** Sensitive data exposure in logs; amount-validation errors.

- **Dependencies:** Accounts service and transfers service.

- **Team Definition of Done (DoD):** Unit tests, brief documentation, and reviewed PR.

## 3) Output

Devuelve **solo** un documento Markdown con estas secciones y bullets:

1. **Summary** Add a pre-send transfer confirmation with a concise summary and validation of transfer data. Target: 20% reduction in duplicate-transfer complaints in one month.

2. **Scope**

   - Dentro del alcance
   - Fuera del alcance

3. **Supuestos**

4. **Decisiones técnicas por tomar (pendientes o resueltas)**

5. **Riesgos y mitigaciones**

6. **Criterios de aceptación (medibles)**

   \- 95%+ of valid attempts show confirmation before submission. - Invalid data blocks submission with a validation message. - Duplicate complaints drop 20% within one month. - No sensitive values appear in confirmation event logs.

7. **Plan de validación**

   - Pruebas unitarias
   - Pruebas funcionales
   - Seguridad (comprobaciones mínimas)
   - Evidencia requerida (qué adjuntar)

8. **Tareas sugeridas por rol**

   - Chapter/PO
   - Tech Lead
   - Backend
   - Frontend
   - QA
   - Cyber

9. **Preguntas abiertas**

   - What baseline measures the 20% reduction? 
   - Which API version owns the confirmation contract?

## 4) Constraints

- No inventes requisitos: si falta información, inclúyela bajo **Preguntas abiertas**.
- No propongas herramientas fuera del stack permitido.
- No incluyas datos sensibles ni secretos.
- Los criterios de aceptación deben ser verificables; no escribas “mejorar el rendimiento” sin una métrica.
- El plan de validación debe incluir al menos un elemento de evidencia concreto, como salida de pruebas, un checklist o un archivo actualizado.
- Mantén la salida en un máximo de 1-2 páginas para que siga siendo usable.

## 5) Validation Rules

La salida es válida si:

- Incluye todas las secciones definidas en Output.
- Tiene al menos 3 criterios de aceptación medibles.
- Tiene al menos 3 tareas para cada rol central: Tech Lead, Backend y QA, o explica por qué un rol no aplica.
- Incluye al menos 2 riesgos con mitigaciones.
- No contiene datos sensibles ni secretos.
- No contiene supuestos no declarados.

## 6) Evidence

Adjunta o referencia estos elementos en el PR o entrega:

- `SKILL.md` versionado.
- `examples/input.sample.md`.
- `examples/output.sample.md`.
- Tag de versión para el Skill, como `skill-feature-intake-v0.1.0`.