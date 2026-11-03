# Gestión de originales y validación de recuperación

Fecha de revisión: 2026-11-03 (America/Lima). Petición vigente: utilizar los dos ZIP del profesor; GitHub se pospone.

## Fuente y organización

Se recuperaron cuatro CSV originales PANEL2021–2025 y dos DBF ESCALE desde los ZIP INEI/MINEDU del Drive docente. Se conservan los nombres reales, no se presentan archivos multianuales como publicaciones anuales. `data/raw/inei_enaho/` y `data/raw/minedu_escale/` contienen los archivos; los manifiestos registran miembros ZIP, tamaños, CRC32 y SHA256. Las rutas de datos son relativas al proyecto.

Las copias descomprimidas existentes coincidieron en tamaño y CRC con los miembros ZIP. Se reutilizaron mediante enlaces físicos y se calcularon sus SHA256; no se duplicaron varios GB ni se editaron originales. Se necesitan archivos en el mismo volumen para reutilizar con `--reuse-dir`; sin esa opción se extraen directamente desde los ZIP.

## Archivos creados/modificados y motivo

|Archivo|Cambio|
|---|---|
|scripts/download_raw_data.py|Recuperación idempotente desde los ZIP; extracción verificable; descarga HTTPS sólo mediante URL directa explícita; rechazo de HTML/login y de sobrescritura de originales distintos.|
|src/teacher_inputs.py|Lectura de CSV multianuales, sólo2025, llaves y año texto, códigos faltantes por variable; adaptación a DBF locales.|
|src/build_data.py|Modo teacher predeterminado, raw-dir relativo, run-dir aislado; modo annual anterior explícito conservado.|
|scripts/reproduce_teacher.py|Reconstrucción segura; opción train para repetir ML/SHAP/informe/verificación en carpeta aislada.|
|scripts/validate_raw_rebuild.py|Equivalencia por claves persona, grupos de prueba, hashes originales y conservación de artefactos previos.|
|src/verify_outputs.py|Verificación de hashes de los originales extraídos; opción skip-notebooks que declara que no se ejecutaron.|
|src/make_report.py y update_model_dictionary.py|Describir correctamente fuente teacher o annual al regenerar, sin alterar el informe histórico.|
|src/package_submission.py|Incluir scripts y excluir todos los CSV/DBF crudos del paquete; sólo metadatos de raw.|
|.gitignore|Datos originales ignorados; README/manifiestos versionables; temporales, entornos y reconstrucción aislada excluidos.|
|tests/test_data.py y test_raw_recovery.py|Pruebas compatibles con ambas fuentes y regresiones de extracción/no sobrescritura/corte2025.|
|README y data/raw/README|Procedimiento macOS, colocación manual, descarga, ejecución y límites.|

## Validaciones ejecutadas

- Recuperación: seis archivos verificados por SHA256 y CRC; originales existentes reutilizados sin modificación.
- Reconstrucción desde teacher: 23,345 residentes, 16,544 elegibles, 4,294 positivos. Coincidencia por claves y valores comunes con la base histórica; cinco campos adicionales de nacimiento vacíos no son predictores.
- Uniones ENAHO y ESCALE: sin multiplicación; ceros de llaves conservados; mismos conglomerados de prueba con semilla42.
- 14 pruebas unittest del proyecto aprobadas. Incluyen rechazar sobrescritura, corte temporal, cardinalidades, fuga, imputación y pesos.
- Ejecución completa de scripts en `reports/rebuild_teacher/`: construcción, entrenamiento, SHAP, auditoría de medición, diccionario, informe y verificación. 147 controles aprobados, cero fallidos. No se reejecutaron notebooks en esta validación; la advertencia queda registrada.
- Artefactos históricos protegidos mediante inventario SHA256: modelos, datos procesados, gráficos, métricas, artículo y entregas sin cambios.

Evidencia: `reports/raw_management/validation.json`, `tests.log`, `reproduction.log`, y `reports/rebuild_teacher/reports/final_verification.json`. Los resultados nuevos no sustituyen a los históricos.

## Descargas y limitaciones

Fuente requerida: Drive del docente, enlazado en data/raw/README. Se usaron archivos locales, no descargas nuevas. Se comprobaron los portales oficiales https://proyectos.inei.gob.pe/microdatos/ y https://escale.minedu.gob.pe/; el primero presenta el sistema de microdatos y el segundo devuelve verificación humana Check Point. No se inventaron URLs de descarga automática. Google Drive puede requerir permisos/navegación manual; el script explica cómo colocar los ZIP.

Las métricas históricas proceden de la fuente anual original; el manifiesto anterior se conserva en `reports/raw_management/historical_annual_source_manifest.json`. Cambiar la fuente de recuperación no cambia retrospectivamente esa procedencia. La nueva ejecución con teacher queda separada y documentada. No se modificó la etiqueta ni la metodología predictiva.

## Git

No se realizó commit ni push. Mensaje sugerido para una revisión posterior: `chore(data): improve ENAHO ESCALE raw data reproducibility`. La exclusión de los seis originales fue comprobada con git check-ignore; los README, manifiestos y scripts no están ignorados. No usar git add indiscriminadamente: el proyecto todavía contiene resultados locales que requieren su propia selección de publicación.

## Resultados nuevos separados

La ejecución docente conserva CatBoost como ganador por validación. En esta corrida: ROC-AUC ponderado 0.820282, AP 0.599633 y F1 macro 0.681567. No sustituyen las métricas históricas. La equivalencia de valores por clave no implica identidad numérica de reentrenamiento: el orden de filas de las publicaciones difiere y afecta submuestreo y algoritmos aleatorios, incluso con semilla fija. Se conservan las mismas reglas de población, predictores y separación por conglomerados. Las seis páginas del informe de prueba se renderizaron y revisaron.
