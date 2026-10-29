# Decisión científica sobre el objetivo

Revisión conceptual de la ampliación: 2026-10-28, America/Lima. La decisión de conservar la etiqueta se cerró **antes de ejecutar la nueva búsqueda de modelos**. Existe una versión predictiva anterior cuyo conjunto de prueba ya fue observado; la nueva evaluación sobre esa partición es retrospectiva, no una validación externa nueva. La guía del docente y el cuestionario tienen prioridad sobre interpretaciones previas.

## Decisión y relación con la guía

Se mantiene como objetivo principal **no uso de internet durante el mes anterior entre estudiantes de 6-17 matriculados y asistentes a primaria/secundaria**, excluida CEBA declarada. Tiene una definición directa, ventana temporal explícita y observación para todo el universo escolar definido. No se cambia la etiqueta para mejorar métricas ni para favorecer un algoritmo.

La guía propone rezago o exclusión digital efectiva, descrita con competencias y uso de internet. Esta etiqueta mide **una dimensión operacional de la exclusión tecnológica**. No identifica por sí sola ausencia de competencias digitales, exclusión persistente ni riesgo futuro. Por tanto, la equivalencia completa con el constructo multidimensional de la guía queda **parcial**. La adecuación de esta operacionalización al criterio docente es una limitación que debe reconocerse al defender el proyecto, no ocultarse con un nombre más ambicioso.

La revisión completa del cuestionario corrigió una omisión de la versión anterior: **ENAHO 2025 sí incluye un bloque de competencias TIC, P316B/P316C**, pero solo para personas de 14 o más años y con saltos condicionados al uso de dispositivo. No permite observar competencias de todos los escolares de 6-17. No es correcto afirmar que estas variables no existen, ni convertir sus saltos en falta demostrada de habilidades.

## Definición matemática

El dataset integrado ya restringe a residentes habituales de 6-17. La cohorte final exige:

```text
E = 6 <= P208A <= 17
    y P306=1 y P307=1
    y P308A en {2 primaria, 3 secundaria}
    y no existe declaración P307D=1 (CEBA)
    y P314A en {1,2}
    y FACPOB07 es válido y positivo.

y = 1 si P314A=2; y=0 si P314A=1, solo en E.
```

Un faltante o código inválido en P314A no equivale a 0. La exclusión de CEBA se basa en respuesta afirmativa; el NA estructural por edad de P307D no se convierte en CEBA. No se exige grado válido para etiquetar no uso, aunque la versión anterior tenía grado válido en todos los 16,544 elegibles.

La reconstrucción anual y la ejecución vigente confirmaron 16,544 elegibles, 4,294 positivos y 12,250 negativos en 4,040 conglomerados. Los conteos completos quedan en `reports/tables/target_comparison.csv` y `reports/tables/target_measurement_audit.json`.

## Qué mide realmente cada rama TIC

| Rama | Medición | Universo/salto | Consecuencia |
|---|---|---|---|
| P314A | Uso individual de internet mes anterior | Personas6+ | Etiqueta principal directa. No mide destreza ni conexión del hogar. |
| P314B / P314B1 | Lugares/modalidades y dispositivos de conexión | Usuarios de internet | No son un test de competencias; sus respuestas y NA pueden revelar la etiqueta. |
| P314D | Frecuencia de uso | Usuarios | No confundir con P316; excluir del modelo de no uso. |
| P316_1...12 | Finalidades: información, comunicación, compras, banca, educación, trámites, ocio, venta, otros, software | Usuarios | P316_5=2 significa que no declaró uso educativo, no que no sabe usar herramientas. |
| P316B | Uso de computadora/laptop/tablet/similar en últimos 3 meses | Personas14+ | Si no, se salta P316C. No uso reciente de dispositivo no demuestra incapacidad. |
| P316C1...9 | Actividades informáticas concretas autorreportadas |14+ y P316B=1 | Información sobre experiencia relacionada con habilidades. Solo observable en un subconjunto seleccionado; no es prueba de desempeño. |
| P316C10 | Otras actividades | Igual subconjunto | No sumar como una habilidad uniforme comparable con cada ítem enumerado. |

El cuestionario ENAHO.01A 2025, página PDF5, confirma P314A=1 sí/2 no y el salto de no usuarios hacia P316A. Su página 6 identifica el bloque de competencias para 14+ y el salto desde P316B=2 al capítulo 400. El diccionario anual 2025, páginas PDF 107-111, confirma nombres/códigos; el panel conserva las columnas `_25` y algunos rótulos heredados. Véase `docs/VARIABLE_VALIDATION.md` para el contraste por variable.

Como sensibilidad descriptiva se audita, entre 14-17 con las nueve actividades observadas, cuántos no usan internet y no reportan ninguna. Ese subconjunto no representa a todos los escolares y no crea una nueva etiqueta entrenada. No imputar C=No cuando B=No o edad < 14: los mecanismos de ausencia son parte del diseño del cuestionario.

## Comparación con rezago escolar

Se evaluó la alternativa de desfase observado edad-grado:

```text
edad_normativa = P308C+5 en primaria; P308B+11 en secundaria.
desfase = P208A-edad_normativa.
rezago_1 = I(desfase >= 1); rezago_2 = I(desfase >= 2).
```

