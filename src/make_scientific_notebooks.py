"""Generate genuinely executable reviews of the frozen definitive artifacts."""
from pathlib import Path
import nbformat as nb
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
SETUP='''from pathlib import Path
import sys, json
import pandas as pd
from IPython.display import display, Image, Markdown
from threadpoolctl import threadpool_limits
ROOT=Path.cwd()
if not (ROOT/'src').is_dir(): ROOT=ROOT.parent
sys.path.insert(0,str(ROOT/'src'))
from scientific_audit import evaluate, sha
pd.set_option('display.precision',9)
def audit(phase):
    with threadpool_limits(limits=4): record=evaluate(phase)
    display(pd.DataFrame(record['checks']))
    print('Controles ejecutados:',len(record['checks']),'| Estado:',record['status'])
    print(record['historical_test_warning'])
    return record['detail']
def table(name): display(pd.read_csv(ROOT/'reports/tables'/name))
def figure(name):
    path=ROOT/'reports/figures'/name
    print('Figura:',name,'| SHA-256:',sha(path))
    display(Image(filename=str(path)))
print('Evaluación real de artefactos guardados; no se entrenan clasificadores.')
'''
SECTIONS=[
('01_Ingenieria_Datos_EDA','Integración de datos y análisis exploratorio','dataset',
 'La unidad de análisis es la persona residente habitual de 6 a 17 años. Se conserva el dataset anual y su orden de filas, vinculados al modelo guardado. El corte 2025 del panel docente se reconstruye por separado: sus valores comunes coinciden por llaves, pero su orden es distinto. Este notebook verifica llaves, variables, transformaciones, población, pesos y particiones. La reconstrucción independiente se documenta en docs/SCIENTIFIC_SYNC.md; esta ejecución no se presenta como una reconstrucción desde raw.',
 ['target_comparison.csv','population_flow_model.csv'],['raw_eda.png','eda.png']),
('02_Clustering_Perfilamiento','Segmentación y perfiles socioeducativos','clustering',
 'Se evalúa el GMM guardado de dos componentes. Se recalculan asignaciones, silueta en 2 500 casos con semilla 42, Davies–Bouldin y Calinski–Harabasz en desarrollo; se contrastan tamaños y tasas ponderadas. La etiqueta no interviene en el ajuste ni la selección. La comparación completa y la ablación se contrastan también mediante entrenamiento aislado.',
 ['clustering_comparison.csv','cluster_profiles.csv','clustering_stability.csv'],['clustering.png','silhouette.png']),
('03_Modelado_Supervisado','Clasificación del no uso de internet','classification',
 'Se recalculan predicciones de los cuatro modelos guardados, alineadas por índice y orden. Se verifican columnas, preprocesamiento, pesos, calibración y métricas. La comprobación de calibración reajusta únicamente la sigmoide sobre las predicciones OOF originales de desarrollo. No utiliza prueba. Los clasificadores se mantienen congelados; el entrenamiento completo de 200 ajustes se reproduce y compara aparte. El ganador se seleccionó por AP de cinco folds GroupKFold; las transformaciones se ajustaron dentro de cada fold. Umbral fijo: 0.5. La prueba fue observada anteriormente: esta evaluación es retrospectiva, no una validación externa inédita.',
 ['model_comparison_cv.csv','model_comparison_test.csv','weight_sensitivity.csv'],['model_curves.png','confusion_matrix.png']),
('04_Explicabilidad_SHAP','Explicabilidad e interacciones predictivas','shap',
 'Se recalculan TreeSHAP del CatBoost guardado e interacciones de XGBoost, un complemento que no sustituye al ganador. Se verifican muestra, aditividad, importancia, scores y contribuciones de casos. Las unidades son log-odds anteriores a calibrar, no puntos porcentuales de probabilidad. Las figuras son artefactos definitivos identificados por hash. SHAP describe el modelo, no demuestra causalidad ni mide competencias digitales.',
 ['shap_importance.csv','shap_interactions_xgboost.csv'],['shap_beeswarm.png','shap_dependence_1.png','shap_dependence_2.png','shap_waterfall_alto.png','shap_waterfall_bajo.png','shap_interaction_1.png','shap_interaction_2.png'])]


def make(path,title,cells):
    n=nb.v4.new_notebook()

    n.metadata={'kernelspec':{'name':'ia-project','display_name':'Python IA U2','language':'python'},'language_info':{'name':'python'},'scientific_role':'Real reevaluation of frozen artifacts; independent training documented separately.'}
    n.metadata['scientific_inputs']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/scientific_audit.py','src/run_analysis.py','src/nonlinear_shap.py','models/best_model.joblib','models/clustering.joblib','models/all_models.joblib','data/processed/dataset_enaho_escale_2025.csv','reports/results.json']}
    n.cells=[nb.v4.new_markdown_cell('# '+title),nb.v4.new_code_cell(SETUP),*cells]
    nb.write(n,path)


def main():
    (ROOT/'notebooks').mkdir(exist_ok=True);combined=[]
    for name,title,phase,intro,tables,figures in SECTIONS:
        code=f"detail=audit({phase!r})\n"
        if phase=='classification':code+="print('Ganador:',detail['winner'],'| Umbral:',detail['threshold'])\ndisplay(pd.DataFrame(detail['metrics']))\n"
        elif phase=='shap':code+="print('Modelo:',detail['model'],'| Casos:',detail['n_explained'],'| Residuo:',detail['max_additivity_residual'])\ndisplay(pd.DataFrame(detail['importance']).sort_values('mean_abs_shap',ascending=False))\nprint('Complemento:',detail['complementary_model'],'| Residuo:',detail['xgboost_residual'])\n"
        elif phase=='clustering':code+="display(pd.DataFrame([detail['selected']]))\nprint('Ablación:',detail['access_ablation'])\n"
        else:code+='display(pd.DataFrame([detail]))\n'
        code+='\n'.join(f'table({t!r})' for t in tables)+'\n'
        code+='\n'.join(f'figure({f!r})' for f in figures)
        cells=[nb.v4.new_markdown_cell('## Método y alcance\n\n'+intro),nb.v4.new_code_cell(code)]
        make(ROOT/'notebooks'/f'{name}.ipynb',title,cells)
        combined += [nb.v4.new_markdown_cell('## '+title+'\n\n'+intro),nb.v4.new_code_cell(code)]
    make(ROOT/'notebooks/00_Proyecto_Completo_Ejecutado.ipynb','Brecha digital y no uso de internet: ENAHO + ESCALE 2025',[
        nb.v4.new_markdown_cell('**Inteligencia Artificial · Universidad Peruana Unión**\n\nEste recorrido se ejecuta completo en un kernel propio. No ensambla salidas de otros notebooks. Evalúa artefactos definitivos conservados; el entrenamiento aislado y las diferencias históricas se documentan en docs/SCIENTIFIC_SYNC.md. La prueba previamente observada tiene carácter retrospectivo.'),*combined])
    print('Cinco plantillas generadas; ejecutar src/execute_notebooks.py antes de entregar.')


if __name__=='__main__':main()
