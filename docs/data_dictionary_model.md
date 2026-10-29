# Diccionario del dataset de modelado2025

Generado por `src/update_model_dictionary.py` desde el Parquet real, la lista explícita de predictores y los resultados guardados. Complementa `docs/data_dictionary.md` y `docs/SOURCE_RECONCILIATION.md`.

La tabla `data/processed/dataset_modelado_2025.parquet` (CSV compatible: `dataset_modelado_internet_2025.csv`) contiene **16,544 personas, 120 columnas y 13 predictores**. La etiqueta tiene 4,294 positivos y 12,250 negativos, conteos muestrales.

## Cohorte y fuente canónica

Una fila por residente habitual6–17. Fuente canónica: módulos anuales ENAHO2025(100/200/300/Sumaria); ESCALE Padrón cruzado con Padlocal y agregado por distrito-área. El panel docente se usa únicamente para reconciliación de fuentes. AÑO y llaves se mantienen como texto en Parquet.

Elegible: P306=P307=1, P308A∈{2,3}, sin CEBA afirmativa(P307D!=1), P314A∈{1,2} y FACPOB07 positivo. Un NA estructural de CEBA no se convierte en afirmación de CEBA; una respuesta faltante de internet no se convierte en clase0.

No uso reciente es una dimensión operativa de exclusión digital; no acredita falta de competencias. P316B/C tiene universo14+ y saltos por uso de equipo: los NA de menores y no usuarios no significan incapacidad. Estas ramas se retienen solo para auditar esa limitación.

## Entradas reales del clasificador

| Predictor | Tipo usado | Definición |
|---|---|---|
| edad | numérico(mediana/escalado) | Alias de P208A (años cumplidos). |
| sexo | categoría(one-hot) | Alias de P207 (categoría). |
| lengua_materna | categoría(one-hot) | Alias de P300A (categoría). |
| rural | categoría(one-hot) | 1 si ESTRATO 6-8; 0 si ESTRATO 1-5; otro -> faltante. |
| pobreza | categoría(one-hot) | Sumaria: 1 pobreza extrema, 2 pobreza no extrema, 3 no pobre. |
| electricidad | categoría(one-hot) | P1121 recodificada: 1 sí, 0 no; otros -> faltante. |
| internet_hogar | categoría(one-hot) | P1144 recodificada: conexión de internet fijo/móvil, 1 sí, 0 no; otros -> faltante. |
| altitud | numérico(mediana/escalado) | Altitud del hogar de módulo100, metros; fuera [-100,7000] -> faltante. |
| log_ingreso_pc | numérico(mediana/escalado) | ln(1+ingreso neto mensual per cápita), solo importe>=0; negativos/faltantes→NA. Sin parámetros aprendidos. |
| log_gasto_pc | numérico(mediana/escalado) | ln(1+gasto mensual per cápita), solo importe>=0; negativos/faltantes→NA. Sin parámetros aprendidos. |
| ratio_alumnos_docente | numérico(mediana/escalado) | SUM(TALUM)/SUM(TDOC) en distrito+área; faltante si SUM(TDOC)<=0. |
| prop_publicas | numérico(mediana/escalado) | Proporción de servicios elegibles con GESTION 1 o 2; gestión3 privada. |
| escale_coincide | categoría(one-hot) | 1 si UBIGEO+área enlazó a ESCALE, 0 si sin correspondencia. |

`escale_coincide` es la única bandera de cobertura incluida como predictor predefinido: indica disponibilidad del contexto territorial y no contiene la respuesta individual. Las otras banderas de merge no se utilizan. Los agregados escolares describen distrito-área de residencia; no el colegio observado de cada estudiante. La latitud y longitud individuales de hogares no se cargan ni se exportan.

## Transformaciones, pesos y partición

Dentro de cada fold se ajustan mediana+StandardScaler para variables numéricas, moda+OneHotEncoder para categorías. El logaritmo determinista se aplica antes de la partición y no estima parámetros. La prueba nunca ajusta imputadores, escalas, categorías, pesos de clase, hiperparámetros ni calibradores.

