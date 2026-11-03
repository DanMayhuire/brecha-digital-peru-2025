# Diccionario de datos ENAHO + ESCALE 2025

Cohorte: 23,345 personas residentes habituales de 6 a 17 años. Una fila por CONGLOME+VIVIENDA+HOGAR+CODPERSO de 2025.

Fuente canónica: descargas anuales ENAHO2025. El corte panel2025 se compara por llaves y valores, sin usarlo para completar datos. Las llaves y AÑO permanecen como texto; no se cargan nombres, direcciones ni coordenadas de hogares.

## Procedencia y decisiones

- Ficha técnica PANEL 2021-2025 p.6: archivos con hogares paneles y no paneles de cada año.
- Diccionario anual ENAHO2025: pp.14,16 servicios; pp.29-31 edad/residencia/factor persona; pp.94-95 educación; pp.107-111 uso/TIC/competencias; p.119 factor de educación. Los códigos de missing se normalizan por variable, nunca globalmente.
- ESCALE: Padrón activo, NIV_MOD=B0/F0, cruzado por CODLOCAL con Padlocal único; se auditan distrito y área antes de agregar. No se asigna un colegio individual a estudiantes ENAHO.
- Se mantienen entrevistas incompletas cuando hay personas elegibles; el faltante queda explícito. No se imputa ni escala en este paso.
- P308B y P308C son componentes distintos (año y grado). La etiqueta de rezago no se define aquí y debe justificarse antes del modelado.
- Los módulos usados no incluyen fecha de nacimiento para corregir edad al31marzo; no se reconstruyen cumpleaños ni se afirma que no exista en otros módulos no utilizados.
- Padlocal no contiene coordenadas ni mediciones físicas de infraestructura. Coordenadas provienen de Padrón y se promedian una vez por local geográficamente validado. No se inventan computadoras, conectividad ni altitud escolar.
- Los pesos se conservan por unidad (persona, hogar y educación); no se mezclan con los pesos longitudinales FACPANEL.

## Campos

