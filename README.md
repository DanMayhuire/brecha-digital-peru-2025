# Inteligencia Artificial U2: ENAHO–ESCALE 2025

Proyecto existente `InteliogenciaArtificial`, Universidad Peruana Unión. Clasifica **no uso de internet en el mes anterior** en residentes habituales de6–17 años matriculados/asistentes a primaria o secundaria, sin CEBA declarada. No mide directamente competencias digitales ni efectos causales.

## Fuentes y privacidad

Los originales se conservan externamente, sin modificarlos. El pipeline compara el corte 2025 del panel del docente con la descarga anual y utiliza una única fuente canónica. La decisión exacta y las diferencias ejecutadas figuran en `docs/SOURCE_RECONCILIATION.md` y `reports/tables/source_comparison.json` cuando finaliza la reconstrucción. Los nombres de los ZIP, tamaños y hashes están en `data/raw/source_manifest.json`.

Requisitos locales:

- Carpeta de cuatro archivos anuales: `1031-Modulo01.zip`, `1031-Modulo02.zip`, `1031-Modulo03.zip`, `1031-Modulo34.zip`. El módulo04 es Salud; no sustituye a Sumaria34.
- Carpeta del docente: ZIP exterior `INEI-20261028T132135Z-1-001.zip` (contraste panel y documentación) y `MINEDU-20261028T132134Z-1-001.zip` (Padrón y Padlocal).
- Los ZIP no forman parte del paquete de entrega. Para reconstruir en otro equipo es necesario obtenerlos de las fuentes declaradas, colocarlos en dos carpetas y ajustar las variables de entorno que aparecen abajo.

Los datos procesados conservan claves técnicas de la publicación anonimizada de INEI para auditar las uniones; no se cargan nombres, DNI, direcciones ni contactos. No publique el paquete ni las predicciones de personas. El ZIP es una entrega privada al docente: excluye originales, entornos, cachés y predicciones por fila. ESCALE representa contexto territorial del distrito/área de residencia, no el colegio identificado de cada encuestado.

## Entorno

Python3.12; se conservan las versiones ML existentes. Se añadieron nbformat, nbclient e ipykernel únicamente para ejecutar los cuatro notebooks. Dependencias directas fijadas en `requirements.txt`.

