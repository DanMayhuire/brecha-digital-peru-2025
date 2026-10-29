"""Auditoría agregada de la medición TIC; no entrena ni publica identificadores.

La presencia de P316C no autoriza imputar ausencia de competencia en los saltos.
Se ejecuta después de build_data.py, sobre respuestas previas a imputación ML.
"""
from pathlib import Path
import argparse
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [f'p316c{i}' for i in range(1, 10)]


def audit_measurement(dataset=None, output=None):
    dataset = Path(dataset or ROOT/'data/processed/dataset_enaho_escale_2025.csv')
    output = Path(output or ROOT/'reports/tables/target_measurement_audit.json')
    df = pd.read_csv(dataset, dtype={'conglome':str,'vivienda':str,'hogar':str,'codperso':str,'ubigeo':str})
    required = ['edad','p306','p307','p307d','p308a','p314a','p316b',*SKILLS]
    absent = [c for c in required if c not in df]
    if absent:
        raise ValueError(f'Falta reconstruir el dataset con columnas de auditoría: {absent}')
    for c in required:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    eligible = (df.edad.between(6,17) & df.p306.eq(1) & df.p307.eq(1)
                & df.p308a.isin([2,3]) & ~df.p307d.eq(1) & df.p314a.isin([1,2]))
    if 'peso_persona' in df:
        eligible &= pd.to_numeric(df.peso_persona, errors='coerce').gt(0)
    def summary(sub):
        valid = sub[SKILLS].isin([1,2]).all(axis=1)
        any_yes = sub[SKILLS].eq(1).any(axis=1)
        none_reported = valid & ~any_yes
        return {
            'n': len(sub), 'internet_use_yes':int(sub.p314a.eq(1).sum()),
            'internet_use_no':int(sub.p314a.eq(2).sum()),
            'p316b_yes':int(sub.p316b.eq(1).sum()), 'p316b_no':int(sub.p316b.eq(2).sum()),
            'p316b_missing_or_invalid':int((~sub.p316b.isin([1,2])).sum()),
            'complete_nine_named_activities':int(valid.sum()),
            'at_least_one_activity_reported':int((valid & any_yes).sum()),
            'zero_nine_activities_reported_conditional_on_observation':int(none_reported.sum()),
            'joint_nonuse_and_zero_activities_fully_observed':int((none_reported & sub.p314a.eq(2)).sum()),
            'p316b_no_with_observed_skill_response':int((sub.p316b.eq(2) & sub[SKILLS].notna().any(axis=1)).sum()),
            'nonmissing_by_activity':{c:int(sub[c].notna().sum()) for c in SKILLS}
        }
    cohorts = {
        'integrated_residents_6_17':summary(df),
        'attending_ebr_main':summary(df.loc[eligible]),
        'attending_ebr_6_13':summary(df.loc[eligible & df.edad.between(6,13)]),
        'attending_ebr_14_17':summary(df.loc[eligible & df.edad.between(14,17)])
    }
    checks = {
        'no_observed_p316b_under14': bool(df.loc[df.edad.lt(14),'p316b'].isna().all()),
        'no_observed_p316c_under14': bool(df.loc[df.edad.lt(14),SKILLS].isna().all().all()),
        'p316c_skip_after_p316b_no': cohorts['integrated_residents_6_17']['p316b_no_with_observed_skill_response']==0,
        'cohort_age_groups_sum':cohorts['attending_ebr_main']['n']==cohorts['attending_ebr_6_13']['n']+cohorts['attending_ebr_14_17']['n']
    }
    result = {
        'source_dataset':str(dataset), 'source_sha256':hashlib.sha256(dataset.read_bytes()).hexdigest(),
        'questionnaire_reference':'CUESTIONARIO_ENAHO01A_2025.pdf, página PDF6: competencias TIC para personas14+; si P316B=2, salto a capítulo400.',
        'cohorts':cohorts, 'checks':checks,
        'decision':'Mantener no uso de internet mes anterior como objetivo operativo para6-17; el bloque de actividades informáticas no identifica competencia de todos los escolares.',
        'warnings':[
            'P316B/P316C son autorreportes de exposición/actividades, no una prueba de desempeño.',
            'Menores14 y quienes P316B=2 presentan saltos estructurales; no imputar cero competencias.',
            'El indicador conjunto completamente observado es sensibilidad descriptiva en un subconjunto seleccionado; no es etiqueta de toda la cohorte ni un objetivo entrenado.',
            'Conteos muestrales; no tasas nacionales oficiales.'
        ]
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if not all(checks.values()):
        raise AssertionError(f'Inconsistencia en saltos del cuestionario: {checks}')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=audit_measurement(args.dataset,args.output)
    print(json.dumps({'cohorts':result['cohorts'],'checks':result['checks']},ensure_ascii=False,indent=2))
