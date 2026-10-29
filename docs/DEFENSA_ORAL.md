# Guía de defensa oral: IA U2, brecha digital ENAHO-ESCALE 2025

Esta guía usa la ejecución vigente de `reports/results.json`, registrada el 29 de octubre de 2026 a las 04:23:42 UTC (28 de octubre, 23:23:42 en Lima), firma `1a8d2e8c341eef89399f6b813f2ae3d358dd9cd042566f5708f13d714678768b`. Los resultados pueden regenerarse; si se cambia el análisis, hay que volver a contrastar esta guía. No confundirla con la versión anterior cuyo ganador era logística.

## Guion de aproximadamente cinco minutos

**0:00-0:45. Problema y alcance.**

«Estudiamos el no uso de internet durante el mes anterior entre estudiantes residentes de 6 a 17 años, matriculados y asistentes a primaria o secundaria, excluyendo CEBA declarada. La respuesta es P314A: dos significa no usó internet y constituye nuestra clase positiva. Es una dimensión observable de la brecha digital; no equivale a medir todas las competencias. Verificamos que ENAHO sí pregunta actividades informáticas, pero solo desde los 14 años y con saltos según el uso de dispositivos. Por eso no inventamos falta de habilidades en los menores ni en los faltantes».

**0:45-1:35. Fuentes e integración.**

«Usamos los cuatro módulos anuales de 2025, encontrados en Descargas. Antes comparamos sus llaves y variables analíticas con el corte 2025 del panel docente. Las respuestas compartidas coinciden tras normalizar coma decimal y códigos de falta de información. El panel educativo tiene 2,512 filas adicionales sin respuesta en las preguntas seleccionadas. Unimos hogares, personas, educación y Sumaria preservando códigos como texto y validando cardinalidad. La base integrada contiene 23,345 residentes; el modelo utiliza 16,544. Integramos realmente Padrón y Padlocal: todos los 54,038 servicios elegibles encontraron local y detectamos un conflicto de distrito. ESCALE empareja el 98.179% de la cohorte. Es contexto territorial por residencia, no la escuela identificada de cada estudiante».

**1:35-2:15. Validación y prevención de fuga.**

«Reservamos 808 conglomerados con 3,439 personas para prueba. Desarrollo contiene 3,232 conglomerados y 13,105 personas; no comparten conglomerados. En desarrollo usamos los mismos cinco pliegues GroupKFold para todos los modelos. Imputación, escalado y codificación se ajustan solo en el entrenamiento de cada pliegue. Excluimos la respuesta y las ramas TIC cuyos valores o faltantes podrían revelarla. La prueba ya había sido observada en la versión previa: esta es una reevaluación retrospectiva, no una validación externa inédita».

**2:15-2:55. Perfiles.**

«Comparamos K-Means y GMM para dos a seis grupos. La regla seleccionó GMM con dos grupos y silueta 0.454. Los perfiles son descriptivos: el menor grupo tiene mayor ruralidad y menos acceso a servicios. La estabilidad fue perfecta en las perturbaciones ensayadas, pero al quitar electricidad e internet el acuerdo cayó a ARI 0.081 y la silueta a 0.279. Esto revela que el acceso básico domina los grupos; no presentamos los perfiles como descubrimientos independientes de esas variables ni como categorías naturales».

**2:55-3:50. Clasificación y errores.**

«Comparamos logística, Random Forest, XGBoost y CatBoost. Evaluamos cuatro estrategias de pesos y seis configuraciones por familia, con un presupuesto de 200 ajustes. CatBoost obtuvo la mayor AP media de validación, 0.5935, muy cerca de XGBoost, 0.5931; no afirmamos superioridad estadística. En prueba, CatBoost calibrado logró ROC-AUC 0.8204, AP 0.6013 y F1 macro 0.6933. Al umbral fijo de 0.5 su precisión ponderada fue 69.1%, pero el recall fue 38.1%. Hay 464 falsos negativos y 185 falsos positivos en conteos. El buen ordenamiento no implica detectar a todos los no usuarios. La calibración se aprendió con predicciones fuera de pliegue de desarrollo y redujo el Brier en prueba de 0.1616 a 0.1273».

