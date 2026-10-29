# Checklist de entrega vigente

Este resumen deriva de la auditoría final; no sustituye sus pruebas.

|Requisito|Evidencia|Estado|Observación|
|---|---|---|---|
|Fuentes ENAHO2025 verificadas|SOURCE_RECONCILIATION.md; source_comparison.json|CUMPLIDO|Anual canónica; panel contraste,2512 filasextra sin respuestas|
|Codificación,decimales,llaves y año texto|source_audit.load_annual; tests/test_data.py|CUMPLIDO|Anual latin1/;/coma; panel UTF8BOM/coma|
|Cardinalidad y ausencia de multiplicación|data_audit.json merges; merge_audit|CUMPLIDO|4 cruces conservan23345 filas|
|Población6–17 y target observado|population_flow_model.csv; target_measurement_audit.json|CUMPLIDO|16544etiquetas válidas,4294 positivos|
|EDA raw previo a ML|raw_eda_variables.csv; raw_eda.png/pdf; raw_sumaria_correlation.csv|CUMPLIDO|95 perfiles de columnas; selección analítica documentada|
|Padlocal auditado e integrado|dbf_schemas en data_audit; escale_join_coverage.csv|CUMPLIDO|69642 locales únicos;54038 serviciosmatches;1conflicto apartado|
|Infraestructura escolar completa sugerida|SOURCE_RECONCILIATION.md; data_audit escale|PARCIAL|Fuentes disponibles no contienen computadoras/agua/internet/altitud escolar. No se inventa|
|Distrito+área y razón agregada|build_data.read_padron; escale_distrito_area_2025.parquet|CUMPLIDO|Ratio SUM(TALUM)/SUM(TDOC); locales únicos para coordenadas|
|Separación por conglomerado|partitions.csv; cv_assignments.csv; final_verification.json|CUMPLIDO|Cero intersección; cincofolds reproducidos seed 42|
|Transformaciones en cada fold|evaluate_models; test_preprocessing_training_only|CUMPLIDO|Imputación/escalado/OHE en Pipeline; testcategorías no vistas|
|Exclusión de fugas|assert_features; test_leakage_rejected; diccionario_model|CUMPLIDO|13 predictores explícitos; no ramasdel objetivo|
|PCA y al menos2 métodos de clustering|clustering_comparison.csv; clustering.png|CUMPLIDO|KMeans/GMM k 2–6; etiqueta no usada|
|Justificaciónk por3métricas y tamaños|clustering_comparison.csv; silhouette.png|CUMPLIDO|GMM k 2; silueta 0.4539|
|Estabilidad y perfiles|clustering_stability.csv; cluster_profiles.csv; clustering_access_ablation.json|CUMPLIDO|ARI 1 entre semillas/submuestras; ablaciónARI0.081 muestra dependencia fuerte del acceso|
|Exclusión digital efectiva completa|TARGET_DECISION.md; VARIABLE_VALIDATION.md; audit_target_measurement.py|PARCIAL|No uso reciente6–17válido; competencias autorreportadas solo14+, condicionadas. No equivalencia plena|
|Baseline y3avanzados|model_search.csv; model_comparison_cv.csv|CUMPLIDO|Logística/RF/XGBoost/CatBoost|
|BúsquedaHP y comparación justa|MODELING_PROTOCOL.md; model_search.csv; cv_folds.csv|CUMPLIDO|24 configs*5 folds+16 estrategias*5 folds=200 ajustes; no exhaustiva ni anidada|
|Desbalance y factores de expansión|weight_sensitivity.csv; MODELING_PROTOCOL.md|CUMPLIDO|Cuatro estrategias por familia; FACPOB07principal,FACTORA07sensibilidad|
|Selección del ganador sin usar prueba|CVtabla; model_metadata.json|CUMPLIDO|CatBoost; AP-CV 0.593466|
|Evaluación inédita/externa|results.json historical_test_warning|NO VERIFICABLE|Prueba heredada ya observada: evaluación retrospectiva, no nuevo test externo|
|Métricasponderadas/no ponderadas,calibración y baselines|model_comparison_test.csv; constant_baselines_test.csv; model_curves.png|CUMPLIDO|AP distintaPRtrap; calibrador conOOF y pesos de desarrollo;umbral0.5|
|ErroresFP/FN/subgrupos|subgroup_performance_test.csv; confusion_matrix.png|CUMPLIDO|TN 2385,FP 185,FN 464,TP 405; recall ponderado0.381|
|SHAP global top 10 ganador|shap_beeswarm.png; shap_importance.csv; results.json|CUMPLIDO|CatBoost; residuo aditividad6.22e-15|
|Dependencias e interacciones no lineales|shap_dependence_1/2.png; nonlinear_shap.json; shap_interaction_1/2.png|CUMPLIDO|Ganador no lineal explicado;XGBoost complementario identificado con 2phiij|
|Dos waterfalls correctos|shap_cases.json; shap_waterfall_alto/bajo.png|CUMPLIDO|Estado actual;score antes calibración yprobabilidad separados;sin identificadores personales en artículo|
|Cuatro notebooks ejecutables|notebook_execution.json;4ipynb|CUMPLIDO|Kernel limpio por notebook; ejecución real de fases y tiempos|
|DatasetsCSV/Parquet y diccionarios|data/processed;docs/data_dictionary*.md|CUMPLIDO|Base 112 columnas;modelo 120;13 predictores|
|Artículo 4–6p y Markdown|output/pdf/Informe_U2_Brecha_Digital_2025.pdf;reports/article.md|CUMPLIDO|PDF 6p;estilo académico MDPI1col;verificación visual en REPORT_QA.md|
|Pruebas y trazabilidad|final_verification.json; tests.log|CUMPLIDO|152 controles aprobados;0fallidos|
|Defensa oral|DEFENSA_ORAL.md|NO VERIFICABLE|Guía entregada; dominio del estudiante requiere sustentación real|
|Paquete portable y privacidad|delivery_manifest.json;package_verification.json|CUMPLIDO|Sin originales/entorno/predicciones por fila;SHA/CRC. Datos procesados para entrega privada|
