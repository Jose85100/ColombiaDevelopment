# Figuras isométricas de /proyectos

Ilustraciones hechas con el kit de [Anatomy](https://github.com/wheresryan22/anatomy) (MIT; `kit/` es una copia de `kit/iso-kit.mjs`).
Cada figura es un módulo que lee `../out/resultados.json` y escribe `out/<slug>.fragment.svg`; `../build_results.py` la inserta en la página.

    node integridad.mjs; node agro.mjs; node fraude.mjs; node territorial.mjs; node judicial.mjs; node build_css.mjs
    python3 ../build_results.py <sitio-principal>

- Sin estilos en línea ni scripts: encajan con la política de contenido del sitio. Los colores salen de `out/anatomia.css`, que sigue el tema claro/oscuro del sitio.
- Son ilustraciones, no gráficos de datos: cada una lo dice en su nota y trae la tabla con los valores.
- Las vistas previas (`out/*-preview-*.html`) sirven para revisar una figura sola; no se publican.