**3:50-4:35. Explicación.**

«Explicamos al ganador real con SHAP: edad, gasto per cápita y proporción de servicios públicos tienen las mayores contribuciones absolutas medias. SHAP explica el score antes de calibración; la probabilidad calibrada se muestra aparte. Los casos extremos correctos tienen probabilidades 97.86% y 0.43%. Además analizamos interacciones del XGBoost competitivo, identificado como complemento, con TreeSHAP. Las interacciones describen cómo opera el modelo y no prueban que cambiar una variable produzca un efecto educativo».

**4:35-5:00. Recomendaciones y límites.**

«Los resultados justifican estudiar conjuntamente acceso del hogar, edad y contexto socioeconómico; tener conexión no garantiza uso ni competencia. Se necesita diagnóstico pedagógico directo para diseñar apoyo. El modelo requiere revisar umbral, costos y validación adicional antes de utilizarse para priorización real. La cohorte excluye a quienes no asisten y los resultados ponderados no son tasas nacionales oficiales. La medición completa de exclusión digital efectiva queda como limitación explícita».

## Cifras que conviene dominar

| Resultado | Valor vigente | Cómo explicarlo |
|---|---:|---|
| Cohorte integrada / modelada | 23,345 / 16,544 | La primera comprende residentes habituales de 6-17; la segunda exige matrícula, asistencia y etiqueta/peso válidos. |
| No usuarios / usuarios en modelado | 4,294 / 12,250 | Conteos muestrales; no población expandida. |
| No uso muestral / ponderado | 25.955% / 22.671% | Son estimandos distintos; el peso cambia la contribución de cada persona. |
| Desarrollo / prueba | 13,105 / 3,439 | Personas; no confundir con conglomerados. |
| Conglomerados desarrollo / prueba / comunes | 3,232 / 808 / 0 | Separación exigida por la guía. |
| Ganador | CatBoost, profundidad 3 y L2=3 | 300 iteraciones y learning rate 0.05; preprocesamiento one-hot común a todos los modelos. |
| AP media CV CatBoost / XGBoost | 0.5935 / 0.5931 | Diferencia mínima; selección por regla, sin prueba de superioridad. |
| ROC-AUC / AP / PR trapezoidal en prueba | 0.8204 / 0.6013 / 0.6007 | Métricas ponderadas FACPOB07. AP y área trapezoidal no son sinónimos. |
| F1 macro / precisión / recall | 0.6933 / 0.6909 / 0.3812 | Umbral fijo0.5; recall es sensibilidad de la clase no uso. |
| Especificidad ponderada | 0.9519 | Fracción ponderada de usuarios correctamente identificados como usuarios. |
| Brier sin calibrar / calibrado | 0.1616 / 0.1273 | Menor es mejor; mide error probabilístico, no solo clasificación. |
| Matriz de confusión de conteos | TN 2385, FP 185, FN 464, TP 405 | Estos números no se usan directamente para recalcular las métricas ponderadas. |
| Recall muestral / ponderado | 46.605% / 38.118% | La diferencia surge de los pesos; ambos se guardan. |
| Recall rural / urbano ponderado | 64.113% / 22.092% | Diferencia descriptiva al mismo umbral; no demuestra causa ni equidad. |
| Clustering | GMM, k=2, silueta 0.4539 | Silueta sobre2,500 observaciones, selección y semilla documentadas. |
| Davies-Bouldin / Calinski-Harabasz | 1.4524 / 3037.70 | DB menor y CH mayor orientan comparación dentro del mismo espacio. |
| ARI de estabilidad ensayada | 1.0 | Semillas42-44 y ajuste sobre 80%; no garantiza estabilidad fuera de esta fuente. |
| Ablación sin acceso | silueta 0.2791, ARI0.0808 | Diagnostica dependencia de electricidad e internet; no se reeligió usando la etiqueta. |
| SHAP global | 601 casos | Muestra aleatoria de prueba de 600 más extremos correctos, con un caso ya incluido. |
| Error máximo de aditividad ganador | 6.22×10^-15 | Base más contribuciones reproduce el score explicado. |
| SHAP complementario XGBoost | 180 casos, semilla 42 | Error aditivo máximo2.38×10^-6, en log-odds antes de calibrar. |

