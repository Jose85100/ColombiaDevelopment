# Territorial digital twin — arquitectura de referencia

```mermaid
flowchart TB
 subgraph SOURCE[Fuentes verificadas y licenciadas]
  DANE[DANE: demografía y economía]
  IDEAM[IDEAM: clima]
  UPME[UPME/IPSE: energía]
  GOV[Datos territoriales y presupuestales]
 end
 subgraph DATA[Data platform]
  ING[Ingestión versionada] --> DQ[Contratos y calidad]
  DQ --> GEO[Resolución espacial y temporal]
  GEO --> FS[Features por municipio / fecha]
 end
 DANE --> ING
 IDEAM --> ING
 UPME --> ING
 GOV --> ING
 subgraph MODEL[Motor de decisión]
  FS --> MC[Monte Carlo de shocks]
  FS --> OPT[Optimización de proyectos]
  FS --> ECON[NPV y costo social]
  MC --> PORT[Distribución de pérdidas]
  OPT --> PORT
  ECON --> PORT
 end
 PORT --> EX[Explicabilidad / sensibilidad]
 EX --> MAP[Mapas y escenarios]
 MAP --> HUMAN[Comité de evaluación]
 HUMAN --> AUD[Decisión trazable]
```

**Grano:** municipio × período × fuente. **Controles:** fecha de corte, licencia, completitud, revisiones de series, CRS, validación de rango y consistencia de unidades. **No es un gemelo digital operacional** hasta integrar actualización periódica y validación contra observaciones.
