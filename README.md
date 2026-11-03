# Brecha digital y no uso de internet en estudiantes del Perú

Proyecto del curso Inteligencia Artificial, Universidad Peruana Unión. Integra ENAHO y ESCALE 2025 para estudiar el no uso de internet durante el mes anterior en estudiantes residentes habituales de 6 a 17 años, matriculados y asistentes a primaria o secundaria.

La cohorte comprende **16 544 estudiantes**. CatBoost, seleccionado por Average Precision en validación agrupada, obtiene ROC-AUC **0.820357**, AP **0.601272** y F1 macro **0.693294** en prueba ponderada. El agrupamiento seleccionado es GMM con dos componentes y silueta **0.453928**.

## Informe y notebooks

- [Informe PDF](output/pdf/Informe_U2_Brecha_Digital_2025.pdf).
- [Artículo en Markdown](reports/article.md).
- [Recorrido completo](notebooks/00_Proyecto_Completo_Ejecutado.ipynb).
- [Datos y EDA](notebooks/01_Ingenieria_Datos_EDA.ipynb).
- [Clustering](notebooks/02_Clustering_Perfilamiento.ipynb).
- [Clasificación](notebooks/03_Modelado_Supervisado.ipynb).
- [Explicabilidad SHAP](notebooks/04_Explicabilidad_SHAP.ipynb).

Los cinco notebooks contienen salidas guardadas de ejecuciones reales. Sus tablas y figuras se visualizan al abrirlos. Las celdas evalúan los modelos almacenados; el entrenamiento completo se realiza con el procedimiento de reproducción.

## Instalación

Se requiere Python 3.12. Desde una terminal:

```bash
git clone https://github.com/DanMayhuire/brecha-digital-peru-2025.git
cd brecha-digital-peru-2025
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ipykernel install --user --name ia-u2 --display-name "Python IA U2"
```

En Jupyter seleccione el kernel **Python IA U2**.

## Reproducción del análisis

El repositorio incluye los datasets procesados y los modelos. Sus hashes SHA-256 se fijan en [SCIENTIFIC_REFERENCE.json](docs/SCIENTIFIC_REFERENCE.json). El orden de filas forma parte de la especificación reproducible.

```bash
.venv/bin/python scripts/reproduce_scientific.py --run-dir tmp/scientific_run --restore-evaluation-traces
.venv/bin/python src/scientific_audit.py
.venv/bin/python src/execute_notebooks.py
```

El primer comando ejecuta el entrenamiento en una carpeta nueva, compara las predicciones, métricas, folds, clustering y SHAP, y recupera las trazas de evaluación faltantes. Los modelos del directorio principal se conservan. La opción `--run-dir` debe apuntar a una carpeta que todavía no exista.

## Datos originales

Los cuatro CSV de ENAHO PANEL 2021–2025 y los dos DBF de ESCALE se descargan desde los enlaces del material del curso. El análisis de estas fuentes selecciona exclusivamente el corte 2025. El descargador valida tamaños y SHA-256 mediante [download_manifest.json](data/raw/download_manifest.json).

```bash
.venv/bin/python scripts/download_raw_data.py
.venv/bin/python scripts/reproduce_teacher.py
```

Los originales quedan en `data/raw/`, excluidos de Git. La reconstrucción queda en `reports/teacher_run/`. Para ejecutar también su análisis:

```bash
.venv/bin/python scripts/reproduce_teacher.py --train
```

ENAHO anual y el corte del panel coinciden en las personas y valores comunes seleccionados, pero tienen distinto orden de filas y algunas columnas distintas. Un ajuste aleatorio puede depender de ese orden. La reproducción de los modelos incluidos utiliza el dataset procesado y la secuencia fijados por hash. Consulte [fuentes e integración](docs/SOURCE_RECONCILIATION.md) y [descarga de originales](data/raw/README.md).

## Verificación

Con los originales descargados y las trazas de evaluación disponibles:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python src/verify_outputs.py
.venv/bin/python scripts/check_github_ready.py
```

Los resultados se registran en `reports/final_verification.json`, `reports/notebook_execution.json` y `docs/SCIENTIFIC_REPRODUCTION.json`. Las predicciones y asignaciones individuales se generan localmente y están excluidas de Git.

## Metodología y alcance

La partición por CONGLOME separa desarrollo y prueba; cinco folds GroupKFold sustentan la selección. La imputación, el escalado y la codificación se ajustan dentro del entrenamiento de cada fold. La calibración sigmoide utiliza predicciones fuera de fold de desarrollo. El umbral es 0.5 y el peso individual principal es FACPOB07.

La evaluación es retrospectiva sobre una partición de prueba previamente examinada; no constituye validación externa independiente. El objetivo mide no uso reciente de internet, no competencias digitales completas. ESCALE aporta contexto de residencia, sin identificar la escuela de cada estudiante. Los resultados son asociaciones predictivas de la cohorte, no efectos causales ni tasas oficiales nacionales.

Documentación: [objetivo](docs/TARGET_DECISION.md), [protocolo](docs/MODELING_PROTOCOL.md), [validación de variables](docs/VARIABLE_VALIDATION.md), [diccionario de integración](docs/data_dictionary.md), [diccionario de modelado](docs/data_dictionary_model.md) y [verificación](docs/VALIDACION_FINAL.md).
