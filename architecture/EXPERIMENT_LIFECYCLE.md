# Ciclo de vida de investigación cuantitativa

```mermaid
stateDiagram-v2
 [*] --> Hipotesis
 Hipotesis --> ContratoDeDatos
 ContratoDeDatos --> Baseline
 Baseline --> Proyecciones
 Proyecciones --> StressTesting
 StressTesting --> Backtesting
 Backtesting --> Revision: evidencia suficiente
 Backtesting --> Hipotesis: falla
 Revision --> Publicacion: aprobado
 Revision --> Hipotesis: cambios
 Publicacion --> Monitoreo
 Monitoreo --> Hipotesis: drift / nuevos datos
```

Cada corrida registra seed, versión, parámetros, horizonte, métricas, supuestos y artefactos. Las proyecciones son condicionales, no predicciones garantizadas.
