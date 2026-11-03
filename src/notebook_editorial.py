"""Academic Markdown for the notebook presentation; computational cells are unchanged."""
PHASES={
'01':[
'# Ingeniería de datos y análisis exploratorio\n\nSe integran los módulos de vivienda, personas, educación y Sumaria de ENAHO con el Padrón de Servicios Educativos y el Padrón de Locales Escolares de ESCALE. El análisis utiliza el corte de 2025 de los archivos multianuales y conserva la trazabilidad de las fuentes y de las transformaciones.',
'## Fuentes de información y unidad de análisis\n\nLa unidad de análisis es la persona residente habitual de 6 a 17 años. Los originales de ENAHO se conservan sin modificaciones y se seleccionan las variables correspondientes a 2025. Los registros se integran mediante claves compuestas de hogar y persona; ESCALE aporta indicadores del distrito y área de residencia.',
'## Calidad de los datos y delimitación de la población\n\nSe examinan valores faltantes, códigos de respuesta, unicidad de claves y cardinalidad de los cruces. Los saltos del cuestionario se distinguen de las respuestas negativas. Los indicadores escolares describen el contexto territorial y no identifican la institución a la que asiste cada estudiante.',
'## Síntesis de la integración\n\nLa base integrada contiene 23 345 residentes de 6 a 17 años; la cohorte de modelado comprende 16 544 estudiantes matriculados y asistentes a primaria o secundaria. El indicador de no uso de internet se define a partir de P314A y no constituye una medición directa de competencias digitales. La imputación y el escalado se reservan al entrenamiento dentro de cada partición de validación.'
],
'02':[
'# Segmentación y perfiles socioeducativos\n\nSe comparan K-Means y modelos de mezclas gaussianas (GMM) para identificar perfiles de condiciones socioeconómicas y acceso tecnológico. El número de grupos se evalúa entre k = 2 y k = 6. La etiqueta supervisada y las preguntas que la revelan se excluyen de la construcción y selección de los grupos.',
'## Preparación y comparación de los agrupamientos\n\nLas variables se imputan por mediana y se estandarizan utilizando únicamente el conjunto de desarrollo. K-Means utiliza distancia euclidiana en ese espacio. La selección considera silueta, Davies–Bouldin, Calinski–Harabasz y tamaño de los grupos. La silueta se estima sobre una muestra de hasta 2 500 observaciones, con semilla 42; las otras dos métricas se calculan sobre el conjunto de desarrollo completo. Se exige una proporción mínima del 5 % por grupo.',
'## Estabilidad y sensibilidad a los indicadores de acceso\n\nLa estabilidad se evalúa mediante el índice de Rand ajustado (ARI) entre semillas y submuestras del 80 %. La ablación de electricidad e internet permite examinar cuánto depende la segmentación de esos indicadores. La proyección PCA es una representación visual y no sustituye a las métricas de calidad.',
'## Interpretación de los perfiles\n\nLos perfiles se caracterizan mediante condiciones del hogar, ruralidad, pobreza, lengua materna y contexto escolar. Sus medias y proporciones descriptivas se ponderan por el factor individual; el ajuste geométrico no utiliza estos pesos. La estabilidad observada coexiste con una fuerte dependencia de los indicadores de acceso. Las diferencias de no uso de internet se describen después del agrupamiento y no se interpretan como relaciones causales.'
],
'03':[
'# Clasificación del no uso de internet\n\nSe comparan regresión logística, Random Forest, XGBoost y CatBoost mediante cinco particiones GroupKFold por conglomerado. La búsqueda contempla cuatro estrategias de ponderación y seis configuraciones de hiperparámetros por familia, con un presupuesto máximo de 200 ajustes. El criterio de selección es la Average Precision (AP) media ponderada de validación.',
'## Diseño de validación y selección de modelos\n\nEl conjunto de prueba se separa por CONGLOME y no participa en la elección de hiperparámetros, estrategia de ponderación ni modelo. Todas las familias utilizan las mismas particiones de desarrollo. La evaluación conserva una partición examinada en una versión previa del estudio; por ello se interpreta como revisión retrospectiva y no como validación externa inédita.',
'## Preprocesamiento, ponderación y calibración\n\nLa imputación, el escalado y la codificación categórica se ajustan exclusivamente con el entrenamiento de cada partición. Los pesos de clase se calculan dentro de ella. La calibración sigmoide utiliza predicciones fuera de partición (OOF) y factores de expansión de desarrollo. El umbral de clasificación se fija en 0.5.',
'## Evaluación y alcance de los resultados\n\nLa interpretación conjunta de discriminación, calibración y errores permite valorar el alcance del clasificador. AP y el área trapezoidal de la curva precisión–recall son medidas distintas. El recall al umbral 0.5 muestra que una proporción importante de los casos positivos no se identifica. Los factores de expansión no reproducen por sí solos todo el diseño complejo de la encuesta; las diferencias entre modelos no se consideran automáticamente significativas.'
],
'04':[
'# Explicabilidad del modelo y análisis de interacciones\n\nLos valores SHAP permiten estudiar las contribuciones predictivas del modelo seleccionado. Se presentan importancia global, gráficos de dependencia y dos casos individuales correctamente clasificados. El análisis se complementa con interacciones TreeSHAP de XGBoost, identificadas como resultados de ese modelo.',
'## Contribuciones globales y casos individuales\n\nSHAP explica el score anterior a la calibración. Su referencia, unidades y muestra de explicación se documentan junto a los resultados. Las contribuciones se diferencian de la probabilidad calibrada y de cualquier efecto causal. Los casos individuales representan extremos correctamente clasificados y se presentan sin identificadores personales.',
'## Interacciones predictivas del modelo de árboles\n\nLos valores de interacción TreeSHAP cuantifican la contribución conjunta de pares de variables al score; el aporte del par se expresa como 2φᵢⱼ. Los pares se seleccionan de forma exploratoria por su contribución absoluta media. El color de un gráfico de dependencia, por sí solo, no demuestra una interacción ni su significación estadística.',
'## Interpretación y limitaciones de la explicabilidad\n\nLas contribuciones permiten describir cómo utiliza el modelo las condiciones individuales, del hogar y del contexto territorial. No identifican mecanismos causales ni diagnostican habilidades digitales. Los casos extremos ilustran el comportamiento del clasificador y no representan a toda la población de estudio. Las recomendaciones requieren contraste y validación en campo.'
]}

