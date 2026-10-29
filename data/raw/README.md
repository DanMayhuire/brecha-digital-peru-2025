# Fuentes originales

Los ZIP originales permanecen en `${SOURCE_DIR}`.
No se copiaron ni descomprimieron íntegramente en este proyecto. `source_manifest.json`
registra sus rutas, tamaños y hashes SHA-256 para comprobar la procedencia.

`src/build_data.py` abre los ZIP anidados y lee solamente las columnas de 2025
necesarias. No carga nombres, direcciones, teléfonos ni contactos de los colegios.

La carpeta INEI contiene archivos multianuales con hogares paneles y no paneles;
se selecciona el corte de 2025, sin exigir pertenencia a un panel longitudinal.
Los archivos `01_Matricula_01.zip` y `04_Docente_01.zip` de MINEDU contienen
respuestas HTML de bloqueo y no se utilizan como datos. El Padrón válido aporta
los agregados educativos de distrito y área.
