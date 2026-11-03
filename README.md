# Inteligencia Artificial U2: ENAHO–ESCALE 2025

Proyecto existente `InteliogenciaArtificial`, Universidad Peruana Unión. Clasifica **no uso de internet en el mes anterior** en residentes habituales de6–17 años matriculados/asistentes a primaria o secundaria, sin CEBA declarada. No mide directamente competencias digitales ni efectos causales.

## Versión científica definitiva

La referencia es el CatBoost guardado, sus predicciones y el dataset anual de 2025 con su orden original. Prueba ponderada: ROC-AUC 0.820357, AP 0.601272 y F1 macro 0.693294. GMM k=2: silueta 0.453928. Los cinco notebooks ejecutan controles reales de estos mismos artefactos; no afirman entrenar modelos cuando sólo los evalúan.

Los seis originales del profesor se recuperan automáticamente desde Drive, con SHA-256. Su corte 2025 tiene las mismas personas y valores comunes, pero distinto orden de filas y cinco columnas adicionales no predictoras. Una semilla fija no hace al ajuste ni al muestreo invariantes al orden. Por eso la reproducción docente es un experimento distinto, no una sustitución automática de las cifras definitivas. La investigación, la reproducción aislada y los hashes se documentan en `docs/SCIENTIFIC_SYNC.md` y `docs/SCIENTIFIC_REFERENCE.json`.

## Entorno

Python3.12; se conservan las versiones ML existentes. Se añadieron nbformat, nbclient e ipykernel únicamente para ejecutar los cuatro notebooks. Dependencias directas fijadas en `requirements.txt`.

