# Medidor de pendiente (ilustración conceptual)

Figura isométrica interactiva del programa 01. Ilustra el cribado de pendientes que hace `profile_metrics` en `python/colombia_dev/topography.py`.

**Es una ilustración conceptual. No es un corredor real, no usa datos reales y no es un diseño de ingeniería.**

## Qué muestra
Un medidor de pendiente sobre una placa. Los tres bloques son los tramos de un perfil **sintético**; la altura de cada bloque es la pendiente de su tramo y la aguja de la esfera la lee. Una marca en la esfera señala el límite de cribado de 1,5 %.

| Tramo | Puntos del perfil sintético (distancia m, cota m) | Pendiente |
|---|---|---|
| 1 | (0, 100) a (1 000, 112) | 1,2 % |
| 2 | (1 000, 112) a (2 000, 130) | 1,8 % |
| 3 | (2 000, 130) a (3 000, 139) | 0,9 % |

El límite de 1,5 % es el valor por defecto de `max_grade` (0,015). Con estos puntos, `profile_metrics` devuelve pendientes de 1,2 %, 1,8 % y 0,9 % y marca solo el segundo tramo (`segments_above_limit == [2]`). Los modelos globales de 30 m son para cribado regional; ver `docs/RAIL_TOPOGRAPHY_DATA_CATALOG.md`.

## Cómo se reconstruye
Requiere Node 20.10 o posterior. No tiene dependencias que instalar.

```sh
node build.mjs           # medidor-pendiente.html (tema oscuro)
node build.mjs --light   # medidor-pendiente-light.html
```

`exportar_sitio.py <carpeta del sitio>` convierte la página en un CSS y un JS externos y en un fragmento de marcado, sin código en línea, para sitios con una política de seguridad de contenido estricta.

## Créditos y licencia
Hecha con la skill **Anatomy** de wheresryan22 (https://github.com/wheresryan22/anatomy, licencia MIT), fijada al commit `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`. Su kit está incluido en `vendor/anatomy/` junto con su licencia. `build.mjs` es una adaptación del ejemplo `dial-indicator` de esa skill. La figura no se publicó en la galería de la skill.
