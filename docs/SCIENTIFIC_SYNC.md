# Sincronización científica de ENAHO + ESCALE 2025

Fecha: 3 de noviembre de 2026 (America/Lima). Referencia publicada: `c864fac07f8edd49bba9c54b92c396ec06169afc`. Esta corrección permanece local: no se ha hecho commit ni push.

## Referencia protegida

Antes de modificar artefactos se conservó `snapshots/scientific_before_20261103T165937Z/`, excluido de Git: archivo completo, manifiesto de 150 archivos con tamaño/SHA-256 y parche del estado inicial. SHA-256 de `artifacts.tar.gz`: `739f1336d1bca48af784eef4ec5d82c4d6d7e90bb1078d8ae1751199ac3f31fe`.

La referencia científica es el dataset anual de 2025, en su orden original, y los modelos guardados. `SCIENTIFIC_REFERENCE.json` fija sus hashes. Se mantienen el objetivo P314A=2, las 13 variables, CatBoost seleccionado por AP de desarrollo y el umbral 0.5. No se promueven los modelos recién entrenados sobre los originales.

## Causa de las diferencias

Se reconstruyó de nuevo el corte 2025 desde los seis originales docentes en un directorio aislado. La comparación por CONGLOME, VIVIENDA, HOGAR y CODPERSO confirmó:

- Las mismas 23 345 personas y los mismos valores en las 112 columnas comunes, incluidos los valores numéricos exactos al leer ambas bases.
- Cinco columnas adicionales del panel, no utilizadas como predictoras.
- Diferente orden de filas: 23 344 personas cambian de posición.
- Las mismas 13 105 personas en desarrollo y 3 439 en prueba; los mismos conglomerados en ambos conjuntos y en los cinco folds.
- El mismo código de análisis y las mismas versiones de software en las ejecuciones históricas comparadas.

Los notebooks anteriores provenían de la ejecución del panel docente, mientras que los modelos e informe conservados correspondían al orden anual. Los algoritmos con muestreo y ajuste sensible a la secuencia, y las muestras de silueta y SHAP, pueden producir resultados distintos con la misma semilla cuando cambia el orden. La diferencia no corresponde a otra variable objetivo ni a una selección de modelos basada en prueba. `SOURCE_ORDER_AUDIT.json` conserva los resultados de la investigación; el respaldo mantiene las salidas anteriores.

| Resultado | Referencia anual conservada | Ejecución docente anterior |
|---|---:|---:|
| CatBoost ROC-AUC ponderada | 0.8203566504 | 0.8202818887 |
| CatBoost AP ponderada | 0.6012724932 | 0.5996325850 |
| CatBoost F1 macro ponderado | 0.6932939538 | 0.6815668065 |
| GMM k=2, silueta | 0.4539280521 | 0.450995 aprox. |
| SHAP edad, media absoluta | 1.0570282651 | 1.088106 aprox. |

## Ejecuciones y comprobaciones realizadas

