"""
S4 — train/val/test splits for classification on `Building` (roof type, building function).

Two splits, per §1 pt 4 / §3 item 7:

  * RANDOM  (transductive, DECEPTIVE): i.i.d. node sample. In a city this LEAKS — a train
    neighbour reveals its test neighbour's label through spatial autocorrelation, so scores
    look great for the wrong reason. Reported on the raw (full) label space.

  * SPATIAL-BLOCK  (the honest one): tile the map (KMeans on center_x/center_y), assign WHOLE
    tiles to train/val/test so regions are geographically disjoint. Tests "can the model label an
    unseen part of the city?" — expect a drop; that drop is the result. Reported on a GROUPED,
    few-class label, because blocking geography can empty a rare class's tail entirely, and
    macro-F1 over a vanished class is meaningless.

Roof-type 3-class merge (by ALKIS roof-code semantics -- Hamburg and Helsinki share this code
convention, so no per-city mapping is needed, only the composite-code cleanup done in the loader):
    Flat         = {1000}
    Gable-family = {3100 Gable, 3200 Hip}      ridged / multi-plane
    Other        = everything else (Mono-Pitch, Tent, Tower/Spire, ...)  single-plane / rare forms

Building-function has no such canonical short list (it is long-tailed over 20+ codes even at full
Hamburg scale), so it is grouped generically to its top-`k` classes + "Other" (`topk_plus_other`).

Loader (neo4j_loader.py) is left untouched (v1 locked); every merge/grouping lives here.
"""
import numpy as np
import torch
from sklearn.cluster import KMeans

FLAT = {"1000"}
GABLE_FAMILY = {"3100", "3200"}   # everything else -> "Other"
CLASS3_NAMES = ["Flat", "Gable-family", "Other"]


def merged_3class(data):
    """Map the 5-class roof label to {Flat, Gable-family, Other}. Unlabeled (-1) stays -1.
    If the city's roof codes don't match the known ALKIS codes at all, returns (None, None)."""
    codes = data["Building"].label_codes          # index -> roof_type_code (string)
    y5 = data["Building"].y.numpy()
    if not (set(codes) & (FLAT | GABLE_FAMILY)):
        return None, None                          # merge undefined for this city's label space

    def grp(code):
        if code in FLAT:
            return 0
        if code in GABLE_FAMILY:
            return 1
        return 2

    y3 = np.array([-1 if c < 0 else grp(codes[c]) for c in y5], dtype=np.int64)
    return y3, CLASS3_NAMES


def labeled_mask(y):
    """Boolean mask of nodes that carry a real label (>=0). Others are graph context only."""
    return torch.tensor(np.asarray(y) >= 0)


def _masks(n, tr_idx, va_idx, te_idx):
    def m(idx):
        t = torch.zeros(n, dtype=torch.bool)
        t[idx] = True
        return t
    return m(tr_idx), m(va_idx), m(te_idx)


def random_split(n, seed, val_frac=0.15, test_frac=0.15, labeled=None):
    """i.i.d. split over labeled nodes only (unlabeled stay out of train/val/test, kept as context)."""
    idx = np.arange(n) if labeled is None else np.where(np.asarray(labeled))[0]
    g = np.random.default_rng(seed)
    idx = g.permutation(idx)
    m = len(idx)
    n_test = int(round(test_frac * m))
    n_val = int(round(val_frac * m))
    te, va, tr = idx[:n_test], idx[n_test:n_test + n_val], idx[n_test + n_val:]
    return _masks(n, tr, va, te)


def spatial_block_split(pos, seed, n_blocks=10, val_frac=0.15, test_frac=0.15):
    """Whole-tile assignment: KMeans blocks, greedily fill test then val to the target fractions."""
    pos = np.asarray(pos, dtype=np.float64)
    n = pos.shape[0]
    k = min(n_blocks, n)
    blocks = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(pos)
    g = np.random.default_rng(seed)
    order = g.permutation(np.unique(blocks))
    counts = {b: int((blocks == b).sum()) for b in order}

    te_blocks, cnt = [], 0
    for b in order:
        if cnt >= test_frac * n:
            break
        te_blocks.append(b); cnt += counts[b]
    va_blocks, cnt = [], 0
    for b in order:
        if b in te_blocks:
            continue
        if cnt >= val_frac * n:
            break
        va_blocks.append(b); cnt += counts[b]

    te_mask = torch.tensor(np.isin(blocks, te_blocks))
    va_mask = torch.tensor(np.isin(blocks, va_blocks))
    tr_mask = ~(te_mask | va_mask)
    return tr_mask, va_mask, te_mask


