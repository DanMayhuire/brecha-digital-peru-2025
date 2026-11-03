# Protocolo de revisión fijado antes del nuevo entrenamiento

Se conserva la pregunta operacional, los13predictores, las cuatro familias, el split por conglomerado con semilla42 y los mismos5folds. La decisión final sobre las fuentes y el objetivo precede a la ejecución supervisada.

## Búsqueda acotada en desarrollo

1. Por familia se compara una configuración representativa bajo cuatro estrategias: uniforme, expansión poblacional, balance de clases y expansión con balance. La normalización y el balance se calculan en el subconjunto de ajuste de cada fold. Las cuatro estrategias se comparan por AP media de los cinco folds, ponderada por FACPOB07.
2. Se fija la estrategia de mayor AP para cada familia; se prueban seis configuraciones de hiperparámetros por familia sobre los mismos folds. El código `models_config` enumera exactamente24configuraciones.
3. Se elige la familia/configuración con mayor AP-CV media. El máximo presupuesto son200ajustes:80de sensibilidad y120de hiperparámetros. No es optimización conjunta ni exhaustiva. El sesgo de selección de CV permanece y se declara.
4. Las probabilidades OOF de la configuración elegida por familia entrenan un calibrador sigmoide con pesos poblacionales. El calibrador no ve prueba. El umbral principal permanece0.5; no se optimiza en prueba.
5. Se ajusta cada modelo con desarrollo y se evalúa en prueba. Se guardan todos los resultados, sin sustituir al ganador por una métrica de prueba. Se añaden predictores constantes (mayoría y prevalencia de desarrollo) y métricas ponderadas/no ponderadas. AP y áreaPRtrapezoidal son distintos.

Rangos: logística C0.01–3 contempla regularización fuerte/moderada; RF profundidad8–ilimitada, hojas3–12 y fracción de características; XGBoost profundidades2–5, peso mínimo de hoja y penalización; CatBoost profundidades3–6 y L2. Árboles limitados a180/260/300 y4hilos para CPU. No se aumenta el presupuesto según el resultado de prueba.

## Clustering y explicación

Se conserva KMeans/GMM k2–6 con preprocesamiento en desarrollo, mínima masa5%, máxima silueta y DB como desempate. Se agrega estabilidad ARI por semillas42–44 y submuestras80%, además de ablación sin electricidad/internet al mismo método/k. Los perfiles se describen después de formar grupos; la etiqueta no determina la selección.

SHAP explica el ganador real antes de calibrar. Se añade XGBoost como análisis no lineal explícito con interaccionesTreeSHAP en hasta180casos de prueba, semilla42; se agrupan dummies mediante suma de contribuciones y bloques de interacción. Se escogen exploratoriamente los dos pares con mayor contribución absoluta entre variables territoriales, lengua, acceso y condiciones económicas. No se atribuyen causalidad ni significación estadística a estos pares.

## Límite de la evaluación

La prueba se observó en la versión anterior. La nueva selección no utiliza sus valores, pero no puede considerarse una evaluación inédita ni externa. Se mantiene la partición para comparar versiones y se declara el carácter retrospectivo de esta auditoría. Una nueva fuente temporal o muestra externa sería necesaria para una validación independiente posterior.
