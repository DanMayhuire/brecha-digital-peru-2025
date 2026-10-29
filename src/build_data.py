#!/usr/bin/env python3
"""Build a 2025 ENAHO + ESCALE student table from the teacher's nested ZIPs.

Original archives remain in --source-dir. Only selected 2025 columns are streamed;
names, addresses, telephone numbers and direct school contacts are never loaded.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import struct
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, is_zipfile

import numpy as np
import pandas as pd
from source_audit import load_annual, compare_sources, save_raw_eda, save_context_map

ROOT = Path(__file__).resolve().parents[1]
HH = ["conglome", "vivienda", "hogar"]
PERSON = HH + ["codperso"]
KEY_WIDTH = {"conglome": 6, "vivienda": 3, "hogar": 2, "codperso": 2, "ubigeo": 6}
MODS = {
    "vivienda": ("1474", {
        "año", "mes", *HH, "ubigeo", "dominio", "estrato", "result", "tipenc",
        "p1121", "p1144", "factor07", "altitud",
        "nconglome", "sub_conglome",
    }),
    "personas": ("1479", {
        "año", "mes", *PERSON, "ubigeo", "dominio", "estrato", "p203",
        "p204", "p205", "p206", "p207", "p208a", "p208a1", "p208a2",
        "p208b", "p208b1", "p208c1", "p208d1", "facpob07",
    }),
    "educacion": ("1475", {
        "año", *PERSON, "p300a", "p301a", "p301b", "p301c", "p301d",
        "p306", "p307", "p307d", "p308a", "p308b", "p308c", "p308d",
        "p308c1", "p308c2", "p314a", "p314d", "p316b",
        *{f"p316c{i}" for i in range(1,11)}, *{f"p314b_{i}" for i in range(1,8)},
        *{f"p316_{i}" for i in range(1,13)}, "factor07", "factora07",
    }),
    "sumaria": ("1478", {
        "año", *HH, "mieperho", "inghog2d", "gashog2d", "pobreza", "factor07",
    }),
}


def canonical(col: str) -> str:
    return unicodedata.normalize("NFC", col).strip().lower()


def strip_year(col: str) -> str:
    col = canonical(col)
    return col[:-3] if col.endswith("_25") else col


def json_default(x):
    if isinstance(x, (np.integer, np.floating)):
        return x.item()
    if isinstance(x, Path):
        return str(x)
    raise TypeError(type(x).__name__)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_keys(frame: pd.DataFrame, keys=KEY_WIDTH) -> pd.DataFrame:
    for name in keys:
        if name in frame:
            value = frame[name].astype("string").str.strip().replace("", pd.NA)
            valid = value.str.fullmatch(r"\d+", na=False)
            if (~valid & value.notna()).any():
                raise ValueError(f"Non-numeric identifier in {name}")
            frame[name] = value.str.zfill(KEY_WIDTH[name])
    return frame


def assert_unique(frame: pd.DataFrame, keys: list[str], table: str):
    if frame[keys].isna().any().any():
        raise ValueError(f"Missing required identifiers in {table}")
    duplicates = int(frame.duplicated(keys).sum())
    if duplicates:
        raise ValueError(f"{table}: {duplicates} duplicate keys; no silent deduplication")


def load_2025(archive: ZipFile, name: str, audit: dict) -> pd.DataFrame:
    module, wanted = MODS[name]
    nested_name = next(n for n in archive.namelist() if f"Modulo{module}.zip" in n)
    parts, scanned = [], 0
    with ZipFile(io.BytesIO(archive.read(nested_name))) as nested:
        csv_name = next(n for n in nested.namelist() if n.lower().endswith(".csv") and "12g" not in n.lower())
        with nested.open(csv_name) as handle:
            source_column_count=len(pd.read_csv(handle,encoding="utf-8-sig",nrows=0).columns)
        with nested.open(csv_name) as handle:
            for chunk in pd.read_csv(
                handle, encoding="utf-8-sig", dtype="string", chunksize=10000,
                usecols=lambda c: canonical(c).endswith("_25") and strip_year(c) in wanted,
                na_values=["", " ", "  ", "   ", "    "],
            ):
                scanned += len(chunk)
                chunk.columns = [strip_year(c) for c in chunk.columns]
                for col in chunk:
                    chunk[col] = chunk[col].str.strip().replace("", pd.NA)
                mask = chunk["conglome"].notna() & chunk["año"].eq("2025")
                if mask.any():
                    parts.append(chunk.loc[mask].copy())
        if not parts:
            raise ValueError(f"No 2025 observations in {csv_name}")
        frame = clean_keys(pd.concat(parts, ignore_index=True))
        required = PERSON if name in {"personas", "educacion"} else HH
        assert_unique(frame, required, name)
        for col in frame.columns.difference(KEY_WIDTH):
            if col not in {"nconglome", "sub_conglome"}:
                frame[col] = pd.to_numeric(frame[col], errors="coerce")
        audit["modules"][name] = {
            "source_member": nested_name + "!" + csv_name,
            "encoding": "utf-8-sig", "all_year_rows_scanned": scanned,
            "rows_with_2025_identifiers": len(frame), "unique_keys": True,
            "conglomerates": int(frame.conglome.nunique()), "columns": list(frame.columns), "source_total_columns":source_column_count,
        }
        print(f"Loaded {name}: {len(frame):,} rows in 2025", flush=True)
        return frame


def read_dbf(outer, member, selected, audit, label):
    with ZipFile(io.BytesIO(outer.read(member))) as nested:
        info = next(i for i in nested.infolist() if i.filename.lower().endswith('.dbf'))
        with nested.open(info) as handle:
            head=handle.read(32); rows,hb,rb=struct.unpack('<IHH',head[4:12])
            desc=handle.read(hb-32); fields=[]; schema=[]; offset=1
            for i in range(0,len(desc)-1,32):
                f=desc[i:i+32]
                if not f or f[0]==13:break
                col=f[:11].split(b'\0')[0].decode('ascii');width=f[16]
                schema.append({'name':col,'type':chr(f[11]),'width':width})
                if col in selected:fields.append((col,offset,offset+width))
                offset+=width
            records=[]
            for _ in range(rows):
                r=handle.read(rb)
                if len(r)!=rb:raise ValueError('Truncated DBF record')
                if r[:1]!=b'*':records.append({c:r[a:b].decode('cp1252').strip() for c,a,b in fields})
    audit.setdefault('dbf_schemas',{})[label]={'rows':rows,'fields':schema,'selected':sorted(selected),
        'encoding':'cp1252','header_update':{'raw_year_byte':head[1],'year':1900+head[1],'month':head[2],'day':head[3],'note':'DBF-standard decoded year is inconsistent with 2025 FECHA_ACT; this metadata is not used for the analytical year.'}}
    return pd.DataFrame(records)


def read_padron(outer: ZipFile, audit: dict) -> pd.DataFrame:
    selected={'COD_MOD','ANEXO','CODLOCAL','NIV_MOD','D_NIV_MOD','CODINST','GESTION','D_GESTION',
        'AREA_CENSO','DAREACENSO','CODGEO','ESTADO','NLAT_IE','NLONG_IE','TALUM','TDOC','TSEC','FECHA_ACT','IMPUTADO'}
    invalid=[]
    for n in outer.namelist():
        if n.endswith('.zip') and n not in {'MINEDU/00_Padron.zip','MINEDU/00_Padlocal.zip'}:
            if not is_zipfile(io.BytesIO(outer.read(n))):invalid.append({'member':n,'reason':'HTML response, not ZIP','bytes':outer.getinfo(n).file_size})
    audit['minedu_invalid_downloads']=invalid
    frame=read_dbf(outer,'MINEDU/00_Padron.zip',selected,audit,'padron')
    local=read_dbf(outer,'MINEDU/00_Padlocal.zip',{'CODLOCAL','CODGEO','ESTADO','AREA_LOC','GES_LOC','CLOC_L1','TIP_ENVIO'},audit,'padlocal')
    for f in [frame,local]:
        for c,w in [('CODLOCAL',6),('CODGEO',6)]:f[c]=f[c].astype('string').str.strip().replace('',pd.NA).str.zfill(w)
    assert_unique(local,['CODLOCAL'],'padlocal_dimension')
    local.to_csv(ROOT/'data/processed/escale_locales_dimension_2025.csv',index=False)
    local.to_parquet(ROOT/'data/processed/escale_locales_dimension_2025.parquet',index=False)
    before=len(frame);levels=frame.groupby('NIV_MOD').D_NIV_MOD.agg(lambda s:sorted(s.unique())).to_dict()
    if levels.get('B0')!=['Primaria'] or levels.get('F0')!=['Secundaria']:raise ValueError('Unexpected educational levels')
    area_labels=frame.groupby('AREA_CENSO').DAREACENSO.agg(lambda x:sorted(x.unique())).to_dict()
    if area_labels!={'1':['Urbana'],'2':['Rural']}:raise ValueError(f'Unexpected school area labels: {area_labels}')
    frame=frame.loc[frame.ESTADO.eq('1') & frame.NIV_MOD.isin(['B0','F0'])].copy()
    assert_unique(frame,['COD_MOD','ANEXO'],'padron_primary_secondary')
    frame=frame.merge(local.rename(columns={c:'LOCAL_'+c for c in local if c!='CODLOCAL'}),on='CODLOCAL',how='left',validate='many_to_one',indicator='_local_merge')
    if len(frame)!=len(frame[['COD_MOD','ANEXO']].drop_duplicates()):raise ValueError('School service rows multiplied')
    matched=frame._local_merge.eq('both')
    geo_bad=matched & frame.CODGEO.ne(frame.LOCAL_CODGEO)
    area_bad=matched & frame.AREA_CENSO.ne(frame.LOCAL_AREA_LOC)
    frame['local_validado']=matched & ~geo_bad & ~area_bad & frame.LOCAL_ESTADO.eq('1')
    frame['ubigeo']=frame.CODGEO; frame['escale_area']=pd.to_numeric(frame.AREA_CENSO,errors='coerce')
    if not frame.ubigeo.str.fullmatch(r'\d{6}',na=False).all() or not frame.escale_area.isin([1,2]).all():raise ValueError('Invalid geographic keys')
    for c in ['TALUM','TDOC','TSEC','NLAT_IE','NLONG_IE']:
        frame[c]=pd.to_numeric(frame[c],errors='coerce')
    for c in ['TALUM','TDOC','TSEC']:frame.loc[frame[c].lt(0),c]=np.nan
    coords_invalid=~frame.NLAT_IE.between(-19,0) | ~frame.NLONG_IE.between(-82,-68)
    frame.loc[coords_invalid,['NLAT_IE','NLONG_IE']]=np.nan
    frame['publica']=frame.GESTION.isin(['1','2']).astype(int)
    frame['imputada']=frame.IMPUTADO.str.startswith(('2_','3_')).astype(int)
    groups=['ubigeo','escale_area']
    agg=frame.groupby(groups).agg(escale_servicios=('COD_MOD','size'),
        escale_instituciones=('CODINST','nunique'),
        escale_alumnos=('TALUM',lambda x:x.sum(min_count=1)),escale_docentes=('TDOC',lambda x:x.sum(min_count=1)),
        escale_secciones=('TSEC',lambda x:x.sum(min_count=1)),prop_publicas=('publica','mean'),
        escale_prop_imputadas=('imputada','mean'),escale_cobertura_padlocal=('local_validado','mean')).reset_index()
    # A local may host several services; count physical context once, after validating its geography.
    physical=frame.loc[frame.local_validado].copy()
    conflicts=physical.groupby('CODLOCAL')[['CODGEO','AREA_CENSO']].nunique().gt(1).any(axis=1)
    bad_local=set(conflicts[conflicts].index)
    physical=physical.loc[~physical.CODLOCAL.isin(bad_local)].copy()
    coordinate_spread=physical.groupby('CODLOCAL')[['NLAT_IE','NLONG_IE']].agg(lambda x:x.max()-x.min())
    bad_coord=set(coordinate_spread.index[coordinate_spread.gt(1e-6).any(axis=1)])
    physical.loc[physical.CODLOCAL.isin(bad_coord),['NLAT_IE','NLONG_IE']]=np.nan
    per_local=physical.groupby([*groups,'CODLOCAL']).agg(
        NLAT_IE=('NLAT_IE','first'),NLONG_IE=('NLONG_IE','first'),servicios_local=('COD_MOD','size')).reset_index()
    per_local['compartido']=per_local.servicios_local.gt(1).astype(int)
    coords=per_local.groupby(groups).agg(escale_latitud=('NLAT_IE','mean'),escale_longitud=('NLONG_IE','mean'),
        escale_locales=('CODLOCAL','nunique'),escale_prop_local_compartido=('compartido','mean')).reset_index()
    agg=agg.merge(coords,on=groups,how='left',validate='one_to_one')
    agg['ratio_alumnos_docente']=agg.escale_alumnos.div(agg.escale_docentes.where(agg.escale_docentes.gt(0)))
    audit['escale']={'dbf_rows':before,'active_primary_secondary_services':len(frame),'levels':levels,
        'filter':'ESTADO=1 and NIV_MOD in {B0,F0}','fecha_act':frame.FECHA_ACT.value_counts().to_dict(),
        'dbf_header_update':audit['dbf_schemas']['padron']['header_update'],'duplicate_codmod_anexo':0,
        'services_zero_teachers':int(frame.TDOC.eq(0).sum()),'services_imputed':int(frame.imputada.sum()),
        'district_area_groups':len(agg),'area_labels_verified':area_labels,
        'padlocal_rows':len(local),'padlocal_unique_codlocal':True,'padron_padlocal_matched_services':int(matched.sum()),
        'padron_padlocal_unmatched_services':int((~matched).sum()),'padron_padlocal_match_rate':float(matched.mean()),
        'geographic_conflicting_services':int(geo_bad.sum()),'area_conflicting_services':int(area_bad.sum()),
        'services_before_local_join':len(frame),'services_after_local_join':len(frame),
        'physical_locals_with_multiple_geographies_excluded':len(bad_local),
        'locals_conflicting_coordinates_excluded_from_coordinate_means':len(bad_coord),
        'invalid_coordinate_service_rows':int(coords_invalid.sum()),
        'physical_locals_validated':int(per_local.CODLOCAL.nunique()),
        'missing_infrastructure_fields':['computers','water','electricity','internet','altitude'],
        'interpretation':'Padlocal validates the unique physical premises and their geography. It has no physical infrastructure, altitude or coordinate fields; coordinates come from Padron, counted once per validated local. Territorial context does not identify individual students schools.'}
    pd.DataFrame([{'join':'padron_padlocal','before_rows':len(frame),'after_rows':len(frame),'matched':int(matched.sum()),
        'unmatched':int((~matched).sum()),'geographic_conflicts':int(geo_bad.sum()),'area_conflicts':int(area_bad.sum())}]).to_csv(ROOT/'reports/tables/escale_join_coverage.csv',index=False)
    return agg


def merge_audit(left: pd.DataFrame, right: pd.DataFrame, keys: list[str], name: str, audit: dict):
    merged = left.merge(right, how="left", on=keys, validate="many_to_one", indicator="_matched")
    audit["merges"][name] = {
        "left_rows": len(left), "right_rows": len(right), "output_rows": len(merged),
        "matched": int(merged._matched.eq("both").sum()),
        "unmatched": int(merged._matched.eq("left_only").sum()), "keys": keys,
        "cardinality": "many_to_one", "row_multiplication": len(merged) != len(left),
    }
    merged[f"coincide_{name}"] = merged._matched.eq("both").astype(int)
    return merged.drop(columns="_matched")


def binary_code(series: pd.Series, yes=1, no=2):
    result = pd.Series(np.nan, index=series.index, dtype=float)
    result.loc[series.eq(yes)] = 1
    result.loc[series.eq(no)] = 0
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path.home() / "Downloads/DocenteMaterial")
    parser.add_argument("--annual-dir", type=Path, default=None, help="Directory containing 1031-Modulo01/02/03/34.zip; defaults to source-dir parent")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    args = parser.parse_args()
    for folder in [args.output_dir, ROOT / "data/raw", ROOT / "reports/tables", ROOT / "docs"]:
        folder.mkdir(parents=True, exist_ok=True)
    inei = next(args.source_dir.glob("INEI*.zip"))
    minedu = next(args.source_dir.glob("MINEDU*.zip"))
    audit = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "year": 2025,
             "modules": {}, "filters": {}, "merges": {}, "warnings": []}
    annual_dir=args.annual_dir or args.source_dir.parent
    annual_files=[annual_dir/f'1031-Modulo{m}.zip' for m in ['01','02','03','34']]
    for p in annual_files:
        if not p.is_file():raise FileNotFoundError(f'Required annual input missing: {p}')
    manifest = {"source_dir": str(args.source_dir), "annual_dir":str(annual_dir), "copies_of_archives_created":False,
        "reference_source":"annual_2025", "archives":[{"path":str(p),"bytes":p.stat().st_size,"sha256":sha256(p),
            "role":"comparison_only" if p==inei else "pipeline_input"} for p in [*annual_files,minedu,inei]]}
    (ROOT / "data/raw/source_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    members={name:load_annual(annual_dir,name,wanted,clean_keys,assert_unique,HH,PERSON,audit) for name,(_,wanted) in MODS.items()}
    panel_audit={'modules':{}}
    with ZipFile(inei) as archive:
        panel={name:load_2025(archive,name,panel_audit) for name in MODS}
    audit['panel_modules_for_comparison']=panel_audit['modules']
    comparison=compare_sources(panel,members,PERSON,HH)
    (ROOT/'reports/tables/source_comparison.json').write_text(json.dumps(comparison,indent=2,ensure_ascii=False,default=json_default))
    audit['source_comparison']=comparison
    del panel
    save_raw_eda(members,audit,ROOT)
    persons = members["personas"]
    age_ok = persons.p208a.between(6, 17)
    usual = (persons.p204.eq(1) & persons.p205.eq(2)) | (persons.p204.eq(2) & persons.p206.eq(1))
    audit["filters"] = {
        "persons_2025": len(persons), "age_6_17_before_residency": int(age_ok.sum()),
        "residency_rule": "(P204=1 and P205=2) or (P204=2 and P206=1)",
        "usual_residents_6_17": int((age_ok & usual).sum()),
        "age_6_17_excluded_non_usual": int((age_ok & ~usual).sum()),
        "residency_codes_age_6_17": persons.loc[age_ok, ["p204", "p205", "p206"]].fillna(-999).value_counts().rename("n").reset_index().to_dict("records"),
    }
    data = persons.loc[age_ok & usual].copy()
    data["residente_habitual"] = 1
    education = members["educacion"].drop(columns="año").rename(columns={"factor07": "factor07_educacion"})
    data = merge_audit(data, education, PERSON, "educacion", audit)
    geography_check = data[PERSON + ["ubigeo"]].merge(
        members["vivienda"][HH + ["ubigeo"]], on=HH, validate="many_to_one", suffixes=("_persona", "_vivienda"),
    )
    mismatch = geography_check.ubigeo_persona.ne(geography_check.ubigeo_vivienda)
    audit["person_household_ubigeo_mismatches"] = int(mismatch.sum())
    if mismatch.any():
        raise ValueError("Person and household UBIGEO disagree within the same 2025 household key")
    housing = members["vivienda"].drop(columns=["año", "mes", "ubigeo", "dominio", "estrato"]).rename(columns={"factor07": "factor07_vivienda"})
    data = merge_audit(data, housing, HH, "vivienda", audit)
    summary = members["sumaria"].drop(columns="año").rename(columns={"factor07": "factor07_sumaria"})
    data = merge_audit(data, summary, HH, "sumaria", audit)
    data["edad"] = data.p208a
    data["sexo"] = data.p207
    data["lengua_materna"] = data.p300a
    data["rural"] = np.where(data.estrato.between(6, 8), 1.0, np.where(data.estrato.between(1, 5), 0.0, np.nan))
    data["escale_area"] = np.where(data.rural.eq(1), 2.0, np.where(data.rural.eq(0), 1.0, np.nan))
    data["electricidad"] = binary_code(data.p1121, yes=1, no=0)
    data["internet_hogar"] = binary_code(data.p1144, yes=1, no=0)
    denom = data.mieperho.where(data.mieperho.gt(0)) * 12
    data["ingreso_pc_mensual"] = data.inghog2d.div(denom)
    data["gasto_pc_mensual"] = data.gashog2d.div(denom)
    data["peso_persona"] = data.facpob07
    data["peso_hogar"] = data.factor07_sumaria
    data["peso_educacion"] = data.factora07
    data["matriculado"] = binary_code(data.p306)
    data["asiste"] = binary_code(data.p307)
    data["no_uso_internet"] = binary_code(data.p314a, yes=2, no=1)
    data["exclusion_digital"] = data.no_uso_internet.where(data.asiste.eq(1))
    for name, lo, hi in [("altitud", -100, 7000)]:
        invalid = data[name].notna() & ~data[name].between(lo, hi)
        audit.setdefault("invalid_numeric_values", {})[name] = int(invalid.sum())
        data.loc[invalid, name] = np.nan
    with ZipFile(minedu) as archive:
        escale = read_padron(archive, audit)
    escale.to_csv(args.output_dir / "escale_distrito_area_2025.csv", index=False)
    escale.to_parquet(args.output_dir / "escale_distrito_area_2025.parquet",index=False)
    save_context_map(escale,ROOT)
    data = merge_audit(data, escale, ["ubigeo", "escale_area"], "escale", audit)
    data = data.rename(columns={"coincide_escale": "escale_coincide", "año": "ano"})
    assert_unique(data, PERSON, "final_student_table")
    audit["cohort"] = {
        "rows": len(data), "households": len(data[HH].drop_duplicates()),
        "conglomerates": int(data.conglome.nunique()), "districts": int(data.ubigeo.nunique()),
        "attendance": data.asiste.value_counts(dropna=False).rename(index=lambda x: "missing" if pd.isna(x) else str(int(x))).to_dict(),
        "enrolled": data.matriculado.value_counts(dropna=False).rename(index=lambda x: "missing" if pd.isna(x) else str(int(x))).to_dict(),
        "internet_non_use": data.no_uso_internet.value_counts(dropna=False).rename(index=lambda x: "missing" if pd.isna(x) else str(int(x))).to_dict(),
        "digital_exclusion_among_attendees": data.exclusion_digital.value_counts(dropna=False).rename(index=lambda x: "missing" if pd.isna(x) else str(int(x))).to_dict(),
        "household_result": data.result.value_counts(dropna=False).rename(index=lambda x: "missing" if pd.isna(x) else str(int(x))).to_dict(),
        "escale_match_rate": float(data.escale_coincide.mean()),
        "both_primary_grade_fields": data.loc[data.p308a.eq(2), ["p308b", "p308c"]].head(8).fillna(-999).to_dict("records"),
        "both_secondary_grade_fields": data.loc[data.p308a.eq(3), ["p308b", "p308c"]].head(8).fillna(-999).to_dict("records"),
    }
    audit["missingness"] = {c: {"n": int(data[c].isna().sum()), "pct": float(data[c].isna().mean() * 100)} for c in data}
    audit["weights"] = {
        "peso_persona": "FACPOB07, annual population expansion, module 200; retained separately from household and longitudinal weights.",
        "peso_hogar": "FACTOR07, annual household expansion from Sumaria; do not sum this repeated per-person field to estimate household totals.",
        "peso_educacion": "FACTORA07, annual education population factor, education module.",
        "not_used": "FACPANEL* longitudinal weights: this project is a 2025 cross-section, not a continuous multi-year panel subset.",
    }
    audit["warnings"] = [
        "Annual ENAHO2025 is canonical; the teacher panel cut is used only for an explicit aggregate comparison of keys and values. No panel continuity is required.",
        "Incomplete interviews are retained where the required person data exist; missingness is explicit, not fabricated or silently dropped.",
        "ESCALE describes district-area educational context, not the exact school attended. Residence district may differ from school district.",
        "Exclusion_digital is an operational non-use-of-internet indicator among attendees, not a direct digital-competence measurement or causal effect.",
        "Structural skips in internet-use questions can reveal the target; P314A, P314D, P316_5 and exclusion_digital are audit/target fields and must not enter predictors of digital exclusion.",
        "P314B/P316 branches and digital-skills B/C fields are audit-only, conditioned by questionnaire skips; they are not predictors of the internet-use target.",
        "No supervised preprocessing, imputation, scaling or model fitting is performed in this builder. These must be fitted inside training folds.",
    ]
    output = args.output_dir / "dataset_enaho_escale_2025.csv"
    data.to_csv(output, index=False)
    data.to_parquet(args.output_dir / "dataset_enaho_escale_2025.parquet",index=False)
    audit["output"] = {"path": str(output), "sha256": sha256(output), "columns": list(data.columns)}
    (ROOT / "reports/tables/data_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    pd.DataFrame([{"variable": c, **v} for c, v in audit["missingness"].items()]).to_csv(ROOT / "reports/tables/data_audit_missingness.csv", index=False)
    write_dictionary(data, audit, ROOT / "docs/data_dictionary.md")
    print(json.dumps({"output": str(output), "rows": len(data), "columns": len(data.columns), "escale_match_rate": data.escale_coincide.mean(), "digital_exclusion": audit["cohort"]["digital_exclusion_among_attendees"]}, default=json_default, ensure_ascii=False), flush=True)


def write_dictionary(data: pd.DataFrame, audit: dict, path: Path):
    descriptions = {
        "ano": "Año 2025 del archivo anual; texto en Parquet. No se combinan otros años.",
        "conglome": "Código CONGLOME anual, string de 6 dígitos; agrupación obligatoria de partición.",
        "vivienda": "Código VIVIENDA anual, string de 3 dígitos.",
        "hogar": "Código HOGAR anual, string de 2 dígitos.",
        "codperso": "Código CODPERSO anual, string de 2 dígitos.",
        "ubigeo": "Distrito de residencia del miembro, UBIGEO anual, 6 dígitos.",
        "mes": "Mes de encuesta 2025; puede afectar comparaciones de edad, matrícula o asistencia.",
        "p203": "Parentesco con jefe del hogar; campo original módulo 200.",
        "p204": "Miembro del hogar (1 sí, 2 no).", "p205": "Ausente del hogar 30 días o más (1 sí, 2 no).",
        "p206": "Presente en el hogar 30 días o más (1 sí, 2 no).",
        "p207": "Sexo: 1 hombre, 2 mujer.", "p208a": "Edad en años cumplidos, módulo 200.",
        "p208a1": "Componente original adicional de edad/nacimiento; no utilizado en ninguna derivación.",
        "p208a2": "Componente original adicional de edad/nacimiento; no utilizado en ninguna derivación.",
        "p208b": "Edad en meses; campo original.", "p208b1": "Componente original adicional de edad/nacimiento; no utilizado en derivaciones.",
        "p208c1": "Componente original adicional de edad/nacimiento; no utilizado en derivaciones.",
        "p208d1": "Componente original adicional de edad/nacimiento; no utilizado en derivaciones.",
        "p300a": "Lengua materna; 1 quechua, 2 aimara, 4 castellano; conservar las restantes categorías originales.",
        "p301a": "Último nivel aprobado.", "p301b": "Último año de estudios aprobado.", "p301c": "Último grado de estudios aprobado.", "p301d": "Tipo de centro de estudios del último nivel aprobado.",
        "p306": "Matriculado este año: 1 sí, 2 no.", "p307": "Asiste actualmente: 1 sí, 2 no.",
        "p307d": "Recibe o recibió primaria/secundaria en CEBA: 1 sí, 2 no; pregunta condicionada.",
        "p308a": "Nivel matriculado: 1 inicial, 2 primaria, 3 secundaria, 4 superior no universitaria, 5 universitaria, 6 posgrado, 7 especial.",
        "p308b": "Año de estudios actualmente matriculado; no combinar a ciegas con P308C.",
        "p308c": "Grado de estudios actualmente matriculado; verificar nivel antes de usar.",
        "p308d": "Centro actualmente matriculado: 1 estatal, 2 no estatal.",
        "p308c1": "Institución a la que asiste se ubica aquí en el distrito (variable original).",
        "p308c2": "Institución a la que asiste se ubica en otro distrito (variable original).",
        "p314a": "Uso de internet el mes anterior: 1 sí, 2 no. Componente de la etiqueta digital; excluir de sus predictores.",
        "p314d": "Frecuencia de internet entre usuarios; salto estructural revela P314A. Excluir de predictores digitales.",
        "p316_5": "Uso de internet para educación formal/capacitación, pregunta condicionada. Excluir de predictores digitales.",
        "facpob07": "Factor anual de población del módulo 200.", "factor07_vivienda": "Factor anual del módulo 100.",
        "factor07_educacion": "Factor anual original del módulo educación.",
        "factora07": "Factor de población ajustado por grupos quinquenales del módulo educación.",
        "factor07_sumaria": "Factor anual original de Sumaria, unidad hogar.",
        "dominio": "Dominio geográfico ENAHO (categoría).", "estrato": "Estrato: 1-5 urbano; 6-8 rural.",
        "result": "Resultado de entrevista: 1 completa, 2 incompleta; otros estados se conservan si aparecieran.",
        "tipenc": "Tipo de selección: 3 panel; otros códigos incluyen selección no panel.",
        "nconglome": "Conglomerado del marco, identificador original, no predictor.",
        "sub_conglome": "Subconglomerado del marco, identificador original, no predictor.",
        "p1121": "Electricidad como alumbrado: 1 sí, 0 no.", "p1144": "Conexión de internet fijo/móvil en hogar: 1 sí, 0 no; cuestionario 2025 p.4.",
        "mieperho": "Miembros del hogar utilizados para per cápita, Sumaria.",
        "inghog2d": "Ingreso neto anual del hogar, Sumaria, soles; se conserva sin sustituir faltantes.",
        "gashog2d": "Gasto anual del hogar, Sumaria, soles.",
        "pobreza": "Sumaria: 1 pobreza extrema, 2 pobreza no extrema, 3 no pobre.",
        "edad": "Alias de P208A (años cumplidos).", "sexo": "Alias de P207 (categoría).",
        "lengua_materna": "Alias de P300A (categoría).", "rural": "1 si ESTRATO 6-8; 0 si ESTRATO 1-5; otro -> faltante.",
        "electricidad": "P1121 recodificada: 1 sí, 0 no; otros -> faltante.",
        "internet_hogar": "P1144 recodificada: conexión de internet fijo/móvil, 1 sí, 0 no; otros -> faltante.",
        "ingreso_pc_mensual": "INGHOG2D / (12*MIEPERHO), solo denominador >0. Soles por persona/mes.",
        "gasto_pc_mensual": "GASHOG2D / (12*MIEPERHO), solo denominador >0. Soles por persona/mes.",
        "peso_persona": "Alias FACPOB07, peso de población; revisar uso según análisis, no predictor.",
        "peso_hogar": "Alias FACTOR07 de Sumaria, unidad hogar; no sumar por cada estudiante para estimar hogares.",
        "peso_educacion": "Alias FACTORA07 de educación, peso de población ajustado por grupos quinquenales.",
        "residente_habitual": "1 en cohorte; selección (P204=1 y P205=2) o (P204=2 y P206=1).",
        "matriculado": "P306 1 -> 1, 2 -> 0; otros -> faltante.", "asiste": "P307 1 -> 1, 2 -> 0; otros -> faltante.",
        "no_uso_internet": "P314A 2 -> 1, 1 -> 0; otros -> faltante. Etiqueta potencial, no predictor digital.",
        "exclusion_digital": "NO_USO_INTERNET solo si ASISTE=1; demás -> faltante. Proxy operativo; no mide competencias.",
        "escale_area": "Área contextual: 1 urbana, 2 rural, derivada de ESTRATO.",
        "escale_coincide": "1 si UBIGEO+área enlazó a ESCALE, 0 si sin correspondencia.",
        "escale_servicios": "Número de servicios escolares activos de primaria y secundaria por distrito+área.",
        "escale_alumnos": "Suma TALUM de servicios elegibles por distrito+área.",
        "escale_docentes": "Suma TDOC de servicios elegibles por distrito+área; no personas docentes únicas.",
        "escale_secciones": "Suma TSEC por distrito+área.",
        "ratio_alumnos_docente": "SUM(TALUM)/SUM(TDOC) en distrito+área; faltante si SUM(TDOC)<=0.",
        "prop_publicas": "Proporción de servicios elegibles con GESTION 1 o 2; gestión3 privada.",
        "escale_prop_imputadas": "Proporción de servicios con IMPUTADO parcial o total de MINEDU.",
        "escale_locales": "Locales físicos distintos con Padlocal activo y geografía consistente, por distrito+área.",
        "escale_instituciones": "CODINST distintos en servicios elegibles; no confundir con servicios ni locales.",
        "escale_cobertura_padlocal": "Fracción de servicios cuyo local está activo y coincide en distrito/área con Padlocal.",
        "escale_prop_local_compartido": "Fracción de locales físicos validados con más de un servicio EBR elegible.",
        "p316b": "Uso de computadora/laptop/tablet en últimos3meses, solo14+; 1sí2no. Auditoría de medición, nunca predictor digital.",
        "escale_latitud": "Promedio de NLAT_IE en locales distintos (CODLOCAL), distrito+área.",
        "escale_longitud": "Promedio de NLONG_IE en locales distintos (CODLOCAL), distrito+área.",
        "latitud": "Latitud del hogar de módulo100; valores fuera [-90,90] -> faltante.",
        "longitud": "Longitud del hogar de módulo100; valores fuera [-180,180] -> faltante.",
        "altitud": "Altitud del hogar de módulo100, metros; fuera [-100,7000] -> faltante.",
    }
    for i in range(1,11):
        descriptions[f'p316c{i}']='Actividad TIC autorreportada '+str(i)+'; solo14+ que usaron computadora/laptop/tablet. 1sí2no; NA estructural no significa incapacidad. Auditoría, excluir del modelo digital.'
    for i in range(1,8):
        descriptions[f'p314b_{i}']='Lugar de uso de internet, respuesta múltiple '+str(i)+' entre usuarios; rama condicionada P314A. Auditoría, excluir del modelo digital.'
    for i in range(1,13):
        descriptions[f'p316_{i}']='Finalidad de uso de internet '+str(i)+' entre usuarios; 1sí2no. No mide directamente habilidad. Auditoría, excluir del modelo digital.'
    lines = [
        "# Diccionario de datos ENAHO + ESCALE 2025", "",
        f"Cohorte: {len(data):,} personas residentes habituales de 6 a 17 años. Una fila por CONGLOME+VIVIENDA+HOGAR+CODPERSO de 2025.", "",
        "Fuente canónica: descargas anuales ENAHO2025. El corte panel2025 se compara por llaves y valores, sin usarlo para completar datos. Las llaves y AÑO permanecen como texto; no se cargan nombres, direcciones ni coordenadas de hogares.", "",
        "## Procedencia y decisiones", "",
        "- Ficha técnica PANEL 2021-2025 p.6: archivos con hogares paneles y no paneles de cada año.",
        "- Diccionario anual ENAHO2025: pp.14,16 servicios; pp.29-31 edad/residencia/factor persona; pp.94-95 educación; pp.107-111 uso/TIC/competencias; p.119 factor de educación. Los códigos de missing se normalizan por variable, nunca globalmente.",
        "- ESCALE: Padrón activo, NIV_MOD=B0/F0, cruzado por CODLOCAL con Padlocal único; se auditan distrito y área antes de agregar. No se asigna un colegio individual a estudiantes ENAHO.",
        "- Se mantienen entrevistas incompletas cuando hay personas elegibles; el faltante queda explícito. No se imputa ni escala en este paso.",
        "- P308B y P308C son componentes distintos (año y grado). La etiqueta de rezago no se define aquí y debe justificarse antes del modelado.",
        "- Los módulos usados no incluyen fecha de nacimiento para corregir edad al31marzo; no se reconstruyen cumpleaños ni se afirma que no exista en otros módulos no utilizados.",
        "- Padlocal no contiene coordenadas ni mediciones físicas de infraestructura. Coordenadas provienen de Padrón y se promedian una vez por local geográficamente validado. No se inventan computadoras, conectividad ni altitud escolar.",
        "- Los pesos se conservan por unidad (persona, hogar y educación); no se mezclan con los pesos longitudinales FACPANEL.", "",
        "## Campos", "", "| Variable | Tipo | Faltantes | Definición / uso |", "|---|---|---:|---|",
    ]
    for col in data:
        description = descriptions.get(col)
        if description is None and col.startswith("coincide_"):
            description = "Bandera de auditoría: 1 si la tabla de origen pudo enlazarse; no predictor por defecto."
        if description is None:
            raise ValueError(f"Undocumented variable: {col}")
        dtype = "texto" if col in KEY_WIDTH or col in {"ano", "mes", "nconglome", "sub_conglome"} else "numérico"
        lines.append(f"| {col} | {dtype} | {int(data[col].isna().sum())} | {description} |")
    lines += ["", "## Exclusiones del modelado supervisado", "",
              "Excluir identificadores, pesos, el objetivo y banderas de coincidencia internas. La única excepción predefinida es ESCALE_COINCIDE: indica disponibilidad de contexto territorial, no la respuesta individual; el modelo la incluye explícitamente. Para exclusión digital, excluir P314A, NO_USO_INTERNET, EXCLUSION_DIGITAL y preguntas posteriores condicionadas por el uso (P314D, P316_5). Si se elige rezago, revisar además edad, nivel/año/grado actual y trayectoria educativa para que los predictores no reconstruyan la etiqueta.", "",
              "Los indicadores agregados de ESCALE pueden repetirse entre conglomerados del mismo distrito. GroupKFold por CONGLOME cumple el mínimo de la guía; no demuestra por sí solo generalización a distritos no observados.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