def spatial_kfold(pos, seed, k=5, labeled=None):
    """K spatial tiles over labeled nodes; each tile is the test fold once. Returns (folds, blocks).

    folds = [(train_mask, test_mask), ...] over ALL n nodes, but only labeled nodes are ever
    train/test (unlabeled remain in the graph as message-passing context). The K test masks
    partition the labeled set, so pooling out-of-fold predictions tests each labeled building
    exactly once (fixes the all-Flat-test lottery). Reshuffle the tiling via `seed`.
    """
    pos = np.asarray(pos, dtype=np.float64)
    n = pos.shape[0]
    lab_idx = np.arange(n) if labeled is None else np.where(np.asarray(labeled))[0]
    blocks_lab = KMeans(n_clusters=min(k, len(lab_idx)), n_init=10,
                        random_state=seed).fit_predict(pos[lab_idx])
    blocks = np.full(n, -1)
    blocks[lab_idx] = blocks_lab
    folds = []
    for b in np.unique(blocks_lab):
        te = torch.tensor(blocks == b)                 # labeled test tile
        tr = torch.tensor(np.isin(np.arange(n), lab_idx)) & ~te  # labeled, not this tile
        folds.append((tr, te))
    return folds, blocks


def oof_scores(y_true, y_pred, n_classes):
    """Pooled out-of-fold macro-F1 + per-class F1 (README §1 pt 9)."""
    from sklearn.metrics import f1_score
    labels = list(range(n_classes))
    macro = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
    per = f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    return macro, per


def splits_for_labels(pos, y_full, names_full, y_merged=None, names_merged=None, seed=0, k=5):
    """Build the 'random' + 'spatial_cv' split dict from an arbitrary label array (roof type,
    building function, ...), so the same splitting logic serves every classification target.

    `y_full`/`names_full` is the raw label space, used for the random split. `y_merged` (optional,
    e.g. a grouped few-class version) is used for spatial CV instead, because blocking geography can
    empty a rare class's tail (see S4) — pass None to reuse the raw label space for both."""
    y_full = np.asarray(y_full)
    lab = y_full >= 0
    n = len(y_full)
    out = {
        "random": {
            "mask": random_split(n, seed, labeled=lab),
            "y": torch.tensor(y_full, dtype=torch.long), "n_classes": int(y_full[lab].max()) + 1,
            "names": names_full,
        },
    }
    if pos is None:
        return out
    y_cv, names_cv = (y_full, names_full) if y_merged is None else (np.asarray(y_merged), names_merged)
    folds, blocks = spatial_kfold(pos, seed, k=k, labeled=(y_cv >= 0))
    out["spatial_cv"] = {"folds": folds, "blocks": blocks, "y": torch.tensor(y_cv, dtype=torch.long),
                         "n_classes": int(y_cv[y_cv >= 0].max()) + 1, "names": names_cv}
    return out


def make_splits(data, seed=0, k=5):
    """Roof-type splits: random single hold-out (5-class) + spatial K-fold CV (merged 3-class if
    defined for this city's label space, else the raw one). Restricts train/test to labeled nodes."""
    y5 = data["Building"].y.numpy()
    y3, names3 = merged_3class(data)
    pos = data["Building"].pos.numpy() if "pos" in data["Building"] else None
    return splits_for_labels(pos, y5, data["Building"].label_names, y3, names3, seed, k)