1. Se copiaron código y entradas procesadas en `tmp/scientific_sync/run/`, sin modificar los artefactos principales. Se ejecutó realmente `src/run_analysis.py` completo: preparación, clustering, sensibilidad de pesos, búsqueda de hiperparámetros, ajuste/calibración y SHAP. No se cambiaron configuraciones para mejorar prueba.
2. La reproducción se contrastó con la referencia: 35 comprobaciones, todas aprobadas. Las predicciones de prueba y OOF difieren como máximo en 3.33e-16; folds, particiones, asignaciones, perfiles, silueta, importancia SHAP e interacciones coinciden dentro de las tolerancias registradas. Las tablas de clustering y SHAP coinciden exactamente. Se excluyen tiempos de ejecución de la comparación numérica. Evidencia: `SCIENTIFIC_REPRODUCTION.json`.
3. Se recalcularon predicciones a partir de los modelos originales y se comprobaron orden/identidad de filas, variables, transformaciones deterministas, pipelines, factores individuales, calibración OOF, umbral, métricas ponderadas/sin ponderar y matriz de confusión. Se verificaron por separado asignaciones y geometría del GMM, TreeSHAP de CatBoost e interacciones de XGBoost. Los controles están implementados en `src/scientific_audit.py`.
4. Los cinco notebooks se ejecutan realmente en kernels nuevos. El notebook 00 ejecuta su recorrido completo; no concatena resultados de otras corridas. Sus salidas evalúan modelos congelados, y lo declaran expresamente. La comprobación de calibración reajusta una sigmoide independiente con OOF de desarrollo, sin modificar la almacenada. El entrenamiento completo tiene evidencia separada.
5. El PDF y su Markdown se regeneraron desde los resultados conservados. Se reemplazaron comentarios operativos por redacción académica, conservando procedencia, resultados y limitaciones. Se renderizaron e inspeccionaron las seis páginas.
6. Se ejecutaron 20 pruebas unitarias y `pip check`. Las tres regresiones nuevas comprueban alineación por identidad y rechazo de filas duplicadas o inexistentes. La verificación final vuelve a ejecutar los controles; no hereda un estado histórico `passed`.
7. Se probó además una copia de la superficie publicable sin las trazas individuales: la comparación contra el entrenamiento aislado y la recuperación de trazas faltantes funcionaron; sus auditorías se ejecutaron sobre los modelos de referencia. Esta comprobación reutiliza la corrida aislada, no se presenta como otra descarga limpia ni otro entrenamiento nuevo.

## Estado de la comprobación final

La verificación vigente aprobó 336 controles, sin fallos. Las 20 pruebas unitarias y la comprobación de dependencias aprobaron. El inventario se genera de los archivos actuales y no reutiliza huellas históricas. Los cinco notebooks tienen salidas reales y hashes de entrada coincidentes.

## Tabla de correcciones

Las rutas son relativas a la raíz del repositorio. Los registros de ejecución actuales y `reports/final_verification.json` son la evidencia vigente.