def edit_phase(nb,name):
    phase=name[:2];texts=PHASES[phase];cells=[c for c in nb['cells'] if c['cell_type']=='markdown']
    if len(cells)!=len(texts):raise ValueError('Unexpected Markdown structure: '+name)
    for cell,text in zip(cells,texts):cell['source']=text
    return nb

def cover(results):
    best=next(x for x in results['supervised']['test'] if x['seleccionado_cv'])
    return ('# Brecha digital y no uso de internet en estudiantes de educación básica del Perú\n\n'
      '**Integración de ENAHO y ESCALE, corte 2025**\n\n'
      '**Curso:** Inteligencia Artificial  \n**Institución:** Universidad Peruana Unión\n\n'
      '## Resumen\n\n'
      'Se analizan las condiciones socioeconómicas, el acceso tecnológico y el contexto educativo territorial de '+f"{results['n_eligible']:,}".replace(',',' ')+' estudiantes de 6 a 17 años matriculados y asistentes a primaria o secundaria. Se integran el corte de 2025 de ENAHO PANEL 2021–2025 y los padrones escolares de ESCALE. El estudio combina segmentación socioeducativa, clasificación del no uso de internet durante el mes anterior y explicabilidad mediante SHAP.\n\n'
      f"{results['supervised']['winner']} obtuvo la mayor AP media de validación. En prueba, las métricas ponderadas fueron ROC-AUC = {best['roc_auc']:.4f}, AP = {best['average_precision']:.4f} y F1 macro = {best['f1_macro']:.4f}. Estos resultados describen la cohorte analítica y no constituyen estimaciones oficiales nacionales.\n\n"
      '## Objetivo\n\nIdentificar perfiles socioeducativos y evaluar modelos de clasificación del no uso reciente de internet, considerando condiciones individuales, del hogar y del entorno escolar territorial.\n\n'
      '## Organización del análisis\n\n1. Integración de fuentes y análisis exploratorio.\n2. Segmentación y caracterización de perfiles.\n3. Modelado supervisado y evaluación.\n4. Explicabilidad global, local y de interacciones.')

LIMITATIONS='''## Discusión y limitaciones del estudio

El indicador analizado mide no uso de internet durante el mes anterior; no acredita ausencia de competencias digitales. La cohorte excluye a personas no matriculadas o no asistentes. ESCALE aporta contexto de residencia y no una escuela identificada para cada estudiante.

La evaluación reutiliza una partición de prueba examinada previamente y no sustituye una validación externa. La separación por conglomerados reduce la dependencia entre entrenamiento y prueba, pero no garantiza generalización a distritos o regiones nuevos. La ponderación y el bootstrap por conglomerado no incorporan íntegramente el diseño complejo de ENAHO. El carácter transversal del estudio impide atribuir causalidad a las asociaciones predictivas.

Las recomendaciones educativas se limitan a orientar hipótesis de apoyo y verificación de necesidades. Su aplicación requiere validación adicional y evaluación en campo.
'''
