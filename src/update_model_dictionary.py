"""Generate the model data dictionary from actual columns, roles and saved results."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]


def main():
    d=pd.read_parquet(ROOT/'data/processed/dataset_modelado_2025.parquet')
    r=json.loads((ROOT/'reports/results.json').read_text())
    base={}
    for line in (ROOT/'docs/data_dictionary.md').read_text().splitlines():
        if line.startswith('| '):
            cells=[x.strip() for x in line.strip('|').split('|')]
            if len(cells)==4:base[cells[0]]=cells[3]
    features=r['features'];cats=['sexo','lengua_materna','rural','pobreza','electricidad','internet_hogar','escale_coincide']
    descriptions={**base,
      'indice_dataset':'Índice de la fila en la tabla integrada anual. Solo enlaza artefactos de auditoría; nunca se entrena con él.',
      'edad_normativa':'P308C+5 si primaria; P308B+11 si secundaria. Referencia exploratoria, sin cumpleaños al31marzo.',
      'desfase_edad_grado':'Edad de entrevista menos edad normativa. No es la medición administrativa SIAGIE; no predictor digital.',
      'target_rezago':'Etiqueta alternativa descriptiva: desfase>=1, solo grado y nivel válidos. No entrenada ni usada para elegir el objetivo por score.',
      'target_rezago_2':'Sensibilidad descriptiva: desfase>=2, misma cohorte de grado válido. No equivale a edad SIAGIE al31marzo.',
      'target_internet':'Etiqueta principal:1 si P314A=2(no usó internet mes anterior),0 si P314A=1. Solo asistentesEBR elegibles.',
      'log_ingreso_pc':'ln(1+ingreso neto mensual per cápita), solo importe>=0; negativos/faltantes→NA. Sin parámetros aprendidos.',
      'log_gasto_pc':'ln(1+gasto mensual per cápita), solo importe>=0; negativos/faltantes→NA. Sin parámetros aprendidos.'}
    lines=['# Diccionario del dataset de modelado2025','',
      'Generado por `src/update_model_dictionary.py` desde el Parquet real, la lista explícita de predictores y los resultados guardados. Complementa `docs/data_dictionary.md` y `docs/SOURCE_RECONCILIATION.md`.','',
      f'La tabla `data/processed/dataset_modelado_2025.parquet` (CSV compatible: `dataset_modelado_internet_2025.csv`) contiene **{len(d):,} personas, {len(d.columns)} columnas y {len(features)} predictores**. La etiqueta tiene {int(d.target_internet.eq(1).sum()):,} positivos y {int(d.target_internet.eq(0).sum()):,} negativos, conteos muestrales.','',
      '## Cohorte y fuente canónica','',
      'Una fila por residente habitual6–17. Fuente canónica: módulos anuales ENAHO2025(100/200/300/Sumaria); ESCALE Padrón cruzado con Padlocal y agregado por distrito-área. El panel docente se usa únicamente para reconciliación de fuentes. AÑO y llaves se mantienen como texto en Parquet.','',
      'Elegible: P306=P307=1, P308A∈{2,3}, sin CEBA afirmativa(P307D!=1), P314A∈{1,2} y FACPOB07 positivo. Un NA estructural de CEBA no se convierte en afirmación de CEBA; una respuesta faltante de internet no se convierte en clase0.','',
      'No uso reciente es una dimensión operativa de exclusión digital; no acredita falta de competencias. P316B/C tiene universo14+ y saltos por uso de equipo: los NA de menores y no usuarios no significan incapacidad. Estas ramas se retienen solo para auditar esa limitación.','',
      '## Entradas reales del clasificador','',
      '| Predictor | Tipo usado | Definición |','|---|---|---|']
    for c in features:
        lines.append(f"| {c} | {'categoría(one-hot)' if c in cats else 'numérico(mediana/escalado)'} | {descriptions[c]} |")
    lines+=['',
      '`escale_coincide` es la única bandera de cobertura incluida como predictor predefinido: indica disponibilidad del contexto territorial y no contiene la respuesta individual. Las otras banderas de merge no se utilizan. Los agregados escolares describen distrito-área de residencia; no el colegio observado de cada estudiante. La latitud y longitud individuales de hogares no se cargan ni se exportan.','',
      '## Transformaciones, pesos y partición','',
      'Dentro de cada fold se ajustan mediana+StandardScaler para variables numéricas, moda+OneHotEncoder para categorías. El logaritmo determinista se aplica antes de la partición y no estima parámetros. La prueba nunca ajusta imputadores, escalas, categorías, pesos de clase, hiperparámetros ni calibradores.','',
      '`peso_persona`(FACPOB07 del módulo200) es el peso principal individual para selección y evaluación. `peso_hogar`(FACTOR07 Sumaria) es de hogar y no se acumula por estudiante. `peso_educacion`(FACTORA07 del módulo300) es un factor anual de población para educación y se usa como sensibilidad de evaluación. Ningún peso es predictor.','',
      'En desarrollo se comparan por algoritmo cuatro estrategias: uniforme, solo población normalizada, solo clase y población×clase. Los balances y normalizaciones se calculan con el entrenamiento de cada fold. La estrategia se selecciona por AP media ponderada de validación con las mismas cinco particiones, antes de explorar hiperparámetros. Las métricas de sensibilidad se guardan en `weight_sensitivity.csv`; combinar pesos es una alternativa evaluada, no una regla automática.','',
      'La calibración sigmoide usa logits de predicciones OOF y pesos individuales de desarrollo. Umbral fijo0.5; no se optimiza mirando prueba. Se distinguen AP y áreaPR trapezoidal, y métricas muestrales y ponderadas. La búsqueda y selección sobre los mismos folds puede producir optimismo de validación; no se afirma validación anidada.','',
      f"Partición semilla42: {r['n_train']:,} personas / {r['groups_train']:,} conglomerados de desarrollo; {r['n_test']:,} / {r['groups_test']:,} de prueba. Intersección CONGLOME={r['group_overlap']}. GroupKFold de5pliegues en desarrollo. El particionado evalúa conglomerados no vistos, sin garantizar distritos enteramente nuevos.",'']
    if 'supervised' in r:
        lines+=['### Estrategias de ajuste elegidas en desarrollo','', '| Modelo | Estrategia |','|---|---|']
        for model,strategy in r['supervised']['weight_strategies'].items():lines.append(f'| {model} | {strategy} |')
        lines+=['',f"Ganador por AP media de GroupKFold: **{r['supervised']['winner']}**. Esta selección se documenta después de su ejecución; el modelo no se elige por el score de prueba.",'']
    lines+=['## Rol de las columnas realmente presentes','',
      'La presencia en el archivo no implica uso en entrenamiento. Todas las preguntas de la familia P314/P315/P316 y sus saltos/derivados quedan fuera de la lista de predictores; matrícula, asistencia y componentes del objetivo son de auditoría.','',
      '| Columna | Tipo almacenado(Parquet) | Rol | Faltantes | Definición |', '|---|---|---|---:|---|']
    for c in d:
        if c in features:role='predictor categórico' if c in cats else 'predictor numérico'
        elif c=='target_internet':role='etiqueta principal'
        elif c in ['target_rezago','target_rezago_2']:role='etiqueta alternativa descriptiva(no entrenada)'
        elif c in ['peso_persona','facpob07','peso_hogar','peso_educacion','factora07'] or c.startswith('factor07'):role='peso/metadato; no predictor'
        elif c.startswith(('p314','p315','p316')) or c in ['no_uso_internet','exclusion_digital']:role='auditoría condicionada/target; excluido por fuga'
        else:role='auditoría/contexto; no predictor'
        if c not in descriptions:raise ValueError('Missing definition '+c)
        lines.append(f'| {c} | {d[c].dtype} | {role} | {int(d[c].isna().sum())} | {descriptions[c]} |')
    (ROOT/'docs/data_dictionary_model.md').write_text('\n'.join(lines)+'\n')
    print(f'Model dictionary: {len(d)} rows, {len(d.columns)} columns, {len(features)} features')

if __name__=='__main__':main()
