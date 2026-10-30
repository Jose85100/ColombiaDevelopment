# Catálogo de datos topográficos y geotécnicos — 2026-10-24

**Área piloto:** Villavicencio–Puerto López–Puerto Gaitán. **Extensión futura separada:** cruces de la cordillera Oriental. No hay DEM descargado ni corredor optimizado todavía.

| Fuente | Información | Uso | Restricción |
|---|---|---|---|
| Copernicus DEM GLO-30 | Modelo digital de superficie ~30 m | Altitud, pendiente, corredores preliminares | DSM incluye vegetación/edificios; no sirve para diseño de detalle |
| NASA SRTMGL1 v3 | Elevación ~1 segundo de arco | Contraste independiente del DEM | Cobertura, vacíos, resolución y error vertical |
| IGAC Colombia en Mapas / datos abiertos | Cartografía base, catastro, red geodésica | Nodos, límites, servidumbres exploratorias | Verificar licencias y precisión de cada capa |
| SGC Geoportal | Geología, neotectónica, movimientos en masa | Amenaza de laderas y túneles | Mapas regionales no reemplazan sondeos |
| SGC amenaza sísmica | Espectros/curvas de amenaza regional | Screening sísmico | No reemplaza diseño ni efectos locales |
| IDEAM | Inundación, hidrología y clima | Puentes, drenaje y resiliencia | Verificar escala, periodo de retorno y actualidad |

## Fuentes verificadas
- https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM
- https://registry.opendata.aws/copernicus-dem/
- https://www.earthdata.nasa.gov/
- https://www.igac.gov.co/datos-abiertos/datos-abiertos-geoespaciales
- https://www2.sgc.gov.co/sgc/mapas/paginas/geoportal.aspx
- https://geoportal.sgc.gov.co/arcgis/rest/services/Mapa_Nacional_Amenaza_Mov_Masa_100K/Mapa_Nacional_Amenaza_Movimientos_Masa_100K/FeatureServer
- https://amenazasismica.sgc.gov.co/
- https://www.ideam.gov.co/

## Pipeline propuesto
1. Definir AOI poligonal con buffer para alternativas; no limitarse a línea recta.
2. Descargar tiles DEM y registrar URL, fecha, licencia, SHA256, CRS y datum vertical.
3. Reproyectar a CRS métrico apropiado; no calcular pendiente en grados geográficos.
4. Comparar Copernicus vs SRTM y revisar nodata, vegetación y anomalías.
5. Derivar pendiente, curvatura, drenaje, cuencas, cruces de ríos y riesgos geológicos.
6. Generar alternativas de ruta y perfiles longitudinales con restricciones de tren de carga y pasajeros.
7. Evaluar viaductos/túneles/terraplenes, costos y amenazas mediante ingeniería conceptual.
8. Revisión independiente; escalar a LiDAR, batimetría, sondeos y topografía de precisión en factibilidad.

**Advertencia:** los modelos globales de 30 m son para cribado regional, no para radios de curva, cotas de riel, cimentaciones o trazados constructivos.
