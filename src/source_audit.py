"""Source-level audits; no fitting, imputation or predictive selection.

Only selected analytical columns are read. Direct names, addresses and contacts
are deliberately excluded from microdata products.
"""
from __future__ import annotations
import json
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd

ANNUAL_MODULES = {'vivienda':'01','personas':'02','educacion':'03','sumaria':'34'}
# Official annual dictionary2025 pp.94-95,107-110; codes are field-specific.
MISSING_CODES = {'p208a':[99], 'p300a':[99], 'p301a':[99], 'p301b':[99], 'p301c':[9],
                 'p301d':[9], 'p308b':[9], 'p308d':[9]}


def normalize_name(c):
    import unicodedata
    return unicodedata.normalize('NFC',c).strip().lower().replace('$','_')


def annual_member(z, name):
    suffix = {'vivienda':'-100.csv','personas':'-200.csv','educacion':'-300.csv','sumaria':'sumaria-2025.csv'}[name]
    found = [n for n in z.namelist() if not n.startswith('__MACOSX') and n.lower().endswith(suffix)]
    if len(found)!=1: raise ValueError(f'Ambiguous/missing annual {name}: {found}')
    return found[0]


def load_annual(directory, name, wanted, clean_keys, assert_unique, hh, person, audit):
    path = Path(directory)/f'1031-Modulo{ANNUAL_MODULES[name]}.zip'
    with ZipFile(path) as z:
        member = annual_member(z,name)
        full_columns=list(pd.read_csv(z.open(member),encoding='latin1',sep=';',nrows=0).columns)
        frame = pd.read_csv(z.open(member), encoding='latin1', sep=';', dtype='string',
                            usecols=lambda c:normalize_name(c) in wanted,
                            na_values=['',' ','  ','   ','    '])
    frame.columns=[normalize_name(c) for c in frame]
    raw=[]
    for c in frame:
        s=frame[c]
        stripped=s.str.strip().replace('',pd.NA)
        numeric=pd.to_numeric(stripped.str.replace(',','.',regex=False),errors='coerce')
        r={'module':name,'variable':c,'rows':len(s),'missing_raw':int(stripped.isna().sum()),
           'missing_pct':float(stripped.isna().mean()*100),
           'whitespace_values':int((s.notna() & s.str.fullmatch(r'\s*',na=False)).sum()),
           'decimal_comma_values':int(s.str.contains(',',regex=False,na=False).sum()),
           'numeric_parse_failures':int((stripped.notna() & numeric.isna()).sum())}
        if c not in {'año','mes',*hh,'codperso','ubigeo','nconglome','sub_conglome'}:
            r.update({f'q{int(q*100):02}':float(numeric.quantile(q)) if numeric.notna().any() else None for q in [0,.01,.25,.5,.75,.99,1]})
            if c in {'inghog2d','gashog2d','mieperho','facpob07','factor07','factora07','altitud','p208a'} and numeric.notna().any():
                q1,q3=numeric.quantile([.25,.75]);iqr=q3-q1
                r['iqr_flag_count']=int(((numeric<q1-1.5*iqr)|(numeric>q3+1.5*iqr)).sum()) if iqr else 0
            if numeric.nunique()<=25:r['codes']=json.dumps({('missing' if pd.isna(k) else str(k)):int(v) for k,v in stripped.value_counts(dropna=False).items()})
        raw.append(r)
        frame[c]=stripped
    frame=clean_keys(frame)
    required=person if name in {'personas','educacion'} else hh
    assert_unique(frame, ['año',*required], 'annual_'+name)
    if not frame['año'].eq('2025').all():raise ValueError('Annual source contains another year')
    for c in frame:
        if c not in {'año','mes',*hh,'codperso','ubigeo','nconglome','sub_conglome'}:
            frame[c]=pd.to_numeric(frame[c].str.replace(',','.',regex=False),errors='coerce')
            if c in MISSING_CODES:frame[c]=frame[c].replace(MISSING_CODES[c],np.nan)
    audit['modules'][name]={'source_member':str(path)+'!'+member,'encoding':'latin1','separator':';','decimal':',',
        'rows_with_2025_identifiers':len(frame),'unique_keys':True,'conglomerates':int(frame.conglome.nunique()),
        'columns':list(frame),'source_total_columns':len(full_columns),'source_column_names':full_columns,'missing_requested_columns':sorted(wanted-set(frame.columns))}
    audit.setdefault('raw_eda',[]).extend(raw)
    print(f'Loaded annual {name}: {len(frame):,} rows',flush=True)
    return frame


