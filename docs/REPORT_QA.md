# Revisión del informe científico

## Revisión inicial de la entrega anterior

Se releyeron las siete páginas de la guía, el generador, el artículo editable y los resultados anteriores antes de modificar el informe. Se conserva el estilo sobrio a una columna, válido como artículo técnico de inspiración MDPI; la consigna pide IEEE o MDPI y no impone dos columnas.

Problemas corregidos en el generador:

- Conteos de personas, perfiles y diagramas dependían de cifras literales.
- La prosa suponía que el ganador siempre sería logística y que los casos individuales tendrían edades de siete y diecisiete años.
- El texto de hiperparámetros suponía sólo dos configuraciones por familia.
- El esquema anterior describía Padrón, pero no el enlace real con Padlocal.
- Faltaban estabilidad del clustering, ablación de acceso y comparación de estrategias de peso.
- Los gráficos de dependencia de un ganador lineal no permitían afirmar interacciones no lineales.
- El Markdown editable conservaba etiquetas HTML del motor PDF.

## Cambios de alcance del artículo revisado

El documento mantendrá seis páginas y derivará cifras y ganador de los resultados guardados. Se incorporan EDA de módulos crudos, contraste anual/panel de los campos seleccionados, Padlocal, estabilidad y ablación de agrupamientos, sensibilidad de entrenamiento a pesos, mayor búsqueda de hiperparámetros e interacciones TreeSHAP de un modelo no lineal identificado explícitamente.

La fuente canónica revisada son los CSV anuales oficiales. La comparación con el panel se limita a llaves y variables analíticas seleccionadas, después de normalizar faltantes y coma decimal; no afirma identidad de los CSV completos. Padlocal valida locales y geografía y carece de campos de coordenadas, altitud y conectividad: las coordenadas proceden del Padrón y se cuentan una vez por local validado.

Se mantienen las siguientes distinciones:

- No uso mensual frente a competencias digitales.
- Descripción ponderada del universo analítico frente a tasa oficial nacional.
- AP frente a PR-AUC trapezoidal.
- Selección por validación en desarrollo frente a evaluación de prueba.
- Ganador de clasificación frente a modelo de análisis no lineal complementario.
- Score SHAP previo a calibración frente a probabilidad calibrada.
- Conteos de la matriz de confusión frente a métricas ponderadas.
- Bootstrap por conglomerados frente al diseño muestral ENAHO completo.
- Separación de conglomerados frente a separación de distritos.
- Reevaluación de una prueba ya observada frente a validación externa nueva.

## Verificación final completada

- [x] Confirmar que `reports/results.json` contiene resultados finales de todas las etapas.
- [x] Contrastar el enlace Padlocal y el EDA crudo con sus auditorías reales.
- [x] Revisar todas las cifras y la narrativa de las figuras con las tablas guardadas.
- [x] Generar un PDF de seis páginas exactas.
- [x] Reabrir el PDF y comprobar texto, enlaces, tamaño y ausencia de desbordes.
- [x] Renderizar y revisar visualmente las seis páginas definitivas.
- [x] Verificar legibilidad de tablas, ejes y explicaciones SHAP.
- [x] Confirmar que el Markdown reproduce las cifras definitivas sin HTML residual.

El generador se niega a usar la versión anterior de los resultados si faltan estabilidad, sensibilidad de pesos, interacciones no lineales o auditoría de Padlocal. No se han inventado valores para completar el artículo.


## Evidencia final

- PDF final: `output/pdf/Informe_U2_Brecha_Digital_2025.pdf`, **6 páginas**, 1 337 817 bytes.
- SHA-256: `3e60cce38e3b9b52a6c5a867399803a37af4d689d8ac249963f9dc904d0388b2`.
- Se reabrió el PDF con pypdf; las seis páginas tienen contenido y tres enlaces de referencia activos. No se detectaron caracteres de cuadrado negro ni HTML en el Markdown.
- Render final revisado: `tmp/pdfs/report_review_v2/pagina-1.png` a `pagina-6.png`. No hay cortes, tablas fuera de página, solapamientos ni figuras deformadas.
- Se conservó el estilo a una columna, cuerpo de 9,1-9,4 pt, referencias 7,8 pt y márgenes de 42 pt. Los ejes/leyendas pequeños se redibujaron a tamaño físico de artículo; el mínimo efectivo estimado es superior a 7 pt.
- Las figuras `paper_*` proceden de modelos, predicciones y particiones guardados, **sin reajustar modelos**. Se comprobó coincidencia de importancia SHAP, pares de interacción y secuencia de silueta con resultados canónicos. Su procedencia está en `reports/figures/paper_figures_provenance.json`.
- El EDA crudo se regeneró con las mismas observaciones y fuentes mayores; el gasto se expresa visualmente en miles de soles. No cambia los datos ni sus estadísticos.
- Ganador del análisis revisado: CatBoost. Se conserva precisión de cuatro decimales en AP-CV para no ocultar la diferencia pequeña con XGBoost, sin atribuir significación estadística.
- Las métricas de prueba, matriz de errores, perfiles, estabilidad, ablación y casos se leen del JSON/CSV final. No se actualizaron manualmente para mejorar el resultado.
- El informe declara prueba previamente observada, selección secuencial/no anidada, alcance parcial del constructo de exclusión digital, ausencia de infraestructura escolar y límites de causalidad/representatividad.

No se harán más cambios en figuras o PDF después de esta verificación salvo una corrección explícita y nueva revisión.

## Revisión final de redacción

Se sustituyó la afirmación amplia sobre ausencia de nacimiento por la precisión de que esta integración no reconstruyó edad al 31 de marzo. El módulo Salud puede contener nacimiento y no se usó como Sumaria. Se regeneraron y renderizaron las seis páginas; no cambiaron datos, modelos ni métricas. PDF final SHA256: b0c079acacca43f86c98e60ae5216493c3b6a49dc219d81869b775a4531a92a8.