`peso_persona`(FACPOB07 del módulo200) es el peso principal individual para selección y evaluación. `peso_hogar`(FACTOR07 Sumaria) es de hogar y no se acumula por estudiante. `peso_educacion`(FACTORA07 del módulo300) es un factor anual de población para educación y se usa como sensibilidad de evaluación. Ningún peso es predictor.

En desarrollo se comparan por algoritmo cuatro estrategias: uniforme, solo población normalizada, solo clase y población×clase. Los balances y normalizaciones se calculan con el entrenamiento de cada fold. La estrategia se selecciona por AP media ponderada de validación con las mismas cinco particiones, antes de explorar hiperparámetros. Las métricas de sensibilidad se guardan en `weight_sensitivity.csv`; combinar pesos es una alternativa evaluada, no una regla automática.

La calibración sigmoide usa logits de predicciones OOF y pesos individuales de desarrollo. Umbral fijo0.5; no se optimiza mirando prueba. Se distinguen AP y áreaPR trapezoidal, y métricas muestrales y ponderadas. La búsqueda y selección sobre los mismos folds puede producir optimismo de validación; no se afirma validación anidada.

Partición semilla42: 13,105 personas / 3,232 conglomerados de desarrollo; 3,439 / 808 de prueba. Intersección CONGLOME=0. GroupKFold de5pliegues en desarrollo. El particionado evalúa conglomerados no vistos, sin garantizar distritos enteramente nuevos.

### Estrategias de ajuste elegidas en desarrollo

| Modelo | Estrategia |
|---|---|
| Logística | uniform |
| Random Forest | uniform |
| XGBoost | uniform |
| CatBoost | class |

Ganador por AP media de GroupKFold: **CatBoost**. Esta selección se documenta después de su ejecución; el modelo no se elige por el score de prueba.

## Rol de las columnas realmente presentes

La presencia en el archivo no implica uso en entrenamiento. Todas las preguntas de la familia P314/P315/P316 y sus saltos/derivados quedan fuera de la lista de predictores; matrícula, asistencia y componentes del objetivo son de auditoría.

