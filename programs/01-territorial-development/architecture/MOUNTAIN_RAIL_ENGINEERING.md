# Ingeniería ferroviaria en montaña — alternativas

```mermaid
flowchart TB
 GEO[DEM, geología, fallas, hidrología] --> ALT[Generación de corredores]
 ALT --> S[Alternativa superficial]
 ALT --> T[Alternativa túnel]
 ALT --> V[Alternativa viaducto]
 S --> SCORE[Optimización multicriterio]
 T --> SCORE
 V --> SCORE
 SCORE --> RISK[Riesgo geotécnico, ambiental y constructivo]
 RISK --> COST[CAPEX, OPEX, plazo y contingencias]
 COST --> REVIEW[Revisión por especialistas y autoridades]
```

Tecnologías candidatas según geología: TBM de roca dura, tuneladora EPB/slurry en suelos adecuados, NATM/SEM, perforación y voladura, viaductos segmentales y monitoreo instrumental. Ninguna tecnología es universal: seleccionar tras investigación geotécnica, hidrogeológica y sísmica.
