# Definición del objetivo y población analítica

El objetivo es clasificar el **no uso de internet durante el mes anterior** en estudiantes residentes habituales de 6 a 17 años matriculados y asistentes a primaria o secundaria. Se utiliza la respuesta P314A de ENAHO 2025.

## Población y etiqueta

```text
6 <= P208A <= 17
P306 = 1: matriculado
P307 = 1: asistente
P308A en {2 primaria, 3 secundaria}
Sin declaración afirmativa P307D = 1 de CEBA
P314A en {1, 2}
FACPOB07 válido y positivo

y = 1 si P314A = 2; y = 0 si P314A = 1.
```

La residencia habitual se define mediante `(P204=1 y P205=2) o (P204=2 y P206=1)`. Los valores ausentes o inválidos de P314A quedan fuera del objetivo. Los saltos estructurales de P307D no se interpretan como una declaración de CEBA.

La cohorte contiene 16 544 estudiantes: 4 294 no usuarios y 12 250 usuarios, distribuidos en 4 040 conglomerados.

## Alcance de la medición

La etiqueta representa una dimensión de la exclusión tecnológica: uso individual reciente. No equivale a ausencia de conexión del hogar, falta de competencias, exclusión permanente ni riesgo futuro.

| Variables | Medición | Universo | Uso analítico |
|---|---|---|---|
| P314A | Uso de internet el mes anterior | Personas de 6 años o más | Objetivo |
| P314B/P314B1 | Lugares y dispositivos de conexión | Usuarios | Auditoría; excluidas de predictores |
| P314D | Frecuencia de uso | Usuarios | Auditoría; excluida de predictores |
| P316_1…12 | Finalidades de uso | Usuarios | Auditoría; excluidas de predictores |
| P316B | Uso de computadora o dispositivo en tres meses | Personas de 14 años o más | Auditoría de medición |
| P316C1…9 | Actividades informáticas autorreportadas | Personas de 14 años o más con uso de dispositivo | Sensibilidad descriptiva |

El universo y los saltos de P316B/P316C impiden construir una medición homogénea de competencias para toda la cohorte de 6 a 17 años. Los saltos y las respuestas ausentes no se convierten en falta de habilidades. El autorreporte de actividades tampoco constituye una prueba de desempeño.

## Desfase edad-grado

La comparación descriptiva de objetivos utiliza `P308C+5` como edad normativa en primaria y `P308B+11` en secundaria. Los umbrales de uno y dos años de desfase producen 6 707 y 679 casos, respectivamente. La edad al momento de la encuesta no es intercambiable con la edad al 31 de marzo utilizada en indicadores administrativos de ESCALE. La etiqueta principal se define por su medición directa y cobertura poblacional, sin utilizar el rendimiento de prueba para elegirla.

## Predictores y evaluación

Se excluyen la respuesta, sus derivados, preguntas condicionadas P314B/P314D/P315/P316, variables de escolaridad que definan la población, identificadores, coordenadas, mes y pesos como predictores. El indicador `escale_coincide` describe disponibilidad de contexto territorial. Los clusters se analizan por separado y no se incorporan al clasificador.

FACPOB07 es el factor individual principal; FACTORA07 se conserva para sensibilidad. FACTOR07 de Sumaria tiene unidad hogar. Los pesos de clase y su normalización se calculan dentro de cada entrenamiento. La calibración utiliza OOF de desarrollo con pesos de población.

La evaluación es retrospectiva sobre una partición de prueba previamente examinada. La separación por CONGLOME reduce dependencia entre conjuntos, pero no garantiza generalización a distritos nuevos ni a otro año. Las estimaciones ponderadas describen la cohorte y no reproducen toda la inferencia del diseño complejo de ENAHO.

Fuentes metodológicas: `docs/sources.json`. Tablas: `reports/tables/target_comparison.csv` y `reports/tables/target_measurement_audit.json`.
