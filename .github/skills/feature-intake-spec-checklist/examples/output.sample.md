# Feature Intake -> Spec Checklist

## 1. Summary
- Permitir que la persona usuaria confirme una transferencia antes de enviarla, revise un resumen y valide los datos para reducir transferencias duplicadas.
- Impacto esperado: reducir 20% las quejas por transferencias duplicadas en un mes. La medición requiere acordar la línea base.

## 2. Scope
- **Dentro del alcance:** confirmación previa al envío, mensaje resumen y validación de datos de transferencia; integración con los servicios existentes de cuentas y transferencias.
- **Fuera del alcance:** cambios de infraestructura y rediseño completo de la interfaz.

## 3. Supuestos
- La funcionalidad se incorpora al frontend web y a la API REST existentes.
- Se mantienen los estándares de logging actuales y se evita registrar datos sensibles.
- Los servicios de cuentas y transferencias siguen siendo las dependencias para consultar y enviar transferencias.

## 4. Decisiones técnicas por tomar (pendientes o resueltas)
- **Pendiente:** definir qué campos aparecen en el resumen y confirmar que coinciden con los datos que se enviarán.
- **Pendiente:** acordar qué validaciones de datos aplican y qué mensajes se muestran cuando fallan, especialmente para el importe.
- **Pendiente:** determinar el contrato de API y el límite de responsabilidad entre frontend y backend para la confirmación y validación.
- **Resuelto por el alcance:** reutilizar la API REST, el frontend web y los estándares de logging existentes; no hacer cambios de infraestructura.

## 5. Riesgos y mitigaciones
- **Exposición de datos sensibles en logs.** Mitigación: revisar los eventos de logging relacionados, limitar sus campos a datos no sensibles y comprobar la salida durante las pruebas.
- **Validación incorrecta del importe.** Mitigación: acordar reglas con el equipo responsable, probar límites y valores inválidos, y bloquear el envío si la validación falla.
- **Desacuerdo entre resumen y transferencia enviada.** Mitigación: verificar que el resumen corresponde a los datos validados y enviados, y cubrir ese flujo con pruebas funcionales.

## 6. Criterios de aceptación (medibles)
- Para cada intento con datos válidos, se muestra una confirmación con un resumen antes de invocar el envío de la transferencia.
- Para cada intento con datos inválidos, el envío no se invoca y se muestra un mensaje de validación.
- Los campos del resumen coinciden con los datos validados que se envían a la API.
- Los eventos de logging del flujo no contienen datos sensibles de la transferencia.
- En el primer mes de medición acordado, las quejas por transferencias duplicadas se reducen 20% respecto de la línea base definida.

## 7. Plan de validación
- **Pruebas unitarias:** cubrir la validación de los datos e importes acordados; comprobar que el envío solo se habilita con datos válidos; comprobar la composición del resumen.
- **Pruebas funcionales:** recorrer la confirmación y envío exitosos; verificar que datos inválidos detienen el envío; verificar que el resumen mostrado corresponde a la transferencia enviada.
- **Seguridad (comprobaciones mínimas):** inspeccionar los eventos de logging para confirmar que no incluyen datos sensibles; comprobar que el flujo no expone información de cuentas fuera del resumen aprobado.
- **Evidencia requerida (qué adjuntar):** salida de las pruebas unitarias y funcionales, checklist de revisión de logs y referencia al documento breve actualizado con las reglas de validación y la métrica de quejas.

## 8. Tareas sugeridas por rol
- **Chapter/PO:** definir la línea base y fuente de las quejas por duplicados; confirmar el objetivo del 20% y periodo de medición; aprobar el contenido del resumen y los mensajes de validación.
- **Tech Lead:** definir el contrato entre frontend y API; asignar responsabilidades de validación; revisar el diseño de logging para minimizar datos y documentar las decisiones.
- **Backend:** revisar las capacidades existentes de la API y del servicio de transferencias; implementar las validaciones acordadas en el límite correspondiente; añadir pruebas unitarias para validación, envío y campos registrados.
- **Frontend:** implementar la confirmación previa al envío; presentar el resumen de los datos validados; impedir el envío y mostrar el mensaje acordado ante datos inválidos.
- **QA:** preparar casos para datos válidos e inválidos, incluidos importes límite acordados; verificar el orden confirmación-envío y la coincidencia del resumen; adjuntar resultados de pruebas funcionales y registrar la medición del impacto al cumplirse un mes.
- **Cyber:** revisar los campos de los eventos de logging; comprobar que los datos sensibles no se exponen en la interfaz ni en registros; documentar los hallazgos y su resolución.

## 9. Preguntas abiertas
- ¿Cuál es la fuente y el periodo de referencia para calcular la línea base de quejas por transferencias duplicadas?
- ¿Qué campos debe incluir el resumen de confirmación?
- ¿Cuáles son las reglas válidas y los límites de importe que deben aplicarse?
- ¿Qué contrato o versión de la API debe soportar el flujo y qué servicio es responsable de cada validación?
- ¿Qué datos se consideran sensibles según los estándares de logging existentes?