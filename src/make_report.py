"""Genera el artículo de seis páginas a partir de resultados ya calculados.

No calcula modelos ni cambia decisiones. Requiere reports/results.json completo
con SHAP y todas las figuras; exporta PDF y una versión Markdown editable.
"""
from pathlib import Path
import json
import html
import argparse
import csv
import re

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import ImageReader
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/Informe_U2_Brecha_Digital_2025.pdf'
FIG = ROOT / 'reports/figures'
TAB = ROOT / 'reports/tables'
INK = colors.HexColor('#172c40')
TEAL = colors.HexColor('#087d84')
LIGHT = colors.HexColor('#edf5f5')
GRAY = colors.HexColor('#52616b')
W,H = A4
M=42
CW=W-2*M

def n(x): return f'{int(x):,}'.replace(',',' ')
def pct(x): return f'{100*float(x):.1f}%'
def f(x,k=3): return f'{float(x):.{k}f}'
def esc(x): return html.escape(str(x),quote=False)
def readcsv(name):
    with (TAB/name).open(encoding='utf-8') as h:return list(csv.DictReader(h))

def paper_figures(r):
    """Replot de explicaciones guardadas, sin ajustar modelos ni cambiar métricas.

    Los formatos pequeños mantienen fuentes impresas legibles. El muestreo y
    las contribuciones se contrastan con las salidas canónicas antes de dibujar.
    """
    import os
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'tmp/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import joblib
    import shap
    from catboost import Pool,CatBoostClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import silhouette_samples,roc_curve,precision_recall_curve
    from threadpoolctl import threadpool_limits
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':9,
      'xtick.labelsize':8.5,'ytick.labelsize':8.5,'axes.spines.top':False,
      'axes.spines.right':False,'savefig.dpi':300})
    data=pd.read_csv(ROOT/'data/processed/dataset_modelado_internet_2025.csv').set_index('indice_dataset')
    parts=pd.read_csv(TAB/'partitions.csv')
    train=data.loc[parts.loc[parts.particion.eq('desarrollo'),'indice']]
    test=data.loc[parts.loc[parts.particion.eq('prueba'),'indice']]
    bundle=joblib.load(ROOT/'models/best_model.joblib');features=bundle['features']
    train[features]=train[features].astype(float);test[features]=test[features].astype(float)
    pipe=bundle['pipeline'];ct=pipe.named_steps['preprocess'];model=pipe.named_steps['model']
    rng=np.random.default_rng(r['seed']);sample=rng.choice(len(test),min(600,len(test)),replace=False)
    # Recover extremes from saved predictions; public results need no row identifiers.
    predictions=pd.read_csv(TAB/'test_predictions.csv').set_index('indice').loc[test.index]
    probability=predictions[bundle['winner']].to_numpy();target=predictions.y.to_numpy()
    high=np.flatnonzero((target==1)&(probability>=.5));low=np.flatnonzero((target==0)&(probability<.5))
    extra=[high[np.argmax(probability[high])],low[np.argmin(probability[low])]]
    ids=np.unique(np.r_[sample,extra]);sub=test.iloc[ids];z=ct.transform(sub[features])
    if isinstance(model,CatBoostClassifier):
        raw=model.get_feature_importance(Pool(z),type='ShapValues');sv=raw[:,:-1];base=raw[:,-1]
        expected=model.predict(z,prediction_type='RawFormulaVal')
    elif isinstance(model,LogisticRegression):
        mean=ct.transform(train[features]).mean(axis=0);sv=(z-mean)*model.coef_[0]
        base=np.repeat(model.intercept_[0]+mean@model.coef_[0],len(z));expected=model.decision_function(z)
    else:
        result=shap.TreeExplainer(model)(z);sv=result.values;base=result.base_values
        if sv.ndim==3:sv=sv[:,:,1];base=base[:,1]
        expected=model.predict_proba(z)[:,1] if isinstance(model,RandomForestClassifier) else model.predict(z,output_margin=True)
    assert np.max(np.abs(np.asarray(base)+sv.sum(axis=1)-expected))<.01
    def origins(transformer):
        return [max([f for f in features if n.split('__',1)[1]==f or n.split('__',1)[1].startswith(f+'_')],key=len)
                for n in transformer.get_feature_names_out()]
    orig=np.array(origins(ct));agg=np.column_stack([sv[:,orig==f].sum(axis=1) for f in features])
    actual=np.abs(agg).mean(axis=0);expected_importance={v['variable']:v['mean_abs_shap'] for v in r['shap']['importance']}
    assert np.allclose(actual,[expected_importance[f] for f in features],rtol=1e-5,atol=1e-6)
    def save(name):
        plt.savefig(FIG/name,bbox_inches='tight',pad_inches=.025,facecolor='white');plt.close()
    for k,(x,color) in enumerate([('log_gasto_pc','rural'),('internet_hogar','lengua_materna')],1):
        fig,ax=plt.subplots(figsize=(3.25,1.70))
        sc=ax.scatter(sub[x],agg[:,features.index(x)],c=sub[color],s=4.7,cmap='coolwarm',alpha=.65,rasterized=True)
        ax.set(xlabel='Log gasto per cápita' if k==1 else 'Internet del hogar (0/1)',ylabel='SHAP (log-odds)')
        cb=fig.colorbar(sc,ax=ax,fraction=.05,pad=.035)
        cb.set_label('Rural (0/1)' if k==1 else 'Lengua (código)',size=8)
        if k==1:cb.set_ticks([0,1])
        cb.ax.tick_params(labelsize=7.5);save(f'paper_shap_dependence_{k}.png')
    # Interacciones del mismo modelo y de la misma muestra canónica de 180 casos.
    xgb=joblib.load(ROOT/'models/all_models.joblib')['pipelines']['XGBoost']
    transformer=xgb.named_steps['preprocess'];tree=xgb.named_steps['model']
    sample=np.random.default_rng(r['seed']).choice(len(test),r['nonlinear_shap']['n_explained'],replace=False)
    sub=test.iloc[sample];z=transformer.transform(sub[features])
    ex=shap.TreeExplainer(tree,feature_perturbation='tree_path_dependent',model_output='raw')
    with threadpool_limits(limits=4):iv=np.asarray(ex.shap_interaction_values(z))
    origin=np.array(origins(transformer))
    for k,pair in enumerate(r['nonlinear_shap']['pairs'][:2],1):
        x=pair['variable_1'];color=pair['variable_2']
        i=np.flatnonzero(origin==x);j=np.flatnonzero(origin==color)
        values=2*iv[:,i,:][:,:,j].sum(axis=(1,2))
        assert np.isclose(np.mean(np.abs(values)),pair['mean_abs_pair_contribution'],rtol=1e-5,atol=1e-6)
        fig,ax=plt.subplots(figsize=(3.25,1.70))
        sc=ax.scatter(sub[x],values,c=sub[color],s=6,cmap='viridis',alpha=.7,rasterized=True)
        ax.axhline(0,color='gray',lw=.6)
        ax.set(xlabel='Altitud (m)' if x=='altitud' else NAMES.get(x,x),ylabel='Interacción 2φij')
        cb=fig.colorbar(sc,ax=ax,fraction=.05,pad=.035)
        cb.set_label('Proporción pública' if color=='prop_publicas' else 'Alumnos/docente' if color=='ratio_alumnos_docente' else NAMES.get(color,color),size=7.5)
        cb.ax.tick_params(labelsize=7.5);save(f'paper_shap_interaction_{k}.png')
    # Silueta reproducible del ajuste ya guardado; no se reestima el clustering.
    clustered=joblib.load(ROOT/'models/clustering.joblib');z=clustered['preprocess'].transform(train[clustered['features']])
    labels=clustered['model'].predict(z);rng=np.random.default_rng(r['seed'])
    rng.choice(len(z),min(5000,len(z)),replace=False) # misma secuencia de la figura canónica
    ids=rng.choice(len(z),min(1800,len(z)),replace=False)
    with threadpool_limits(limits=4):values=silhouette_samples(z[ids],labels[ids])
    fig,ax=plt.subplots(figsize=(2.6,1.65));y0=4
    for group in sorted(np.unique(labels)):
        vals=np.sort(values[labels[ids]==group]);y1=y0+len(vals)
        ax.fill_betweenx(np.arange(y0,y1),0,vals,color=plt.cm.viridis(group/max(1,len(np.unique(labels))-1)),alpha=.8)
        ax.text(-.07,(y0+y1)/2,str(group),fontsize=9,va='center');y0=y1+4
    ax.axvline(np.mean(values),color='gray',linestyle='--',linewidth=.7)
    ax.set(xlabel='Silueta',ylabel='Grupo',yticks=[]);save('paper_silhouette.png')
    # Las curvas de prueba y PCA se redibujan desde predicciones/ajustes guardados.
    # El ancho físico coincide con el del artículo para no reducir fuentes a 4 pt.
    palette=['#117c83','#db8e39','#6654a1','#4575a5']
    comp=pd.read_csv(TAB/'clustering_comparison.csv')
    fig,axs=plt.subplots(1,2,figsize=(7.0,2.2))
    for j,method in enumerate(['KMeans','GMM']):
        row=comp[comp.metodo.eq(method)];axs[0].plot(row.k,row.silueta,'o-',label=method,color=palette[j],markersize=3)
    axs[0].set(xlabel='Número de grupos',ylabel='Silueta',xticks=range(2,7));axs[0].legend(fontsize=8,frameon=False)
    projection=clustered['pca'].transform(z)
    idx=np.random.default_rng(r['seed']).choice(len(z),min(5000,len(z)),replace=False)
    axs[1].scatter(projection[idx,0],projection[idx,1],c=labels[idx],cmap='viridis',s=2,alpha=.45,rasterized=True)
    variance=clustered['pca'].explained_variance_ratio_
    axs[1].set(xlabel=f'PC1 ({variance[0]:.0%})',ylabel=f'PC2 ({variance[1]:.0%})')
    fig.subplots_adjust(left=.075,right=.99,bottom=.24,top=.96,wspace=.30);save('paper_clustering.png')
    preds=pd.read_csv(TAB/'test_predictions.csv');yy=preds.y.to_numpy();ww=preds.peso.to_numpy()
    fig,axs=plt.subplots(1,3,figsize=(7.0,1.93))
    short={'Logística':'Logit','Random Forest':'RF','XGBoost':'XGB','CatBoost':'Cat'}
    for i,name in enumerate(['Logística','Random Forest','XGBoost','CatBoost']):
        prob=preds[name].to_numpy();fpr,tpr,_=roc_curve(yy,prob,sample_weight=ww)
        precision,recall,_=precision_recall_curve(yy,prob,sample_weight=ww)
        axs[0].plot(fpr,tpr,label=short[name],color=palette[i],linewidth=.9)
        axs[1].plot(recall,precision,color=palette[i],linewidth=.9)
        bins=pd.cut(prob,np.linspace(0,1,11),include_lowest=True);xx=[];zz=[]
        for b in bins.categories:
            mask=bins==b
            if mask.sum()>=10:xx.append(np.average(prob[mask],weights=ww[mask]));zz.append(np.average(yy[mask],weights=ww[mask]))
        axs[2].plot(xx,zz,'o-',markersize=2,color=palette[i],linewidth=.9)
    axs[0].plot([0,1],[0,1],'--',color='gray',linewidth=.6)
    axs[0].set(xlabel='FPR',ylabel='TPR',title='ROC');axs[0].legend(fontsize=8,ncol=2,frameon=False,columnspacing=.6,handlelength=1,loc='lower right')
    axs[1].axhline(np.average(yy,weights=ww),ls='--',color='gray',linewidth=.6)
    axs[1].set(xlabel='Recall',ylabel='Precisión',title='Precisión-recall')
    axs[2].plot([0,1],[0,1],'--',color='gray',linewidth=.6)
    axs[2].set(xlabel='p media',ylabel='Frecuencia',title='Calibración')
    for ax in axs:
        ax.set_xlim(0,1);ax.set_ylim(0,1.02);ax.set_xticks([0,.5,1]);ax.set_yticks([0,.5,1]);ax.title.set_fontsize(9)
    fig.subplots_adjust(left=.06,right=.99,bottom=.27,top=.83,wspace=.48);save('paper_model_curves.png')
    matrix=np.asarray(r['supervised']['confusion_counts'])
    fig,ax=plt.subplots(figsize=(2.55,2.1));ax.imshow(matrix,cmap='Blues')
    for row in range(2):
        for col in range(2):
            ax.text(col,row,n(matrix[row,col]),ha='center',va='center',fontsize=11,
              color='white' if matrix[row,col]>matrix.max()/2 else '#172c40')
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Uso','No uso'],yticklabels=['Uso','No uso'],
      xlabel='Predicción',ylabel='Observación',title=r['supervised']['winner'])
    ax.title.set_fontsize(9);fig.subplots_adjust(left=.23,right=.98,bottom=.23,top=.88);save('paper_confusion_matrix.png')
    provenance={'purpose':'Figuras de artículo con fuentes mayores; sin reajuste ni selección',
      'dataset_sha256':r['dataset_sha256'],'run_signature':r['run_signature'],
      'winner':r['supervised']['winner'],'winner_sample':len(agg),'nonlinear_sample':len(sub),
      'checks':'SHAP agrupado coincide con importancia canónica; pares coinciden con JSON; misma secuencia de submuestra de silueta.'}
    (FIG/'paper_figures_provenance.json').write_text(json.dumps(provenance,indent=2,ensure_ascii=False),encoding='utf-8')

