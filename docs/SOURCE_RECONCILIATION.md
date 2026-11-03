# Fuentes e integración de ENAHO y ESCALE 2025

## Fuentes

ENAHO aporta vivienda (módulo 100), población (200), educación (300) y Sumaria. ESCALE aporta el Padrón de Servicios Educativos y el Padrón de Locales Escolares. Las referencias metodológicas están en `sources.json`; los enlaces descargables y hashes de los seis originales del material del curso están en `data/raw/download_manifest.json`.

Los modelos incluidos utilizan el dataset procesado de ENAHO anual 2025 y su orden fijado por SHA-256. La lectura de los originales multianuales selecciona exclusivamente columnas y registros de 2025, sin exigir continuidad longitudinal.

El contraste por CONGLOME, VIVIENDA, HOGAR y CODPERSO identifica las mismas 23 345 personas y valores en las 112 columnas comunes seleccionadas. El panel aporta cinco campos adicionales no predictivos y otra secuencia de filas. La igualdad por llaves no implica identidad byte a byte ni invariancia del ajuste aleatorio al orden. `SCIENTIFIC_REFERENCE.json` especifica los artefactos utilizados para reproducir los modelos.

## Formatos y uniones

Los archivos anuales se leen en Latin-1, con punto y coma como separador y coma decimal. Los CSV del panel utilizan UTF-8 con BOM y separador coma. Se conservan los ceros iniciales de identificadores y se normalizan los códigos ausentes por variable.

- Módulos 200 y 300: CONGLOME, VIVIENDA, HOGAR y CODPERSO.
- Módulos 100 y Sumaria: CONGLOME, VIVIENDA y HOGAR.
- Padrón y Padlocal: CODLOCAL; agregación educativa por UBIGEO y área.

Se comprueban unicidad de claves, cardinalidad, cobertura y ausencia de multiplicación de personas. El filtro de edad y residencia produce 23 345 personas; la aplicación de reglas escolares y respuesta válida produce 16 544 estudiantes.

## Contexto educativo y pesos

Se consideran servicios activos de primaria y secundaria. La razón alumnos/docente se calcula como SUM(TALUM)/SUM(TDOC). Las coordenadas proceden del Padrón y se cuentan una vez por local geográficamente validado. Padlocal valida correspondencia territorial; un conflicto geográfico se excluye de esa validación. ESCALE describe contexto del distrito y área de residencia, no la escuela individual del encuestado.

FACPOB07 es el factor de población de personas. FACTORA07 es un factor del módulo educativo y FACTOR07 de Sumaria corresponde al hogar. Los factores longitudinales FACPANEL no se utilizan para este corte transversal.

## Reproducción

`python scripts/download_raw_data.py` recupera y verifica los originales. `python scripts/reproduce_teacher.py` construye datos en `reports/teacher_run/`. La reproducción de los modelos incluidos usa `python scripts/reproduce_scientific.py --run-dir tmp/scientific_run --restore-evaluation-traces`, conservando el dataset procesado y su secuencia.
