# Validación final de la sincronización científica

Registro vigente: `reports/final_verification.json`. Estado: **passed**; 336 controles aprobados y 0 fallidos. La fecha exacta y las huellas están en el registro, que debe regenerarse después de cualquier cambio de artefactos.

## Ejecuciones reales

| Notebook | Celdas de código | Segundos observados | Estado |
|---|---:|---:|---|
| `notebooks/01_Ingenieria_Datos_EDA.ipynb` | 2 | 2.81 | passed |
| `notebooks/02_Clustering_Perfilamiento.ipynb` | 2 | 2.53 | passed |
| `notebooks/03_Modelado_Supervisado.ipynb` | 2 | 4.92 | passed |
| `notebooks/04_Explicabilidad_SHAP.ipynb` | 2 | 2.70 | passed |
| `notebooks/00_Proyecto_Completo_Ejecutado.ipynb` | 5 | 5.55 | passed |

Los cinco notebooks evalúan realmente los modelos conservados en kernels nuevos. El recorrido 00 ejecuta su código completo en su propio kernel. No se ensamblan outputs de otras corridas ni se presenta evaluación como entrenamiento. Los hashes de entrada y ejecución son comprobados por el verificador.

## Entrenamiento aislado y pruebas

Se ejecutó realmente el análisis completo en un directorio aislado y se contrastó con la referencia: 35 comprobaciones aprobadas. `docs/SCIENTIFIC_REPRODUCTION.json` conserva las diferencias y tolerancias; `docs/SCIENTIFIC_SYNC.md` detalla el método y los cambios.

Se ejecutaron 20 pruebas unitarias y `pip check`; ambos aprobaron. Las nuevas pruebas comprueban alineación por identidad y rechazo de filas duplicadas o inexistentes. Se revisaron las seis páginas del PDF renderizado. El control de privacidad de archivos candidatos aprobó. Los modelos y datasets congelados no se reemplazaron.

## Resultados conservados

| Magnitud | Valor |
|---|---:|
| CatBoost ROC-AUC ponderada | 0.8203566504 |
| CatBoost AP ponderada | 0.6012724932 |
| CatBoost F1 macro ponderado | 0.6932939538 |
| GMM k=2: silueta | 0.4539280521 |
| Desarrollo / prueba | 13105 / 3439 |
| Solapamiento CONGLOME | 0 |

## Alcance y límites

El corte docente reconstruido tiene las mismas personas y valores comunes que la referencia anual, con otro orden de filas y cinco campos adicionales no predictivos. La reproducción de esta referencia usa el dataset procesado versionado con su orden fijado por hash. La igualdad por llaves no implica identidad byte a byte entre publicaciones ni invariancia al orden.

La partición de prueba ya se inspeccionó en la versión anterior. Se conserva para comparabilidad, sin usarla para selección nueva; esta auditoría es retrospectiva y no aporta una prueba externa inédita.

Los resultados anteriores están preservados en el respaldo verificable documentado en el informe de sincronización. No se cambió el objetivo ni se eligió otro ganador por prueba. La corrección permanece local, pendiente de revisión; no se ha hecho commit ni push.
