# Validación del prototipo IPV

El alcance validado corresponde al laboratorio sintético de hashes encadenados y raíz Merkle. No autentica personas, fechas ni la veracidad material de los documentos y no constituye una blockchain desplegada.

Desde la raíz del repositorio:

- Pruebas: `python -m pytest programs/05-public-integrity/tests -q`.
- Demo: `PYTHONPATH=programs/05-public-integrity/python python programs/05-public-integrity/examples/integrity_demo.py`.

Los resultados no justifican por sí solos un piloto institucional. Antes de ello se requiere amenaza y modelo de confianza, checkpoint externo autenticado, controles de acceso, revisión jurídica y de protección de datos, integración de firmas, evaluación de costo/latencia y una prueba con actores autorizados y datos sintéticos.
