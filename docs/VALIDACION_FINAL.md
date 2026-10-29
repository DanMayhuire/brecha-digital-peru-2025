# Validación final ejecutada

Fecha UTC: 2026-10-29T04:34:35.530194+00:00. Estado: **passed**. 152 controles aprobados; 0 fallidos. Véase `reports/final_verification.json` para detalles, fuentes, hashes, versiones, configuración y métricas.

## Ejecución real

Los cuatro notebooks ejecutaron los scripts canónicos en kernels nuevos. Registro:

|Notebook|Segundos observados|Estado|Celdas código|
|---|---:|---|---:|
|01_Ingenieria_Datos_EDA.ipynb|31.26|passed|4|
|02_Clustering_Perfilamiento.ipynb|5.96|passed|3|
|03_Modelado_Supervisado.ipynb|81.30|passed|4|
|04_Explicabilidad_SHAP.ipynb|6.25|passed|3|

## Datos y resultados regenerados

- Fuente anual 2025 única, contrastada con corte panel; mismos valores comunes seleccionados normalizados. Educación panel añade 2512 filas sin respuestas. No se afirma equivalencia de columnas no leídas.
- Base 23345 residentes, cohorte 16544; desarrollo 13105 y prueba 3439. Grupos 3232/808; intersección 0.
- Padlocal 69642 locales únicos;54038 servicios enlazados sin multiplicación. Un conflicto geográfico se aparta de coordenadas/contexto físico. Coincidencia ENAHO 100%;contexto ESCALE 98.179482%.
- Ganador CatBoost, AP-CV 0.593466±0.010857; ventaja sobre XGBoost pequeña y no establecida como estadísticamente significativa.
- Prueba ponderada: ROC-AUC 0.820357; AP 0.601272; PR trapezoidal0.600666; F1 macro0.693294; precisión 0.690899; recall 0.381181; especificidad 0.951893; Brier 0.127282.
- Clustering GMM k 2, silueta 0.453928; ARI 1 entre las semillas/submuestras evaluadas. Sin internet/electricidad, ARI 0.080753 y silueta 0.279132: los grupos dependen fuertemente de los accesos; no se presentan como estructuras latentes independientes de ellos.
- SHAP del ganador residuo 6.22e-15; interacciones XGBoost residuo 2.38e-06. Score antes de calibración y probabilidad calibrada diferenciados.

## Pruebas ejecutadas

Se ejecutó unittest sobre `tests/`: pruebas negativas de uniones duplicadas y variables prohibidas, ceros/códigos, aislamiento del preprocesamiento, pesos, faltantes de la etiqueta y datos reales. Se recalcularon métricas desde predicciones; se comparó el modelo persistido; se reconstruyeron particiones y folds seed 42; se comprobó aditividad SHAP, fuentes y huellas de notebooks/artefactos. `pip check` aprobó las dependencias.

## Errores y correcciones durante ejecución

La primera apertura de kernel en sandbox fue bloqueada por puertos locales; se ejecutó con acceso local autorizado. Un intento inicial se detuvo por la guarda de versión al cambiar código entre fases. Se conservaron trazas en `notebook_execution_attempt1.json` y se repitieron los cuatro notebooks con versión congelada. No se presentan esos resultados intermedios como ejecución final. El aviso TCP del kernel se refiere a comunicación local en loopback; no hubo exposición remota. El encabezado DBF tiene año no estándar/inconsistente con FECHA_ACT2025 y no determina el año analítico. Detalles en SOURCE_RECONCILIATION.

## Comandos comprobados

```bash
.venv/bin/python src/execute_notebooks.py
.venv/bin/python src/make_report.py
.venv/bin/python src/verify_outputs.py
.venv/bin/python src/finalize_docs.py
.venv/bin/python src/package_submission.py
```

Los originales deben existir; configure IA_SOURCE_DIR/IA_ANNUAL_DIR como indica README. El ZIP no incluye las fuentes. La validación registra solo pruebas ejecutadas; no certifica generalización externa ni la defensa oral.

## Límites pendientes

La medición completa de competencias para 6–17 no está disponible por universo/saltos del cuestionario; la aproximación digital continúa siendo parcial frente al constructo amplio de la guía. Faltan atributos de infraestructura escolar en Padlocal; no se fabrican. La prueba ya fue observada en la versión previa. La cohorte no representa una tasa nacional oficial. Falta la sustentación por el estudiante; no hay bloqueo técnico para la entrega privada con estas limitaciones declaradas.
