# Auditoría de rúbrica: estado inicial y cierre verificable

Auditoría iniciada el 28-10-2026 (America/Lima). Fuente normativa: guía docente completa, 7 páginas, y consigna de aula (EDA de datos crudos). Los dos prompts del usuario amplían el control de calidad; sus mejoras adicionales se distinguen de los requisitos docentes. Esta sección registra el estado ANTES de modificar código; el cierre se añadirá con evidencia nueva.

## Protección y alcance

Raíz: `InteliogenciaArtificial`. Git contiene archivos sin versionar; no hay entrega previa confirmada por un commit. Se preservó el estado en `snapshots/pre_mejora_20261028_230358.tar.gz`, con huella y estado Git en `snapshots/manifest.json`. No se duplicaron ni modificaron los ZIP originales. No se autorizaron commits, publicación ni subida de microdatos.

Estados: CUMPLIDO, PARCIAL, FALTANTE, NO VERIFICABLE. Un requisito cumplido inicialmente puede requerir regeneración si cambian sus dependencias. Las cifras iniciales son resultados previos, no resultados nuevos.

| Requisito fiel a la guía / ampliación del usuario | Estado inicial | Evidencia real inicial | Deficiencia | Acción correctiva | Prueba de cierre |
|---|---|---|---|---|---|
| Ingesta ENAHO100/200/300/Sumaria2025; guía pp2-5 | PARCIAL | build_data.load_2025; source_manifest | Corte panel sin contraste anual | Comparar llaves/valores/cohortes; seleccionar fuente única | Comparación ejecutada y hashes |
| Preservar texto, ceros, espacios y codificación real; pp4-5 | PARCIAL | clean_keys, dtype string, UTF8BOM | AÑO se convierte a numérico; solo formato panel | Conservar año texto, detectar/documentar formato anual/panel | Esquema y longitudes de llaves |
| Uniones persona/hogar/distrito sin multiplicación; pp5,7 | CUMPLIDO | merge_audit, validate many_to_one | Debe revalidarse al ampliar ESCALE | Auditar cada unión y descartes | Unicidad, cardinalidades y conteos |
| Población6-17; guía p5 | CUMPLIDO | builder filtros edad/residencia | Falta flujo secuencial completo de elegibilidad | Exportar flujo y causas | Recalcular reglas desde originales |
| EDA crudo antes de preprocesar; consigna aula | PARCIAL | ingesta auditada; run_analysis.eda | EDA principal sobre train integrado con logs | EDA por módulos antes de unión/imputación, faltantes/códigos/distribuciones/atípicos | Tablas y figuras regeneradas |
| Validar variables con documentación oficial; usuario | PARCIAL | TARGET_DECISION, sources.json | P314B/P316 completos y factores sin sensibilidad | Auditar cuestionario/saltos y pesos por unidad | Evidencia documental y comprobación de valores |
| Padrón+Padlocal; guía p3 y misión | PARCIAL | read_padron; no lectura Padlocal | Padlocal no integrado ni auditado | Dimensión local y join o exclusión fundada; no inventar infraestructura | Esquemas, duplicados, cobertura y conflictos |
| Agregar distrito+área, ratio sumas, público/privado, coordenadas; p5 | PARCIAL | read_padron produce ratios correctos | Área/códigos/locales necesitan auditoría; atributos limitados | Validar área y locales únicos con Padlocal | Tabla control de agregaciones |
| Diagrama de cruces y faltantes; p7 | CUMPLIDO | PDFp2, data_audit.json | Cifras fijas y Padlocal ausente | Actualizar diagrama según ejecución | PDF contra auditoría nueva |
| Partición por CONGLOME; p5 | CUMPLIDO | GroupShuffleSplit, GroupKFold | Prueba ya observada en entrega previa | Mantener separación; revelar historial, no alegar prueba inédita | Cero intersección train/test/folds |
| Transformaciones dentro de fold; p5 | CUMPLIDO | Pipeline+ColumnTransformer en evaluate_models | No pruebas de comportamiento con datos sintéticos | Añadir test mediana train/categorías desconocidas | Test ejecutado, pipeline persistido |
| Excluir respuestas/proxies directas; p5 | CUMPLIDO | Lista13features sin ramasP314/P316 | Validación prohibida incompleta por prefijos | Centralizar guardas y justificar predictores | Intento de fuga rechazado |
| PCA o UMAP; p5 | CUMPLIDO | clustering PCA2D | Nada obligatorio faltante | Conservar y regenerar si datos cambian | Varianza/proyección verificadas |
| Al menos2 métodos y selecciónk; pp5-6 | CUMPLIDO | KMeans/GMM k 2-6 | Solo semilla42, estabilidad no evaluada | Conservar búsqueda; estabilidad y ablación acceso (usuario) | ARI entre semillas/submuestras |
| Silueta, Davies-Bouldin, Calinski-Harabasz; p6 | CUMPLIDO | clustering_comparison10 filas | Silueta submuestral; interpretación binaria frágil | Documentar muestra y contraste sin acceso | Métricas recalculadas |
| Perfiles interpretables y nombres; p6 | PARCIAL | cluster_profiles, PDFp3 | Pobreza/lengua/contexto escolar poco descritos | Ampliar perfil ponderado, nombres basados en datos | Tabla y conclusiones concordantes |
| Uno de objetivos: rezago o exclusión digital; p6 | PARCIAL | P314A2 no uso reciente; comparación rezago | No mide competencias digitales completas | Mantener objetivo defendible si evidencia lo respalda, declarar operacionalización y límite | TARGET_DECISION cerrada antes de entrenar |
| Baseline+3avanzados; p6 | CUMPLIDO | Logística,RF,XGB,CatBoost ejecutados | Nada obligatorio faltante | Preservar familias | Evidencia5 folds por familia |
| AjusteHP, comparación justa; rúbrica p7 | PARCIAL | 2 configs/familia,40fits previos | Exploración acotada | Búsqueda CPU acotada y parámetros registrados | Registro config/fold/tiempo y selección |
| Desbalance y factor expansión; p6 | PARCIAL | FACPOB07+balance fold | No sensibilidad, mezcla automática | Comparar sin pesos/población/clase/combinado solo desarrollo | Sensibilidad OOF y política predefinida |
| Test ROC/PR/F1/confusión/calibración; p6 | CUMPLIDO | model_comparison_test, curvas, bootstrap | Parte métricas sin ponderar incompletas | Expandir métricas y baselines constantes | Recomputar desde predicciones |
| FP/FN y discusión crítica; p7 | CUMPLIDO | PDFp4 470FN/207FP previos | Faltan sensibilidad/especificidad y evaluación granular completa | Métricas por subgrupo y umbral0.5 | Conteos y tasas verificadas |
| SHAP global top 10 ganador; p6 | CUMPLIDO | beeswarm, descomposición lineal aditiva | Fondo no ponderado declarado | Conservar explicación y regenerar | Aditividad modelo real |
| Dos dependencias para no linealidad; p6 | PARCIAL |2plots del ganador lineal | No estudia interacción no lineal | Análisis complementario árbol competitivo separado con interacciones | SHAP interacción y aditividad; etiquetas modelo |
| Dos waterfalls extremos correctos; p6 | CUMPLIDO | shap_cases, dosfiguras | Explica score previo a calibración; casos hardcoded en prosa | Mantener distinción y narrativa automática | Etiqueta,umbral,predicción y suma |
| Carpeta estructurada y código ejecutable semilla42; pp6-7 | PARCIAL | scripts + requirements | Notebook solo revisión; AIenv incompleto |4notebooks ejecutan fases reales, scripts canónicos | Ejecución limpia y tiempos |
| Dataset y diccionario; p7 | CUMPLIDO |2CSV +2diccionarios | Parquet adicional solicitado usuario | Exportar ambos formatos, actualizar roles | Esquemas, conteos, igualdad CSV/Parquet |
| Artículo 4-6p estiloIEEE/MDPI; p7 | PARCIAL | PDF 6p, Markdown | Formato general, cifras/narrativas rígidas | Conservar contenido válido, estilo científico y datos dinámicos | Render6p, revisión visual y consistencia |
| Pruebas y verificación final; usuario | PARCIAL | verify_outputs pasado | Conteos/fits rígidos, pruebas limitadas | Tests unitarios/integración, reporte versiones/hashes/config | final_verification.json ejecución real |
| ZIP portable/manifiesto; usuario | PARCIAL | package_submission | Rutas personales, predicciones identificables y copia vieja notebook | Paquete privado docente mínimo, sin predicciones/coords individuales/IDs originales | TestZIP,hashes,escaneo contenido |
| Defensa oral; rúbrica p7 | NO VERIFICABLE | No exposición observada | Dominio del estudiante requiere preparación | Guía de defensa con preguntas y límites | Entregar guía; dominio oral no certificable |

## Distinciones

Regresión es opcional; no se exige MLP, UMAP además de PCA ni publicación en GitHub. No inventaremos medidas de competencias, computadoras o infraestructura que no existan en los originales. La falta de un atributo no se arregla mediante imputación conceptual. Una prueba ya inspeccionada no recupera su condición de prueba inédita al reentrenar.

## Cierre de auditoría tras ejecución

Fecha UTC: 2026-10-29T04:34:35.530194+00:00. Estado de verificación: passed.

| REQUISITO | EVIDENCIA | ESTADO | OBSERVACIÓN |
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

No se garantiza 20/20. Los parciales conceptuales y la sustentación oral no se convierten en cumplimiento por tener código o buenas métricas. Regresión y publicación en GitHub no son obligatorias.
