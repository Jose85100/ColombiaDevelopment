# Modelo financiero privado: supuestos sintéticos y lectura de riesgos

**Unidad monetaria:** millones de COP constantes. No son precios, salarios, rendimientos ni costos observados en Colombia. Simulación reproducible: `python/colombia_dev/agro_finance.py` y notebook 09.

## Escenario demostrativo (NO presupuesto de inversión)
- 200 ha, rendimiento 6 t/ha, merma 8%, precio 2.4 millones COP/t.
- CAPEX inicial 4.500 millones COP; capital de trabajo 350 millones COP.
- Costos de campo 3.5 millones COP/ha/año; variable industrial 0.85 millones COP/t comercializada.
- Costos fijos 600 millones COP/año; mantenimiento 120 millones COP/año.
- Dos cuadrillas de 16 personas: 32 puestos presupuestados; costo anual cargado por persona 52 millones COP + 12 millones COP transporte/alojamiento.
- Tasa de descuento 16%, horizonte 12 años, crecimiento nominal/real ilustrativo 2% (interpretar como real en moneda constante), tasa tributaria simplificada 35% sobre EBITDA positivo solo como aproximación matemática.
- Uso hídrico supuesto 150 m3/t cosechada y techo 200.000 m3/año; **no son coeficientes agronómicos calibrados**.

## Riesgos de modelo
La simulación no incorpora depreciación, impuesto de renta real, inflación, deuda, DSCR, inventarios estacionales, IVA, seguridad social detallada, recargos legales, primas por certificación, beneficios ambientales, valor residual de activos, diferencias entre cultivo y transformación ni aportes de productores. No usarla para decisiones de inversión sin completar estos componentes.

## Escenarios de estrés a modelar
Precio -20%, rendimiento -25%, CAPEX +35%, costo laboral/logístico +25%, WACC +400 puntos básicos, merma +10 puntos porcentuales, sequía y bloqueo de transporte. Escenarios correlacionados deben modelarse conjuntamente y considerar continuidad de caja.

## Regla de reparto
La remuneración por trabajo y la compra de cosecha se pagan antes de distribuciones patrimoniales. La participación campesina debe estar representada en un cap table, y las regalías contractuales no pueden comprometer la solvencia ni ocultar obligaciones laborales. El inversionista tiene derecho al retorno contratado o residual según instrumento, **no a una rentabilidad garantizada por el proyecto**.
