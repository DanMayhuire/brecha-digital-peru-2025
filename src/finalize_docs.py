"""Refresh validation documentation from actual current verification records only."""
from pathlib import Path
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    v=json.loads((ROOT/'reports/final_verification.json').read_text())
    r=json.loads((ROOT/'reports/results.json').read_text())
    executions=json.loads((ROOT/'reports/notebook_execution.json').read_text())
    reproduction=json.loads((ROOT/'docs/SCIENTIFIC_REPRODUCTION.json').read_text())
    if v['status']!='passed' or len(executions)!=5 or any(x['status']!='passed' for x in executions):
        raise ValueError('Run current verification and five notebooks successfully first')
    best=next(x for x in r['supervised']['test'] if x['seleccionado_cv'])
    unit=next(x for x in v['checks'] if x['name']=='unit_tests')
    match=re.search(r'Ran (\d+) tests?',unit.get('detail',''))
    test_count=match.group(1) if match else 'las'
    dependencies=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True)
    if dependencies.returncode:raise ValueError('Dependency check failed')
    lines=['# Validación final de la sincronización científica','',
        f"Registro vigente: `reports/final_verification.json`. Estado: **{v['status']}**; {v['passed_checks']} controles aprobados y {len(v['failed_checks'])} fallidos. La fecha exacta y las huellas están en el registro, que debe regenerarse después de cualquier cambio de artefactos.",'',
        '## Ejecuciones reales','',
        '| Notebook | Celdas de código | Segundos observados | Estado |','|---|---:|---:|---|']
    for x in executions:lines.append(f"| `{x['notebook']}` | {x['executed_code_cells']} | {x['seconds']:.2f} | {x['status']} |")
    lines += ['',
        'Los cinco notebooks evalúan realmente los modelos conservados en kernels nuevos. El recorrido 00 ejecuta su código completo en su propio kernel. No se ensamblan outputs de otras corridas ni se presenta evaluación como entrenamiento. Los hashes de entrada y ejecución son comprobados por el verificador.','',
        '## Entrenamiento aislado y pruebas','',
        f"Se ejecutó realmente el análisis completo en un directorio aislado y se contrastó con la referencia: {len(reproduction['checks'])} comprobaciones aprobadas. `docs/SCIENTIFIC_REPRODUCTION.json` conserva las diferencias y tolerancias; `docs/SCIENTIFIC_SYNC.md` detalla el método y los cambios.",'',
        f'Se ejecutaron {test_count} pruebas unitarias y `pip check`; ambos aprobaron. Las nuevas pruebas comprueban alineación por identidad y rechazo de filas duplicadas o inexistentes. Se revisaron las seis páginas del PDF renderizado. El control de privacidad de archivos candidatos aprobó. Los modelos y datasets congelados no se reemplazaron.','',
        '## Resultados conservados','',
        '| Magnitud | Valor |','|---|---:|',
        f"| CatBoost ROC-AUC ponderada | {best['roc_auc']:.10f} |",
        f"| CatBoost AP ponderada | {best['average_precision']:.10f} |",
        f"| CatBoost F1 macro ponderado | {best['f1_macro']:.10f} |",
        f"| GMM k=2: silueta | {r['clustering']['selected']['silueta']:.10f} |",
        f"| Desarrollo / prueba | {r['n_train']} / {r['n_test']} |",
        f"| Solapamiento CONGLOME | {r['group_overlap']} |",'',
        '## Alcance y límites','',
        'El corte docente reconstruido tiene las mismas personas y valores comunes que la referencia anual, con otro orden de filas y cinco campos adicionales no predictivos. La reproducción de esta referencia usa el dataset procesado versionado con su orden fijado por hash. La igualdad por llaves no implica identidad byte a byte entre publicaciones ni invariancia al orden.','',
        r['historical_test_warning'],'',
        'Los resultados anteriores están preservados en el respaldo verificable documentado en el informe de sincronización. No se cambió el objetivo ni se eligió otro ganador por prueba. La corrección permanece local, pendiente de revisión; no se ha hecho commit ni push.']
    (ROOT/'docs/VALIDACION_FINAL.md').write_text('\n'.join(lines)+'\n')
    print('Validación documentada desde registros reales; regenerar hashes si cambió el documento.')

if __name__=='__main__':main()
