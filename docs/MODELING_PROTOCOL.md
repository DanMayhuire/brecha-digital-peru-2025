# Protocolo de modelado y evaluación

## Población y particiones

La cohorte se define en `TARGET_DECISION.md`. GroupShuffleSplit, semilla 42 y proporción de prueba 0.2, separa CONGLOME: 13 105 personas en desarrollo y 3 439 en prueba, sin solapamiento de conglomerados. Cinco folds GroupKFold sobre desarrollo sustentan ajuste y selección.

## Preprocesamiento

Las variables numéricas utilizan imputación por mediana y estandarización; las categorías, imputación por moda y one-hot con manejo de categorías no vistas. Los parámetros se ajustan dentro del entrenamiento de cada fold. Las transformaciones deterministas log(1+x) de ingreso y gasto per cápita no estiman parámetros de población.

## Comparación de modelos

Se comparan regresión logística, Random Forest, XGBoost y CatBoost. Por familia se evalúan entrenamiento uniforme, ponderación poblacional, balance de clase y combinación de ambos. Los pesos se calculan exclusivamente con el entrenamiento de cada fold. La estrategia se selecciona por Average Precision ponderada de validación; después se exploran seis configuraciones de hiperparámetros por familia. El presupuesto es 200 ajustes: 16 combinaciones de familia-peso y 24 configuraciones, cada una con cinco folds.

La selección utiliza la mayor AP media en desarrollo. Las diferencias entre modelos no se consideran automáticamente estadísticamente significativas. La búsqueda es secuencial, no exhaustiva ni anidada.

## Calibración y métricas

El calibrador sigmoide se ajusta sobre el logit de las predicciones OOF de desarrollo, con factores de expansión individuales. El umbral de clasificación es 0.5. Se informan ROC-AUC, Average Precision, PR-AUC trapezoidal, F1 macro, precisión, recall, especificidad y Brier, con y sin ponderación. El bootstrap por conglomerados estima intervalos descriptivos, sin reproducir toda la estratificación de ENAHO.

## Clustering y SHAP

Se comparan K-Means y GMM con k=2,…,6 sobre desarrollo imputado y estandarizado. La regla selecciona máxima silueta entre soluciones con grupos de al menos 5%; Davies-Bouldin sirve de desempate. Se evalúan estabilidad entre semillas/submuestras y ablación de electricidad e internet del hogar. La etiqueta se utiliza sólo para caracterizar perfiles después del ajuste.

TreeSHAP explica el CatBoost guardado en log-odds previos a calibrar. Las dummies se agrupan sumando contribuciones. Las interacciones de XGBoost constituyen un análisis complementario; los pares se seleccionan exploratoriamente por contribución absoluta. Las explicaciones no identifican efectos causales.

## Alcance

La evaluación es retrospectiva sobre una partición de prueba previamente examinada; requiere validación externa independiente. La prueba no interviene en la elección de hiperparámetros, estrategia de pesos, calibración ni umbral.
