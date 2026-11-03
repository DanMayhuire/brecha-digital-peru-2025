# Plan de mejoras y registro de decisiones

## Prioridad1: validez de datos y objetivo

- Auditar fuentes anuales y panel mediante contenido, no nombre; mantener una fuente canónica.
- Verificar códigos, saltos, universo y factores. Cerrar definición antes de entrenar.
- Auditar y relacionar Padrón/Padlocal sin duplicar servicios, docentes, alumnos ni locales.

## Prioridad2: requisitos parciales de rúbrica

- Completar EDA raw por módulo y flujo de población.
- Añadir análisis no lineal complementario SHAP sin falsear al ganador.
- Regenerar perfilamiento, resultados dependientes e informe4-6p.

## Prioridad3: rigor estadístico

- Búsqueda acotada mayor a2 configs por familia; mismos5 folds, CPU limitada y tiempos.
- Sensibilidad de pesos en desarrollo, calibraciónOOF, baselines constantes y métricas ponderadas/no ponderadas.
- Estabilidad del clustering y diagnóstico de separación trivial por acceso.
- Declarar que la prueba de la versión anterior ya se observó; la revisión no constituye evaluación externa nueva.

## Prioridad4: reproducibilidad

- Scripts canónicos reutilizables por cuatro notebooks que ejecutan fases reales.
- Parquet+CSV, tests de integridad/leakage/métricas/artefactos, final_verification.json.
- Rutas configurables y dependencias existentes, sin actualizaciones indiscriminadas.

## Prioridad5: presentación y entrega

- Informe y Markdown consistentes; render y lectura de todas las páginas.
- README, matriz final, validación y guía de defensa.
- ZIP con manifiesto sin originales voluminosos ni predicciones identificables.

## Condiciones de recálculo

La integración de Padlocal y ampliación de búsqueda/sensibilidad justifican ejecutar resultados dependientes. Se conserva la versión anterior en snapshot. Una corrección puramente textual no justifica repetir entrenamiento.

## Estado inicial

Auditoría completa creada antes de modificar código. Snapshot y estado Git en `snapshots/manifest.json`. Las actividades se cerrarán solamente con evidencia de ejecución.

## Mejoras ejecutadas y pendientes

Se ejecutaron las cinco prioridades: reconciliaciónanual/panel yPadlocal; EDAraw; sensibilidadpesos/HP acotados/estabilidad; interacciones SHAP; cuatro notebooks ejecutables; CSV/Parquet/diccionarios; pruebas y documentación; informe científico y paquete validado. La tabla de cierre y las pruebas exactas están en AUDITORIA_RUBRICA y VALIDACION_FINAL.

Pendientes conceptuales que los archivos no pueden resolver: competencias directas para todos 6–17, infraestructuraescolar no incluida en las fuentes, muestra externa nueva y dominio oral del estudiante. No se cambia arbitrariamente la etiqueta para aparentarcumplimiento. Mejoras opcionales futuras: validación temporal/distrital externa, inferencia con diseño complejo completo y medición directa de competencias. Regresión queda opcional y no se añade por decoración.
