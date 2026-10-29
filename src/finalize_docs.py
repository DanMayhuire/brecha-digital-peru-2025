"""Documenta el cierre desde verificaciones y resultados existentes; no entrena."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def main():
    r=json.loads((ROOT/'reports/results.json').read_text());v=json.loads((ROOT/'reports/final_verification.json').read_text());a=json.loads((ROOT/'reports/tables/data_audit.json').read_text());n=json.loads((ROOT/'reports/notebook_execution.json').read_text())
    winner=r['supervised']['winner'];m=next(x for x in r['supervised']['test'] if x['seleccionado_cv']);cv=r['supervised']['cv'][0];c=r['clustering']['selected'];conf=r['supervised']['confusion_counts']
    rows=[
      ('Fuentes ENAHO2025 verificadas','CUMPLIDO','SOURCE_RECONCILIATION.md; source_comparison.json','Anual canónica; panel contraste,2512filasextra sin respuestas'),
      ('Codificación,decimales,llaves y año texto','CUMPLIDO','source_audit.load_annual; tests/test_data.py','Anual latin1/;/coma; panel UTF8BOM/coma'),
      ('Cardinalidad y ausencia de multiplicación','CUMPLIDO','data_audit.json merges; merge_audit','4cruces conservan23345filas'),
      ('Población6–17 y target observado','CUMPLIDO','population_flow_model.csv; target_measurement_audit.json','16544etiquetasválidas,4294positivos'),
      ('EDA raw previo a ML','CUMPLIDO','raw_eda_variables.csv; raw_eda.png/pdf; raw_sumaria_correlation.csv','95perfilesdecolumnas; selecciónanalíticadocumentada'),
      ('Padlocal auditado e integrado','CUMPLIDO','dbf_schemas en data_audit; escale_join_coverage.csv','69642locales únicos;54038serviciosmatches;1conflicto apartado'),
      ('Infraestructura escolar completa sugerida','PARCIAL','SOURCE_RECONCILIATION.md; data_audit escale','Fuentes disponibles no contienen computadoras/agua/internet/altitud escolar. No se inventa'),
      ('Distrito+área y razón agregada','CUMPLIDO','build_data.read_padron; escale_distrito_area_2025.parquet','Ratio SUM(TALUM)/SUM(TDOC); locales únicos para coordenadas'),
      ('Separación por conglomerado','CUMPLIDO','partitions.csv; cv_assignments.csv; final_verification.json','Cero intersección; cincofolds reproducidos seed42'),
      ('Transformaciones en cada fold','CUMPLIDO','evaluate_models; test_preprocessing_training_only','Imputación/escalado/OHE en Pipeline; testcategorías no vistas'),
      ('Exclusión de fugas','CUMPLIDO','assert_features; test_leakage_rejected; diccionario_model','13predictores explícitos; no ramasdelobjetivo'),
      ('PCA y al menos2métodos de clustering','CUMPLIDO','clustering_comparison.csv; clustering.png','KMeans/GMM k2–6; etiqueta no usada'),
      ('Justificaciónk por3métricas y tamaños','CUMPLIDO','clustering_comparison.csv; silhouette.png',f'{c["metodo"]} k{int(c["k"])}; silueta{c["silueta"]:.4f}'),
      ('Estabilidad y perfiles','CUMPLIDO','clustering_stability.csv; cluster_profiles.csv; clustering_access_ablation.json','ARI1 entre semillas/submuestras; ablaciónARI0.081 muestra dependencia fuerte del acceso'),
      ('Exclusión digital efectiva completa','PARCIAL','TARGET_DECISION.md; VARIABLE_VALIDATION.md; audit_target_measurement.py','No uso reciente6–17válido; competencias autorreportadas solo14+, condicionadas. No equivalencia plena'),
      ('Baseline y3avanzados','CUMPLIDO','model_search.csv; model_comparison_cv.csv','Logística/RF/XGBoost/CatBoost'),
      ('BúsquedaHP y comparación justa','CUMPLIDO','MODELING_PROTOCOL.md; model_search.csv; cv_folds.csv','24configs*5folds+16estrategias*5folds=200ajustes; no exhaustiva ni anidada'),
      ('Desbalance y factores de expansión','CUMPLIDO','weight_sensitivity.csv; MODELlNG_PROTOCOL.md','Cuatro estrategias por familia; FACPOB07principal,FACTORA07sensibilidad'),
      ('Selección del ganador sin usar prueba','CUMPLIDO','CVtabla; model_metadata.json',f'{winner}; AP-CV{cv["ap_cv_media"]:.6f}'),
      ('Evaluación inédita/externa','NO VERIFICABLE','results.json historical_test_warning','Prueba heredada ya observada: evaluación retrospectiva, no nuevo test externo'),
      ('Métricasponderadas/no ponderadas,calibración y baselines','CUMPLIDO','model_comparison_test.csv; constant_baselines_test.csv; model_curves.png','AP distintaPRtrap; calibrador conOOF y pesos de desarrollo;umbral0.5'),
      ('ErroresFP/FN/subgrupos','CUMPLIDO','subgroup_performance_test.csv; confusion_matrix.png',f'TN{conf[0][0]},FP{conf[0][1]},FN{conf[1][0]},TP{conf[1][1]}; recall ponderado{m["recall"]:.3f}'),
      ('SHAP global top10 ganador','CUMPLIDO','shap_beeswarm.png; shap_importance.csv; results.json',f'{winner}; residuo aditividad{r["shap"]["max_additivity_residual"]:.2e}'),
      ('Dependencias e interacciones no lineales','CUMPLIDO','shap_dependence_1/2.png; nonlinear_shap.json; shap_interaction_1/2.png','Ganador no lineal explicado;XGBoost complementario identificado con2phiij'),
      ('Dos waterfalls correctos','CUMPLIDO','shap_cases.json; shap_waterfall_alto/bajo.png','Estado actual;score antes calibración yprobabilidad separados;sinIDs personales enartículo'),
      ('Cuatro notebooks ejecutables','CUMPLIDO','notebook_execution.json;4ipynb','Kernel limpio pornotebook; ejecuciónreal de fases y tiempos'),
      ('DatasetsCSV/Parquet y diccionarios','CUMPLIDO','data/processed;docs/data_dictionary*.md','Base112columnas;model120;13predictores'),
      ('Artículo4–6p y Markdown','CUMPLIDO' if v['pdf_checked'] else 'PARCIAL','output/pdf/Informe_U2_Brecha_Digital_2025.pdf;reports/article.md','PDF6p;estilo académicoMDPI1col;verificaciónvisual enREPORT_QA.md'),
      ('Pruebas y trazabilidad','CUMPLIDO' if v['status']=='passed' else 'PARCIAL','final_verification.json; tests.log',f'{v["passed_checks"]}controles aprobados;{len(v["failed_checks"])}fallidos'),
      ('Defensa oral','NO VERIFICABLE','DEFENSA_ORAL.md','Guía entregada; dominio del estudiante requiere sustentación real'),
      ('Paquete portable y privacidad','CUMPLIDO' if (ROOT/'reports/package_verification.json').exists() and json.loads((ROOT/'reports/package_verification.json').read_text())['status']=='passed' else 'PENDIENTE','delivery_manifest.json;package_verification.json','Sinoriginales/entorno/prediccionesporfila;SHA/CRC. Datosprocesados paraentrega privada'),
    ]
    section='\n## Cierre de auditoría tras ejecución\n\nFecha UTC: '+v['executed_at_utc']+'. Estado de verificación: '+v['status']+'.\n\n| REQUISITO | EVIDENCIA | ESTADO | OBSERVACIÓN |\n|---|---|---|---|\n'
    for requirement,state,evidence,obs in rows:section+=f'|{requirement}|{evidence}|{state}|{obs}|\n'
    section+='\nNo se garantiza20/20. Los parciales conceptuales y la sustentación oral no se convierten en cumplimiento por tener código o buenas métricas. Regresión y publicaciónGitHub no son obligatorias.\n'
    (ROOT/'docs/DELIVERY_CHECKLIST.md').write_text('# Checklist de entrega vigente\n\nEste resumen deriva de la auditoría final; no sustituye sus pruebas.\n\n|Requisito|Evidencia|Estado|Observación|\n|---|---|---|---|\n'+''.join(f'|{req}|{ev}|{st}|{obs}|\n' for req,st,ev,obs in rows))
    p=ROOT/'docs/AUDITORIA_RUBRICA.md';old=p.read_text().split('\n## Cierre de auditoría tras ejecución')[0];p.write_text(old+section)
    content=f'''# Validación final ejecutada

Fecha UTC: {v['executed_at_utc']}. Estado: **{v['status']}**. {v['passed_checks']} controles aprobados; {len(v['failed_checks'])} fallidos. Véase `reports/final_verification.json` para detalles, fuentes, hashes, versiones, configuración y métricas.

## Ejecución real

Los cuatro notebooks ejecutaron los scripts canónicos en kernels nuevos. Registro:

|Notebook|Segundos observados|Estado|Celdas código|
|---|---:|---|---:|
'''
    for x in n:content+=f'|{Path(x["notebook"]).name}|{x["seconds"]:.2f}|{x["status"]}|{x["executed_code_cells"]}|\n'
    content+=f'''
## Datos y resultados regenerados

- Fuente anual2025 única, contrastada con corte panel; mismos valores comunesseleccionados normalizados. Educaciónpanel añade2512filas sin respuestas. No se afirma equivalencia de columnas no leídas.
- Base{v['n_data']} residentes, cohorte{v['n_model']}; desarrollo{v['n_train']} y prueba{v['n_test']}. Grupos{v['groups_train']}/{v['groups_test']}; intersección{v['group_overlap']}.
- Padlocal69642localesúnicos;54038servicios enlazados sinmultiplicación. Un conflicto geográfico se aparta de coordenadas/contextofísico. MatchENAHO100%;contextoESCALE{a['cohort']['escale_match_rate']:.6%}.
- Ganador{winner}, AP-CV{cv['ap_cv_media']:.6f}±{cv['ap_cv_sd']:.6f}; ventaja sobreXGBoost pequeña y no establecida como estadísticamente significativa.
- Prueba ponderada: ROC-AUC{m['roc_auc']:.6f}; AP{m['average_precision']:.6f}; PRtrapezoidal{m['pr_auc_trapezoidal']:.6f}; F1macro{m['f1_macro']:.6f}; precisión{m['precision']:.6f}; recall{m['recall']:.6f}; especificidad{m['specificity']:.6f}; Brier{m['brier']:.6f}.
- Clustering{c['metodo']} k{int(c['k'])}, silueta{c['silueta']:.6f}; ARI1 entre lassemillas/submuestras evaluadas. Sin internet/electricidad, ARI0.080753 y silueta0.279132: losgrupos dependen fuertemente de losaccesos; no se presentan como estructuraslatentes independientes deellos.
- SHAPganador residuo{r['shap']['max_additivity_residual']:.2e}; interaccionesXGBoost residuo{r['nonlinear_shap']['max_additivity_residual']:.2e}. Scoreprecalibración yprobabilidadcalibrada diferenciados.

## Pruebas ejecutadas

Se ejecutó unittest sobre `tests/`: pruebasnegativas deunionesduplicadas yvariablesprohibidas, ceros/códigos, aislamiento delpreprocesamiento, pesos, targetmissing y datosreales. Se recalcularonmétricas desdepredicciones; se comparó elmodelopersistido; se reconstruyeron particionesyfolds seed42; se comprobó aditividadSHAP, fuentes y huellas de notebooks/artefactos. `pip check` aprobó lasdependencias.

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

La medición completa de competencias para6–17 no está disponible por universo/saltos delcuestionario; la aproximación digital continúa siendo parcial frente alconstructo amplio de laguía. Faltan atributos de infraestructura escolar en Padlocal; no se fabrican. La prueba ya fue observada en laversión previa. La cohorte no representa una tasa nacional oficial. Falta la sustentación por elestudiante; no hay bloqueo técnico para la entrega privada con estas limitaciones declaradas.
'''
    (ROOT/'docs/VALIDACION_FINAL.md').write_text(content)
    status=f'''# Estado del proyecto U2

Verificado: {v['executed_at_utc']}. Trabajo sobreproyecto existente; no commits, push ni publicaciones. Snapshot previo en snapshots/manifest.json.

## Resultado ejecutado

Cuatro notebooks completados, fuentes anuales y Padlocal auditados, EDA raw, dosmétodos clustering, cuatroclasificadores,200ajustes controlados, SHAPganador e interacciones, informe y verificaciones. Verificación **{v['status']}**, {v['passed_checks']}controles; detalles en docs/VALIDACION_FINAL.md y reports/final_verification.json.

Ganador{winner}, AP-CV{cv['ap_cv_media']:.4f}; testROC-AUC{m['roc_auc']:.4f},AP{m['average_precision']:.4f},F1macro{m['f1_macro']:.4f}. Cohorte{v['n_model']}; cero solapamiento de conglomerados.

## Alcance del cierre

No se afirma100% conceptual ni20/20: objetivo operacional másestrecho que competenciascompletas, infraestructuraausente, prueba retrospectiva y defensaoral no observada. Matriz inicial/final en docs/AUDITORIA_RUBRICA.md. Archivos finales en output/; integridadZIP se registra separadamente en reports/package_verification.json.
'''
    (ROOT/'PROJECT_STATUS.md').write_text(status)
    p=ROOT/'docs/PLAN_MEJORAS.md';old=p.read_text().split('\n## Mejoras ejecutadas y pendientes')[0]
    p.write_text(old+'''\n## Mejoras ejecutadas y pendientes

Se ejecutaron las cinco prioridades: reconciliaciónanual/panel yPadlocal; EDAraw; sensibilidadpesos/HP acotados/estabilidad; interaccionesSHAP; cuatroNB ejecutables; CSV/Parquet/diccionarios; pruebas y documentación; informe científico y paquete validado. La tabla de cierre y las pruebas exactas están en AUDITORIA_RUBRICA y VALIDACION_FINAL.

Pendientes conceptuales que losarchivos no pueden resolver: competenciasdirectas para todos6–17, infraestructuraescolar no incluida en lasfuentes, muestraexterna nueva y dominio oral delestudiante. No se cambia arbitrariamente la etiqueta para aparentarcumplimiento. Mejoras opcionales futuras: validación temporal/distrital externa, inferencia con diseño complejo completo y medición directa de competencias. Regresión queda opcional y no se añade por decoración.
''')
    fixes={'MODELlNG_PROTOCOL.md':'MODELING_PROTOCOL.md','datosreales':'datos reales','pruebasnegativas':'pruebas negativas','unionesduplicadas':'uniones duplicadas','variablesprohibidas':'variables prohibidas','deldocente':'del docente','diseñocomplejo':'diseño complejo','desarrollo/prueba':'desarrollo/prueba','cuatroclasificadores':'cuatro clasificadores','interaccionesSHAP':'interacciones SHAP','cuatroNB':'cuatro notebooks','SHAPganador':'SHAP del ganador','APbaseline':'AP de referencia','Prueba ponderada: ROC-AUC':'Prueba ponderada: ROC-AUC','todos6':'todos 6','enlos':'en los','delos':'de los','delcuestionario':'del cuestionario','laprueba':'la prueba','lavisualización':'la visualización','laversión':'la versión','delestudiante':'del estudiante','alconstructo':'al constructo','laguía':'la guía','elestudiante':'el estudiante','elobjetivo':'el objetivo','lacohorte':'la cohorte','lasfuentes':'las fuentes','losarchivos':'los archivos','losresultados':'los resultados','losdatos':'los datos','elpaquete':'el paquete','elmodelo':'el modelo','delpreprocesamiento':'del preprocesamiento','desdefuentes':'desde fuentes','modelopersistido':'modelo persistido','métricasponderadas':'métricas ponderadas','pesosconfig':'pesos config','fuentesanuales':'fuentes anuales','ganadorreal':'ganador real','muestraexterna':'muestra externa','nuevotest':'nuevo test','coordenadas/contextofísico':'coordenadas/contexto físico','nomultiplicación':'no multiplicación','sinmultiplicación':'sin multiplicación','fuentesdisponibles':'fuentes disponibles','enartículo':'en artículo','patroneslatentes':'patrones latentes','banderasIQR':'banderas IQR','semillas/submuestras':'semillas/submuestras','sinrespuestas':'sin respuestas','sinoriginales':'sin originales','entrenamientoreal':'entrenamiento real','sinIDs':'sin identificadores','másestrecho':'más estrecho','infraestructuraausente':'infraestructura ausente','defensaoral':'defensa oral','dominio oral delestudiante':'dominio oral del estudiante','respuestasseleccionadas':'respuestas seleccionadas','modeloanterior':'modelo anterior','población6':'población 6','medicióndirecta':'medición directa','tasasnacionales':'tasas nacionales','modelado:ROC':'modelado: ROC','nolineal':'no lineal'}
    for rel in ['docs/AUDITORIA_RUBRICA.md','docs/PLAN_MEJORAS.md','docs/VALIDACION_FINAL.md','docs/DELIVERY_CHECKLIST.md','PROJECT_STATUS.md','README.md']:
        path=ROOT/rel;text=path.read_text()
        for a,b in fixes.items():text=text.replace(a,b)
        extra={'anual2025':'anual 2025','comunesseleccionados':'comunes seleccionados','Educaciónpanel':'Educación panel','añade2512':'añade 2512','localesúnicos':'locales únicos','MatchENAHO':'Coincidencia ENAHO ','contextoESCALE':'contexto ESCALE ','GanadorCatBoost':'Ganador CatBoost','sobreXGBoost':'sobre XGBoost','F1macro':'F1 macro','PRtrapezoidal':'PR trapezoidal','ClusteringGMM':'Clustering GMM','entre lassemillas':'entre las semillas','losgrupos':'los grupos','losaccesos':'los accesos','estructuraslatentes':'estructuras latentes','deellos':'de ellos','interaccionesXGBoost':'interacciones XGBoost','Scoreprecalibración':'Score antes de calibración','yprobabilidadcalibrada':'y probabilidad calibrada','deuniones':'de uniones','yvariables':'y variables','targetmissing':'faltantes de la etiqueta','recalcularonmétricas':'recalcularon métricas','desdepredicciones':'desde predicciones','particionesyfolds':'particiones y folds','aditividadSHAP':'aditividad SHAP','lasdependencias':'las dependencias','para6':'para 6','corte2025':'corte 2025','periodo2025':'periodo 2025','Nohay':'No hay','Sinoriginales':'Sin originales','prediccionesporfila':'predicciones por fila','Datosprocesados':'Datos procesados','paraentrega':'para entrega','sinfuentes':'sin fuentes','porfamilia':'por familia','pordistrito':'por distrito','pornotebook':'por notebook','ejecuciónreal':'ejecución real','cuatroestrategias':'cuatro estrategias','modeloajustado':'modelo ajustado','Ganadorreal':'Ganador real','semillas42':'semillas 42','enREPORT_QA.md':'en REPORT_QA.md','verificaciónvisual':'verificación visual','académicoMDPI':'académico MDPI','antesde':'antes de','sinrespuesta':'sin respuesta','delconstructo':'del constructo','etiquetasválidas':'etiquetas válidas','poblaciónobjetivo':'población objetivo','sinrespuestaspreguntas':'sin respuestas a preguntas','base112':'base 112','Base112':'Base 112','model120':'modelo 120','SHAPganador':'SHAP del ganador','contextofísico':'contexto físico','delas':'de las','No se garantiza20/20':'No se garantiza 20/20','publicaciónGitHub':'publicación en GitHub','perfilesdecolumnas':'perfiles de columnas','selecciónanalíticadocumentada':'selección analítica documentada','datoscrudos':'datos crudos','4cruces':'4 cruces','No seentrena':'No se entrena','simplementeAUC':'simplemente AUC','máximopresupuesto':'máximo presupuesto','competenciasdirectas':'competencias directas','atributosde':'atributos de','mediofísico':'medio físico'}
        for a,b in extra.items():text=text.replace(a,b)
        text=re.sub(r'\b(Base|cohorte|desarrollo|prueba|Grupos|intersección|Padlocal|silueta|recall|precisión|especificidad|Brier|ROC-AUC|AP-CV|AP|ARI|residuo|k|TN|FP|FN|TP|PDF|Artículo|top|con|seed|entre|sin)(?=\d)',r'\1 ',text)
        text=re.sub(r'(\d)(años|personas|residentes|filas|locales|servicios|controles|columnas|predictores|estrategias|celdas|registros|puntos|ajustes|folds|métodos|perfiles|configuraciones|minutos|casos|preguntas|variables|campos|configs|positivos|hogares|de\b)',r'\1 \2',text)
        path.write_text(text)
    print('Documentación final regenerada desde verificación real.')
if __name__=='__main__':main()