| Archivo | Inconsistencia original | Causa identificada | Corrección realizada | Prueba que respalda la corrección | Estado final |
|---|---|---|---|---|---|
| `notebooks/00_Proyecto_Completo_Ejecutado.ipynb` | Resumen y salidas docentes distintos del modelo anual | Ensamblado de otra ejecución | Recorrido completo ejecutado en un kernel propio sobre la referencia | Contadores, outputs, hashes de entradas y ejecución | Sincronizado |
| `notebooks/01_Ingenieria_Datos_EDA.ipynb` | Reconstrucción docente presentada junto a resultados anuales | Fuentes y orden sin una referencia única | Evaluación real de cohorte, variables, llaves, pesos y particiones; reconstrucción raw documentada aparte | Auditoría dataset y registro de ejecución | Sincronizado |
| `notebooks/02_Clustering_Perfilamiento.ipynb` | Silueta 0.450995 frente a 0.453928 | Orden de filas y submuestra diferentes | Recalcula geometría y asignaciones del GMM definitivo | Silueta/DB/CH, asignaciones, perfiles y reproducción | Sincronizado |
| `notebooks/03_Modelado_Supervisado.ipynb` | AP/F1 diferentes del modelo guardado | Entrenamiento con otra secuencia | Predicción y evaluación reales del modelo de referencia; entrenamiento separado | Predicciones, pesos, calibración OOF y métricas | Sincronizado |
| `notebooks/04_Explicabilidad_SHAP.ipynb` | Importancias y residuos de otra ejecución | Otro ajuste y orden de muestra | Recalcula SHAP e interacciones de los modelos guardados | Importancias, casos, aditividad y pares | Sincronizado |
| `reports/notebook_execution.json` | Huellas antiguas y estados no aplicables a archivos actuales | Cambios posteriores a la ejecución y mezcla de versiones | Nuevo registro de las cinco ejecuciones reales | SHA-256 exacto de cada notebook | Regenerado |
| `reports/verification.json` | Inventario desactualizado y rutas personales | Registro histórico del entorno canónico | Nuevos controles e inventario de artefactos publicables presentes | Verificación ejecutada después de las correcciones | Regenerado |
| `reports/final_verification.json` | Mismo problema que el registro anterior | Misma procedencia histórica | Nuevo registro de la verificación actual | Controles y hashes actuales | Regenerado |
| `reports/public_summary.json` | Procedencia docente junto a cifras de versiones diferentes | Resumen de presentación separado de la referencia | Resumen de la referencia anual y sus resultados | Comparación con `results.json` | Sincronizado |
| `reports/results.json` | Índices locales de casos SHAP en la copia de trabajo | Reincorporación de trazabilidad individual | Retira únicamente vínculos a filas; conserva números | Auditoría de probabilidades y contribuciones | Saneado; sin cambios numéricos |
| `reports/tables/shap_cases.json` | Índices locales de casos | Misma causa | Elimina vínculos a filas para publicación | Igualdad de probabilidades, scores y contribuciones | Saneado; sin cambios numéricos |
| `reports/tables/data_audit.json` | Rutas personales en la copia local | Registro del entorno de ejecución | Rutas parametrizadas | Control de privacidad y hash del dataset | Saneado |
| `reports/tables/target_measurement_audit.json` | Ruta absoluta del dataset | Misma causa | Ruta parametrizada | Hash del dataset y controles de medición | Saneado |
| `output/pdf/Informe_U2_Brecha_Digital_2025.pdf` | Comentarios operativos y redacción defensiva | Mezcla de explicación interna y exposición académica | Redacción académica, fecha de revisión y resultados conservados | Extracción de cifras y revisión visual de seis páginas | Sincronizado |
| `reports/article.md` | Texto anterior del PDF | Fuente editable anterior | Regenerado con el PDF | Mismo generador y datos | Sincronizado |
| `src/make_report.py` | Comentarios internos y dependencia de índices SHAP publicables | Diseño editorial y enlace a filas | Texto académico y recuperación de extremos desde predicciones locales | Generación completa del PDF y aserciones SHAP | Corregido |
| `src/scientific_audit.py` | Faltaba una evaluación independiente de artefactos congelados | Control anterior insuficiente | Controles de dataset, clasificación, clustering y SHAP | Ejecución en referencia y copia sin trazas iniciales | Nuevo |
| `src/make_scientific_notebooks.py` | Faltaban plantillas coherentes con una referencia única | Generación por fases que entrenaba otra fuente | Plantillas de evaluación real con entradas identificadas por hash | Cinco ejecuciones reales | Nuevo |
| `src/make_notebooks.py` | Generaba las antiguas fases docentes sobre el directorio abierto | Flujo de generación anterior | Delega en el generador definitivo | Generación y ejecución completas | Corregido |
| `src/execute_notebooks.py` | Sólo cuatro fases; registro no cubría el recorrido 00 | Flujo de ensamblado | Ejecuta cinco kernels nuevos, guarda outputs y hashes | Registro de cinco ejecuciones | Corregido |
| `scripts/save_presentation_notebooks.py` | Podía sobrescribir la presentación con otra corrida docente | Copia desde una carpeta histórica | Ejecuta los notebooks vigentes; elimina la importación de salidas antiguas | Revisión del código y flujo de ejecución vigente | Corregido |
| `src/finalize_docs.py` | Podía volver a generar documentación de cuatro fases como si fuera vigente | Generador histórico | Redacta sólo desde los cinco registros y controles actuales; conserva el alcance retrospectivo | Ejecución del generador y verificación posterior | Corregido |
| `src/verify_outputs.py` | Estados históricos, hashes inconsistentes y control científico limitado | Verificación anterior al paquete vigente | Control numérico independiente, cinco notebooks, entradas e inventario vigente | Verificación final ejecutada | Corregido |
| `scripts/reproduce_scientific.py` | Faltaba reproducir específicamente el orden/modelo definitivo | Reproducción docente era otro experimento | Entrena aislado, compara y permite recuperar sólo trazas faltantes | Reproducción completa y prueba sin trazas | Nuevo |
| `scripts/check_github_ready.py` | Rechazaba modelos/procesados ya versionados y no distinguía enlaces SHAP | Política anterior al estado real de Git | Conserva los archivos existentes y detecta datos nuevos o enlaces individuales | Control de privacidad aprobado | Corregido |
| `tests/test_scientific_audit.py` | Sin regresiones de identidad/orden de evaluación | Falta de prueba negativa específica | Tres pruebas de orden, duplicados y claves inexistentes | unittest | Nuevo |
| `docs/SCIENTIFIC_REFERENCE.json` | Referencia no fijada explícitamente | Mezcla de versiones | Bloqueo SHA-256 de datasets/modelos y procedencia anual | Comparación con respaldo | Nuevo |
| `docs/SCIENTIFIC_REPRODUCTION.json` | Sin contraste de la referencia definitiva | Evidencia previa de otra fuente | Comparaciones numéricas de la corrida aislada | 35 comprobaciones | Nuevo |
| `docs/SOURCE_ORDER_AUDIT.json` | Causa del desacuerdo no identificada | Diferente orden de fuentes | Comparación por llaves, orden, grupos y versiones | Reconstrucción docente nueva | Nuevo |
| `README.md` | Permitía interpretar la corrida docente como equivalente a la referencia | Dos rutas científicas mezcladas | Distingue referencia congelada, recuperación raw y evaluación de notebooks | Comandos y comprobaciones documentadas | Corregido |
| `docs/VALIDACION_FINAL.md` | Describía ejecución histórica como vigente | Documento no actualizado al paquete | Remite a controles y ejecuciones actuales | Registros regenerados | Actualizado |
| `docs/SCIENTIFIC_SYNC.md` | Sin informe integrado de causas y correcciones | Auditorías fragmentadas | Este informe, con resultados anteriores, cambios y límites | Evidencias enlazadas por ruta | Nuevo |

