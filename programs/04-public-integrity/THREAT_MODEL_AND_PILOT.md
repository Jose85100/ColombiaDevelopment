# Amenazas, contrato de eventos y piloto
## Fronteras de confianza
Operador del expediente, proveedor, interventoría, ordenador del gasto, tesorería,
administrador tecnológico, testigo y público son actores separados.
Atacantes posibles: funcionario con acceso legítimo, proveedor coludido, administrador
con control de almacenamiento, cuenta comprometida o testigo que presenta historia incompleta.

| Ataque | Control propuesto | Riesgo residual / ensayo |
|---|---|---|
| Cambiar acta o monto | Hash de archivo original y evento versionado | Sustituir archivo; detectar frente al checkpoint confiable |
| Reescribir toda la historia | Checkpoint firmado externo y múltiples testigos | Sin referencia externa un atacante puede recalcular hashes |
| Eliminar últimos eventos | Conteo y raíz de checkpoint | El checkpoint viejo no detecta omisiones posteriores |
| Omitir un contrato desde origen | Conciliar inventario con fuente externa | La criptografía no descubre lo que nunca se registró |
| Acta falsa o colusión | Inspección aleatoria y fuentes independientes | Registro íntegro puede contener falsedad |
| Pago duplicado / carrera | Clave idempotente, bloqueo/versionado y conciliación | Ensayar peticiones simultáneas y respuestas bancarias inciertas |
| Aprobar con cuenta robada | MFA, firma, límites y detección de sesión | Revocación, recuperación y análisis de alcance |
| Firmante revocado | PKI, evidencia temporal y política de revocación | No borrar evidencia histórica; evaluar validez al momento de firma |
| Bifurcar historia por auditor | Comparación entre testigos y consistencia | Colusión de todos los testigos sigue siendo posible |
| Filtrar información | Bóveda cifrada, minimización y redacción | Hashes y metadatos también pueden identificar |
| Alerta algorítmica errónea | Revisión humana y mecanismo de corrección | Una alerta no prueba corrupción |

## Contrato candidato v1 para integración
event_id único, schema_version, contract_id y milestone_id seudónimos,
tipo, versión de agregado, digest de evidencia, previous_hash, actor_id, actor_org,
rol verificado, tiempo declarado UTC y tiempo de recepción UTC, correlation_id,
policy_version y firma separada con key_id y algoritmo.
No aceptar roles del cliente como autoridad. Validar identidad contra el directorio.
Importes en unidades mínimas enteras y moneda explícita; nunca float.
La firma cubre bytes canónicos y contexto de dominio; usar serialización estandarizada
antes de interoperar. El tiempo declarado no constituye sello de tiempo confiable.
El prototipo usa un subconjunto sintético del contrato y no incluye firmas ni identidad.

## Gobierno y privacidad
Definir custodio documental, administrador de claves, auditor y responsable de publicación.
Separar claves de firma y cifrado, rotar y probar recuperación; registrar uso administrativo.
No poner PII, expedientes reservados, denuncias o secretos en cadena. Las correcciones del
registro inmutable se expresan con nuevos eventos; el ciclo de retención del contenido
fuera de cadena debe diseñarse antes de recolectar datos reales.
Integraciones candidatas: SECOP, sistemas presupuestales y tesorería; conectores, permisos,
calidad, cobertura y licencias pendientes de verificar. No se afirma integración operativa
ni cumplimiento jurídico; esas validaciones son entregables previos al piloto real.

## Evaluación reproducible
1. Generar contratos e hitos sintéticos con semilla fija y etiqueta de ataque conocida.
2. Comparar expediente convencional, registro hash con testigos y ledger permisionado,
   conservando volumen, distribución de ataques y presupuesto de infraestructura.
3. Inyectar edición, eliminación intermedia, truncación, duplicación, reordenamiento,
   reescritura completa, omisión de origen y falsedad inicial.
4. Medir detecciones / ataques inyectados por tipo, falsos positivos / casos limpios,
   cobertura de conciliación, latencias p50/p95, coste por evento, disponibilidad,
   tiempo de recuperación y tiempo de atención humana.
5. Criterio propuesto: detectar el 100% de mutaciones de eventos cubiertos por checkpoint
   externo y cero falsos positivos en corpus sintético. Esto no estima corrupción evitada.
   Los SLO de latencia y coste se fijarán con la entidad antes de probar, no después.
6. Fallar explícitamente ante checkpoint faltante o no autenticado; diferenciar
   integridad comprobada, cobertura incompleta y autenticidad no comprobada.

## Evidencia actual
Las pruebas unitarias cubren cambios de contenido, orden, eliminación, duplicación,
truncación, reescritura recalculada y entrada vacía. La demo muestra que una historia
reescrita puede ser internamente consistente y aun así no coincidir con un checkpoint.
No hay aún benchmark, firma digital, datos reales ni evaluación causal.
