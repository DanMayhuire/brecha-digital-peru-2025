# Originales ENAHO y ESCALE: descarga verificable

Los seis CSV/DBF no están en GitHub. Los nombres, versiones y SHA-256 esperados se fijan en `download_manifest.json`; sus URLs son enlaces públicos de los archivos del Drive docente, referencias persistentes de las fuentes. La carpeta de origen es https://drive.google.com/drive/folders/1J2ExK_k8T9TAveZForau6i90lb8Ef7P2?usp=sharing .

## Procedimiento automático

Desde la raíz del repositorio:

```bash
python3 scripts/download_raw_data.py
```

No requiere bibliotecas adicionales: utiliza Python estándar. Descarga los seis ZIP a `data/raw/archives/`, extrae cuatro CSV multianuales y dos DBF, valida cada SHA-256 antes de aceptar el resultado y escribe los manifiestos de preparación. Los originales se conservan con sus nombres; el builder usa únicamente el corte2025. Los manifiestos del estado actual y el archivo de bloqueo de descargas tienen funciones distintas: el último fija los hashes esperados y no se reemplaza por los calculados.

## Archivos públicos exactos

|Módulo|ZIP en Drive|Archivo extraído|
|---|---|---|
|Vivienda|[1041-Modulo1474.zip](https://drive.google.com/file/d/1VyH-kHKHdugOfb2SOSrKC9If2P6eJZLT/view)|inei_enaho/enaho01-2021-2025-100-panel.csv|
|Personas|[1041-Modulo1479.zip](https://drive.google.com/file/d/1Wcl24s3wJQRkZh3BSejHxeYWurtkOu7V/view)|inei_enaho/enaho01-2021-2025-200-panel.csv|
|Educación|[1041-Modulo1475.zip](https://drive.google.com/file/d/1v99MYB7mQhvPeRAN99dnqSqMnH5VduxU/view)|inei_enaho/enaho01a-2021-2025-300-panel.csv|
|Sumaria|[1041-Modulo1478.zip](https://drive.google.com/file/d/1bZk-o8isVoJ9erZok4mI2WMhgix6SC-1/view)|inei_enaho/sumaria-2021-2025-panel.csv|
|Servicios educativos|[00_Padron.zip](https://drive.google.com/file/d/1cDjrSbG10dwnAid7u79Rfp01tQ_8kVXj/view)|minedu_escale/Padron.dbf|
|Locales escolares|[00_Padlocal.zip](https://drive.google.com/file/d/1T6GtuyNHV9iCtMTKAnKgO-1TStDYqe-S/view)|minedu_escale/Padlocal.dbf|

## Alternativa manual si cambia el acceso de Drive

Abra los enlaces anteriores, descargue los seis ZIP y descomprima únicamente los archivos indicados en las rutas relativas de la tabla. Después ejecute el mismo comando automático: comprueba los originales ya colocados mediante SHA-256 y genera los manifiestos sin volver a descargarlos. Si los permisos han cambiado deberá solicitar acceso al propietario; el código no automatiza autenticación ni evade cuotas. Si un archivo cambia de versión, la discrepancia SHA-256 exige revisar la fuente y no debe ignorarse.

También se conserva la recuperación desde los dos ZIP exteriores INEI/MINEDU descargados manualmente de las subcarpetas del profesor:

```bash
python3 scripts/download_raw_data.py --source-dir ./archivos-del-profesor
```

Esa ruta también valida los seis originales contra el bloqueo de hashes. La opción local `--reuse-dir` puede crear enlaces físicos de copias idénticas; no es necesaria, no es predeterminada. Nunca edite un original in situ.
