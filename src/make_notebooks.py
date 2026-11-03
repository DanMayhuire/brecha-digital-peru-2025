"""Cuatro recorridos ejecutables: cada fase llama a los scripts canónicos."""
from pathlib import Path
import nbformat as nb
ROOT=Path(__file__).resolve().parents[1]
SETUP='''from pathlib import Path
import os,sys,json,subprocess,time
import pandas as pd
from IPython.display import display,Image,Markdown
ROOT=Path.cwd()
if not (ROOT/'src').is_dir(): ROOT=ROOT.parent
assert (ROOT/'src/run_analysis.py').exists(), 'Abra el notebook dentro del proyecto'
os.environ['MPLCONFIGDIR']=str(ROOT/'tmp/matplotlib')
os.environ['XDG_CACHE_HOME']=str(ROOT/'tmp/cache')
sys.path.insert(0,str(ROOT/'src'))
def run_script(name,*args):
    started=time.perf_counter()
    result=subprocess.run([sys.executable,str(ROOT/'src'/name),*map(str,args)],cwd=ROOT,text=True,capture_output=True)
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports'/f'notebook_{name}_{Path(str(args[-1])).name if args else "run"}.log').write_text(result.stdout+result.stderr)
    print(result.stdout[-4500:].replace(str(ROOT),'${PROJECT_ROOT}').replace(str(Path.home()),'${HOME}'))
    if result.returncode: print(result.stderr); result.check_returncode()
    print(f'Ejecución real completada en {time.perf_counter()-started:.1f} segundos')
def show(name): display(Image(filename=str(ROOT/'reports/figures'/name)))
def table(name): display(pd.read_csv(ROOT/'reports/tables'/name).head(20))
def results(): return json.loads((ROOT/'reports/results.json').read_text())
print('Python:',sys.version.split()[0], '| kernel del entorno del proyecto')
'''
def make(name,title,intro,cells):
    n=nb.v4.new_notebook();n.metadata={'kernelspec':{'name':'ia-u2','display_name':'Python IA U2','language':'python'},'language_info':{'name':'python','version':'3.12'},'canonical_code':'src/'}
    n.cells=[nb.v4.new_markdown_cell('# '+title+'\n\n'+intro),nb.v4.new_code_cell(SETUP)]
    for kind,text in cells:n.cells.append(nb.v4.new_code_cell(text) if kind=='code' else nb.v4.new_markdown_cell(text))
    from notebook_editorial import edit_phase
    edit_phase(n,name)
    nb.write(n,ROOT/'notebooks'/name)