Se requieren grados válidos 1-6 en primaria/años 1-5 en secundaria, asistencia/matrícula y exclusión CEBA declarada. El [documento metodológico INEI de indicadores educativos 2022](https://www.inei.gob.pe/media/MenuRecursivo/investigaciones/indicadores-de-educacion.pdf), páginas PDF 29 y 33-34, fundamenta el desfase con edad actual. La [ficha ESCALE/SIAGIE](https://escale.minedu.gob.pe/tendencias-2016-portlet/servlet/tendencias/archivo?idCuadro=14&tipo=meta) emplea dos años y edad al 31 de marzo; no es una definición intercambiable.

La exploración anterior encontró 6,707 casos para >=1 y 679 para >=2; la primera frecuencia varió de 10.6% en marzo a 69.4% en diciembre. Esa variación es compatible con cumpleaños y composición mensual, sin identificar por separado cada mecanismo. Los campos adicionales de nacimiento leídos del módulo 200 estaban vacíos; esto **no prueba ausencia de fechas en toda ENAHO**: el módulo 400 de Salud incluye preguntas de nacimiento. Ese módulo no es Sumaria y no se integra al objetivo principal actual. No se inventaron cumpleaños ni se restó un año automáticamente.

Rezago observado sería una alternativa legítima si se declara su definición y universos; no se adopta ahora solo para aparentar mayor ajuste a la consigna o elegir el target de mejor AUC. La claridad de P314A y su cobertura6-17 justifican mantenerlo y reconocer su alcance limitado.

## Factores de expansión y evaluación

La unidad analítica es la persona estudiante. FACPOB07, factor anual de población del módulo 200, es la referencia principal. FACTORA07, factor poblacional del módulo educativo descrito por el panel como ajustado por grupos quinquenales, se conserva para sensibilidad. FACTOR07 de Sumaria tiene unidad hogar: al repetirlo en filas de personas no se vuelve automáticamente un factor de persona. Los pesos longitudinales FACPANEL no corresponden al corte transversal seleccionado.

La ampliación compara en desarrollo estrategias sin pesos, balance de clases, pesos poblacionales y su combinación. La normalización y las masas de clase se calculan solo en el entrenamiento de cada fold. La selección se efectúa por AP ponderada FACPOB07; se presentan métricas sin ponderar y sensibilidad FACTORA07. El calibrador se aprende de predicciones OOF de desarrollo, con pesos de población y sin balance que altere artificialmente la prevalencia de referencia.

Los resultados ponderados describen esta cohorte bajo el factor empleado; no son tasas nacionales oficiales ni una reproducción de la inferencia completa del diseño complejo. La prueba por conglomerados evalúa vecindarios no vistos dentro de esta fuente y población; no garantiza distritos nuevos ni otro año.

## Fuga y predictores

Excluir P314A y todos sus derivados, P314B*, P314D, P315*, P316*, sus banderas de falta/respuesta e imputaciones. Excluir las etiquetas alternativas y las variables que definieron matrícula, asistencia y trayectoria; identificadores, coordenadas y mes no son predictores. P1144 se conserva porque mide conexión del hogar, distinta del uso individual; no autoriza inferir causalidad.

La lista principal sigue siendo explícita y se fija antes de la nueva búsqueda. Las banderas de unión ENAHO se conservan solo para auditoría. `escale_coincide` sí forma parte del conjunto de predictores como indicador contextual de disponibilidad; no contiene la etiqueta. Esa elección debe declararse de forma consistente y limita el transporte a geografías con otra cobertura. Clustering se presenta por separado y no se añade a los clasificadores como una transformación ajustada fuera de fold.

## Procedencia y límites de defensa

La comparación ejecutada eligió los archivos ENAHO anuales 2025 como fuente única; la evidencia se documenta en `docs/SOURCE_RECONCILIATION.md` y `reports/tables/source_comparison.json`; el nombre «panel» no basta para excluir una fuente que contiene corte 2025 panel y no panel. No se afirma equivalencia entre archivos por compartir recuentos; se requiere comparación por llaves y variables.

ESCALE es contexto por distrito/área de residencia. ENAHO no identifica aquí el local escolar asistido: no asignar a cada estudiante las instalaciones de un colegio concreto. Las asociaciones predictivas y SHAP no demuestran causalidad. Quienes no están matriculados o no asisten quedan fuera de la cohorte final; no se generaliza a toda la niñez ni a todas las dimensiones de exclusión educativa.

La rúbrica de competencias debe permanecer como adaptación explícita mientras la medición no identifique todo el constructo. Resolver esa limitación exigiría un instrumento comparable para 6-17 o una redefinición y validación de población/constructo; no es un faltante que se arregle llenando NA con ceros.

## Cierre de la auditoría de medición ejecutada

La ejecución sobre el dataset anual reconstruido confirmó 11,503 asistentes de 6-13 sin P316B/C por universo, y 5,041 de 14-17 con P316B observado. En estos últimos, 2,097 respondieron las nueve actividades y 2,944 saltaron C tras no usar dispositivo. Hubo 77 sin ninguna actividad declarada entre los 2,097 observados y cero casos con esa combinación completamente observada junto con no uso de internet. Los cuatro controles de edad/saltos y suma de cohortes aprobaron. Esto no demuestra competencias de todos: confirma la selección estructural y la inviabilidad de imponer una etiqueta conjunta completa con esos faltantes. Evidencia: `reports/tables/target_measurement_audit.json`, hash del dataset `e46ff2b57a84c34319b94609460a7d7a 0972be087a93cb39e3fa7dc5e24a96a5`.
