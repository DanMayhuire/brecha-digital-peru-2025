# Fuentes y reconciliación ENAHO2025 / ESCALE

Decisión previa al nuevo entrenamiento: **ENAHO anual2025 es la única fuente canónica del pipeline**. Los cuatro ZIP anuales estaban disponibles localmente; no se sustituyeron fuentes por la palabra «panel». El corte `_25` del material docente se leyó exclusivamente para comprobar llaves, cobertura y equivalencia de valores. No se completaron respuestas anuales utilizando otros años o valores de la base panel.

## Inspección y equivalencia comprobada

| Tabla | Archivo anual dentro del ZIP | Filas anual | Filas corte panel2025 | Llaves coincidentes | Filas solo panel | Columnas originales anual / multianual |
|---|---|---:|---:|---:|---:|---:|
| Hogar | 1031-Modulo01/Enaho01-2025-100.csv | 44,599 | 44,599 | 44,599 | 0 | 336 / 1,689 |
| Personas | 1031-Modulo02/Enaho01-2025-200.csv | 115,145 | 115,145 | 115,145 | 0 | 40 / 254 |
| Educación | 1031-Modulo03/Enaho01A-2025-300.csv | 104,446 | 106,958 | 104,446 | 2,512 | 495 / 2,613 |
| Sumaria | 1031-Modulo34/Sumaria-2025.csv | 33,702 | 33,702 | 33,702 | 0 | 161 / 868 |

Las 2,512 personas adicionales de educación panel no tienen respuesta observada en ninguna de las preguntas educativas/TIC seleccionadas. No se sumaron como observaciones educativas útiles. La cohorte final anual mantiene 23,345 residentes6–17, con cobertura100% de los cruces ENAHO necesarios. No se deduce equivalencia de todas las columnas: la comparación exhaustiva es de **todas las variables analíticas seleccionadas y compartidas**, con sus factores de expansión. Hay cinco campos adicionales de nacimiento/edad del panel que no están en el archivo200 anual seleccionado y no se usan para construir etiquetas.

Después de normalizar separadores decimales y códigos de missing documentados por variable, no quedan diferencias en los valores compartidos seleccionados dentro de tolerancia numérica relativa1e-10 / absoluta1e-8. El resultado reproducible por módulo y variable está en `reports/tables/source_comparison.json`. Esa equivalencia no autoriza a afirmar representatividad nacional de una cohorte filtrada ni causalidad.

## Formato real y reglas

- Anuales: `latin1`, separador `;`, coma decimal. Leer con ajustes del panel convertiría factores e importes a NA por error.
- Panel: UTF8 con BOM, separador coma, punto decimal y columnas `_25`. La ficha declara panel y no panel de cada año; no se exige continuidad longitudinal.
- Las llaves AÑO, CONGLOME, VIVIENDA, HOGAR, CODPERSO y UBIGEO se conservan como texto. Se fijan anchos de códigos sin convertirlos primero a número. Todas las tablas están restringidas a2025 antes de cruzarse; por ello el año es constante y se conserva una vez en la tabla integrada.
- Missing se trata por variable según diccionario. Por ejemplo P300A=99 y P308B=9 son falta de información; **el código9 no se elimina globalmente**, pues puede ser una categoría válida en otros campos. Espacios en blanco, saltos y no respuesta se distinguen de respuesta negativa.
- Sumaria usa el archivo exacto `Sumaria-2025.csv`, no la variante `-12g`. El módulo04 es Salud y no reemplaza al34.
- Los hashes de cada archivo, su papel (entrada/comparación) y sus ubicaciones se guardan en `data/raw/source_manifest.json`. Los originales no se copian ni modifican.

## ESCALE: servicio, institución y local

`Padron.dbf` contiene112,724 registros; se seleccionan54,038 servicios activos de primaria/secundaria (NIV_MOD B0/F0). La llave de servicio COD_MOD+ANEXO es única. CODINST identifica institución; CODLOCAL identifica local físico. Los totales de estudiantes, docentes y secciones se suman una vez por servicio; no equivalen a personas docentes únicas en todas las instituciones.

`Padlocal.dbf` contiene69,642 locales, con CODLOCAL único. Se cruzó realmente con Padrón mediante `many_to_one`:54,038/54,038 servicios emparejados (100%), sin multiplicación. Hay **un conflicto de distrito** y ningún conflicto de área urbana/rural entre ambos archivos. Ese servicio conserva sus totales y distrito del Padrón, pero su local no participa en el contexto físico derivado de un cruce inconsistente. Tras validar, se cuentan43,631 locales distintos en los servicios elegibles. La evidencia de cardinalidad y cobertura está en `reports/tables/escale_join_coverage.csv` y `data_audit.json`.

El esquema real de Padlocal incluye CODGEO, AREA_LOC, ESTADO, GES_LOC, CLOC_L1 y TIP_ENVIO; **no contiene altitud, coordenadas ni indicadores de computadoras, agua, electricidad o internet escolar**. CLOC_L1 y TIP_ENVIO no se transforman en equipamiento ficticio. Las coordenadas provienen de Padrón, se validan y se agregan una vez por local físico, sin dar más peso a un local por albergar varios servicios. El encabezado DBF usa un byte de año25, cuya interpretación estándar1925 es inconsistente con FECHA_ACT=29-10-2025: no se usa ese metadato para fijar el año analítico.

Se agrega por distrito+área: suma de TALUM/suma de TDOC, proporción de servicios públicos, conteos de servicios/instituciones/locales y coordenadas medias de locales validados. La fracción de locales compartidos describe organización de servicios, no calidad de infraestructura. ENAHO usa estratos1–5 urbanos y6–8 rurales; ESCALE confirma etiquetas AREA_CENSO1=Urbana y2=Rural, y Padlocal AREA_LOC coincide en54,038 servicios. Esta es compatibilidad de categorías, sin afirmar identidad de cada centro poblado entre marcos.

La tabla contextual tiene2,439 combinaciones distrito-área. Empareja22,920/23,345 residentes (98.179%);425 permanecen sin contexto. El modelo imputa dentro de folds, conserva la bandera de cobertura y no asigna a cada estudiante una escuela identificada. Residencia y escuela pueden estar en distritos distintos.

## EDA raw y privacidad

`source_audit.py` produce perfiles de las columnas seleccionadas **antes de unir, filtrar población escolar, transformar logaritmos o imputar**: filas, vacíos, formatos decimales, fallos de parseo, distribución de códigos, cuantiles y banderas IQR para campos numéricos pertinentes. Las banderas no eliminan observaciones. `raw_eda_variables.csv` conserva los resultados; `raw_eda.png/pdf` muestra distribuciones de módulos completos. El gasto solo se recorta P1-P99 para legibilidad del histograma, sin borrar filas de datos.

El mapa `escale_context_map.png/pdf` dibuja únicamente centroides contextuales de distrito-área. No hay puntos de hogares ni predicciones individuales. Las coordenadas de hogares no se cargan ni se exportan. Las llaves anonimizadas de microdatos quedan para verificar uniones y agrupaciones; no son nombres ni contactos. Los ZIP originales y las predicciones por fila no se incluyen automáticamente en el paquete docente.