El intervalo bootstrap por conglomerados de ROC-AUC del ganador es [0.7918,0.8455], con 300 réplicas. Es aproximado y no reproduce todo el diseño de encuesta; no se interpreta como prueba de superioridad entre modelos.

## Preguntas difíciles y respuestas defendibles

**¿Por qué no afirma “exclusión digital efectiva” completa?** Porque no uso de internet y competencia son conceptos distintos. En nuestra cohorte hay11,503 estudiantes de 6-13, fuera del bloque P316B/C. Entre los 5,041 de 14-17, solo 2,097 tienen las nueve actividades observadas; 2,944 no usaron dispositivo en los tres meses previos y saltan esas preguntas. De los 2,097 observados, 77 no reportaron ninguna de las nueve actividades y ninguno de esos 77 coincide con no uso de internet. Rellenar los saltos como falta de competencias fabricaría el constructo. Se defiende una operacionalización parcial y transparente.

**¿Qué falta para cerrar ese constructo?** Un instrumento comparable de competencias para todo 6-17, o una nueva pregunta de investigación con población/medición delimitadas y validación propia. Aceptar NA como incapacidad no lo resuelve. No hace falta inventar un archivo escolar para aparentar cumplimiento.

**¿Por qué no eligió rezago para ajustarse literalmente a la guía?** Es una alternativa legítima. Sin embargo, la edad al entrevistar difiere de la edad al 31 de marzo; además los umbrales de uno y dos años producen resultados distintos. La etiqueta actual tiene una pregunta directa para6-17 y se conservó antes de la nueva búsqueda, sin elegir por desempeño. El módulo400 incluye preguntas de nacimiento, aunque no se utiliza en este objetivo; no se afirma que ENAHO carezca de fechas en todos sus módulos.

**¿Por qué usa anual si el docente entregó panel?** Porque se verificaron ambas fuentes y se encontraron los ZIP anuales exigidos. Coinciden llaves y respuestas analíticas compartidas tras normalización; educación panel conserva2,512 filas adicionales sin respuestas seleccionadas. Se eligió una fuente única, sin completar con otros años ni reemplazar por el nombre del archivo. La comparación no afirma identidad de todas las columnas originales.

**¿Qué contiene realmente Padlocal?** Valida locales y geografía; tiene 69,642 locales con CODLOCAL único. El archivo recibido no contiene computadoras, agua, electricidad, internet, altitud ni coordenadas. Estas últimas provienen de Padrón y se agregan una vez por local validado. No se inventó equipamiento. Un conflicto de distrito entre archivos se excluyó del contexto físico, conservando los totales del servicio en su geografía de Padrón.

**¿Por qué los factores de expansión no son predictores?** Describen la contribución muestral/poblacional, no una característica educativa que se quiera usar para clasificar. FACPOB07 es de persona; FACTOR07 de Sumaria es de hogar y se repite al unir estudiantes; FACTORA07 se utiliza para sensibilidad. Sumarlos por persona no estima automáticamente hogares.

**¿Por qué CatBoost se entrenó con pesos de clase y no con población?** Se evaluaron las cuatro estrategias solo en desarrollo. Con la configuración representativa, AP media fue 0.5935 con clase,0.5913 uniforme,0.5823 población y 0.5822 combinado. La elección no elimina los factores: FACPOB07 se usa en selección, evaluación, calibración y perfiles, y FACTORA07 en sensibilidad. No se multiplicaron pesos automáticamente para aparentar rigor.

**¿Cómo funciona exactamente GroupKFold?** Se divide desarrollo en cinco conjuntos de conglomerados. En cada vuelta se ajusta con cuatro y se predice el quinto. Ningún conglomerado aparece a ambos lados de una vuelta. Las mismas asignaciones se usan en todos los modelos y configuraciones; se guardan en `cv_assignments.csv`. Todo el preprocesamiento se vuelve a ajustar dentro del fold. Los808 conglomerados de prueba quedan fuera de esas cinco vueltas.