| Columna | Tipo almacenado(Parquet) | Rol | Faltantes | Definición |
|---|---|---|---:|---|
| indice_dataset | int64 | auditoría/contexto; no predictor | 0 | Índice de la fila en la tabla integrada anual. Solo enlaza artefactos de auditoría; nunca se entrena con él. |
| ano | str | auditoría/contexto; no predictor | 0 | Año 2025 del archivo anual; texto en Parquet. No se combinan otros años. |
| mes | int64 | auditoría/contexto; no predictor | 0 | Mes de encuesta 2025; puede afectar comparaciones de edad, matrícula o asistencia. |
| conglome | str | auditoría/contexto; no predictor | 0 | Código CONGLOME anual, string de 6 dígitos; agrupación obligatoria de partición. |
| vivienda | str | auditoría/contexto; no predictor | 0 | Código VIVIENDA anual, string de 3 dígitos. |
| hogar | str | auditoría/contexto; no predictor | 0 | Código HOGAR anual, string de 2 dígitos. |
| codperso | str | auditoría/contexto; no predictor | 0 | Código CODPERSO anual, string de 2 dígitos. |
| ubigeo | str | auditoría/contexto; no predictor | 0 | Distrito de residencia del miembro, UBIGEO anual, 6 dígitos. |
| dominio | int64 | auditoría/contexto; no predictor | 0 | Dominio geográfico ENAHO (categoría). |
| estrato | int64 | auditoría/contexto; no predictor | 0 | Estrato: 1-5 urbano; 6-8 rural. |
| p203 | int64 | auditoría/contexto; no predictor | 0 | Parentesco con jefe del hogar; campo original módulo 200. |
| p204 | int64 | auditoría/contexto; no predictor | 0 | Miembro del hogar (1 sí, 2 no). |
| p205 | float64 | auditoría/contexto; no predictor | 76 | Ausente del hogar 30 días o más (1 sí, 2 no). |
| p206 | float64 | auditoría/contexto; no predictor | 16468 | Presente en el hogar 30 días o más (1 sí, 2 no). |
| p207 | int64 | auditoría/contexto; no predictor | 0 | Sexo: 1 hombre, 2 mujer. |
| p208a | int64 | auditoría/contexto; no predictor | 0 | Edad en años cumplidos, módulo 200. |
| p208b | float64 | auditoría/contexto; no predictor | 16544 | Edad en meses; campo original. |
| facpob07 | float64 | peso/metadato; no predictor | 0 | Factor anual de población del módulo 200. |
| residente_habitual | int64 | auditoría/contexto; no predictor | 0 | 1 en cohorte; selección (P204=1 y P205=2) o (P204=2 y P206=1). |
| p300a | float64 | auditoría/contexto; no predictor | 0 | Lengua materna; 1 quechua, 2 aimara, 4 castellano; conservar las restantes categorías originales. |
| p301a | float64 | auditoría/contexto; no predictor | 0 | Último nivel aprobado. |
| p301b | float64 | auditoría/contexto; no predictor | 18 | Último año de estudios aprobado. |
| p301c | float64 | auditoría/contexto; no predictor | 7198 | Último grado de estudios aprobado. |
| p301d | float64 | auditoría/contexto; no predictor | 19 | Tipo de centro de estudios del último nivel aprobado. |
| p306 | float64 | auditoría/contexto; no predictor | 0 | Matriculado este año: 1 sí, 2 no. |
| p307 | float64 | auditoría/contexto; no predictor | 0 | Asiste actualmente: 1 sí, 2 no. |
| p307d | float64 | auditoría/contexto; no predictor | 11498 | Recibe o recibió primaria/secundaria en CEBA: 1 sí, 2 no; pregunta condicionada. |
| p308a | float64 | auditoría/contexto; no predictor | 0 | Nivel matriculado: 1 inicial, 2 primaria, 3 secundaria, 4 superior no universitaria, 5 universitaria, 6 posgrado, 7 especial. |
| p308b | float64 | auditoría/contexto; no predictor | 1 | Año de estudios actualmente matriculado; no combinar a ciegas con P308C. |
| p308c | float64 | auditoría/contexto; no predictor | 7654 | Grado de estudios actualmente matriculado; verificar nivel antes de usar. |
| p308d | float64 | auditoría/contexto; no predictor | 6 | Centro actualmente matriculado: 1 estatal, 2 no estatal. |
| p308c1 | float64 | auditoría/contexto; no predictor | 0 | Institución a la que asiste se ubica aquí en el distrito (variable original). |
| p308c2 | float64 | auditoría/contexto; no predictor | 7 | Institución a la que asiste se ubica en otro distrito (variable original). |
| p314a | float64 | auditoría condicionada/target; excluido por fuga | 0 | Uso de internet el mes anterior: 1 sí, 2 no. Componente de la etiqueta digital; excluir de sus predictores. |
| p314b_1 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Lugar de uso de internet, respuesta múltiple 1 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_2 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Lugar de uso de internet, respuesta múltiple 2 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_3 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Lugar de uso de internet, respuesta múltiple 3 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_4 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Lugar de uso de internet, respuesta múltiple 4 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_5 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Lugar de uso de internet, respuesta múltiple 5 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_6 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Lugar de uso de internet, respuesta múltiple 6 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_7 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Lugar de uso de internet, respuesta múltiple 7 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314d | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Frecuencia de internet entre usuarios; salto estructural revela P314A. Excluir de predictores digitales. |
| p316_1 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 1 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_2 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 2 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_3 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 3 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_4 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 4 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_5 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 5 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_6 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 6 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_7 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 7 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_8 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 8 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_9 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 9 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_10 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 10 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_11 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 11 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_12 | float64 | auditoría condicionada/target; excluido por fuga | 4294 | Finalidad de uso de internet 12 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316b | float64 | auditoría condicionada/target; excluido por fuga | 11503 | Uso de computadora/laptop/tablet en últimos3meses, solo14+; 1sí2no. Auditoría de medición, nunca predictor digital. |
| p316c1 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 1; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c2 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 2; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c3 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 3; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c4 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 4; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c5 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 5; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c6 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 6; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c7 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 7; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c8 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 8; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c9 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 9; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c10 | float64 | auditoría condicionada/target; excluido por fuga | 14447 | Actividad TIC autorreportada 10; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| factor07_educacion | float64 | peso/metadato; no predictor | 0 | Factor anual original del módulo educación. |
| factora07 | float64 | peso/metadato; no predictor | 0 | Factor de población ajustado por grupos quinquenales del módulo educación. |
| coincide_educacion | int64 | auditoría/contexto; no predictor | 0 | Bandera de auditoría: 1 si la tabla de origen pudo enlazarse; no predictor por defecto. |
| tipenc | int64 | auditoría/contexto; no predictor | 0 | Tipo de selección: 3 panel; otros códigos incluyen selección no panel. |
| result | int64 | auditoría/contexto; no predictor | 0 | Resultado de entrevista: 1 completa, 2 incompleta; otros estados se conservan si aparecieran. |
| p1121 | int64 | auditoría/contexto; no predictor | 0 | Electricidad como alumbrado: 1 sí, 0 no. |
| p1144 | int64 | auditoría/contexto; no predictor | 0 | Conexión de internet fijo/móvil en hogar: 1 sí, 0 no; cuestionario 2025 p.4. |
| factor07_vivienda | float64 | peso/metadato; no predictor | 0 | Factor anual del módulo 100. |
| nconglome | int64 | auditoría/contexto; no predictor | 0 | Conglomerado del marco, identificador original, no predictor. |
| sub_conglome | int64 | auditoría/contexto; no predictor | 0 | Subconglomerado del marco, identificador original, no predictor. |
| altitud | float64 | predictor numérico | 0 | Altitud del hogar de módulo100, metros; fuera [-100,7000] -> faltante. |
| coincide_vivienda | int64 | auditoría/contexto; no predictor | 0 | Bandera de auditoría: 1 si la tabla de origen pudo enlazarse; no predictor por defecto. |
| mieperho | int64 | auditoría/contexto; no predictor | 0 | Miembros del hogar utilizados para per cápita, Sumaria. |
| inghog2d | float64 | auditoría/contexto; no predictor | 0 | Ingreso neto anual del hogar, Sumaria, soles; se conserva sin sustituir faltantes. |
| gashog2d | float64 | auditoría/contexto; no predictor | 0 | Gasto anual del hogar, Sumaria, soles. |
| pobreza | float64 | predictor categórico | 0 | Sumaria: 1 pobreza extrema, 2 pobreza no extrema, 3 no pobre. |
| factor07_sumaria | float64 | peso/metadato; no predictor | 0 | Factor anual original de Sumaria, unidad hogar. |
| coincide_sumaria | int64 | auditoría/contexto; no predictor | 0 | Bandera de auditoría: 1 si la tabla de origen pudo enlazarse; no predictor por defecto. |
| edad | float64 | predictor numérico | 0 | Alias de P208A (años cumplidos). |
| sexo | float64 | predictor categórico | 0 | Alias de P207 (categoría). |
| lengua_materna | float64 | predictor categórico | 0 | Alias de P300A (categoría). |
| rural | float64 | predictor categórico | 0 | 1 si ESTRATO 6-8; 0 si ESTRATO 1-5; otro -> faltante. |
| escale_area | float64 | auditoría/contexto; no predictor | 0 | Área contextual: 1 urbana, 2 rural, derivada de ESTRATO. |
| electricidad | float64 | predictor categórico | 0 | P1121 recodificada: 1 sí, 0 no; otros -> faltante. |
| internet_hogar | float64 | predictor categórico | 0 | P1144 recodificada: conexión de internet fijo/móvil, 1 sí, 0 no; otros -> faltante. |
| ingreso_pc_mensual | float64 | auditoría/contexto; no predictor | 0 | INGHOG2D / (12*MIEPERHO), solo denominador >0. Soles por persona/mes. |
| gasto_pc_mensual | float64 | auditoría/contexto; no predictor | 0 | GASHOG2D / (12*MIEPERHO), solo denominador >0. Soles por persona/mes. |
| peso_persona | float64 | peso/metadato; no predictor | 0 | Alias FACPOB07, peso de población; revisar uso según análisis, no predictor. |
| peso_hogar | float64 | peso/metadato; no predictor | 0 | Alias FACTOR07 de Sumaria, unidad hogar; no sumar por cada estudiante para estimar hogares. |
| peso_educacion | float64 | peso/metadato; no predictor | 0 | Alias FACTORA07 de educación, peso de población ajustado por grupos quinquenales. |
| matriculado | float64 | auditoría/contexto; no predictor | 0 | P306 1 -> 1, 2 -> 0; otros -> faltante. |
| asiste | float64 | auditoría/contexto; no predictor | 0 | P307 1 -> 1, 2 -> 0; otros -> faltante. |
| no_uso_internet | float64 | auditoría condicionada/target; excluido por fuga | 0 | P314A 2 -> 1, 1 -> 0; otros -> faltante. Etiqueta potencial, no predictor digital. |
| exclusion_digital | float64 | auditoría condicionada/target; excluido por fuga | 0 | NO_USO_INTERNET solo si ASISTE=1; demás -> faltante. Proxy operativo; no mide competencias. |
| escale_servicios | float64 | auditoría/contexto; no predictor | 339 | Número de servicios escolares activos de primaria y secundaria por distrito+área. |
| escale_instituciones | float64 | auditoría/contexto; no predictor | 339 | CODINST distintos en servicios elegibles; no confundir con servicios ni locales. |
| escale_alumnos | float64 | auditoría/contexto; no predictor | 339 | Suma TALUM de servicios elegibles por distrito+área. |
| escale_docentes | float64 | auditoría/contexto; no predictor | 339 | Suma TDOC de servicios elegibles por distrito+área; no personas docentes únicas. |
| escale_secciones | float64 | auditoría/contexto; no predictor | 339 | Suma TSEC por distrito+área. |
| prop_publicas | float64 | predictor numérico | 339 | Proporción de servicios elegibles con GESTION 1 o 2; gestión3 privada. |
| escale_prop_imputadas | float64 | auditoría/contexto; no predictor | 339 | Proporción de servicios con IMPUTADO parcial o total de MINEDU. |
| escale_cobertura_padlocal | float64 | auditoría/contexto; no predictor | 339 | Fracción de servicios cuyo local está activo y coincide en distrito/área con Padlocal. |
| escale_latitud | float64 | auditoría/contexto; no predictor | 339 | Promedio de NLAT_IE en locales distintos (CODLOCAL), distrito+área. |
| escale_longitud | float64 | auditoría/contexto; no predictor | 339 | Promedio de NLONG_IE en locales distintos (CODLOCAL), distrito+área. |
| escale_locales | float64 | auditoría/contexto; no predictor | 339 | Locales físicos distintos con Padlocal activo y geografía consistente, por distrito+área. |
| escale_prop_local_compartido | float64 | auditoría/contexto; no predictor | 339 | Fracción de locales físicos validados con más de un servicio EBR elegible. |
| ratio_alumnos_docente | float64 | predictor numérico | 339 | SUM(TALUM)/SUM(TDOC) en distrito+área; faltante si SUM(TDOC)<=0. |
| escale_coincide | float64 | predictor categórico | 0 | 1 si UBIGEO+área enlazó a ESCALE, 0 si sin correspondencia. |
| edad_normativa | float64 | auditoría/contexto; no predictor | 0 | P308C+5 si primaria; P308B+11 si secundaria. Referencia exploratoria, sin cumpleaños al31marzo. |
| desfase_edad_grado | float64 | auditoría/contexto; no predictor | 0 | Edad de entrevista menos edad normativa. No es la medición administrativa SIAGIE; no predictor digital. |
| target_rezago | float64 | etiqueta alternativa descriptiva(no entrenada) | 0 | Etiqueta alternativa descriptiva: desfase>=1, solo grado y nivel válidos. No entrenada ni usada para elegir el objetivo por score. |
| target_rezago_2 | float64 | etiqueta alternativa descriptiva(no entrenada) | 0 | Sensibilidad descriptiva: desfase>=2, misma cohorte de grado válido. No equivale a edad SIAGIE al31marzo. |
| target_internet | float64 | etiqueta principal | 0 | Etiqueta principal:1 si P314A=2(no usó internet mes anterior),0 si P314A=1. Solo asistentesEBR elegibles. |
| log_ingreso_pc | float64 | predictor numérico | 0 | ln(1+ingreso neto mensual per cápita), solo importe>=0; negativos/faltantes→NA. Sin parámetros aprendidos. |
| log_gasto_pc | float64 | predictor numérico | 0 | ln(1+gasto mensual per cápita), solo importe>=0; negativos/faltantes→NA. Sin parámetros aprendidos. |
