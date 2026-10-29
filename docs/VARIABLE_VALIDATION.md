# Validación conceptual de variables y factores de expansión

Revisión: 2026-10-28, America/Lima. Las variables se contrastaron con el cuestionario ENAHO 2025 del material docente y el diccionario anual oficial 2025. Las páginas indicadas son páginas PDF, contadas desde 1. El diccionario panel contiene nombres heredados y algunos rótulos que no reproducen el cuestionario de 2025; se prioriza el significado de la pregunta del cuestionario y se verifica el contenido observado.

## Fuentes comprobadas

- **Q01**: `INEI/1041-Modulo1479.zip!1041-Modulo1479/CUESTIONARIO_ENAHO01_2025.pdf`, páginas 7-8: miembros, ausencia, presencia y edad.
- **Q01A**: `INEI/1041-Modulo1475.zip!1041-Modulo1475/CUESTIONARIO_ENAHO01A_2025.pdf`, páginas 2, 5 y 6: educación, uso de internet y competencias TIC.
- **D25**: [INEI, Diccionario de Datos ENAHO 2025, mayo de 2026](https://proyectos.inei.gob.pe/iinei/srienaho/Descarga/DocumentosMetodologicos/2025-55/20_Diccionario_2025.pdf): páginas 14, 16, 30-31, 94-95, 107-111, 119 y 375.
- **DP**: `Diccionario_panel_2021_2025.pdf` dentro de los módulos originales: páginas 588-590, 594-595, 599, 660-667; describe campos con sufijo `_25`.

El sufijo anual se quita únicamente después de seleccionar 2025. No se mezclan las respuestas de años anteriores para completar respuestas de 2025.

## Variables exigidas por la guía

| Variable | Significado y códigos verificados | Papel y control |
|---|---|---|
| P1121 | Selección de electricidad como alumbrado: 1 seleccionado, 0 pase/no selección (D25 p. 14). Es una alternativa de respuesta múltiple, no una pregunta binaria con 2=no. | Se deriva electricidad=1/0 solo para códigos válidos; NA permanece NA. No mide horas de servicio, estabilidad ni calidad eléctrica. |
| P1144 | Conexión a internet fijo o móvil del hogar: 1 seleccionado, 0 pase/no selección (D25 p. 16). | internet_hogar=1/0; diferente del uso individual P314A. No se interpreta como internet fijo exclusivamente. |
| P207 | Sexo registrado: 1 hombre, 2 mujer (D25 p. 30). | Variable categórica; los códigos no son una magnitud. |
| P208A | Edad cumplida al entrevistar, no edad al inicio del año escolar (D25 p. 30). 99 es un código de falta de información. | Universo principal 6-17. Edad se admite para predecir no uso de internet; no se usaría de igual forma para un target que la incluye en su definición. |
| P203 | Relación con el jefe del hogar: categorías de parentesco (DP p. 660 y D25 p. 30). | Auditoría, no predictor principal. No confundir miembro del hogar con residente habitual. |
| P300A | Lengua materna; 1 quechua, 2 aimara, 4 castellano; existen otras lenguas y categorías (Q01A p. 2). | Se conserva la categoría original y se codifica one-hot. Un gráfico de códigos no significa una escala continua de lengua. |
| P306 | Matrícula en el año actual: 1 sí, 2 no (Q01A p. 2). | Define población elegible, no predictor. |
| P307 | Asistencia actual: 1 sí, 2 no (Q01A p. 2). | Define población. El rótulo panel que aún menciona educación a distancia no sustituye la pregunta del cuestionario 2025. |
| P307D | Educación primaria/secundaria recibida en CEBA: 1 sí, 2 no. Pregunta para personas de 14 o más años con la trayectoria educativa indicada (Q01A p. 2). | Se excluye CEBA declarado; un salto por edad no equivale a una respuesta afirmativa ni a ausencia aleatoria. |
| P308A | Nivel en el que está matriculado: 2 primaria, 3 secundaria (Q01A p. 2). | Define EBR de interés, con exclusión CEBA declarada. |
| P308B / P308C | Año de secundaria / grado de primaria; el cuestionario separa año y grado (Q01A p. 2; DP p. 590). | Secundaria acepta año 1-5 y primaria grado1-6. No usar P308B como grado de primaria. Los campos P308B1... son opiniones y no el año escolar. |
| P314A | Uso del servicio de internet durante el mes anterior: 1 sí, 2 no (Q01A p. 5; D25 p. 107). | y=1 si 2; y=0 si 1. NA u otro código no es una etiqueta negativa. No prueba destreza ni incapacidad digital. |
| P314B_1...7 | Lugares/modalidades de conexión: hogar, trabajo, establecimiento educativo, cabina, otra casa, otro, acceso móvil (Q01A p. 5). | Preguntas de respuesta múltiple condicionadas al uso; códigos seleccionados difieren por columna. Se excluyen del modelo de P314A, incluso sus faltantes. |
| P314B1_* | Dispositivos de uso: computadora, laptop, tablet, celular con/sin plan, otros (Q01A p. 5). | No medir competencias con disponibilidad/uso de dispositivo. Revisar códigos reales: el diccionario panel contiene rótulos inconsistentes en B1_8/B1_9. |
| P314D | Frecuencia del uso: 1 diario, 2 semanal, 3 mensual, 4 cada 2 meses o más (Q01A p. 5). | No es P316. Excluido por dependencia de la etiqueta; puede describirse condicionando al universo de usuarios. |
| P316_1...12 | Finalidades del uso de internet; P316_5 educación/capacitación, P316_12 descargar software (Q01A p. 5; D25 pp109-110). | Son actividades/finalidades, no examen de competencias. P316_5=2 no significa falta de habilidades. NA de no usuarios es estructural. |
| P316B | Uso de computadora, laptop, tablet o similar durante los últimos 3 meses, para personas de 14+ (Q01A p. 6). | No es la misma ventana ni universo de P314A. Si2, se salta el inventario P316C. |
| P316C1...9 / C10 | Actividades informáticas autorreportadas: archivos, copiar/pegar, adjuntos, fórmulas, dispositivos, software, presentaciones, transferencia, programación; C10=otras (Q01A p. 6; D25 pp110-111). | Información directa sobre actividades relacionadas con habilidades, solo en 14+ y con dispositivo usado. No observado no equivale a incapacidad. No sumar C10 como una destreza comparable a cada actividad enumerada. Excluidas del modelo principal. |
| POBREZA | 1 pobre extremo, 2 pobre no extremo, 3 no pobre (D25 p. 375). | Categórica; no reetiquetar3 como mayor pobreza. Es predictor del no uso, no el objetivo. |
| INGHOG2D | Ingreso neto total del hogar, anualizado (Sumaria). | Ingreso mensual per cápita=INGHOG2D/(12*MIEPERHO), con denominador válido positivo. No son ingresos personales del alumno. |
| GASHOG2D | Gasto total bruto del hogar, anualizado (Sumaria; D25 p. 375). | Gasto mensual per cápita=GASHOG2D/(12*MIEPERHO). No llamarlo gasto monetario, que corresponde a otro campo. |
| FACTOR07 | Factor anual registrado en archivos de hogar/Sumaria (D25 p. 375). | Se conserva como peso de hogar. Repetirlo tras unir a personas no cambia su unidad y no autoriza estimar hogares sumándolo por alumno. |
| FACPOB07 | Factor anual de población (D25 p. 31; DP p. 588). | peso_persona: ponderación principal por corresponder a la unidad estudiante/persona. Nunca predictor. |
| FACTORA07 | Factor anual de población en el módulo educativo (D25 p. 119); DP p. 599 lo describe ajustado por grupos quinquenales. | peso_educacion: sensibilidad documentada. No confundir con el factor de empleo de otros módulos que comparte nombre. |

## Competencias: evidencia y saltos

La revisión anterior del proyecto no había auditado toda la página 6 del cuestionario. **Sí existe un bloque de competencias TIC**, pero no observa de manera completa el universo escolar de 6-17. Los6-13 están fuera de su universo; además P316B=2 evita preguntar C. La ausencia por esos mecanismos no es una respuesta negativa a cada habilidad.

La comprobación directa del CSV crudo de educación, con identificadores de 2025 y sin filtrar edad, encontró 106,958 registros: P314A válido en 99,919; P316B en 84,784 (20,746 sí, 64,038 no); cada P316C1...10 en 20,746. Estos conteos describen el módulo educativo completo del archivo panel docente, no la cohorte final ni la población nacional. Su cobertura específica por edad/cohorte debe consultarse en las tablas de auditoría generadas en la reconstrucción.

Un indicador de baja actividad entre los14-17 que respondieron C sería posible, pero requiere fijar umbral y universo, interpretar selección por uso de dispositivo, y validación externa. No demuestra falta de competencias de los de 6-13, ni de quienes no usaron dispositivo recientemente. Inventar ceros en los saltos produciría una aparente medición completa que el cuestionario no respalda.

## Ponderación y sensibilidad

El protocolo conserva FACPOB07 como peso principal de evaluación y perfilamiento. Compara en desarrollo cuatro estrategias de entrenamiento: sin pesos, solo balance de clase, solo población y población más balance de clase; cada normalización y frecuencia de clase se obtiene en el entrenamiento del fold. El desbalance se considera aunque una estrategia sin balance explícito pueda ganar por AP.

La comparación por FACPOB07/FACTORA07 evalúa sensibilidad al factor. Las métricas sin peso describen la muestra; las ponderadas describen el estimando auxiliar de esta cohorte según el factor. Ni el ajuste ponderado ni un bootstrap de conglomerados reproducen automáticamente toda la estratificación del diseño ENAHO. No se reportan tasas nacionales oficiales ni intervalos de encuesta completos.

## Límite temporal de la validación

El conjunto de prueba de este proyecto ya había sido observado en la versión anterior. La ampliación de búsqueda selecciona configuraciones solo en desarrollo y conserva la partición original; se declara evaluación retrospectiva de un holdout previamente observado. No se afirma que sea una validación externa nueva, ni que la semilla borre ese historial.