```bash
cd brecha-digital-peru-2025
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Si `.venv` ya existe y tiene las dependencias, no es necesario recrearlo. Los archivos `.joblib` se cargan solo si son los generados por este proyecto; pueden regenerarse desde las fuentes.

## Recuperar originales y reproducir en macOS

```bash
git clone https://github.com/DanMayhuire/brecha-digital-peru-2025.git
cd brecha-digital-peru-2025
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/download_raw_data.py
.venv/bin/python scripts/reproduce_teacher.py
```

El descargador consulta los seis enlaces públicos del profesor registrados en `data/raw/download_manifest.json`, descarga únicamente los ZIP necesarios, extrae los originales y exige que sus tamaños y SHA-256 coincidan con esa versión. No necesita sesión de Google ni archivos previos. Si Drive exige inicio de sesión, limita la cuota o deja de compartir un archivo, el script se detiene con un error: consulte la alternativa manual en `data/raw/README.md`. No se sustituyen datos por una versión distinta.

El último comando reconstruye sólo datos en una carpeta de validación. Para ejecutar también entrenamiento, SHAP, gráficos, informe y verificación sin alterar el trabajo anterior:

```bash
.venv/bin/python scripts/reproduce_teacher.py --train
```

La ejecución se realiza con copias del código y de los originales en `reports/rebuild_teacher/`. Por defecto no se usan enlaces físicos. La opción `--link-raw` permite reutilización local voluntaria y no se utilizó en la prueba del clon limpio. Los nuevos resultados se guardan allí, incluidos el PDF y `reports/final_verification.json`. No se reejecutan los notebooks en esta ruta: la verificación lo declara. No atribuya automáticamente las cifras nuevas al artículo histórico.

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

### Notebooks sincronizados

Se conserva la ejecución anterior en un respaldo local con manifiesto SHA-256. Los notebooks actuales recalculan métricas, asignaciones y explicaciones de los modelos definitivos guardados. El recorrido 00 se ejecuta completo en su propio kernel; no concatena salidas de otras ejecuciones. El entrenamiento completo se reproduce por separado y se compara sin promover ni reemplazar modelos.

## Qué contiene GitHub y cómo reproducir

La versión de Git contiene código, pruebas, cuatro notebooks con salidas reales guardadas, documentación, tablas agregadas y el informe. Los notebooks ejecutados se conservan con sus salidas para que las tablas y gráficos aparezcan al abrirlos. Los respaldos permanecen locales en snapshots. El registro histórico de ejecución no es un hash de la versión sin salidas: es evidencia local de aquella corrida.

Los seis originales crudos no están versionados y `.gitignore` los excluye. **El remoto existente sí contiene ocho archivos procesados y cuatro archivos de modelos de una publicación anterior**; `.gitignore` no retira archivos ya versionados. No se eliminan ni se reescribe su historial en esta corrección. El nuevo procedimiento descarga y reconstruye desde originales sin utilizar esos productos previos. Las predicciones individuales nuevas, logs, respaldos y entregas Power BI se excluyen de los commits preparados. `reports/public_summary.json` resume la referencia definitiva. Los registros de verificación actuales contienen hashes del paquete presente y excluyen las trazas individuales que se regeneran localmente.

No se usan rutas con nombres de usuario. `Path(__file__)` resuelve el proyecto y `--source-dir` permite elegir la carpeta de los ZIP en cada computadora. Una ruta de entrada configurada por el usuario es necesaria para sus archivos locales, pero no se fija a la computadora del autor. Siga los comandos de recuperación y `scripts/reproduce_teacher.py --train` de este README.

Antes de un commit:

```bash
.venv/bin/python scripts/check_github_ready.py
```

Para usar Jupyter, registre el entorno de su propio clon y seleccione ese kernel:

```bash
.venv/bin/python -m ipykernel install --user --name ia-u2 --display-name "Python IA U2"
```

Los notebooks evalúan los artefactos definitivos guardados. Las trazas individuales de evaluación se regeneran mediante el entrenamiento aislado cuando no existen. Consulte el procedimiento científico siguiente; descargar raw y entrenar con su orden docente original constituye otro experimento.

## Presentación en JupyterLab: abrir sin volver a ejecutar

La entrega para exposición conserva outputs y contadores de ejecución reales. No se borran para GitHub: portabilidad significa eliminar rutas personales, no borrar resultados. Las imágenes están embebidas en los ipynb, por lo que ver los resultados no requiere kernel activo, originales ni descompresión. Para recalcular sí se necesitan el entorno y los originales ya preparados.

Abra `notebooks/00_Proyecto_Completo_Ejecutado.ipynb` para el recorrido unificado, o los cuatro notebooks de fases. El unificado se ejecuta completo en un kernel nuevo, con contadores y salidas propios. La evidencia vigente es `reports/notebook_execution.json`. Los generadores de notebooks crean plantillas: deben ir seguidos de `src/execute_notebooks.py`, que ejecuta y guarda las cinco versiones.

## Prueba de recuperación en un clon limpio

Se auditó el remoto y se probó el mecanismo con descargas nuevas, sin caché pip ni archivos del proyecto original y sin enlaces físicos. La prueba previa a la publicación y sus límites se documentan en `docs/CLEAN_CLONE_REPRODUCIBILITY.md`. El inventario adjunto corresponde al commit anterior identificado en esa auditoría.

## Reproducción de la referencia científica congelada

Desde un clon con Python 3.12 y las dependencias instaladas:

```bash
.venv/bin/python scripts/reproduce_scientific.py --run-dir tmp/scientific_reproduction --restore-evaluation-traces
```

Este comando entrena en una carpeta nueva a partir del dataset procesado versionado, con el orden congelado, y compara predicciones, métricas, folds, clustering y SHAP. Se detiene si hay diferencias y no reemplaza modelos del proyecto principal. `docs/SCIENTIFIC_REPRODUCTION.json` registra el resultado de la comparación actual. Esto reproduce la referencia publicada; la recuperación desde raw y su equivalencia por llaves tienen evidencia separada en `docs/SOURCE_ORDER_AUDIT.json`.

Las trazas individuales están excluidas de Git. La opción `--restore-evaluation-traces` recupera sólo las que falten después de comparar con la referencia; no reemplaza modelos ni trazas existentes. Se probó esta recuperación en una copia sin trazas iniciales. Para revisar la referencia:

```bash
.venv/bin/python src/scientific_audit.py
.venv/bin/python src/execute_notebooks.py
.venv/bin/python src/verify_outputs.py
.venv/bin/python -m unittest discover -s tests -v
```

Los registros históricos no se reutilizan como pruebas actuales. La prueba final ya había sido observada y la evaluación es retrospectiva. No se altera el objetivo ni se elige un ganador nuevo por sus cifras de prueba.