def compare_sources(panel,annual,person,hh):
    result={}
    for name,p in panel.items():
        a=annual[name];keys=person if name in {'personas','educacion'} else hh
        x=p.merge(a,on=keys,how='outer',indicator=True,suffixes=('_panel','_annual'),validate='one_to_one')
        common=x._merge.eq('both'); diffs=[]
        for c in sorted(set(p)&set(a)-set(keys)):
            s,t=x[c+'_panel'],x[c+'_annual']
            if c in ['año','mes','nconglome','sub_conglome']:
                sp=pd.to_numeric(s,errors='coerce');tp=pd.to_numeric(t,errors='coerce')
            else:sp=pd.to_numeric(s,errors='coerce');tp=pd.to_numeric(t,errors='coerce')
            if c in MISSING_CODES:
                sp=sp.replace(MISSING_CODES[c],np.nan);tp=tp.replace(MISSING_CODES[c],np.nan)
            equal=np.isclose(sp.astype(float),tp.astype(float),rtol=1e-10,atol=1e-8,equal_nan=True)
            diff=common & ~equal
            valid=common & sp.notna() & tp.notna()
            if diff.any():diffs.append({'variable':c,'different':int(diff.sum()),
                'max_abs_difference':float((sp[valid]-tp[valid]).abs().max()) if valid.any() else None})
        panel_extra=x._merge.eq('left_only')
        substantive=[c for c in p if c.startswith('p') and c not in keys]
        if name=='educacion':
            extra=p.merge(a[keys],on=keys,how='left',indicator=True).query('_merge=="left_only"')
            extra_substantive=int(extra[substantive].notna().any(axis=1).sum())
        else:extra_substantive=None
        result[name]={'annual_rows':len(a),'panel_2025_rows':len(p),'matched_keys':int(common.sum()),
            'panel_only_rows':int(panel_extra.sum()),'annual_only_rows':int(x._merge.eq('right_only').sum()),
            'panel_extra_with_any_observed_question':extra_substantive,
            'panel_only_columns':sorted(set(p)-set(a)), 'annual_only_columns':sorted(set(a)-set(p)),
            'value_differences_after_decimal_missing_normalization':diffs,
            'numeric_tolerance':'rtol=1e-10, atol=1e-8; no replacement of unequal sources'}
    return result


def save_raw_eda(members,audit,root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tables=root/'reports/tables';figures=root/'reports/figures';figures.mkdir(exist_ok=True,parents=True)
    pd.DataFrame(audit['raw_eda']).to_csv(tables/'raw_eda_variables.csv',index=False)
    plt.rcParams.update({'font.size':16,'axes.labelsize':16,'xtick.labelsize':16,'ytick.labelsize':16,'savefig.dpi':220})
    fig,ax=plt.subplots(2,2,figsize=(12,8))
    for (name,col,title),a in zip([
      ('personas','p208a','Edad: todas las personas\ndel módulo 200'),
      ('sumaria','gashog2d','Gasto anual del hogar: escala original\n(P1-P99 solo para visualización)'),
      ('educacion','p314a','Uso de internet\nMódulo 300 completo'),
      ('vivienda','estrato','Estrato geográfico\nMódulo 100 completo')],ax.ravel()):
        s=members[name][col].dropna()
        if col in ['p314a','estrato']:
            counts=s.value_counts().sort_index(); a.bar(counts.index.astype(str),counts.values,color='#0b6683');a.set_ylabel('Registros muestrales')
        else:
            if col=='gashog2d':s=s[s.between(s.quantile(.01),s.quantile(.99))]
            a.hist(s,bins=35,color='#0b6683');a.set_ylabel('Registros muestrales')
            if col=='gashog2d':
                from matplotlib.ticker import FuncFormatter
                a.xaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x/1000:g}'))
                a.set_xlabel('Soles (miles)')
        a.set_title(title,fontsize=16);a.spines[['top','right']].set_visible(False)
    fig.suptitle('EDA de módulos originales 2025\nAntes de cruces, filtrado escolar e imputación',fontsize=18)
    fig.tight_layout();fig.savefig(figures/'raw_eda.png');fig.savefig(figures/'raw_eda.pdf');plt.close(fig)
    # Full raw values are retained: visual trimming never deletes analytical rows.
    cols=['inghog2d','gashog2d','mieperho','pobreza']
    members['sumaria'][cols].corr().to_csv(tables/'raw_sumaria_correlation.csv')


def save_context_map(escale,root):
    import matplotlib.pyplot as plt
    valid=escale.dropna(subset=['escale_longitud','escale_latitud'])
    fig,ax=plt.subplots(figsize=(6,7))
    s=ax.scatter(valid.escale_longitud,valid.escale_latitud,c=valid.ratio_alumnos_docente,s=5,cmap='viridis',vmin=5,vmax=35,alpha=.6)
    ax.set(xlabel='Longitud',ylabel='Latitud',title='Contexto escolar por distrito y área\nPromedio de locales validados; sin hogares individuales')
    fig.colorbar(s,ax=ax,label='Alumnos / docentes (color limitado 5-35)')
    ax.set_aspect('equal');fig.tight_layout();fig.savefig(root/'reports/figures/escale_context_map.png',dpi=220);fig.savefig(root/'reports/figures/escale_context_map.pdf');plt.close(fig)