`models/model_metadata.json`, las tablas de ablación/interacciones y otros JSON sólo requerían normalización o saneamiento de su serialización. Sus valores científicos se conservaron. Los modelos `.joblib`, datasets procesados y el código de entrenamiento no se reemplazaron. Los gráficos del artículo se regeneraron desde esos mismos modelos y tablas; las magnitudes se contrastan antes de dibujar.

## Reproducción y alcance

Con el entorno fijado instalado, la referencia se reproduce a partir del dataset procesado versionado:

```bash
.venv/bin/python scripts/reproduce_scientific.py --run-dir tmp/scientific_reproduction --restore-evaluation-traces
.venv/bin/python src/scientific_audit.py
.venv/bin/python src/execute_notebooks.py
.venv/bin/python src/verify_outputs.py
.venv/bin/python -m unittest discover -s tests -v
```

La opción de recuperación copia únicamente trazas individuales faltantes, excluidas de Git. No sobrescribe trazas existentes ni modelos. La verificación completa de raw necesita antes `scripts/download_raw_data.py`. El entrenamiento puede tardar varios minutos; no debe presentarse una evaluación de modelos guardados como si fuera entrenamiento.

La reconstrucción docente conserva su propio orden y sus resultados en un directorio separado. No se afirma identidad byte a byte entre un CSV reconstruido desde panel y la publicación anual. La evidencia raw establece igualdad de valores comunes por persona; el entrenamiento definitivo usa el dataset y orden fijados por hash. No se afirma haber hecho una segunda descarga anónima limpia durante esta sincronización: aquella prueba está documentada por separado en `CLEAN_CLONE_REPRODUCIBILITY.md`.

## Limitaciones pendientes

La coherencia interna de los artefactos definitivos no convierte el conjunto de prueba previamente observado en una validación externa inédita. La evaluación es retrospectiva. La medición corresponde a no uso reciente, no a competencias digitales completas. La separación por CONGLOME, la ponderación y el bootstrap no garantizan generalización a territorios nuevos ni reproducen todo el diseño complejo de ENAHO.

Las ejecuciones históricas quedan preservadas y explícitamente separadas; sus cifras no se ocultan ni se mezclan con las definitivas. Los ZIP de entrega antiguos y productos ajenos a este conjunto de artefactos no se presentan como regenerados por esta corrección. La aprobación para commit y push sigue pendiente de revisión del usuario.
