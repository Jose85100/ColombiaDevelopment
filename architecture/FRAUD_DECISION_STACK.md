# Fraud and KYC — arquitectura multicapa

```mermaid
flowchart LR
 subgraph EDGE[Captura con consentimiento y base legal]
  A[Solicitud] --> ID[Identidad/documento]
  A --> DEV[Dispositivo y red]
  A --> VEL[Velocidad de eventos]
  A --> BEH[Conducta]
 end
 subgraph CONTROL[Confianza y seguridad]
  ID --> VAL[Validación y minimización]
  DEV --> VAL
  VEL --> VAL
  BEH --> VAL
  VAL --> F[Features con TTL]
 end
 subgraph DETECT[Detección]
  F --> RULE[Reglas]
  F --> ANOM[Anomalías]
  F --> GRAPH[Grafos de vínculos]
  F --> UNC[Incertidumbre / drift]
 end
 RULE --> ORCH[Orquestación]
 ANOM --> ORCH
 GRAPH --> ORCH
 UNC --> ORCH
 ORCH --> PASS[Continuar]
 ORCH --> STEP[Verificación reforzada]
 ORCH --> CASE[Revisión humana]
 CASE --> LABEL[Etiquetas verificadas]
 LABEL --> MON[Monitoreo y recalibración]
 MON --> DETECT
```

No usar señales sensibles o geolocalización sin fundamento legal, proporcionalidad, controles de retención y evaluación de sesgo. La salida es **riesgo para revisión**, no determinación automática de fraude.
