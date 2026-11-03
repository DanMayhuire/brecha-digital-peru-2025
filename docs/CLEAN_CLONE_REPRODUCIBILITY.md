# Reproducibilidad desde un clon limpio

Auditoría: 2026-11-03 (America/Lima). Remoto inspeccionado: `DanMayhuire/brecha-digital-peru-2025`, commit `87d8fb907e8ecdb94b0b94a3508641d7bb9183d7`.

## Resultado y alcance

**El mecanismo corregido se probó satisfactoriamente en un clon limpio antes de autorizar su publicación.** Los hallazgos sobre el remoto que siguen corresponden al commit inspeccionado, identificado arriba; el commit de publicación incorpora las correcciones documentadas.

El remoto actual no contiene ninguno de los seis originales. Su README tiene un nombre de carpeta incorrecto tras el clon y su descargador exige ZIP locales o URLs que no proporciona. Sus manifiestos incluyen rutas relativas, hashes y el enlace a una carpeta pública del Drive, pero no seis enlaces de descarga directa. No son únicamente rutas del Mac, aunque resultan insuficientes para una descarga automática reproducible.

## Evidencia de la prueba

1. Se clonó GitHub por HTTPS en un directorio temporal nuevo con `--no-local --no-hardlinks`; no se copió `.git` del proyecto original.
2. Se aplicaron únicamente los cambios propuestos de código y el manifiesto de URLs/hashes. No se trasladaron datos del Mac.
3. Se creó un entorno Python3.12 nuevo y se instalaron requirements con `pip --no-cache-dir`; `pip check` aprobó sus dependencias.
4. Se retiraron del clon los procesados y modelos que ya estaban versionados, así como los principales registros de resultados, antes de reconstruir. Las carpetas de la ejecución aislada empezaron vacías.
5. Se descargaron anónimamente los seis ZIP desde las URLs públicas identificadas en el Drive. Todos los originales se extrajeron de esas descargas nuevas y coincidieron con los tamaños y SHA-256 fijados. Cada original tuvo un solo enlace físico.
6. La reproducción utilizó copias independientes de esos originales: inodos distintos y un solo enlace físico por archivo. No se utilizó `--reuse-dir` ni `--link-raw`.
7. Se ejecutaron construcción de datos, modelos, SHAP, auditoría de medición, diccionario, PDF y verificación. Resultado: 23,345 residentes, 16,544 estudiantes modelados, cero intersección de conglomerados; **147 controles aprobados y cero fallidos**.
8. Se ejecutaron **17 pruebas unitarias**, incluidas tres nuevas de confirmación de descarga, rechazo de originales diferentes y rechazo de SHA-256 incorrecto. Los notebooks no se reejecutaron en esta prueba; se ejecutaron los scripts y la verificación lo declara.
9. La comparación de hashes confirmó que los artefactos científicos del proyecto original permanecieron sin cambios. No se hizo commit ni push.

Resumen verificable: `CLEAN_CLONE_VERIFICATION.json`. Inventario exacto del remoto inspeccionado: `REMOTE_FILE_INVENTORY.txt`. Los logs detallados de la prueba permanecen locales en la carpeta temporal y en `reports/raw_management/`.

## Fuentes exactas de los seis originales

Los enlaces persistentes de archivo, las URLs de descarga y los SHA-256 completos están en `data/raw/download_manifest.json`. Se descargan los ZIP interiores necesarios, no se intenta reproducir un ZIP exterior con nombre/timestamp generado por Google Drive.

|Original|ZIP público del profesor|
|---|---|
|enaho01-2021-2025-100-panel.csv|[1041-Modulo1474.zip](https://drive.google.com/file/d/1VyH-kHKHdugOfb2SOSrKC9If2P6eJZLT/view)|
|enaho01-2021-2025-200-panel.csv|[1041-Modulo1479.zip](https://drive.google.com/file/d/1Wcl24s3wJQRkZh3BSejHxeYWurtkOu7V/view)|
|enaho01a-2021-2025-300-panel.csv|[1041-Modulo1475.zip](https://drive.google.com/file/d/1v99MYB7mQhvPeRAN99dnqSqMnH5VduxU/view)|
|sumaria-2021-2025-panel.csv|[1041-Modulo1478.zip](https://drive.google.com/file/d/1bZk-o8isVoJ9erZok4mI2WMhgix6SC-1/view)|
|Padron.dbf|[00_Padron.zip](https://drive.google.com/file/d/1cDjrSbG10dwnAid7u79Rfp01tQ_8kVXj/view)|
|Padlocal.dbf|[00_Padlocal.zip](https://drive.google.com/file/d/1T6GtuyNHV9iCtMTKAnKgO-1TStDYqe-S/view)|

## Comandos de reproducción de la versión corregida

Requisitos: Git y Python3.12 instalados; acceso a Internet y espacio libre para originales, copias de trabajo y entorno virtual (conviene disponer de al menos12GB).

```bash
git clone https://github.com/DanMayhuire/brecha-digital-peru-2025.git
cd brecha-digital-peru-2025
python3.12 -m venv .venv
.venv/bin/python -m pip --no-cache-dir install -r requirements.txt
.venv/bin/python scripts/download_raw_data.py
.venv/bin/python scripts/reproduce_teacher.py --train
```

No hay descarga manual ni autenticación en la ruta pública que se probó. Si el propietario cambia permisos, Drive impone cuotas o falla la red, se necesita intervención: abrir los enlaces de archivo, solicitar acceso si corresponde y colocar los originales indicados en `data/raw/`. Al repetir el descargador se validan sus hashes sin suponer que un faltante sea un dato válido. No se garantiza la disponibilidad futura de un servicio externo.

## Contenido real de GitHub

El commit inspeccionado contiene127archivos. Bajo `data/raw/` hay dos manifiestos, un README y dos marcadores `.gitkeep`: **no contiene los seis CSV/DBF**. Los seis están excluidos por `.gitignore`.

Sí existen ocho archivos procesados y cuatro de modelos que fueron versionados anteriormente; `.gitignore` no los retira del historial. También están código, pruebas, documentación, cinco notebooks con salidas, informe, gráficos y tablas/registros de resultados. La lista exacta es el inventario adjunto. Esta auditoría no borra ni vuelve a publicar esos archivos.

## Cambios propuestos

- `src/public_data_download.py`: descarga pública, confirmación de archivos grandes y verificación SHA-256 antes de aceptar los originales.
- `data/raw/download_manifest.json`: seis URLs reales y seis versiones fijadas por hash.
- `scripts/download_raw_data.py`: descarga pública predeterminada; conserva la opción de ZIP exteriores manuales y ahora exige los hashes fijados.
- `scripts/reproduce_teacher.py`: copia por defecto; enlaces físicos sólo por opción explícita.
- `tests/test_public_download.py`: regresiones de integridad y recuperación.
- README y documentación de raw: comandos corregidos, inventario real de Git y alternativa manual.
- Manifiestos locales: referencias a las fuentes públicas y al bloqueo de descarga; no se modificaron originales ni resultados científicos.