**¿Esto garantiza distritos nuevos?** No. Dos conglomerados de un mismo distrito pueden quedar en particiones diferentes y compartir contexto agregado. La evaluación es de conglomerados no vistos. Para transporte distrital se necesitaría otra partición por distrito y otra pregunta de validación.

**¿Por qué ahora ganó CatBoost si antes era logística?** La ampliación fijó un protocolo antes de reentrenar: estrategias de pesos y seis configuraciones por familia, con un presupuesto común y pliegues compartidos. Ganó CatBoost por AP-CV, no por observar la prueba. La diferencia con XGBoost es pequeña; no se presenta como una superioridad estadísticamente demostrada ni se manipula al ganador para obtener gráficos.

**¿La prueba es completamente independiente de la historia del proyecto?** No. Se observó en la versión anterior. La nueva selección usa solo desarrollo, pero la comparación final es retrospectiva. Esta limitación no desaparece al mantener semilla 42. Una muestra temporal o externa nueva aportaría una validación posterior más fuerte.

**¿Por qué calibrar?** Los pesos de clase favorecen errores de una clase y pueden distorsionar la probabilidad bruta. El calibrador sigmoide aprende de predicciones OOF de desarrollo y usa pesos poblacionales, sin balance artificial de clases. Después se aplica a prueba. La reducción observada de Brier es un resultado, no una garantía para otro año.

**¿Por qué no bajar el umbral si hay tantos falsos negativos?** Sería razonable si se conoce el costo relativo y capacidad de atención. No lo optimizamos con prueba. Se mantiene0.5 para una comparación transparente; un umbral operativo debe seleccionarse exclusivamente en validación de desarrollo y evaluarse en datos no usados para decidirlo. No se promete detección universal.

**¿Qué diferencia hay entre AP y PR-AUC?** AP agrega precisión en los incrementos de recall, con interpolación escalonada; el área trapezoidal une puntos con segmentos. Con empates pueden diferir mucho. Un predictor constante tiene aquí AP 0.220, pero PR trapezoidal0.610 por la curva degenerada y su interpolación; ese0.610 no significa que ordene mejor que CatBoost. Por eso la selección usa AP y se distingue de PR-AUC.

**¿Cómo explicar que recall sea38.1% y405/(405+464) sea46.6%?** El primer resultado pondera por FACPOB07; el segundo usa personas de la muestra con el mismo peso. No mezclar conteos de la matriz con métricas expandidas. Las dos versiones están reportadas.

**¿Los grupos “descubren” algo que no se podía ver en internet/electricidad?** La ablación revela fuerte dependencia de acceso. El grupo menor tiene ruralidad ponderada58.9%, electricidad40.3%, internet 48.6% y gasto per cápita S/474.03; el mayor, ruralidad18.3%, ambos accesos100% y gastoS/704.69. Son perfiles útiles para descripción, pero no tipologías socioeducativas independientes de las variables que los construyen. El no uso ponderado 47.7%/21.1% se calcula después; no eligió los grupos.

**¿Qué demuestra ARI=1?** Que las particiones coinciden en los ensayos, aun si los números de grupo se permutan. Aquí se perturbaron semillas y se ajustó el modelo con 80% de desarrollo, manteniendo el espacio transformado. No es una prueba de validez sustantiva: una división dominada por variables binarias también puede ser muy estable. ARI0.0808 tras la ablación muestra que al retirar acceso cambia casi toda la partición.

**¿PCA prueba que el clustering es correcto?** No. Las dos componentes muestran aproximadamente 59.0% de la varianza del espacio transformado; la proyección permite mirar, pero las métricas se calculan en el espacio usado para agrupar. Separación visual y validez sustantiva son preguntas distintas.

**¿Qué explica SHAP?** La diferencia del score respecto de una referencia del modelo. Se cumple f(x)=base+ΣSHAP. En CatBoost las unidades son log-odds antes de calibrar; la sigmoide calibrada produce la probabilidad final. Una contribución positiva favorece la clase no uso dentro del modelo, no demuestra que esa variable cause el no uso.

