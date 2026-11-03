# Fuentes originales del profesor (no versionar bases)

`source_manifest.json` y `teacher_source_manifest.json` registran seis archivos reales, tamaño, CRC32 y SHA256, así como los ZIP exteriores y sus huellas. Los nombres multianuales se conservan: estos archivos NO son CSV anuales renombrados.

- `inei_enaho/`: originales `enaho01-2021-2025-100-panel.csv`, `enaho01-2021-2025-200-panel.csv`, `enaho01a-2021-2025-300-panel.csv`, `sumaria-2021-2025-panel.csv`.
- `minedu_escale/`: `Padron.dbf`, `Padlocal.dbf`.

Fuente: https://drive.google.com/drive/folders/1J2ExK_k8T9TAveZForau6i90lb8Ef7P2?usp=sharing

Descargue los dos ZIP exteriores INEI y MINEDU de esa carpeta. Google Drive puede requerir navegación, permisos o confirmación para archivos grandes. No se asume una URL directa inexistente ni se automatiza una sesión autenticada.

```bash
.venv/bin/python scripts/download_raw_data.py --source-dir /ruta/a/los/dos/ZIP
```

El script verifica formato ZIP, CRC de extracción y SHA256; rechaza sobrescribir un original diferente. Permite `--inei-url` y `--minedu-url` para URLs HTTPS directas proporcionadas por el usuario; rechaza HTML/login en lugar de ZIP. No se descargó de nuevo nada durante esta ejecución porque los ZIP ya estaban disponibles.

La opción `--reuse-dir /ruta/data/raw` reutiliza archivos extraídos idénticos mediante enlaces físicos después de comprobar tamaño y CRC. Se usó aquí para evitar duplicar varios GB. Un enlace físico es el mismo contenido en disco: nunca edite los originales in situ. Si no hay copias válidas, se extraen desde el ZIP. La opción de reutilización es local y no es necesaria en otro equipo.

El loader selecciona exclusivamente las columnas `_25` y registros del año2025. No exige continuidad longitudinal. UTF8 con BOM, separador coma, decimal punto; llaves y año como texto. No se confunde el módulo Salud con Sumaria.

Los originales se ignoran en Git y en el empaquetado. Sólo README, manifiestos y marcadores de carpetas se pueden versionar. El manifiesto histórico de la ejecución ANUAL anterior se conservó aparte para no atribuir sus resultados a otra fuente retrospectivamente.