def make_splits_function(data, seed=0, k=5, topk=8):
    """Building-function splits: same machinery as roof type, but grouped to the `topk` most common
    classes + one 'Other' bucket (function is far more long-tailed than roof type -- see PROGRESS.md
    S2 -- so the raw label space is only usable for the random split, never for spatial CV)."""
    yf = data["Building"].y_function.numpy()
    names_f = data["Building"].function_names
    y_top, names_top = topk_plus_other(yf, names_f, topk)
    pos = data["Building"].pos.numpy() if "pos" in data["Building"] else None
    return splits_for_labels(pos, yf, names_f, y_top, names_top, seed, k)


def make_splits_roof_material(data, seed=0, k=5):
    """Roof-material splits (Hamburg only, ML-predicted, ~50% coverage -- see PROGRESS.md S8-REAL /
    BENCHMARK_B_HANDOFF.md). Only 5 classes and no long tail (majority 55.8%), unlike building
    function, so the raw label space is used directly for both regimes -- no top-k grouping needed."""
    ym = data["Building"].y_roof_material.numpy()
    names_m = data["Building"].roof_material_names
    pos = data["Building"].pos.numpy() if "pos" in data["Building"] else None
    return splits_for_labels(pos, ym, names_m, None, None, seed, k)


def topk_plus_other(y, names, k):
    """Group a long-tailed label to its `k` most frequent classes + one 'Other' bucket. Unlabeled
    (-1) stays -1. Used for building function, which (unlike roof type) has no small canonical
    class set -- see PROGRESS.md S2 (13 of 21 Hamburg function classes have n<=2 at pilot scale)."""
    y = np.asarray(y)
    codes, counts = np.unique(y[y >= 0], return_counts=True)
    top = codes[np.argsort(-counts)[:k]]
    remap = {c: i for i, c in enumerate(top)}
    other = len(top)
    y_grouped = np.array([-1 if c < 0 else remap.get(c, other) for c in y], dtype=np.int64)
    return y_grouped, [names[c] for c in top] + ["Other"]


def _report(data, seed=0, k=5):
    sp = make_splits(data, seed, k=k)

    # random single hold-out (5-class)
    s = sp["random"]; tr, va, te = s["mask"]; y = s["y"].numpy()
    print(f"\n[random]  seed={seed}  {s['n_classes']} classes  "
          f"train={int(tr.sum())} val={int(va.sum())} test={int(te.sum())}")
    for nm, m in [("train", tr), ("val", va), ("test", te)]:
        u, c = np.unique(y[m.numpy()], return_counts=True)
        print(f"    {nm:5s} {dict(zip((s['names'][int(i)] for i in u), c.tolist()))}")

    # spatial K-fold CV (3-class): verify coverage + per-fold class safety
    s = sp["spatial_cv"]; folds = s["folds"]; y = s["y"].numpy(); ncl = s["n_classes"]
    print(f"[spatial_cv]  seed={seed}  K={len(folds)} folds  {ncl} classes")
    tested = np.zeros(len(y), dtype=int)
    for i, (trm, tem) in enumerate(folds):
        tested += tem.numpy().astype(int)
        u_tr = set(np.unique(y[trm.numpy()]).tolist())
        u_te, c_te = np.unique(y[tem.numpy()], return_counts=True)
        miss_tr = [s["names"][j] for j in range(ncl) if j not in u_tr]
        tag = f"  TRAIN-MISSING: {miss_tr}" if miss_tr else ""
        print(f"    fold {i}: test_n={int(tem.sum())} "
              f"{dict(zip((s['names'][int(x)] for x in u_te), c_te.tolist()))}{tag}")
    assert (tested == 1).all(), "CV coverage broken: some node not tested exactly once"
    # majority-class baseline under pooled OOF (a floor for macro-F1, validates the metric plumbing)
    maj = np.bincount(y, minlength=ncl).argmax()
    macro, per = oof_scores(y, np.full_like(y, maj), ncl)
    print(f"    [coverage OK: every building tested exactly once] "
          f"majority-baseline pooled macro-F1={macro:.3f} per-class={[round(float(p),3) for p in per]}")


if __name__ == "__main__":
    from neo4j_loader import load_from_neo4j
    data = load_from_neo4j(database="hamburg", city="hamburg", verbose=False)
    for seed in (0, 1, 2):
        _report(data, seed)