**¿Por qué otro modelo para interacciones si CatBoost ganó?** La explicación global y local corresponde al CatBoost real. XGBoost es un complemento competitivo para calcular explícitamente TreeSHAP Interaction Values. Entre pares candidatos, altitud-proporción pública y altitud-ratio alumno/docente tuvieron mayores contribuciones absolutas medias del par,0.0387 y 0.0282 log-odds. El par aporta2φij; son hallazgos exploratorios del árbol ajustado, sin significancia ni causalidad afirmadas.

**¿Los casos SHAP son predicciones futuras?** No. Son clasificaciones del estado reportado en el mes previo. El caso alto, con y=1, tiene p calibrada 0.9786; edad7, falta de internet y electricidad y gasto bajo aportan positivamente en ese ejemplo. El caso bajo, con y=0, tiene p=0.0043; edad17 y mayor gasto reducen el score. No se exponen llaves ni se atribuye a un estudiante real identificable una intervención.

**¿Qué recomendación sostienen realmente los resultados?** Examinar las barreras de acceso junto con edad, recursos del hogar y apoyo pedagógico; el grupo con conexión también contiene no usuarios. El estudio permite plantear diagnóstico e hipótesis de apoyo, no calcular el efecto causal de entregar internet ni seleccionar beneficiarios con certeza. Las diferencias por ruralidad/lengua deben revisarse con sus tamaños muestrales, prevalencias y errores.

## Recorrido breve del código durante la sustentación

1. `src/source_audit.py` y `src/build_data.py`: demostrar lectura distinta anual/panel, columnas string, códigos de missing, unicidad y `validate='many_to_one'`. Mostrar `source_comparison.json` y `escale_join_coverage.csv`.
2. `src/audit_target_measurement.py`: mostrar por qué los faltantes P316C son estructurales y por qué el target es no uso.
3. `src/run_analysis.py`, `prepare_targets`, `preprocess` y `assert_features`: definir etiqueta, listas explícitas y protección frente a respuestas/proxies.
4. `cluster_analysis`: métodos/k, métricas, perfiles, semillas, submuestra y ablación sin acceso.
5. `models_config`, `fitweights`, `evaluate_models`: mostrar cuatro estrategias, seis configuraciones por familia, mismos cinco folds y elección por AP-CV; después calibrador OOF y prueba.
6. `explanations` y análisis no lineal complementario: identificar el modelo de cada figura y comprobar aditividad.
7. Abrir los cuatro notebooks en orden: ejecutan sus etapas mediante los scripts canónicos. La ejecución controlada registrada aprobó 4/4 notebooks. Los tiempos observados fueron31.26 s,5.96 s,81.30 s y6.25 s; son observaciones de este equipo, no una promesa de tiempo en otro Mac.
8. Para las comprobaciones de cierre, abrir `reports/final_verification.json` una vez generado por el verificador final. No afirmar que se ejecutó una prueba únicamente porque aparezca descrita en la documentación.

## Archivos para mostrar si piden evidencia

- `reports/tables/source_comparison.json`: equivalencia acotada de fuentes.
- `reports/tables/data_audit.json` y `escale_join_coverage.csv`: llaves, exclusiones, cobertura y Padlocal.
- `reports/tables/raw_eda_variables.csv`: EDA anterior a cruces y transformación ML.
- `reports/tables/target_measurement_audit.json`: población y saltos de competencias.
- `reports/tables/partitions.csv` y `cv_assignments.csv`: separación por grupos y pliegues.
- `reports/tables/clustering_comparison.csv`, `clustering_stability.csv`, `clustering_access_ablation.json`: selección y límites de los grupos.
- `reports/tables/weight_sensitivity.csv`, `model_search.csv`, `model_comparison_cv.csv` y `model_comparison_test.csv`: comparación íntegra.
- `reports/tables/shap_cases.json`, `shap_importance.csv`, `nonlinear_shap.json`: explicación del ganador y del complemento.
- `reports/notebook_execution.json`: ejecución real de las cuatro etapas desde Jupyter.

No presentar una nota garantizada, una tasa nacional oficial, una habilidad no observada como cero ni una asociación SHAP como efecto causal.