def markdown(text):
    """Conservar semántica y enlaces del PDF en Markdown editable estándar."""
    text=re.sub(r'<link href="([^"]+)"[^>]*>(.*?)</link>',r'[\2](\1)',text)
    for tag,mark in [('b','**'),('i','*')]:text=text.replace(f'<{tag}>',mark).replace(f'</{tag}>',mark)
    text=re.sub(r'<br\s*/?>','\n\n',text)
    return html.unescape(re.sub(r'<[^>]+>','',text))

NAMES={'log_gasto_pc':'log gasto per cápita','edad':'edad','lengua_materna':'lengua materna',
  'electricidad':'electricidad','internet_hogar':'internet del hogar','prop_publicas':'proporción pública',
  'rural':'ruralidad','log_ingreso_pc':'log ingreso per cápita','altitud':'altitud','sexo':'sexo',
  'pobreza':'pobreza','ratio_alumnos_docente':'alumnos/docente distrital','escale_coincide':'cobertura ESCALE'}
WEIGHTS={'uniform':'uniforme','population':'poblacional','class':'balance de clase','population_class':'poblacional + clase'}

class Article:
    def __init__(self,path):
        self.c=canvas.Canvas(str(path),pagesize=A4,pageCompression=1)
        self.c.setTitle('Brecha digital y no uso de internet en estudiantes: ENAHO-ESCALE 2025')
        self.c.setAuthor('Inteligencia Artificial - Universidad Peruana Unión')
        self.c.setSubject('Evaluación U2. Análisis reproducible, clasificación y explicabilidad.')
        self.page=0;self.y=0;self.md=[]

    def new(self):
        if self.page:self.c.showPage()
        self.page+=1;self.y=H-58
        self.c.setStrokeColor(TEAL);self.c.setLineWidth(1.1)
        self.c.line(M,H-36,W-M,H-36)
        self.c.setFont('Helvetica',7.5);self.c.setFillColor(GRAY)
        self.c.drawString(M,H-27,'INTELIGENCIA ARTIFICIAL | EVALUACIÓN U2 | ENAHO-ESCALE 2025')
        self.c.line(M,36,W-M,36)
        self.c.drawString(M,24,'Universidad Peruana Unión | Revisión: 3 de noviembre de 2026')
        self.c.drawRightString(W-M,24,f'{self.page} / 6')
        self.md.append('\n\n---\n')

    def check(self,height):
        if self.y-height<47:raise ValueError(f'Página {self.page}: desborde {height:.1f}; y={self.y:.1f}')

    def para(self,text,size=9.4,leading=12.7,gap=7,color=INK,markdown=True):
        style=ParagraphStyle('body',fontName='Times-Roman',fontSize=size,leading=leading,
            textColor=color,spaceAfter=0,allowWidows=0,allowOrphans=0)
        p=Paragraph(text,style);_,height=p.wrap(CW,1000)
        self.check(height+gap);p.drawOn(self.c,M,self.y-height);self.y-=height+gap
        if markdown:self.md.append(globals()['markdown'](text)+'\n')

    def heading(self,text):
        self.para(esc(text),size=12,leading=15,gap=8,color=TEAL,markdown=False)
        self.md.append('## '+text+'\n')

    def small(self,text,gap=6):self.para(text,size=8.2,leading=10.2,gap=gap,color=GRAY)

    def table(self,headers,rows,widths=None,size=8.5):
        widths=widths or [CW/len(headers)]*len(headers)
        st=ParagraphStyle('cell',fontName='Helvetica',fontSize=size,leading=size+2,textColor=INK)
        hs=ParagraphStyle('head',parent=st,fontName='Helvetica-Bold',textColor=colors.white)
        data=[[Paragraph(esc(h),hs) for h in headers]]+[[Paragraph(esc(v),st) for v in r] for r in rows]
        t=Table(data,colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),TEAL),
            ('BACKGROUND',(0,1),(-1,-1),colors.white),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),
            ('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),
            ('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LINEBELOW',(0,0),(-1,0),.4,TEAL)]))
        _,height=t.wrap(CW,1000);self.check(height+9);t.drawOn(self.c,M,self.y-height);self.y-=height+9
        self.md+=['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']
        self.md+=['| '+' | '.join(map(str,r))+' |' for r in rows];self.md.append('')

    def image(self,name,width=CW,cap=None,maxheight=None):
        path=FIG/name
        im=Image.open(path);height=width*im.height/im.width
        if maxheight and height>maxheight:width*=maxheight/height;height=maxheight
        self.check(height+8)
        self.c.drawImage(ImageReader(im),M+(CW-width)/2,self.y-height,width,height,mask='auto')
        self.y-=height+5
        self.md.append(f'![{markdown(cap or name)}](figures/{name})\n')
        if cap:self.small(cap)

    def paired(self,a,b,capa,capb,maxheight=None):
        gap=12;width=(CW-gap)/2
        ims=[Image.open(FIG/a),Image.open(FIG/b)]
        heights=[width*im.height/im.width for im in ims]
        height=max(heights)
        if maxheight and height>maxheight:
            ratio=maxheight/height;width*=ratio;heights=[h*ratio for h in heights];height=maxheight
        self.check(height+35)
        for j,(im,h) in enumerate(zip(ims,heights)):
            self.c.drawImage(ImageReader(im),M+j*((CW-gap)/2+gap),self.y-h,width,h,mask='auto')
        self.y-=height+4
        style=ParagraphStyle('cap',fontName='Helvetica',fontSize=8,leading=10,textColor=GRAY)
        caps=[Paragraph(capa,style),Paragraph(capb,style)]
        hs=[p.wrap((CW-gap)/2,200)[1] for p in caps]
        for j,p in enumerate(caps):p.drawOn(self.c,M+j*((CW-gap)/2+gap),self.y-hs[j])
        self.y-=max(hs)+8
        self.md.append(f'![{markdown(capa)}](figures/{a})\n\n![{markdown(capb)}](figures/{b})\n')

    def diagram(self,total):
        height=78;self.check(height+9);c=self.c;top=self.y
        boxes=[('ENAHO 200 + 300','Persona: 4 llaves'),('ENAHO 100 + Sumaria','Hogar: 3 llaves'),('Padrón + Padlocal','Local -> distrito-área')]
        width=(CW-24)/3
        for j,(a,b) in enumerate(boxes):
            x=M+j*(width+12);c.setFillColor(LIGHT);c.setStrokeColor(TEAL)
            c.roundRect(x,top-36,width,34,4,fill=1,stroke=1)
            c.setFillColor(INK);c.setFont('Helvetica-Bold',8.5);c.drawCentredString(x+width/2,top-15,a)
            c.setFont('Helvetica',8);c.drawCentredString(x+width/2,top-27,b)
            c.line(x+width/2,top-38,x+width/2,top-49)
        c.line(M+width/2,top-49,W-M-width/2,top-49)
        c.line(W/2,top-49,W/2,top-56)
        c.setFillColor(TEAL);c.roundRect(M+CW*.15,top-78,CW*.7,23,4,fill=1,stroke=0)
        c.setFillColor(colors.white);c.setFont('Helvetica-Bold',9)
        c.drawCentredString(W/2,top-70,f'Cohorte analítica 2025 | {n(total)} estudiantes')
        self.y-=height+9
        self.md.append('Cruce: ENAHO 200 + 300 por persona; 100 + Sumaria por hogar; Padrón + Padlocal por CODLOCAL, luego agregado por UBIGEO y área.\n')

    def local_waterfalls(self,cases,units):
        """Waterfalls vectoriales de los mismos SHAP: top 5 + resto aditivo exacto."""
        gap=18;pw=(CW-gap)/2;height=172
        self.check(height+40);top=self.y;c=self.c
        names={'log_gasto_pc':'Gasto per cápita (log)','edad':'Edad',
          'lengua_materna':'Lengua (código)','electricidad':'Electricidad',
          'internet_hogar':'Internet hogar','prop_publicas':'Proporción pública',
          'rural':'Área rural','log_ingreso_pc':'Ingreso per cápita (log)',
          'altitud':'Altitud','sexo':'Sexo','pobreza':'Pobreza'}
        for j,key in enumerate(['alto','bajo']):
            case=cases[key];x0=M+j*(pw+gap);left=x0+111;right=x0+pw-5
            vals=[dict(v) for v in case['top_contribuciones']]
            rest=case['score_modelo']-case['score_base']-sum(v['shap'] for v in vals)
            vals.append({'variable':'resto','shap':rest,'valor':None})
            path=[case['score_base']]
            for v in vals:path.append(path[-1]+v['shap'])
            assert abs(path[-1]-case['score_modelo'])<1e-8
            lo=min(path)-.25;hi=max(path)+.25
            xx=lambda x:left+(x-lo)/(hi-lo)*(right-left)
            c.setFont('Helvetica-Bold',9);c.setFillColor(INK)
            c.drawString(x0,top-10,'Caso sin uso' if key=='alto' else 'Caso con uso')
            c.setFont('Helvetica',8.4);c.setFillColor(GRAY)
            c.drawString(x0,top-23,f'p calibrada de no uso: {pct(case["probabilidad_calibrada"])}')
            y0=top-43
            for i,v in enumerate(vals):
                y=y0-i*17.2;before=path[i];after=path[i+1]
                label=names.get(v['variable'],'Otras variables')
                if v['valor'] is not None:
                    val=v['valor'];fmt=f'{val:.0f}' if float(val).is_integer() else f'{val:.2f}'
                    label+=f' = {fmt}'
                c.setFont('Helvetica',8);c.setFillColor(INK)
                c.drawRightString(left-8,y+2,label)
                positive=v['shap']>=0
                c.setFillColor(colors.HexColor('#e83d72') if positive else colors.HexColor('#149bd7'))
                x1,x2=xx(before),xx(after)
                c.rect(min(x1,x2),y-1,max(abs(x2-x1),.9),10,fill=1,stroke=0)
                c.setFont('Helvetica-Bold',7.6);c.setFillColor(INK)
                valtext=f'{v["shap"]:+.2f}'
                if abs(x2-x1)>33:
                    c.setFillColor(colors.white);c.drawCentredString((x1+x2)/2,y+1.3,valtext)
                else:
                    tx=min(max((x1+x2)/2,left+13),right-13)
                    c.drawCentredString(tx,y+11,valtext)
                if i<len(vals)-1:
                    c.setStrokeColor(colors.HexColor('#bcc7cb'));c.setLineWidth(.5)
                    c.setDash(1,2);c.line(x2,y-1,x2,y-8.2);c.setDash()
            ay=top-height+9;c.setStrokeColor(GRAY);c.setLineWidth(.5);c.line(left,ay,right,ay)
            c.setFillColor(GRAY);c.setFont('Helvetica',7.5)
            for tick in [lo+(hi-lo)*i/3 for i in range(4)]:
                x=xx(tick);c.line(x,ay,x,ay-3);c.drawCentredString(x,ay-12,f'{tick:.1f}')
            c.drawString(x0,ay-12,f'Base {case["score_base"]:.3f}; final {case["score_modelo"]:.3f}')
        self.y-=height+28
        self.small(f'<b>Figuras 11 y 12.</b> Waterfalls SHAP del score antes de calibrar ({esc(units)}), con cinco contribuciones principales y el resto agregado. Base + contribuciones = score final; la probabilidad calibrada se informa por separado.')
        self.md.append('![Waterfall alto](figures/shap_waterfall_alto.png)\n\n![Waterfall bajo](figures/shap_waterfall_bajo.png)\n')

    def finish(self):
        self.c.save()
        count=len(PdfReader(OUT).pages)
        if count!=6:raise ValueError(f'Se esperaban 6 páginas, se generaron {count}')
        (ROOT/'reports/article.md').write_text('\n'.join(self.md),encoding='utf-8')