```bash
cd /ruta/al/proyecto/InteliogenciaArtificial
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Si `.venv` ya existe y tiene las dependencias, no es necesario recrearlo. Los archivos `.joblib` se cargan solo si son los generados por este proyecto; pueden regenerarse desde las fuentes.

## Ejecución completa desde originales

En el Mac actual, las carpetas conocidas son Downloads/DocenteMaterial y Downloads. En otro equipo ajuste estos dos valores:

```bash
export IA_SOURCE_DIR="$HOME/Downloads/DocenteMaterial"
export IA_ANNUAL_DIR="$HOME/Downloads"
.venv/bin/python src/build_data.py --source-dir "$IA_SOURCE_DIR" --annual-dir "$IA_ANNUAL_DIR"
.venv/bin/python src/run_analysis.py --target internet
.venv/bin/python src/update_model_dictionary.py
.venv/bin/python src/make_report.py
.venv/bin/python src/verify_outputs.py
.venv/bin/python src/finalize_docs.py
.venv/bin/python src/package_submission.py
```

La verificación exige evidencia de los cuatro notebooks. Para obtener toda esa evidencia y ejecutar el pipeline mediante los notebooks, utilice la ruta siguiente en lugar de repetir builder y análisis:

```bash
.venv/bin/python src/execute_notebooks.py
.venv/bin/python src/update_model_dictionary.py
.venv/bin/python src/make_report.py
.venv/bin/python src/verify_outputs.py
.venv/bin/python src/finalize_docs.py
.venv/bin/python src/package_submission.py
```

No es necesario ejecutar ambas rutas de entrenamiento. El runner abre un kernel limpio por notebook y registra tiempos, celdas ejecutadas, estado y hashes en `reports/notebook_execution.json`. Los notebooks llaman a los scripts canónicos; no duplican las implementaciones ni simulan entrenamiento cargando métricas antiguas.

Para abrirlos en su Jupyter actual, seleccione el intérprete del proyecto. Se puede registrar este kernel para el Jupyter que ya tenga instalado:

```bash
.venv/bin/python -m ipykernel install --user --name ia-u2 --display-name "Python IA U2"
```

Abra los cuatro notebooks en orden y seleccione **Python IA U2**. Instalar JupyterLab completo no es necesario si ya dispone de él. El notebook histórico de revisión se conserva como trabajo previo; la entrega usa los cuatro recorridos nuevos.

## Fases y métodos

- `build_data.py`: auditoría de formatos originales, contraste anual/panel, EDA raw, integración persona/hogar/distrito, Padrón+Padlocal, cobertura y diccionarios. No imputa ni escala predictores.
- `run_analysis.py --phase prepare`: definición del objetivo, flujo de cohorte, separación por CONGLOME y EDA en desarrollo. Guarda CSV y Parquet sin imputar.
- `--phase clustering`: KMeans/GMM k 2–6; silueta en2500 casos como máximo, DB/CH sobre desarrollo completo; PCA; estabilidad ARI y ablación sin acceso.
- `--phase supervised`: cincoGroupKFold, cuatro familias, sensibilidad de cuatro estrategias de pesos y seis configuraciones por familia. Presupuesto200 ajustes; cuatro hilos. Selección por AP media ponderada de validación; calibración sigmoide de scoresOOF de desarrollo; umbral0.5.
- `--phase shap`: explica el ganador real y calcula interaccionesTreeSHAP de XGBoost como complemento identificado. Explica el score previo a calibración, no causalidad.

`--phase all` (por defecto) ejecuta las cuatro fases de análisis. El protocolo fijado antes del nuevo entrenamiento está en `docs/MODELING_PROTOCOL.md`; parámetros completos, tiempos y métricas están en las tablas. No hay tuning ilimitado ni cambio de ganador al mirar prueba.

## Entregables

- `output/pdf/Informe_U2_Brecha_Digital_2025.pdf`: artículo4–6p, fuente editable `reports/article.md`.
- `output/Entrega_U2_Brecha_Digital_2025.zip`: paquete con manifiesto y hashes comprobados.
- `data/processed/dataset_enaho_escale_2025.parquet` y CSV: integración auditada.
- `data/processed/dataset_modelado_2025.parquet` y `dataset_modelado_internet_2025.csv`: cohorte y variables antes de imputación.
- Cuatro notebooks académicos en `notebooks/`, código canónico en `src/` y pruebas en `tests/`.
- `docs/data_dictionary*.md`, `docs/TARGET_DECISION.md`, `docs/VARIABLE_VALIDATION.md` y `docs/DEFENSA_ORAL.md`.
- Auditoría inicial/final en `docs/AUDITORIA_RUBRICA.md`; plan y acciones en `docs/PLAN_MEJORAS.md`; comandos y resultados en `docs/VALIDACION_FINAL.md`.
- `reports/final_verification.json`: controles realmente ejecutados, versiones, fuentes, métricas y advertencias. `reports/package_verification.json`: integridad y comprobaciones del ZIP.

## Límites científicos

P314A mide uso reciente. ENAHO sí incluye actividades informáticas autorreportadas en14+, condicionadas por uso de dispositivos, pero no permite convertir pases o ausencia de respuesta en falta de competencias para toda la población 6–17. La operacionalización digital es más estrecha que la redacción amplia de la guía.

La prueba se observó en la versión previa. La nueva búsqueda utiliza solo desarrollo, pero esta revisión retrospectiva no aporta una prueba externa inédita. La separación por conglomerado no demuestra generalización a distritos o regiones nuevos. El diseño transversal impide hablar de predicción temporal o causalidad.

FACPOB07 es el factor individual principal; FACTORA07 se considera en sensibilidad. FACTOR07 del hogar no se acumula como peso individual. La ponderación de esta cohorte y el bootstrap por conglomerado no reproducen toda la estratificación de ENAHO ni constituyen tasas oficiales nacionales. La calibración y el recall deben validarse antes de cualquier uso operativo.

## Estado y resultados

Consulte `reports/results.json` y `docs/VALIDACION_FINAL.md` para las cifras de la ejecución final. La documentación no se considera evidencia suficiente sin los archivos generados y sus verificaciones. El estado anterior completo se conserva en `snapshots/`, excluido del ZIP y de Git. No se hicieron commits, push ni publicaciones remotas.
