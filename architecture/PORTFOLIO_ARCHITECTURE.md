# Arquitectura del portafolio

```mermaid
flowchart LR
 D[Drive: investigación] --> G[Gate de formulación]
 G --> I[Issue / especificación]
 I --> A[Arquitectura]
 A --> C[Código y modelos]
 C --> T[Tests y validación]
 T --> E[Evidencia reproducible]
 E --> R[Resultados a Drive]
 R --> P[Publicación / piloto / financiación]
 T -->|falla| A
```

## Capas comunes
Fuentes → ingestión/contratos → calidad → features → modelos → evaluación → decisión/visualización → auditoría.

Cada programa mantiene separación entre datos brutos, transformaciones, modelos y resultados. Los diagramas Mermaid son versionables; para arquitecturas complejas se incorporarán además fuentes editables draw.io.
