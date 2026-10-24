# Esquema conceptual de red y puertos

```mermaid
flowchart LR
 V[Villavicencio] --> PL[Puerto López]
 PL --> PG[Puerto Gaitán]
 PG --> F[Terminal fluvial hipotética]
 V --> H[Interfaz con red carretera]
 PL --> C[Patio de carga y pasajeros]
 C --> T[Centro de transferencia]
 T --> DC[Zona logística y digital]
 F --> R[Hidrovía: verificar navegabilidad]
 R --> M[Mercados de destino]
```

Este esquema representa conectividad funcional, no coordenadas, alineamiento ni infraestructura existente. Para puertos marítimos, modelar nodos alternativos y conexión terrestre por corredor independiente; no asumir enlace férreo continuo.
