# Integridad Pública Verificable (IPV)

Fecha: 2026-10-24. Diseño R2; componente de integridad R3 experimental. Responsable institucional y entidades participantes: por definir; no hay convenios ni despliegues.

## Problema e hipótesis
Un contrato puede tener documentos sustituidos, actas retroactivas, aprobaciones concentradas o pagos duplicados. IPV propone un expediente verificable desde presupuesto hasta cierre, conectando evidencia física, decisiones y desembolsos. Piloto propuesto: un paquete de obras ferroviarias o logísticas del programa territorial, con datos sintéticos.

Hipótesis falsable: frente al expediente convencional, controles de integridad y separación de funciones reducen alteraciones no detectadas sin volver inviable el trámite. No se presume reducción causal de corrupción por usar blockchain. Un documento falso puede quedar perfectamente registrado.

## Componentes y proyectos
| Proyecto | Resultado propuesto | Control y límite |
|---|---|---|
| Expediente criptográfico | Hash SHA-256 de bytes originales, versiones y cadena de eventos | Detecta cambios frente a una referencia confiable; no acredita veracidad |
| Registro de transparencia | Checkpoints firmados, raíces Merkle y testigos independientes | Detecta reescritura contrastando copias; debe vigilar omisión y bifurcación |
| Hitos tokenizados | Identificador único por contrato/hito y estado de ejecución | Registro no transferible de control; no moneda ni derecho negociable |
| Intranet de integridad | Identidad institucional, MFA, permisos por función y expediente | Una red privada no basta para confiar en un usuario |
| Grafo de contratación | Vínculos proveedor–beneficiario–contrato–pago | Señales para revisión; resolver homónimos y derecho a corregir |
| Verificación de obra | Evidencia de interventoría, mediciones y contraste independiente | Fotos, sensores y geolocalización también pueden ser manipulados |
| Conciliación de pagos | Cruce factura, recepción, obligación y confirmación bancaria | El registro no mueve ni certifica dinero por sí solo |
| Observatorio público | Versiones publicables, indicadores y comprobantes verificables | Reservas y redacción antes de publicar |
| Canal de alertas | Gestión segregada de denuncias y protección de acceso | Identidades de denunciantes fuera de cadena, incluso sus hashes |
| Privacidad verificable | Evaluar credenciales verificables y pruebas de conocimiento cero | Investigación R1; costes y modelo de amenaza por demostrar |

## Flujo del piloto
Presupuesto aprobado → contrato versionado → hito registrado → evidencia presentada → interventoría valida → ordenador autoriza → tesorería ejecuta → conciliación confirma → cierre. Cada paso produce evento inmutable lógicamente; una corrección agrega un evento y conserva historia. Proponente, verificador y autorizador deben ser personas distintas; rol y organización se validan desde identidad, nunca desde texto aportado por el cliente.

## Carpetas y entregables
- `architecture/`: topologías y decisiones comparativas.
- `docs/`: modelo de amenazas, piloto y validación.
- `examples/`: demostración con datos sintéticos.
- `python/colombia_dev/`: prototipo criptográfico.
- `tests/`: pruebas de integridad y manipulación.

Desde la raíz: `PYTHONPATH=programs/05-public-integrity/python python programs/05-public-integrity/examples/integrity_demo.py`.
Pruebas: `python -m pytest programs/05-public-integrity/tests -q`.

## Alcance real
Implementado: hash encadenado, raíz Merkle y verificación contra checkpoint externo.
Pendiente: firmas, PKI/HSM, persistencia WORM, prueba de inclusión, consenso, smart contracts, API, intranet, motor de tokens, integración bancaria y fuentes institucionales.
No es una blockchain, no autoriza pagos y no está listo para producción.
