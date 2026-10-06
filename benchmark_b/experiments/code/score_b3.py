"""Score the B3 exports against manually verified labels.

    python score_b3.py --rset rset.csv [--rset-id gml_id --rset-label verified_material]
    python score_b3.py --mset mset.csv [--mset-gml gml_id --mset-osm osm_id --mset-verdict verdict
                                        --mset-case case_type --mset-component component_id]

R-set (roof material, 5 classes concrete/glass/metal/roof_tiles/tar_paper): macro-F1 and accuracy per
method, separately for (a) buildings WITHOUT an ML prediction (scored with the imputation prediction
imp_*) and (b) buildings WITH one (scored with the out-of-fold prediction oof_*), plus for (b) the
agreement of the upstream ML label itself with the verified label (the reference the models were
trained to reproduce). OSM roof:material is never used as a label.
M-set (matching): every judged candidate pair; 'unsure' verdicts are excluded. ROC-AUC per scorer
(true vs false), overall and by case type, and top-1 accuracy per building (is the highest-scored
candidate of the building a verified-true pair?), by case type. Pairs missing from the export (not an
ENRICHED_BY edge and not among the 5 nearest OSM buildings) are counted and reported, not scored.
"""
import argparse, os

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
CLASSES = ["concrete", "glass", "metal", "roof_tiles", "tar_paper"]


def score_rset(a):
    pred = pd.read_csv(os.path.join(RES, "b3_roofmat_predictions.csv.gz"), keep_default_na=False)
    r = pd.read_csv(a.rset).rename(columns={a.rset_id: "gml_id", a.rset_label: "verified"})
    m = r.merge(pred, on="gml_id", how="left", indicator=True)
    print(f"R-set: {len(r)} rows, {int((m._merge != 'both').sum())} ids not found in Hamburg")
    m = m[(m._merge == "both") & m.verified.isin(CLASSES)]
    methods = [c[4:] for c in pred.columns if c.startswith("oof_")]
    rows = []
    for subset, sel, col in [("(a) no ML prediction -> imputation", m.ml_label == "", "imp_"),
                             ("(b) has ML prediction -> out-of-fold", m.ml_label != "", "oof_")]:
        s = m[sel]
        for meth in methods:
            rows.append({"subset": subset, "method": meth, "n": len(s),
                         "macro_f1": f1_score(s.verified, s[col + meth], labels=CLASSES, average="macro",
                                              zero_division=0),
                         "accuracy": accuracy_score(s.verified, s[col + meth]) if len(s) else np.nan})
        if col == "oof_":
            rows.append({"subset": subset, "method": "upstream ML label itself", "n": len(s),
                         "macro_f1": f1_score(s.verified, s.ml_label, labels=CLASSES, average="macro",
                                              zero_division=0),
                         "accuracy": accuracy_score(s.verified, s.ml_label) if len(s) else np.nan})
    out = pd.DataFrame(rows).round(3)
    out.to_csv(os.path.join(RES, "b3_rset_scores.csv"), index=False)
    print(out.to_markdown(index=False))


def score_mset(a):
    sc = pd.read_csv(os.path.join(RES, "b3_matching_scores_disjoint.csv.gz"), keep_default_na=False)
    lab = pd.read_csv(a.mset).rename(columns={a.mset_gml: "gml_id", a.mset_osm: "osm_id",
                                              a.mset_verdict: "verdict", a.mset_case: "case"})
    lab["verdict"] = lab.verdict.astype(str).str.lower()
    lab = lab[lab.verdict.isin(["true", "false", "1", "0"])]
    lab["y"] = lab.verdict.isin(["true", "1"]).astype(int)
    m = lab.merge(sc, on=["gml_id", "osm_id"], how="left", indicator=True)
    print(f"M-set: {len(lab)} judged pairs (unsure excluded); {int((m._merge != 'both').sum())} not in export")
    m = m[m._merge == "both"]
    scorers = [c for c in sc.columns if c.startswith("score_")]
    rows = []
    for case, s in [("all", m)] + list(m.groupby("case")):
        for col in scorers:
            auc = roc_auc_score(s.y, s[col]) if s.y.nunique() == 2 else np.nan
            top = s.loc[s.groupby("gml_id")[col].idxmax()]
            rows.append({"case": case, "scorer": col[6:], "pairs": len(s), "buildings": s.gml_id.nunique(),
                         "roc_auc": auc, "top1_acc": top.y.mean()})
    out = pd.DataFrame(rows).round(3)
    out.to_csv(os.path.join(RES, "b3_mset_scores.csv"), index=False)
    print(out.to_markdown(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rset"); ap.add_argument("--rset-id", default="gml_id")
    ap.add_argument("--rset-label", default="verified_material")
    ap.add_argument("--mset"); ap.add_argument("--mset-gml", default="gml_id")
    ap.add_argument("--mset-osm", default="osm_id"); ap.add_argument("--mset-verdict", default="verdict")
    ap.add_argument("--mset-case", default="case_type")
    a = ap.parse_args()
    if a.rset:
        score_rset(a)
    if a.mset:
        score_mset(a)
