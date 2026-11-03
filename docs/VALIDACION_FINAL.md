# Verificación del análisis

Los controles ejecutables registran 336 comprobaciones aprobadas y 0 fallidas. Las fechas, entradas y hashes se consultan en `reports/final_verification.json` y `reports/notebook_execution.json`.

## Notebooks

| Archivo | Celdas ejecutadas | Tiempo (s) | Estado |
|---|---:|---:|---|
| `notebooks/01_Ingenieria_Datos_EDA.ipynb` | 2 | 2.63 | passed |
| `notebooks/02_Clustering_Perfilamiento.ipynb` | 2 | 2.49 | passed |
| `notebooks/03_Modelado_Supervisado.ipynb` | 2 | 4.91 | passed |
| `notebooks/04_Explicabilidad_SHAP.ipynb` | 2 | 2.54 | passed |
| `notebooks/00_Proyecto_Completo_Ejecutado.ipynb` | 5 | 5.54 | passed |

Cada notebook ejecuta controles de los datasets y modelos almacenados. Las entradas se identifican mediante SHA-256. El recorrido completo utiliza un kernel propio. El procedimiento de entrenamiento y comparación se encuentra en el README y su registro en `docs/SCIENTIFIC_REPRODUCTION.json`.

## Resultados

| Magnitud | Valor |
|---|---:|
| ROC-AUC ponderada de CatBoost | 0.8203566504 |
| AP ponderada de CatBoost | 0.6012724932 |
| F1 macro ponderado de CatBoost | 0.6932939538 |
| Silueta de GMM k=2 | 0.4539280521 |
| Solapamiento de CONGLOME | 0 |

## Pruebas y alcance

Pruebas unitarias aprobadas: 20. Los controles verifican población, llaves, particiones, transformaciones, predicciones, calibración, ponderaciones, clustering, SHAP, notebooks e integridad de artefactos.

Evaluación retrospectiva sobre una partición de prueba previamente examinada; los resultados requieren validación externa independiente.

La ponderación describe la cohorte analítica y no reproduce todo el diseño complejo de ENAHO. El objetivo representa no uso reciente de internet y no una medición completa de competencias digitales.