def generate():
    r=json.loads((ROOT/'reports/results.json').read_text(encoding='utf-8'))
    required=['shap','nonlinear_shap','supervised','clustering']
    if any(key not in r for key in required):
        raise SystemExit('No se genera el informe: faltan resultados finales de robustez/SHAP.')
    if not r['clustering'].get('stability') or not r['supervised'].get('weight_sensitivity'):
        raise SystemExit('No se genera el informe con la versión previa del análisis.')
    audit=json.loads((TAB/'data_audit.json').read_text(encoding='utf-8'))
    if not audit.get('dbf_schemas',{}).get('padlocal'):
        raise SystemExit('No se genera el informe antes de auditar Padlocal.')
    measurement=json.loads((TAB/'target_measurement_audit.json').read_text(encoding='utf-8'))
    skills=measurement['cohorts']['attending_ebr_14_17']
    cv=r['supervised']['cv'];tests=r['supervised']['test'];winner=r['supervised']['winner']
    best=next(x for x in tests if x['modelo']==winner)
    chosen=r['clustering']['selected'];profiles=r['clustering']['profiles'];sh=r['shap'];nonlinear=r['nonlinear_shap']
    total=r['n_eligible'];candidates={x['objetivo']:x for x in r['target_comparison']}
    internet=candidates['target_internet'];positive=internet['n_positivos']
    subgroup=readcsv('eda_subgroups_train.csv')
    area={x['grupo']:float(x['prevalencia']) for x in subgroup if x['variable']=='Área'}
    cases={x['caso']:x for x in sh['cases']}
    fn=r['supervised']['confusion_counts'][1][0];tp=r['supervised']['confusion_counts'][1][1]
    fp=r['supervised']['confusion_counts'][0][1];ci=r['supervised']['bootstrap_95']
    stability=r['clustering']['stability'];ablation=r['clustering']['access_ablation']
    comparison=readcsv('clustering_comparison.csv');search=readcsv('model_search.csv')
    weightrows=r['supervised']['weight_sensitivity'];selectedweights=r['supervised']['weight_strategies']
    rawrows=audit['cohort']['rows'];merges=audit['merges'];filters=audit['filters'];pad=audit['escale']
    range_no_use=[p['no_uso_ponderado'] for p in profiles]
    min_no_use,max_no_use=min(range_no_use),max(range_no_use)
    leading_variables=[NAMES.get(x['variable'],x['variable']) for x in sh['importance'][:3]]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    paper_figures(r)
    a=Article(OUT)
    # Página 1: problema, medición y EDA del desarrollo.
    a.new()
    a.para('<b>Brecha digital y no uso de internet en estudiantes de 6-17 años: integración ENAHO-ESCALE 2025</b>',size=18,leading=21,gap=10)
    a.small('Inteligencia Artificial | Ingeniería de Sistemas | Universidad Peruana Unión<br/>Docente: Mg. Angel Rosendo Condori Coaquira',gap=10)
    a.heading('Resumen')
    a.para(f'Se integraron ENAHO y ESCALE 2025 para analizar {n(total)} residentes de 6-17 años matriculados y asistentes a primaria/secundaria. El objetivo fue clasificar el <b>no uso de internet en el mes anterior</b>, indicador operativo que no mide competencias digitales. '
      f'Se compararon dos métodos de agrupamiento y cuatro clasificadores mediante cinco folds por conglomerado. {esc(winner)} obtuvo la mayor AP de validación; en prueba alcanzó ROC-AUC={f(best["roc_auc"])}, AP={f(best["average_precision"])} y F1 macro={f(best["f1_macro"])}. '
      f'Los perfiles presentan no uso ponderado entre {pct(min_no_use)} y {pct(max_no_use)} en desarrollo. Se auditaron estabilidad del clustering, estrategias de peso y explicaciones SHAP del ganador y de un árbol no lineal. '
      'El diseño es transversal; los resultados describen asociaciones predictivas y requieren validación externa.',size=9.2,leading=12.3)
    a.small('<b>Palabras clave:</b> ENAHO; ESCALE; brecha digital; validación agrupada; clustering; SHAP.')
    a.heading('1. Problema, medición y alcance')
    a.para('La conexión del hogar no garantiza el uso efectivo de internet. Se busca identificar perfiles socioeconómicos y tecnológicos, comparar modelos de no uso y explicar sus decisiones con contexto educativo de distrito y área [1-3]. '
      f'La cohorte contiene {n(positive)} no usuarios y {n(total-positive)} usuarios: {pct(internet["prevalencia_muestral"])} muestral y {pct(r["prevalence_total"])} ponderado, sin presentarlo como tasa oficial nacional. '
      'Clase 1: P314A=2; clase 0: P314A=1; ausencias y pases no se convierten en ceros.')
    a.para(f'Antes de modelar se contrastó el desfase edad-grado: los umbrales de uno y dos años produjeron {n(candidates["target_rezago"]["n_positivos"])} y {n(candidates["target_rezago_2"]["n_positivos"])} positivos, respectivamente. '
      'No se reconstruyó edad al 31 de marzo en esta integración; el desfase observado varía con el mes y no equivale al indicador ESCALE [4]. Se eligió no uso por su medición directa, sin comparar AUC para decidir la etiqueta.',size=9.2,leading=12.3)
    a.image('raw_eda.png',width=418,maxheight=267,cap='<b>Figura 1.</b> EDA de módulos originales antes de cruzar y filtrar la cohorte. El recorte P1-P99 del gasto es sólo visual: no elimina observaciones analíticas. Se conservan valores originales, faltantes y dominios en las tablas de auditoría.')
    a.small(f'En desarrollo (n={n(r["n_train"])}), el no uso ponderado fue {pct(area["Rural"])} en área rural y {pct(area["Urbana"])} en urbana. La figura EDA de la cohorte y los estadísticos previos a imputar acompañan la entrega; son comparaciones descriptivas.')
    a.para(f'<b>Competencias: alcance parcial.</b> P316B/P316C sólo aplica desde 14 años: {n(skills["n"])} elegibles, {n(skills["complete_nine_named_activities"])} autorreportes completos de nueve actividades y {n(skills["zero_nine_activities_reported_conditional_on_observation"])} sin actividades reportadas. '
      'Los saltos del cuestionario se trataron como ausencia estructural de observación. Este universo restringido y el carácter autorreportado de las actividades impiden definir un indicador de competencias comparable para toda la cohorte.',size=9.1,leading=12,gap=0)
    # Página 2: integración real, datos crudos y protocolo antifuga.
    a.new();a.heading('2. Datos, integración y evaluación reproducible')
    if audit.get('source_mode')=='teacher':
        a.para('Se integró el corte transversal de 2025 de ENAHO PANEL 2021-2025 con el Padrón de Servicios Educativos y el Padrón de Locales Escolares de ESCALE [1,2]. La selección incluyó los registros de 2025, sin exigir continuidad longitudinal. La unidad de análisis fue la persona y el contexto educativo se agregó por distrito y área de residencia.')
    else:
        a.para('Se integraron los módulos anuales de vivienda, población y educación de ENAHO 2025 (100, 200 y 300), la base Sumaria y los padrones de servicios educativos y locales escolares de ESCALE [1,2]. '
          'Los registros se enlazaron mediante identificadores de persona, hogar y territorio. El contraste con el corte 2025 del panel ENAHO confirmó la concordancia de los valores comunes utilizados, una vez homogeneizados los formatos.')
    a.diagram(total)
    a.table(['Paso de construcción','Registros / comprobación'],[
      ['Personas ENAHO 2025',n(filters['persons_2025'])],
      ['Edad 6-17 antes / después de residencia',f'{n(filters["age_6_17_before_residency"])} / {n(rawrows)}'],
      ['Cruces educación, vivienda y Sumaria', '; '.join(f'{name}: {pct(merges[name]["matched"]/merges[name]["left_rows"])}' for name in ['educacion','vivienda','sumaria'])],
      ['Contexto ESCALE en base integrada',f'{n(merges["escale"]["matched"])} / {n(merges["escale"]["left_rows"])} ({pct(merges["escale"]["matched"]/merges["escale"]["left_rows"])})'],
      ['Servicios Padrón enlazados a Padlocal',f'{n(pad["padron_padlocal_matched_services"])} / {n(pad["services_before_local_join"])}; conflictos geográficos: {n(pad["geographic_conflicting_services"])}'],
      ['Cohorte matriculada y asistente EBR',f'{n(total)}; sin declaración CEBA'],
      ['Desarrollo / prueba',f'{n(r["n_train"])} / {n(r["n_test"])} personas; {n(r["groups_train"])} / {n(r["groups_test"])} conglomerados']],
      widths=[CW*.47,CW*.53],size=8.4)
    a.para(('<b>Calidad y exploración de datos.</b> Se leyó el corte 2025 en UTF-8 con BOM, separador coma y decimal punto, preservando originales multianuales. Se revisaron faltantes y dominios antes de los cruces; los saltos se conservaron como ausencia estructural de observación. ' if audit.get('source_mode')=='teacher' else '<b>Calidad y exploración de datos.</b> Se verificaron Latin-1, separador punto y coma y coma decimal en los anuales; el panel usa UTF-8 con BOM y coma de separación. Se inspeccionaron faltantes, tipos, dominios, llaves, cuantiles y extremos; los geocódigos conservan ceros iniciales. ') +
      'Se verificaron la unicidad de los identificadores y la cardinalidad de los cruces, sin multiplicación de personas. La exploración de predictores se realizó exclusivamente en desarrollo; las tablas complementarias describen los faltantes y las distribuciones originales.')
    a.para('<b>Cruce contextual.</b> ENAHO 200 y 300 se enlazaron por CONGLOME, VIVIENDA, HOGAR y CODPERSO; 100 y Sumaria, por las tres llaves del hogar. Padrón se unió a Padlocal por CODLOCAL y se filtraron servicios activos de primaria/secundaria. '
      f'La agregación por UBIGEO y área usa suma de alumnos / suma de docentes, proporción pública y coordenadas del Padrón contadas una vez por local validado ({n(pad["physical_locals_validated"])} locales). Padlocal permitió validar la correspondencia geográfica; las coordenadas proceden del Padrón. Se excluyó de la validación geográfica el registro con conflicto territorial.')
    a.para('<b>Prevención de fuga de información.</b> Se exige residencia habitual, edad 6-17, P306=P307=1, P308A primaria/secundaria, no declaración CEBA y P314A válido. Se excluyeron la respuesta, las ramas condicionadas P314B/P314D/P315/P316, sus derivados, llaves, coordenadas, mes y campos de escolaridad propios. '
      f'GroupShuffleSplit (semilla {r["seed"]}) separó conglomerados: solapamiento={r["group_overlap"]}. Cinco folds GroupKFold en desarrollo sustentan ajuste y selección; sus predicciones fuera de fold alimentan la calibración. Mediana/moda, one-hot y escalado se ajustaron sólo en cada entrenamiento.')
    a.para(f'<b>Predictores y pesos.</b> Se conservaron {len(r["features"])} variables individuales, socioeconómicas, de acceso y contexto. Ingreso y gasto per cápita mensual se transformaron con log(1+x). FACPOB07_25 es el peso anual de población. '
      'Por familia se compararon entrenamiento uniforme, peso poblacional, balance de clase y ambos, con métricas poblacionales comunes. Se eligió por AP-CV en una configuración representativa y luego se ajustaron hiperparámetros; es una búsqueda secuencial, no exhaustiva ni anidada.')
    a.small('<b>Alcance de la evaluación.</b> El conjunto de prueba había sido examinado previamente; por ello, la evaluación es retrospectiva y requiere confirmación externa independiente. La selección de modelos e hiperparámetros se realizó mediante validación cruzada en desarrollo.')
    # Página 3: métodos, elección y estabilidad de perfiles.
    a.new();a.heading('3. Clustering: comparación, estabilidad y perfiles')
    a.para('Se compararon K-Means y mezclas gaussianas (GMM), k=2,...,6, con imputación y estandarización ajustadas en desarrollo. Se usaron log ingreso/gasto, altitud, alumnos/docente, proporción pública y acceso a electricidad e internet del hogar. '
      'La etiqueta sólo caracteriza los perfiles después del ajuste; los clusters no se incorporaron al clasificador. La regla previa priorizó silueta entre soluciones con grupos de al menos 5%, con Davies-Bouldin como desempate.')
    a.image('paper_clustering.png',width=480,maxheight=175,cap=f'<b>Figura 2.</b> Silueta por método y PCA del seleccionado. La comparación estima silueta en {n(r["clustering"].get("silhouette_sample_size",2500))} casos reproducibles. PCA es visualización y explica {pct(sum(r["clustering"]["pca_variance"]))} de varianza.')
    shortlist=[]
    for method in sorted({x['metodo'] for x in comparison}):
        group=[x for x in comparison if x['metodo']==method and x.get('elegible')=='True']
        if not group:group=[x for x in comparison if x['metodo']==method]
        shortlist.append(max(group,key=lambda x:float(x['silueta'])))
    a.table(['Mejor elegible','k','Silueta','Davies-B.','Calinski-H.','Mínimo'],[
      [x['metodo'],x['k'],f(x['silueta']),f(x['davies_bouldin']),f(x['calinski_harabasz'],1),pct(x['min_proporcion'])] for x in shortlist],
      widths=[105,25,75,85,85,CW-375],size=8.2)
    a.para(f'Se seleccionó <b>{esc(chosen["metodo"])}, k={chosen["k"]}</b>: silueta {f(chosen["silueta"])}, Davies-Bouldin {f(chosen["davies_bouldin"])} y Calinski-Harabasz {f(chosen["calinski_harabasz"],1)}. '
      'Los tres criterios pueden discrepar; no se interpreta una única partición como verdad poblacional. En la tabla, n es muestral y las medias/proporciones son ponderadas dentro de desarrollo.')
    a.table(['Perfil','n','Rural','Internet hogar','Gasto S/ mes*','No uso'],[
      [f'G{p["cluster"]}: {p["perfil"]}',n(p['n']),pct(p['rural']),pct(p['internet_hogar']),f(p['gasto_pc_mensual'],0),pct(p['no_uso_ponderado'])] for p in profiles],
      widths=[167,43,52,78,83,CW-423],size=8)
    a.small('* Gasto per cápita. Internet del hogar incluye fijo/móvil; electricidad y conexión son dimensiones de acceso, no competencias digitales.')
    aris=[x['ari_vs_seleccion'] for x in stability]
    a.para(f'<b>Estabilidad.</b> Se repitió el método/k seleccionado cambiando semilla y ajustando en submuestras de 80% de desarrollo ({len(stability)} réplicas). El índice Rand ajustado (ARI) frente a la partición original varió entre {f(min(aris))} y {f(max(aris))}. '
      f'Al quitar electricidad e internet del hogar, la silueta fue {f(ablation["silueta"])} y el ARI frente al agrupamiento completo {f(ablation["ari_vs_completo"])}. Esta ablación comprueba dependencia del acceso; no selecciona un nuevo modelo con la etiqueta. '
      'Las binarias pueden dominar la geometría, por lo que los nombres de perfiles son descripciones y no tipos sociales esenciales.')
    a.image('paper_silhouette.png',width=205,maxheight=136,cap='<b>Figura 3.</b> Distribución de silueta del método elegido en hasta 1 800 casos. Las diez soluciones y las réplicas se incluyen en las tablas reproducibles.')
    # Página 4: sensibilidad, selección y evaluación de clasificación.
    a.new();a.heading('4. Clasificación: selección, sensibilidad y errores')
    candidates_per_model={name:sum(row['modelo']==name for row in search) for name in sorted({row['modelo'] for row in search})}
    a.para(f'Se compararon {len(weightrows)} combinaciones familia-peso y {len(search)} configuraciones HP en cinco folds: {n(r["supervised"].get("fits_budget",0))} ajustes. '
      'Se variaron regularización logística, profundidad, hojas y submuestreo en Random Forest, profundidad/regularización en XGBoost y CatBoost. La selección usa AP-CV; parámetros completos en el código. AP y PR-AUC trapezoidal son resúmenes distintos de la curva PR.')
    a.table(['Familia','Peso elegido','Rango AP-CV por peso','Candidatos HP'],[
      [name,WEIGHTS.get(selectedweights[name],selectedweights[name]),
       f'{f(min(x["ap_cv_media"] for x in weightrows if x["modelo"]==name))}-{f(max(x["ap_cv_media"] for x in weightrows if x["modelo"]==name))}',candidates_per_model[name]]
       for name in candidates_per_model],widths=[95,145,170,CW-410],size=8.1)
    bytest={x['modelo']:x for x in tests}
    a.table(['Modelo','AP-CV ± DE','AUC prueba','PR-AUC prueba','F1 macro'],[
      [x['modelo']+(' *' if x['modelo']==winner else ''),f'{f(x["ap_cv_media"],4)} ± {f(x["ap_cv_sd"],4)}',f(bytest[x['modelo']]['roc_auc']),f(bytest[x['modelo']]['pr_auc_trapezoidal']),f(bytest[x['modelo']]['f1_macro'])] for x in cv],
      widths=[100,115,90,115,CW-420],size=8.3)
    a.small(f'* Ganador CV nominal: {esc(winner)}; diferencias pequeñas no demuestran superioridad estadística. CV usa scores sin calibrar; prueba usa sigmoide sobre predicciones fuera de fold de desarrollo y umbral {r["threshold"]}. El orden de prueba no cambia la selección.')
    a.image('paper_model_curves.png',width=485,maxheight=143,cap='<b>Figura 4.</b> ROC, PR y calibración ponderadas. Referencia PR: prevalencia; diagonal de calibración: acuerdo ideal. Logit: logística; RF: Random Forest; XGB: XGBoost; Cat: CatBoost.')
    constant=next(x for x in r['supervised']['constant_baselines'] if x['modelo']=='Prevalencia desarrollo')
    a.para(f'El ganador alcanzó AP {f(best["average_precision"])} (IC 95% {f(ci["average_precision"][0])}-{f(ci["average_precision"][1])}) y ROC-AUC {f(best["roc_auc"])} '
      f'(IC {f(ci["roc_auc"][0])}-{f(ci["roc_auc"][1])}); {r["supervised"]["group_bootstraps"]} bootstraps de conglomerados no reproducen todo el diseño estratificado. '
      f'Brier: {f(best["brier_sin_calibrar"])} sin calibrar y {f(best["brier"])} calibrado; AP sin ponderar={f(best.get("average_precision_no_ponderado",best["average_precision"]))}. '
      f'La constante de prevalencia logra AP={f(constant["average_precision"])} y Brier={f(constant["brier"])}; se prefiere AP para esa referencia porque el trapecio PR es sensible a empates e interpolación.')
    im=Image.open(FIG/'paper_confusion_matrix.png');iw=190;ih=iw*im.height/im.width
    top=a.y
    a.check(max(ih,157)+12)
    a.c.drawImage(ImageReader(im),M,top-ih,iw,ih,mask='auto')
    text=(f'<b>Errores al umbral {r["threshold"]}.</b><br/>{n(tp)} verdaderos positivos, {n(fn)} falsos negativos y {n(fp)} falsos positivos (conteos). '
      f'Precisión ponderada={pct(best["precision"])}; recall={pct(best["recall"])}. '
      'Omitir no usuarios puede dejar necesidades sin detectar; un falso positivo requiere verificación adicional. El modelo no debe excluir apoyos automáticamente. '
      'Las tasas ponderadas no se calculan a partir de esta matriz sin ponderar. No se optimizó el umbral con prueba.')
    st=ParagraphStyle('side',fontName='Times-Roman',fontSize=9.1,leading=12,textColor=INK)
    p=Paragraph(text,st);_,ph=p.wrap(CW-iw-15,300);a.check(max(ih,ph)+12);p.drawOn(a.c,M+iw+15,top-ph)
    a.y-=max(ih,ph)+8;a.md.append(markdown(text)+'\n\n![Matriz de confusión](figures/confusion_matrix.png)\n')
    a.small('<b>Figura 5.</b> Matriz de confusión de CatBoost en el conjunto de prueba. Evaluación retrospectiva; conteos sin ponderar.',gap=0)
    # Página 5: ganador y análisis no lineal complementario separado.
    a.new();a.heading('5. SHAP del ganador e interacciones no lineales')
    if winner=='Logística':
        method='descomposición lineal interventional con referencia de medias de desarrollo'
    elif winner=='CatBoost':
        method='TreeSHAP nativo de CatBoost con su referencia de árboles'
    else:
        method='TreeSHAP del modelo ajustado, con la referencia de árboles documentada en el código'
    a.para(f'Se explicó {esc(winner)} en {n(sh["n_explained"])} casos de prueba, mediante {method}. Las dummies se sumaron por variable original. '
      f'Las contribuciones están en <b>{esc(sh["units"])}</b> antes de calibrar; no son puntos porcentuales de la probabilidad final. Residuo aditivo máximo={sh["max_additivity_residual"]:.2e}. '
      'La importancia global es media absoluta no ponderada de SHAP de esta muestra, no efecto poblacional ni causal.',size=9.1,leading=12)
    a.image('shap_beeswarm.png',width=428,maxheight=196,cap=f'<b>Figura 6.</b> Diez variables principales del ganador. Destacan {esc(", ".join(leading_variables))}. Positivo aumenta el score de no uso; categorías se muestran con sus códigos, no como escala ordinal.')
    a.paired('paper_shap_dependence_1.png','paper_shap_dependence_2.png',
      '<b>Figura 7.</b> Dependencia del ganador: gasto per cápita, coloreado por ruralidad.',
      '<b>Figura 8.</b> Dependencia del ganador: internet del hogar, coloreado por lengua.',maxheight=122)
    pairtext='; '.join(f'{NAMES.get(x["variable_1"],x["variable_1"])} × {NAMES.get(x["variable_2"],x["variable_2"])}: {f(x["mean_abs_pair_contribution"])}' for x in nonlinear['pairs'][:2])
    a.para(f'<b>Análisis no lineal de {esc(nonlinear["model"])}.</b> {esc(nonlinear["role"])}. En {n(nonlinear["n_explained"])} casos, TreeSHAP path-dependent usa cobertura de hojas de desarrollo. '
      f'La media absoluta de la contribución del par (2φij) fue {esc(pairtext)}. Los pares se eligieron exploratoriamente entre variables de contexto/acceso; no son pruebas de significación.',size=9.1,leading=12)
    a.paired('paper_shap_interaction_1.png','paper_shap_interaction_2.png',
      '<b>Figura 9.</b> Interacción TreeSHAP del primer par: contribución 2φij al score.',
      '<b>Figura 10.</b> Interacción TreeSHAP del segundo par. Colores: otra variable del par.',maxheight=122)
    linear_note=('El ganador lineal es aditivo: sus dependencias no demuestran interacciones; los árboles se analizan por separado. ' if winner=='Logística' else '')
    a.para(linear_note+f'Las interacciones no lineales pertenecen al árbol ajustado, no a personas ni políticas. La suma de interacciones y efectos principales reproduce el score (residuo {nonlinear["max_additivity_residual"]:.2e}). '
      'La lengua y otros atributos requieren especial cautela por tamaños minoritarios, correlación y contexto. No se interpretan sus contribuciones como causas ni como criterio para negar servicios.',size=9.1,leading=12,gap=0)
    # Página 6: casos, interpretación prudente y referencias.
    a.new();a.heading('6. Casos individuales, conclusiones y límites')
    a.local_waterfalls(cases,sh['units'])
    def casenarrative(key):
        case=cases[key]
        contributors=sorted(case['top_contribuciones'],key=lambda x:abs(x['shap']),reverse=True)[:2]
        fields=[f'{NAMES.get(x["variable"],x["variable"])} ({x["shap"]:+.2f})' for x in contributors]
        return ('Alto' if key=='alto' else 'Bajo')+' score: '+', '.join(fields)+'.'
    a.para(casenarrative('alto')+' '+casenarrative('bajo')+' Los extremos correctamente clasificados ilustran el comportamiento del modelo y se presentan sin identificadores personales. Su selección es ilustrativa y no representa la distribución de toda la cohorte.',size=9.1,leading=12)
    a.para(f'<b>Conclusiones.</b> La integración conserva cardinalidad y separación de conglomerados. Los perfiles presentan no uso entre {pct(min_no_use)} y {pct(max_no_use)} en desarrollo; las réplicas y la ablación permiten valorar su estabilidad. '
      f'{esc(winner)} fue seleccionado por AP-CV tras comparar pesos e hiperparámetros; su recall ponderado de {pct(best["recall"])} al umbral {r["threshold"]} limita la detección individual. '
      'La evidencia sugiere explorar apoyos de acceso y acompañamiento apropiados a edad y contexto y evaluar su efecto en campo. SHAP explica el score, no estima el impacto de intervenciones.',size=9.1,leading=12)
    a.para('<b>Limitaciones.</b> No uso en el mes anterior no equivale a falta de habilidades, mala conexión ni exclusión permanente. Se excluyen no asistentes. ESCALE representa residencia, no escuela identificada, e incluye imputaciones; un distrito puede aparecer en ambas particiones. '
      'Las estrategias de peso y HP se eligieron secuencialmente en los mismos folds, por lo que CV puede ser optimista. La prueba ya observada en la versión inicial no es una confirmación externa nueva. Los pesos y bootstraps no reproducen todo el diseño muestral. '
      'La medición transversal, las referencias temporales y los predictores correlacionados impiden causalidad; se requiere nueva validación espacial/temporal antes de uso decisorio.',size=9.1,leading=12)
    a.heading('Referencias y materiales reproducibles')
    references=[
      ('[1] INEI. ENAHO PANEL 2021-2025: corte de 2025, módulos 100, 200, 300 y Sumaria. MINEDU. ESCALE: Padrón de Servicios Educativos y Padrón de Locales Escolares, 2025.' if audit.get('source_mode')=='teacher' else '[1] INEI. Encuesta Nacional de Hogares, 2025: módulos 100, 200, 300 y Sumaria. MINEDU. ESCALE: Padrón de Servicios Educativos y Padrón de Locales Escolares, 2025.'),
      '[2] INEI. ENAHO 2025: Diccionario de Datos. Lima, mayo de 2026. <link href="https://proyectos.inei.gob.pe/iinei/srienaho/Descarga/DocumentosMetodologicos/2025-55/20_Diccionario_2025.pdf" color="#087d84">Documento anual oficial</link>. Cuestionarios ENAHO.01 y ENAHO.01A 2025 incluidos en los archivos suministrados.',
      '[3] Condori Coaquira, A. R. Guía de Evaluación: Proyecto IA, Brecha Digital y Educación 2025 (ENAHO-ESCALE). Universidad Peruana Unión. Material del curso Inteligencia Artificial, 7 p.',
      '[4] INEI. Documento Metodológico de los Indicadores en Educación, 2022, pp. PDF 29 y 33-34. <link href="https://www.inei.gob.pe/media/MenuRecursivo/investigaciones/indicadores-de-educacion.pdf" color="#087d84">Metodología oficial</link>. MINEDU/ESCALE: ficha SIAGIE de atraso, edad al 31 de marzo y desfase de al menos dos años.',
      '[5] INEI. ENAHO 2024: Manual de Consistencia Básica. <link href="https://proyectos.inei.gob.pe/iinei/srienaho/Descarga/DocumentosMetodologicos/2024-55/14_Manual_Consistencia.pdf" color="#087d84">Definición de residente habitual</link>.'
    ]
    for ref in references:a.para(ref,size=7.8,leading=9.7,gap=4,color=GRAY)
    a.small('Material complementario: código de análisis, notebooks ejecutados, diccionario de variables y tablas de validación, ponderación, estabilidad y explicabilidad. La procedencia de las fuentes y sus verificaciones de integridad se documentan en el repositorio.',gap=0)
    a.finish()
    print(f'PDF validado: {OUT} (6 páginas)')

if __name__=='__main__':generate()
