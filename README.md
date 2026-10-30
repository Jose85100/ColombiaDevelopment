# ColombiaDevelopment

Laboratorio técnico de **Colombia Risk**: transforma investigación formulada en Drive en código, modelos, diagramas, pruebas y evidencia reproducible.

## Sistema de trabajo
- Investigación e ideación: https://drive.google.com/drive/folders/1ZC9eMthrbclWNSY08OEgcuBJ2vyxipPF
- Desarrollo técnico: este repositorio.
- Gobierno institucional: BUSS_Colombia Risk.

## Programas

| N.º | Programa | Estado y alcance |
|---|---|---|
| 01 | [Desarrollo territorial y económico](programs/01-territorial-development/README.md) | NOVDE, infraestructura, energía, conectividad y evaluación territorial |
| 02 | [Fraude, identidad y KYC](programs/02-fraud-identity/README.md) | Anomalías, grafos, señales de dispositivo, identidad sintética y defensa multicapa |
| 03 | [Riesgo y analítica judicial](programs/03-judicial-risk/README.md) | Provenance, eventos, entity resolution, supervivencia y exposición con revisión humana |
| 04 | [Agroindustria tecnificada y propiedad campesina](programs/04-agroindustry-farmer-ownership/README.md) | Capital privado, productividad, participación campesina y logística |
| 05 | [Integridad Pública Verificable](programs/05-public-integrity/README.md) | Anticorrupción, expediente criptográfico, hitos tokenizados, intranets y arquitecturas comparables |

## Organización

Cada programa concentra sus entregables y usa solo las subcarpetas que necesita:

- `architecture/`: diagramas y decisiones propias del programa.
- `docs/`: informes técnicos, supuestos y catálogos de datos.
- `notebooks/`: análisis reproducibles.
- `python/`, `cpp/`, `tests/`, `data/`, `examples/`: código, pruebas, datos de muestra y ejecuciones.

Los recursos transversales están en `shared/`; las reglas de investigación y ciclo de experimentos están en `docs/`. La estructura y comandos de desarrollo están definidos en `CMakeLists.txt`, `pyproject.toml` y `.github/workflows/ci.yml`.

## Madurez
R0 Idea → R1 Formulación → R2 Diseño → R3 Prototipo → R4 Validación → R5 Piloto.

Una idea en Drive no equivale a producto terminado. Cada resultado debe registrar fuente, hipótesis, datos/licencia, versión, pruebas, métricas, limitaciones y trazabilidad.

No almacenar PII, expedientes sensibles, secretos ni datos confidenciales. Colombia Risk es independiente de Axioma; Shadow Risk pertenece a Axioma.
