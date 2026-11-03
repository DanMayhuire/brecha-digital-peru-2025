"""Generate the validation summary from executable checks and evaluation records."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]

def main():
    v=json.loads((ROOT/'reports/final_verification.json').read_text())
    r=json.loads((ROOT/'reports/results.json').read_text())
    notebooks=json.loads((ROOT/'reports/notebook_execution.json').read_text())
    if v['status']!='passed' or len(notebooks)!=5 or any(x['status']!='passed' for x in notebooks):
        raise ValueError('Complete verification and notebook execution first')
    unit=next(x for x in v['checks'] if x['name']=='unit_tests');count=re.search(r'Ran (\d+) tests?',unit.get('detail',''))
    best=next(x for x in r['supervised']['test'] if x['seleccionado_cv'])
    lines=['# Verificación del análisis','',f"Los controles ejecutables registran {v['passed_checks']} comprobaciones aprobadas y {len(v['failed_checks'])} fallidas. Las fechas, entradas y hashes se consultan en `reports/final_verification.json` y `reports/notebook_execution.json`.",'','## Notebooks','', '| Archivo | Celdas ejecutadas | Tiempo (s) | Estado |','|---|---:|---:|---|']
    for x in notebooks:lines.append(f"| `{x['notebook']}` | {x['executed_code_cells']} | {x['seconds']:.2f} | {x['status']} |")
    lines += ['', 'Cada notebook ejecuta controles de los datasets y modelos almacenados. Las entradas se identifican mediante SHA-256. El recorrido completo utiliza un kernel propio. El procedimiento de entrenamiento y comparación se encuentra en el README y su registro en `docs/SCIENTIFIC_REPRODUCTION.json`.','', '## Resultados','', '| Magnitud | Valor |','|---|---:|',f"| ROC-AUC ponderada de CatBoost | {best['roc_auc']:.10f} |",f"| AP ponderada de CatBoost | {best['average_precision']:.10f} |",f"| F1 macro ponderado de CatBoost | {best['f1_macro']:.10f} |",f"| Silueta de GMM k=2 | {r['clustering']['selected']['silueta']:.10f} |",f"| Solapamiento de CONGLOME | {r['group_overlap']} |",'', '## Pruebas y alcance','',f"Pruebas unitarias aprobadas: {count.group(1) if count else 'véase registro de unittest'}. Los controles verifican población, llaves, particiones, transformaciones, predicciones, calibración, ponderaciones, clustering, SHAP, notebooks e integridad de artefactos.",'',r['evaluation_note'],'','La ponderación describe la cohorte analítica y no reproduce todo el diseño complejo de ENAHO. El objetivo representa no uso reciente de internet y no una medición completa de competencias digitales.']
    (ROOT/'docs/VALIDACION_FINAL.md').write_text('\n'.join(lines)+'\n')
    print('Documentation generated from validation records.')

if __name__=='__main__':main()