def main():
    make('01_Ingenieria_Datos_EDA.ipynb','1. Ingeniería de datos y EDA desde los originales',
      'Esta fase reconstruye realmente los datos, audita las fuentes y ejecuta el EDA. No carga salidas antiguas como si fueran una ejecución nueva. Los originales ya están organizados en data/raw. Las salidas se guardan tras ejecutar de verdad y pueden verse al abrir el archivo, sin volver a entrenar. La semilla de análisis es42.',[
      ('markdown','## Fuentes del profesor y reconstrucción\nLos originales del profesor ya están preparados en data/raw; no hace falta descomprimirlos durante la exposición. Para reconstruir en otra computadora, siga el README. Esta celda reconstruye datos en el proyecto abierto; use un clon o directorio de trabajo destinado a reproducir para conservar resultados anteriores.'),
      ('code',"run_script('build_data.py','--source','teacher','--raw-dir',ROOT/'data/raw','--run-dir',ROOT)\nrun_script('run_analysis.py','--phase','prepare')"),
      ('markdown','## Calidad y población\nLa información escolar es contexto territorial por distrito/área; no asignamos una escuela concreta a cada encuestado. Los saltos del cuestionario permanecen diferenciados de respuestas negativas.'),
      ('code',"audit=json.loads((ROOT/'reports/tables/data_audit.json').read_text())\ndisplay(pd.DataFrame(audit['merges']).T)\nprint('Población:',audit['filters'])\nprint('Cobertura:',audit['cohort']['escale_match_rate'])\ntable('target_comparison.csv')\nshow('eda.png')\nfor p in sorted((ROOT/'reports/figures').glob('*raw*.png')): display(Image(filename=str(p)))"),
      ('code',"display(Markdown((ROOT/'docs/TARGET_DECISION.md').read_text()))\ndisplay(Markdown((ROOT/'docs/VARIABLE_VALIDATION.md').read_text()))"),
      ('markdown','## Conclusión\nRevise los descartes, los códigos y la cobertura antes de interpretar los datos. P314A mide uso en el mes anterior; no es una prueba de competencias. La imputación y el escalado del modelado se ajustan después, dentro de cada fold. Las tasas de esta cohorte no son cifras oficiales nacionales.')])
    make('02_Clustering_Perfilamiento.ipynb','2. Clustering y perfiles socioeducativos',
      'Ajusta KMeans y GMM, compara k2–6, calcula estabilidad y una ablación de acceso. La etiqueta y sus ramas no se utilizan para formar ni seleccionar grupos.',[
      ('markdown','## Ajuste real en desarrollo\nLa imputación por mediana y el escalado preceden a la distancia euclidiana/GMM en espacio estandarizado. Silueta usa hasta2500observaciones con semilla42; DB/CH usan desarrollo completo. Se prioriza silueta entre soluciones con todos los grupos de al menos5%.'),
      ('code',"run_script('run_analysis.py','--phase','clustering')\ntable('clustering_comparison.csv')\nshow('clustering.png')\nshow('silhouette.png')"),
      ('markdown','## Estabilidad e interpretación\nARI contrasta asignaciones entre semillas y submuestras80%. La ablación elimina internet/electricidad para medir cuánto depende la separación de esos accesos. La proyección PCA ayuda a visualizar, pero no prueba calidad.'),
      ('code',"table('clustering_stability.csv')\nprint(results()['clustering']['access_ablation'])\ntable('cluster_profiles.csv')"),
      ('markdown','## Conclusión\nDescriba tamaños, condiciones del hogar, lengua, pobreza y contexto escolar a partir de la tabla. Las tasas de no uso se incorporan solo para caracterización posterior. Las medias de perfil están ponderadas; el ajuste y las métricas geométricas no. Los grupos son perfiles estadísticos exploratorios, no categorías causales.')])
    make('03_Modelado_Supervisado.ipynb','3. Modelado supervisado, pesos y evaluación',
      'Esta fase ejecuta200ajustes máximos en desarrollo: sensibilidad de pesos por familia y búsqueda acotada de seis configuraciones por familia, con los mismos cinco folds agrupados. Puede tardar varios minutos; el tiempo real queda registrado.',[
      ('markdown','## Protocolo y configuraciones\nLa selección usa AP ponderada de validación. La prueba heredada ya se observó en una versión anterior; se conserva por comparabilidad y esta revisión es retrospectiva. Nunca se cambia el ganador según prueba.'),
      ('code',"from run_analysis import models_config,assert_features\nfor name,model,configs in models_config(): print(name,configs)\ndisplay(Markdown((ROOT/'docs/MODELING_PROTOCOL.md').read_text()))"),
      ('markdown','## Entrenamiento y calibración reales\nCada fold ajusta su imputación, escalado y one-hot exclusivamente en entrenamiento. Se calibra con predicciones OOF de desarrollo y pesos de población. El umbral principal permanece0.5.'),
      ('code',"run_script('run_analysis.py','--phase','supervised')\nprint('Ganador CV:',results()['supervised']['winner'])\ntable('weight_sensitivity.csv')\ntable('model_comparison_cv.csv')\ntable('model_comparison_test.csv')\ntable('constant_baselines_test.csv')"),
      ('code',"show('model_curves.png')\nshow('confusion_matrix.png')\ntable('subgroup_performance_test.csv')"),
      ('markdown','## Conclusión\nAP y áreaPRtrapezoidal son resúmenes diferentes. Discuta recall, especificidad, FP/FN y calibración, además de AUC. La ponderación no reproduce por sí sola todo el diseño complejo. Las diferencias de rendimiento no equivalen automáticamente a significación estadística ni a un uso operativo validado.')])
    make('04_Explicabilidad_SHAP.ipynb','4. SHAP del ganador e interacciones no lineales',
      'Recalcula las explicaciones del ganador real y un análisis explícito de interaccionesTreeSHAP de XGBoost. Este complemento no cambia el ganador y no atribuye causalidad.',[
      ('markdown','## Explicación real\nSHAP explica el score antes de calibrar. Se documentan referencia, muestra y unidades; las probabilidades calibradas son distintas. Los dos casos son extremos correctamente clasificados y se presentan sin identificadores personales.'),
      ('code',"run_script('run_analysis.py','--phase','shap')\nr=results()\nprint('Ganador:',r['supervised']['winner'],'| unidades:',r['shap']['units'])\nprint('Residuo aditividad:',r['shap']['max_additivity_residual'])\ntable('shap_importance.csv')\nfor name in ['shap_beeswarm.png','shap_dependence_1.png','shap_dependence_2.png','shap_waterfall_alto.png','shap_waterfall_bajo.png']: show(name)"),
      ('markdown','## Interacciones del árbol\nLas dependencias coloreadas no prueban por sí solas una interacción. Aquí se calculan valores de interacciónTreeSHAP: el par aporta2φij al score. Los pares se seleccionan exploratoriamente por contribución absoluta, sin afirmar significación.'),
      ('code',"print({k:v for k,v in r['nonlinear_shap'].items() if k!='pairs'})\ntable('shap_interactions_xgboost.csv')\nfor name in ['shap_nonlinear_dependence_1.png','shap_nonlinear_dependence_2.png','shap_interaction_1.png','shap_interaction_2.png']: show(name)"),
      ('markdown','## Conclusión\nExplique qué modelo produce cada figura y cómo se reconstruye su score. Una contribución predictiva no es un efecto causal ni un diagnóstico de habilidades digitales. Los casos extremos ilustran mecanismos del modelo y no representan al conjunto de estudiantes.')])
    print('Cuatro notebooks creados con ejecución real de fases canónicas.')
if __name__=='__main__':main()
