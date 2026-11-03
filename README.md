# Inteligencia Artificial U2: ENAHO–ESCALE 2025

Proyecto existente `InteliogenciaArtificial`, Universidad Peruana Unión. Clasifica **no uso de internet en el mes anterior** en residentes habituales de6–17 años matriculados/asistentes a primaria o secundaria, sin CEBA declarada. No mide directamente competencias digitales ni efectos causales.

## Fuentes actuales y resultados históricos

Se recuperaron los dos ZIP del Drive docente y sus seis originales en `data/raw/`. Los CSV son ENAHO PANEL2021–2025: se conservan sus nombres y se selecciona sólo2025. Padrón/Padlocal son los DBF originales. Consulte `data/raw/README.md` y `source_manifest.json`. Los datos crudos no se incluyen en Git ni en el ZIP de entrega.

Los modelos, métricas, artículo y entregas anteriores se conservan y corresponden a la ejecución ANUAL2025 documentada en octubre. La recuperación del Drive no cambia retrospectivamente su procedencia. La reconstrucción docente se valida aparte en `reports/rebuild_teacher/`; no se mezclan ambas versiones.

## Entorno

Python3.12; se conservan las versiones ML existentes. Se añadieron nbformat, nbclient e ipykernel únicamente para ejecutar los cuatro notebooks. Dependencias directas fijadas en `requirements.txt`.

```bash
cd /ruta/al/proyecto/InteliogenciaArtificial
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Si `.venv` ya existe y tiene las dependencias, no es necesario recrearlo. Los archivos `.joblib` se cargan solo si son los generados por este proyecto; pueden regenerarse desde las fuentes.

## Recuperar originales y reproducir en macOS

```bash
git clone https://github.com/DanMayhuire/brecha-digital-peru-2025.git
cd InteliogenciaArtificial
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/download_raw_data.py --source-dir /ruta/a/los/ZIP/del/profesor
.venv/bin/python scripts/reproduce_teacher.py
```

El repositorio indicado por el usuario es público. Los originales y predicciones individuales nuevos se mantienen fuera del commit. La descarga manual del Drive está documentada; no hacen falta los ZIP anuales para esta ruta. Las rutas del pipeline son relativas al proyecto, y la ubicación externa de los ZIP se proporciona como argumento.

El último comando reconstruye sólo datos en una carpeta de validación. Para ejecutar también entrenamiento, SHAP, gráficos, informe y verificación sin alterar el trabajo anterior:

```bash
.venv/bin/python scripts/reproduce_teacher.py --train
```

La ejecución se realiza con copias del código en `reports/rebuild_teacher/` y originales compartidos mediante enlaces físicos, no duplicados. Los nuevos resultados se guardan allí, incluidos el PDF y `reports/final_verification.json`. No se reejecutan los notebooks en esta ruta: la verificación lo declara. No atribuya automáticamente las cifras nuevas al artículo histórico.

Para validar la equivalencia de entradas y la preservación de los artefactos anteriores:

```bash
.venv/bin/python scripts/validate_raw_rebuild.py
.venv/bin/python -m unittest discover -s tests -v
```

Se mantiene `src/build_data.py --source annual --source-dir ... --annual-dir ...` como compatibilidad explícita con los ZIP anuales originales; no es la ruta predeterminada actual. `--source teacher` es el valor predeterminado y utiliza los CSV/DBF ya organizados. El builder puede usarse directamente con `--raw-dir` y `--run-dir`. No elija el directorio principal como destino de una prueba si desea preservar los resultados existentes.

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

Consulte `reports/results.json` y `docs/VALIDACION_FINAL.md` para las cifras de la ejecución final. La documentación no se considera evidencia suficiente sin los archivos generados y sus verificaciones. El estado anterior completo se conserva en `snapshots/`, excluido del ZIP y de Git. La publicación posterior en GitHub fue autorizada por el usuario; consulte docs/GITHUB_PUBLICATION.md.

### Notebooks históricos

La ejecución anual anterior se conserva en los respaldos. Los notebooks visibles se ejecutaron nuevamente con la fuente del profesor y guardan sus resultados reales para exposición. Las métricas de esa ejecución se resumen en reports/public_summary.json; los modelos y el artículo históricos anteriores permanecen aparte. El builder rechaza mezclar argumentos de fuente anual con teacher.

## Qué contiene GitHub y cómo reproducir

La versión de Git contiene código, pruebas, cuatro notebooks con salidas reales guardadas, documentación, tablas agregadas y el informe. Los notebooks ejecutados se conservan con sus salidas para que las tablas y gráficos aparezcan al abrirlos. Los respaldos permanecen locales en snapshots. El registro histórico de ejecución no es un hash de la versión sin salidas: es evidencia local de aquella corrida.

Los datos crudos/procesados, modelos, predicciones por persona, logs, respaldos y entregas de Power BI no se suben. `reports/public_summary.json` resume la ejecución docente presentada en los notebooks, sin casos individuales. Los registros detallados de verificación y sus hashes permanecen locales; se regeneran al reproducir.

No se usan rutas con nombres de usuario. `Path(__file__)` resuelve el proyecto y `--source-dir` permite elegir la carpeta de los ZIP en cada computadora. Una ruta de entrada configurada por el usuario es necesaria para sus archivos locales, pero no se fija a la computadora del autor. Siga los comandos de recuperación y `scripts/reproduce_teacher.py --train` de este README.

Antes de un commit:

```bash
.venv/bin/python scripts/check_github_ready.py
```

Para usar Jupyter, registre el entorno de su propio clon y seleccione ese kernel:

```bash
.venv/bin/python -m ipykernel install --user --name ia-u2 --display-name "Python IA U2"
```

Los notebooks reconstruyen el proyecto abierto al ejecutarlos. Para conservar entregas existentes, trabaje en un clon nuevo o use la reproducción aislada recomendada. No se garantiza que un clon sin los originales pueda entrenar: el procedimiento de colocación y validación de los ZIP está documentado.

## Presentación en JupyterLab: abrir sin volver a ejecutar

La entrega para exposición conserva outputs y contadores de ejecución reales. No se borran para GitHub: portabilidad significa eliminar rutas personales, no borrar resultados. Las imágenes están embebidas en los ipynb, por lo que ver los resultados no requiere kernel activo, originales ni descompresión. Para recalcular sí se necesitan el entorno y los originales ya preparados.

Abra `notebooks/00_Proyecto_Completo_Ejecutado.ipynb` para el recorrido unificado, o los cuatro notebooks de fases. El unificado compila salidas de ejecuciones reales en kernels independientes, declaradas por fase; no inventa resultados ni contadores. La evidencia se conserva en reports/raw_management/presentation_execution.json. No ejecute scripts/make_notebooks.py antes de exponer: genera plantillas nuevas; debe ir seguido de la ejecución y guardado real.
