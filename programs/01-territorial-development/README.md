# Programa 01 — Desarrollo territorial y económico

Fuente inicial: documento **Desarrollo Económico / NOVDE** en Drive.

## Cartera inicial
1. Atlas multicriterio de oportunidad territorial.
2. Optimizador de localización de microredes y nodos digitales.
3. Modelo tecnoeconómico solar + almacenamiento + biomasa.
4. Simulador de impacto local: empleo, productividad, conectividad y acceso energético.
5. Motor de priorización SGR/cofinanciación con restricciones presupuestales.
6. Stress test climático y de continuidad energética.
7. Digital twin territorial para escenarios de infraestructura.

## Arquitectura
```mermaid
flowchart LR
 S[DANE/UPME/IPSE/IDEAM/territorio] --> Q[Calidad y georreferenciación]
 Q --> F[Feature store territorial]
 F --> M1[MCDA / ranking]
 F --> M2[Optimización de localización]
 F --> M3[Modelo tecnoeconómico]
 M1 --> SC[Escenarios]
 M2 --> SC
 M3 --> SC
 SC --> D[Dashboard + mapas + ficha municipal]
 D --> V[Validación y decisión]
```

## Archivos del programa
- `architecture/`: digital twin, corredores y decisiones ferroviarias.
- `docs/`: riesgos, topografía, supuestos y fuentes de datos.
- `notebooks/`: escenarios territoriales, Monte Carlo, ferrocarril y corredor Chocó–Pacífico.
- `python/colombia_dev/` y `cpp/`: prototipos de evaluación territorial e infraestructura.
- `tests/`: pruebas del código del programa.

Primera exigencia: verificar cifras, cobertura, potencial energético y restricciones ambientales antes de parametrizar modelos.
