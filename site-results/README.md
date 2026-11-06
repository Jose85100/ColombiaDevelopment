# Resultados que muestra colombiarisk.com/proyectos

`build_results.py` ejecuta el código de los programas con sus parámetros sintéticos, calcula los resultados y genera las páginas de cada propuesta (`/proyectos/<propuesta>/`) y las cifras de las tarjetas de `/proyectos/`. Las figuras son SVG propios (`charts.py`) que usan las variables de tema del sitio (`resultados.css`), sin librerías ni estilos en línea.

```sh
python3 site-results/build_results.py <carpeta sitio-principal del sitio>
```

Sin argumento solo calcula y deja `out/resultados.json`. Cada página indica el commit de `programs/` con el que se calculó y la semilla (2026), así que los números se pueden repetir.

**Todo es un ejercicio con parámetros sintéticos.** Ninguna cifra es una proyección real de un proyecto. El texto de cada página declara además lo que sus resultados no dicen.

Los números del texto salen del cálculo, no están escritos a mano. Si cambian los parámetros o el código de un programa, se vuelve a correr el script y las páginas se actualizan.
