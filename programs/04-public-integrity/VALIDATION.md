# Validación del prototipo — 2026-10-24

Entorno local: Python 3.12, pytest 9.1.1.
Comando: `PYTHONPATH=python python -m pytest python/tests/test_integrity.py -q`.
Resultado: **10 pruebas aprobadas** (0.02 segundos en esta ejecución; no es benchmark).

Demo: `PYTHONPATH=python python python/examples/integrity_demo.py`.
- Historia original frente a checkpoint externo: True.
- Historia reescrita frente a su propio checkpoint: True.
- Historia reescrita frente a checkpoint original: False.
- Historia truncada frente a checkpoint original: False.

La suite cubre integridad del subconjunto experimental, no seguridad del sistema completo.
No se ejecutaron pruebas de firmas, tokens, red blockchain, intranet o banco: no están implementados.
No se ejecutó la suite preexistente completa en este entorno; los archivos nuevos se integran
en el descubrimiento de pytest del CI existente.
