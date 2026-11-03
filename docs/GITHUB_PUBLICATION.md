# Publicación en GitHub

Solicitud expresa del usuario: commit y push. Destino: https://github.com/DanMayhuire/brecha-digital-peru-2025 ; visibilidad pública existente, conservada; rama main.

Se incluyen código, scripts, pruebas, documentación, metadatos de recuperación, métricas agregadas, figuras e informe. Los cinco notebooks conservan su ejecución real y las tablas e imágenes embebidas; el unificado compila las cuatro fases ejecutadas y declara su procedencia.

El commit nuevo excluye originales CSV/DBF/ZIP, datos procesados, modelos, predicciones y asignaciones por persona, logs, entornos, respaldos y archivos Power BI ajenos. Los originales se recuperan con el procedimiento del README. Las salidas históricas completas y sus registros permanecen localmente; las rutas personales se excluyen de los archivos que se publican.

La comprobación scripts/check_github_ready.py valida el conjunto candidato. Para conocer el commit publicado: git rev-parse HEAD; para verificar el remoto: git remote -v. Este documento no contiene credenciales y no exige subir los datos originales para mostrar los resultados guardados.

## Corrección de destino

El usuario indicó expresamente brecha-digital-peru-2025. Se integra la versión preparada sobre su rama main, preservando el historial y los archivos ya presentes. La exclusión del commit nuevo no elimina procesados/modelos ni resultados que el repositorio ya contenía. No se fuerza ni se reescribe el historial remoto.