| Variable | Tipo | Faltantes | Definición / uso |
|---|---|---:|---|
| ano | texto | 0 | Año 2025 del archivo anual; texto en Parquet. No se combinan otros años. |
| mes | texto | 0 | Mes de encuesta 2025; puede afectar comparaciones de edad, matrícula o asistencia. |
| conglome | texto | 0 | Código CONGLOME anual, string de 6 dígitos; agrupación obligatoria de partición. |
| vivienda | texto | 0 | Código VIVIENDA anual, string de 3 dígitos. |
| hogar | texto | 0 | Código HOGAR anual, string de 2 dígitos. |
| codperso | texto | 0 | Código CODPERSO anual, string de 2 dígitos. |
| ubigeo | texto | 0 | Distrito de residencia del miembro, UBIGEO anual, 6 dígitos. |
| dominio | numérico | 0 | Dominio geográfico ENAHO (categoría). |
| estrato | numérico | 0 | Estrato: 1-5 urbano; 6-8 rural. |
| p203 | numérico | 0 | Parentesco con jefe del hogar; campo original módulo 200. |
| p204 | numérico | 0 | Miembro del hogar (1 sí, 2 no). |
| p205 | numérico | 103 | Ausente del hogar 30 días o más (1 sí, 2 no). |
| p206 | numérico | 23242 | Presente en el hogar 30 días o más (1 sí, 2 no). |
| p207 | numérico | 0 | Sexo: 1 hombre, 2 mujer. |
| p208a | numérico | 0 | Edad en años cumplidos, módulo 200. |
| p208b | numérico | 23345 | Edad en meses; campo original. |
| facpob07 | numérico | 0 | Factor anual de población del módulo 200. |
| residente_habitual | numérico | 0 | 1 en cohorte; selección (P204=1 y P205=2) o (P204=2 y P206=1). |
| p300a | numérico | 27 | Lengua materna; 1 quechua, 2 aimara, 4 castellano; conservar las restantes categorías originales. |
| p301a | numérico | 27 | Último nivel aprobado. |
| p301b | numérico | 139 | Último año de estudios aprobado. |
| p301c | numérico | 11416 | Último grado de estudios aprobado. |
| p301d | numérico | 141 | Tipo de centro de estudios del último nivel aprobado. |
| p306 | numérico | 27 | Matriculado este año: 1 sí, 2 no. |
| p307 | numérico | 3287 | Asiste actualmente: 1 sí, 2 no. |
| p307d | numérico | 15116 | Recibe o recibió primaria/secundaria en CEBA: 1 sí, 2 no; pregunta condicionada. |
| p308a | numérico | 3287 | Nivel matriculado: 1 inicial, 2 primaria, 3 secundaria, 4 superior no universitaria, 5 universitaria, 6 posgrado, 7 especial. |
| p308b | numérico | 3290 | Año de estudios actualmente matriculado; no combinar a ciegas con P308C. |
| p308c | numérico | 13303 | Grado de estudios actualmente matriculado; verificar nivel antes de usar. |
| p308d | numérico | 3293 | Centro actualmente matriculado: 1 estatal, 2 no estatal. |
| p308c1 | numérico | 5538 | Institución a la que asiste se ubica aquí en el distrito (variable original). |
| p308c2 | numérico | 5548 | Institución a la que asiste se ubica en otro distrito (variable original). |
| p314a | numérico | 27 | Uso de internet el mes anterior: 1 sí, 2 no. Componente de la etiqueta digital; excluir de sus predictores. |
| p314b_1 | numérico | 6392 | Lugar de uso de internet, respuesta múltiple 1 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_2 | numérico | 6392 | Lugar de uso de internet, respuesta múltiple 2 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_3 | numérico | 6392 | Lugar de uso de internet, respuesta múltiple 3 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_4 | numérico | 6392 | Lugar de uso de internet, respuesta múltiple 4 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_5 | numérico | 6392 | Lugar de uso de internet, respuesta múltiple 5 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_6 | numérico | 6392 | Lugar de uso de internet, respuesta múltiple 6 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314b_7 | numérico | 6392 | Lugar de uso de internet, respuesta múltiple 7 entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital. |
| p314d | numérico | 6392 | Frecuencia de internet entre usuarios; salto estructural revela P314A. Excluir de predictores digitales. |
| p316_1 | numérico | 6392 | Finalidad de uso de internet 1 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_2 | numérico | 6392 | Finalidad de uso de internet 2 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_3 | numérico | 6392 | Finalidad de uso de internet 3 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_4 | numérico | 6392 | Finalidad de uso de internet 4 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_5 | numérico | 6392 | Finalidad de uso de internet 5 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_6 | numérico | 6392 | Finalidad de uso de internet 6 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_7 | numérico | 6392 | Finalidad de uso de internet 7 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_8 | numérico | 6392 | Finalidad de uso de internet 8 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_9 | numérico | 6392 | Finalidad de uso de internet 9 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_10 | numérico | 6392 | Finalidad de uso de internet 10 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_11 | numérico | 6392 | Finalidad de uso de internet 11 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316_12 | numérico | 6392 | Finalidad de uso de internet 12 entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital. |
| p316b | numérico | 15042 | Uso de computadora/laptop/tablet en últimos3meses, solo14+; 1sí2no. Auditoría de medición, nunca predictor digital. |
| p316c1 | numérico | 20203 | Actividad TIC autorreportada 1; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c2 | numérico | 20203 | Actividad TIC autorreportada 2; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c3 | numérico | 20203 | Actividad TIC autorreportada 3; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c4 | numérico | 20203 | Actividad TIC autorreportada 4; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c5 | numérico | 20203 | Actividad TIC autorreportada 5; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c6 | numérico | 20203 | Actividad TIC autorreportada 6; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c7 | numérico | 20203 | Actividad TIC autorreportada 7; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c8 | numérico | 20203 | Actividad TIC autorreportada 8; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c9 | numérico | 20203 | Actividad TIC autorreportada 9; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| p316c10 | numérico | 20203 | Actividad TIC autorreportada 10; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital. |
| factor07_educacion | numérico | 0 | Factor anual original del módulo educación. |
| factora07 | numérico | 0 | Factor de población ajustado por grupos quinquenales del módulo educación. |
| coincide_educacion | numérico | 0 | Bandera de auditoría: 1 si la tabla de origen pudo enlazarse; no predictor por defecto. |
| tipenc | numérico | 0 | Tipo de selección: 3 panel; otros códigos incluyen selección no panel. |
| result | numérico | 0 | Resultado de entrevista: 1 completa, 2 incompleta; otros estados se conservan si aparecieran. |
| p1121 | numérico | 0 | Electricidad como alumbrado: 1 sí, 0 no. |
| p1144 | numérico | 0 | Conexión de internet fijo/móvil en hogar: 1 sí, 0 no; cuestionario 2025 p.4. |
| factor07_vivienda | numérico | 0 | Factor anual del módulo 100. |
| nconglome | texto | 0 | Conglomerado del marco, identificador original, no predictor. |
| sub_conglome | texto | 0 | Subconglomerado del marco, identificador original, no predictor. |
| altitud | numérico | 0 | Altitud del hogar de módulo100, metros; fuera [-100,7000] -> faltante. |
| coincide_vivienda | numérico | 0 | Bandera de auditoría: 1 si la tabla de origen pudo enlazarse; no predictor por defecto. |
| mieperho | numérico | 0 | Miembros del hogar utilizados para per cápita, Sumaria. |
| inghog2d | numérico | 0 | Ingreso neto anual del hogar, Sumaria, soles; se conserva sin sustituir faltantes. |
| gashog2d | numérico | 0 | Gasto anual del hogar, Sumaria, soles. |
| pobreza | numérico | 0 | Sumaria: 1 pobreza extrema, 2 pobreza no extrema, 3 no pobre. |
| factor07_sumaria | numérico | 0 | Factor anual original de Sumaria, unidad hogar. |
| coincide_sumaria | numérico | 0 | Bandera de auditoría: 1 si la tabla de origen pudo enlazarse; no predictor por defecto. |
| edad | numérico | 0 | Alias de P208A (años cumplidos). |
| sexo | numérico | 0 | Alias de P207 (categoría). |
| lengua_materna | numérico | 27 | Alias de P300A (categoría). |
| rural | numérico | 0 | 1 si ESTRATO 6-8; 0 si ESTRATO 1-5; otro -> faltante. |
| escale_area | numérico | 0 | Área contextual: 1 urbana, 2 rural, derivada de ESTRATO. |
| electricidad | numérico | 0 | P1121 recodificada: 1 sí, 0 no; otros -> faltante. |
| internet_hogar | numérico | 0 | P1144 recodificada: conexión de internet fijo/móvil, 1 sí, 0 no; otros -> faltante. |
| ingreso_pc_mensual | numérico | 0 | INGHOG2D / (12*MIEPERHO), solo denominador >0. Soles por persona/mes. |
| gasto_pc_mensual | numérico | 0 | GASHOG2D / (12*MIEPERHO), solo denominador >0. Soles por persona/mes. |
| peso_persona | numérico | 0 | Alias FACPOB07, peso de población; revisar uso según análisis, no predictor. |
| peso_hogar | numérico | 0 | Alias FACTOR07 de Sumaria, unidad hogar; no sumar por cada estudiante para estimar hogares. |
| peso_educacion | numérico | 0 | Alias FACTORA07 de educación, peso de población ajustado por grupos quinquenales. |
| matriculado | numérico | 27 | P306 1 -> 1, 2 -> 0; otros -> faltante. |
| asiste | numérico | 3287 | P307 1 -> 1, 2 -> 0; otros -> faltante. |
| no_uso_internet | numérico | 27 | P314A 2 -> 1, 1 -> 0; otros -> faltante. Etiqueta potencial, no predictor digital. |
| exclusion_digital | numérico | 5538 | NO_USO_INTERNET solo si ASISTE=1; demás -> faltante. Proxy operativo; no mide competencias. |
| escale_servicios | numérico | 425 | Número de servicios escolares activos de primaria y secundaria por distrito+área. |
| escale_instituciones | numérico | 425 | CODINST distintos en servicios elegibles; no confundir con servicios ni locales. |
| escale_alumnos | numérico | 425 | Suma TALUM de servicios elegibles por distrito+área. |
| escale_docentes | numérico | 425 | Suma TDOC de servicios elegibles por distrito+área; no personas docentes únicas. |
| escale_secciones | numérico | 425 | Suma TSEC por distrito+área. |
| prop_publicas | numérico | 425 | Proporción de servicios elegibles con GESTION 1 o 2; gestión3 privada. |
| escale_prop_imputadas | numérico | 425 | Proporción de servicios con IMPUTADO parcial o total de MINEDU. |
| escale_cobertura_padlocal | numérico | 425 | Fracción de servicios cuyo local está activo y coincide en distrito/área con Padlocal. |
| escale_latitud | numérico | 425 | Promedio de NLAT_IE en locales distintos (CODLOCAL), distrito+área. |
| escale_longitud | numérico | 425 | Promedio de NLONG_IE en locales distintos (CODLOCAL), distrito+área. |
| escale_locales | numérico | 425 | Locales físicos distintos con Padlocal activo y geografía consistente, por distrito+área. |
| escale_prop_local_compartido | numérico | 425 | Fracción de locales físicos validados con más de un servicio EBR elegible. |
| ratio_alumnos_docente | numérico | 425 | SUM(TALUM)/SUM(TDOC) en distrito+área; faltante si SUM(TDOC)<=0. |
| escale_coincide | numérico | 0 | 1 si UBIGEO+área enlazó a ESCALE, 0 si sin correspondencia. |

## Exclusiones del modelado supervisado

Excluir identificadores, pesos, el objetivo y banderas de coincidencia internas. La única excepción predefinida es ESCALE_COINCIDE: indica disponibilidad de contexto territorial, no la respuesta individual; el modelo la incluye explícitamente. Para exclusión digital, excluir P314A, NO_USO_INTERNET, EXCLUSION_DIGITAL y preguntas posteriores condicionadas por el uso (P314D, P316_5). Si se elige rezago, revisar además edad, nivel/año/grado actual y trayectoria educativa para que los predictores no reconstruyan la etiqueta.

Los indicadores agregados de ESCALE pueden repetirse entre conglomerados del mismo distrito. GroupKFold por CONGLOME cumple el mínimo de la guía; no demuestra por sí solo generalización a distritos no observados.
