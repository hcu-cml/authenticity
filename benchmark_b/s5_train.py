"""
S5 — T2 roof-type node classification: training + evaluation loop.

Reusable across cities and scales. Two evaluation protocols (from S4):
  * "random"     : single i.i.d. hold-out, full label space  (DECEPTIVE — leaks via autocorrelation)
  * "spatial_cv" : spatial K-fold CV, merged label            (HONEST — pooled out-of-fold macro-F1)
Report both, mean±std over seeds, against the majority-class floor.

Methods (all share one signature  train_fn(data, y, train_mask, n_classes, seed, use_prov, **cfg)
-> predictions for ALL nodes; the caller masks). See METHODS below for the full registry:
  * probe : attribute-only logistic regression on Building features (no graph) — the baseline.
  * node2vec / metapath2vec / dgi : unsupervised, frozen-embedding + probe. The first two are
            transductive shallow lookup tables (pilot scale only, don't generalise to unseen nodes);
            dgi is a real inductive GNN encoder trained contrastively, so it scales and could serve
            unseen cities in principle (not exercised here — see the paper's discussion).
  * gnn   : heterogeneous GraphSAGE (via to_hetero). full_batch=True by default; set full_batch=False
            for NeighborLoader mini-batching on the full dataset.
  * gat / hgt / han / rgcn : other message-passing encoders, source-typed (separate parameters per
            relation) but NOT confidence-weighted — the mechanistic step below gnn_aware.
  * gnn_aware : confidence-weighted AND source-typed (realises Eq.1) — the paper's aware encoder.

PORTABILITY: feature widths vary per city; the lazy PyG modules (SAGEConv((-1,-1),...)) adapt with
no change. `use_prov` concatenates Building.x_prov when present (coverage/agreement features); the
confidence-WEIGHTED aggregation of Eq.1 is the aware arm proper (S6 / notebook 2) — extension point
flagged below.

SCALE: device auto-selects CUDA; `amp=True` enables mixed precision; `full_batch=False` streams
sampled subgraphs (num_neighbors / batch_size configurable) for graphs that don't fit in VRAM.
Keep the master HeteroData on CPU; per-run device tensors are built inside each call (§3 item 9).
"""
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.nn import (SAGEConv, GATConv, GraphConv, HGTConv, RGCNConv, HANConv,
                                DeepGraphInfomax, to_hetero, Linear)
from torch_geometric.utils import scatter

from splits import make_splits, oof_scores

# Relations whose edge_weight is a genuine correspondence CONFIDENCE (Eq.1 w_ce). Others (e.g. POI
# distance) are NOT confidences, so the aware arm gives them uniform weight.
CONFIDENCE_RELS = {"enriched_by", "rev_enriched_by"}

CFG = dict(hidden=64, lr=0.01, epochs=150, dropout=0.3, weight_decay=5e-4,
           amp=False, full_batch=True, num_neighbors=[15, 10], batch_size=2048,
           heads=4, layers=2,                                   # GAT / HGT
           emb_dim=64, walk_length=20, context_size=7, walks_per_node=10, n2v_epochs=50)  # shallow


def set_seed(s):
    np.random.seed(s); torch.manual_seed(s)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(s)


def pick_device(prefer="auto"):
    if prefer == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(prefer)


def building_features(data, use_prov, drop=()):
    """Building feature matrix. `drop` removes columns by name (leakage guard for T1 regression:
    drop the target attribute so the model can't read it directly)."""
    x = data["Building"].x
    if drop and "feat_names" in data["Building"]:
        names = data["Building"].feat_names
        drop_set = set(drop) | {d + "_mask" for d in drop}   # also drop the storeys presence mask
        keep = [i for i, nm in enumerate(names) if nm not in drop_set]
        x = x[:, keep]
    if use_prov and "x_prov" in data["Building"]:
        x = torch.cat([x, data["Building"].x_prov], dim=1)
    return x


class HeteroGNN(torch.nn.Module):
    """Two-layer message-passing encoder + linear head; wrapped by to_hetero. `conv` picks the
    aggregator: 'sage' (mean, GraphSAGE) or 'gat' (attention). out=1 gives a regression head (T1)."""
    def __init__(self, hidden, out, conv="sage", heads=4, dropout=0.3):
        super().__init__()
        if conv == "gat":
            mk = lambda: GATConv((-1, -1), hidden, heads=heads, concat=False, add_self_loops=False)
        else:
            mk = lambda: SAGEConv((-1, -1), hidden)
        self.c1, self.c2 = mk(), mk()
        self.lin = Linear(hidden, out)
        # nn.Dropout MODULE (not F.dropout): to_hetero FX-traces at construction and would bake
        # F.dropout's training flag constant -> dropout stuck ON at eval. The module respects eval().
        self.drop = torch.nn.Dropout(dropout)

    def forward(self, x, edge_index):
        x = self.c1(x, edge_index).relu()
        x = self.drop(x)
        x = self.c2(x, edge_index).relu()
        return self.lin(x)


class HGT(torch.nn.Module):
    """Heterogeneous Graph Transformer (typed attention). Operates on dicts directly (not to_hetero)."""
    def __init__(self, hidden, out, heads, layers, metadata):
        super().__init__()
        self.lin_in = torch.nn.ModuleDict({nt: Linear(-1, hidden) for nt in metadata[0]})
        self.convs = torch.nn.ModuleList([HGTConv(hidden, hidden, metadata, heads) for _ in range(layers)])
        self.lin_out = Linear(hidden, out)

    def encode(self, x_dict, ei_dict):
        h = {nt: self.lin_in[nt](x).relu() for nt, x in x_dict.items()}
        for conv in self.convs:
            h = conv(h, ei_dict)
        return h["Building"]

    def forward(self, x_dict, ei_dict):
        return self.lin_out(self.encode(x_dict, ei_dict))


class HAN(torch.nn.Module):
    """Heterogeneous Graph Attention Network (semantic + node-level attention over relations),
    operating on dicts directly like HGT. Source-typed (a separate attention path per relation)
    but not confidence-weighted -- the same "structurally aware, not Eq.1-aware" slot HGT fills."""
    def __init__(self, hidden, out, heads, metadata, dropout=0.3):
        super().__init__()
        self.lin_in = torch.nn.ModuleDict({nt: Linear(-1, hidden) for nt in metadata[0]})
        self.conv = HANConv(hidden, hidden, metadata, heads=heads, dropout=dropout)
        self.lin_out = Linear(hidden, out)

    def forward(self, x_dict, ei_dict):
        h = {nt: self.lin_in[nt](x).relu() for nt, x in x_dict.items()}
        h = self.conv(h, ei_dict)
        return self.lin_out(h["Building"])


def _homogeneous_edge_index_typed(data):
    """Like `_homogeneous_edge_index`, but also returns a per-edge relation-type id (0..R-1, one per
    entry of `data.edge_types`) -- what RGCNConv needs to pick a relation-specific weight matrix."""
    offset, cur = {}, 0
    for nt in data.node_types:
        offset[nt] = cur; cur += data[nt].num_nodes
    eis, ets = [], []
    for ri, (s_, r_, t_) in enumerate(data.edge_types):
        ei = data[s_, r_, t_].edge_index.clone()
        ei[0] += offset[s_]; ei[1] += offset[t_]
        eis.append(ei)
        ets.append(torch.full((ei.size(1),), ri, dtype=torch.long))
    hom = torch.cat(eis, 1) if eis else torch.empty((2, 0), dtype=torch.long)
    et = torch.cat(ets) if ets else torch.empty((0,), dtype=torch.long)
    return hom, et, offset, cur


class RGCN(torch.nn.Module):
    """Relational GCN: one weight matrix per relation type (the textbook source-typed W_{s(e)}),
    uniform (unweighted) aggregation within a relation -- source-typed but not confidence-weighted,
    the mechanistic predecessor to \\cref{eq:confagg}'s aware encoder. Operates on the flattened
    homogeneous graph (RGCNConv needs one relation-tagged edge_index, not a hetero dict); per-type
    inputs are brought to a common width first via `lin_in`, same pattern as HGT/HAN above."""
    def __init__(self, hidden, out, num_relations, node_types, dropout=0.3):
        super().__init__()
        self.lin_in = torch.nn.ModuleDict({nt: Linear(-1, hidden) for nt in node_types})
        self.c1 = RGCNConv(hidden, hidden, num_relations)
        self.c2 = RGCNConv(hidden, hidden, num_relations)
        self.lin_out = Linear(hidden, out)
        self.drop = torch.nn.Dropout(dropout)

    def forward(self, x_dict, order, hom_ei, edge_type):
        h = torch.cat([self.lin_in[nt](x_dict[nt]) for nt in order], dim=0)
        h = self.c1(h, hom_ei, edge_type).relu()
        h = self.drop(h)
        h = self.c2(h, hom_ei, edge_type).relu()
        return self.lin_out(h)


class ProvGNN(torch.nn.Module):
    """S6b — provenance-AWARE encoder realizing Eq.1:
        h_c' = σ(W_self h_c + Σ_{e∈N(c)} (w_ce/Σw)·W_{s(e)} h_e).
    GraphConv consumes per-edge weights; we pre-normalize them per target node so add-aggregation
    becomes the confidence-weighted MEAN. to_hetero gives a separate weight matrix per relation ->
    that is the source-typed W_{s(e)} (a refinement of per-source, since relations nest within source)."""
    def __init__(self, hidden, out, dropout=0.3):
        super().__init__()
        self.c1 = GraphConv((-1, -1), hidden)
        self.c2 = GraphConv((-1, -1), hidden)
        self.lin = Linear(hidden, out)
        self.drop = torch.nn.Dropout(dropout)

    def forward(self, x, edge_index, edge_weight=None):
        x = self.c1(x, edge_index, edge_weight).relu()
        x = self.drop(x)
        x = self.c2(x, edge_index, edge_weight).relu()
        return self.lin(x)


def _norm_edge_weight_dict(data, device):
    """Per-relation, per-target normalized weights: confidence (jaccard) on correspondence edges,
    uniform elsewhere -> add-aggregation in GraphConv == (w_ce/Σw) weighted mean of Eq.1."""
    ewd = {}
    for et in data.edge_types:
        src, rel, dst = et
        ei = data[et].edge_index
        if rel in CONFIDENCE_RELS and "edge_weight" in data[et]:
            w = data[et].edge_weight.clone().float()
        else:
            w = torch.ones(ei.size(1))
        dst_idx = ei[1]
        denom = scatter(w, dst_idx, dim=0, dim_size=data[dst].num_nodes, reduce="sum")
        ewd[et] = (w / (denom[dst_idx] + 1e-16)).to(device)
    return ewd


# ---------------------------------------------------------------- methods (shared signature)
def probe_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    from sklearn.linear_model import LogisticRegression
    X = building_features(data, use_prov).cpu().numpy()
    tr = train_mask.cpu().numpy()
    clf = LogisticRegression(max_iter=2000).fit(X[tr], y.cpu().numpy()[tr])
    return torch.tensor(clf.predict(X), dtype=torch.long)


def gnn_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, conv="sage", **cfg):
    c = {**CFG, **cfg}
    device = device or pick_device()
    if c["full_batch"]:
        return _gnn_full(data, y, train_mask, n_classes, seed, use_prov, device, c, conv)
    return _gnn_minibatch(data, y, train_mask, n_classes, seed, use_prov, device, c, conv)


def gat_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    return gnn_predict(data, y, train_mask, n_classes, seed, use_prov, device, conv="gat", **cfg)


def _device_graph(data, use_prov, device):
    xd = {nt: data[nt].x.to(device) for nt in data.node_types}
    xd["Building"] = building_features(data, use_prov).to(device)
    ed = {et: data[et].edge_index.to(device) for et in data.edge_types}
    return xd, ed


def _gnn_full(data, y, train_mask, n_classes, seed, use_prov, device, c, conv="sage"):
    set_seed(seed)
    xd, ed = _device_graph(data, use_prov, device)
    model = to_hetero(HeteroGNN(c["hidden"], n_classes, conv, c["heads"], c["dropout"]),
                      data.metadata(), aggr="sum").to(device)
    with torch.no_grad():
        model(xd, ed)                               # lazy-param init BEFORE optimizer (§3 item 5)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    scaler = torch.amp.GradScaler("cuda", enabled=c["amp"] and device.type == "cuda")
    yb, tr = y.to(device), train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        with torch.autocast(device_type=device.type, enabled=c["amp"] and device.type == "cuda"):
            out = model(xd, ed)["Building"]
            loss = F.cross_entropy(out[tr], yb[tr])
        scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
    model.eval()
    with torch.no_grad():
        return model(xd, ed)["Building"].argmax(1).cpu()


def _gnn_minibatch(data, y, train_mask, n_classes, seed, use_prov, device, c, conv="sage"):
    """NeighborLoader training for graphs too large for full-batch; full-batch inference at the end
    (fine on a 96 GB box; swap in a subgraph inference loader if even that won't fit)."""
    from torch_geometric.loader import NeighborLoader
    set_seed(seed)
    d = data.clone()
    d["Building"].x = building_features(data, use_prov)
    d["Building"].y = y
    model = to_hetero(HeteroGNN(c["hidden"], n_classes, conv, c["heads"], c["dropout"]),
                      data.metadata(), aggr="sum").to(device)
    loader = NeighborLoader(d, num_neighbors=c["num_neighbors"],
                            input_nodes=("Building", train_mask),
                            batch_size=c["batch_size"], shuffle=True)
    b0 = next(iter(loader)).to(device)
    with torch.no_grad():
        model(b0.x_dict, b0.edge_index_dict)        # lazy init
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    for _ in range(c["epochs"]):
        model.train()
        for batch in loader:
            batch = batch.to(device); opt.zero_grad()
            bs = batch["Building"].batch_size
            out = model(batch.x_dict, batch.edge_index_dict)["Building"][:bs]
            F.cross_entropy(out, batch["Building"].y[:bs]).backward(); opt.step()
    model.eval()
    xd, ed = _device_graph(data, use_prov, device)
    with torch.no_grad():
        return model(xd, ed)["Building"].argmax(1).cpu()


def gnn_aware_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    """S6b full aware arm: coverage/agreement features (x_prov) + confidence-weighted, source-typed
    aggregation (Eq.1). Full-batch (fits large graphs on 96 GB; for the mini-batch big run, attach the
    normalized weights to the cloned data so NeighborLoader carries them — same pattern as _gnn_minibatch)."""
    c = {**CFG, **cfg}
    device = device or pick_device()
    set_seed(seed)
    xd, ed = _device_graph(data, use_prov=True, device=device)   # aware always uses prov features
    ewd = _norm_edge_weight_dict(data, device)
    model = to_hetero(ProvGNN(c["hidden"], n_classes, c["dropout"]), data.metadata(), aggr="sum").to(device)
    with torch.no_grad():
        model(xd, ed, ewd)                              # lazy init before optimizer (§3 item 5)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    yb, tr = y.to(device), train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        out = model(xd, ed, ewd)["Building"]
        F.cross_entropy(out[tr], yb[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return model(xd, ed, ewd)["Building"].argmax(1).cpu()


def hgt_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    c = {**CFG, **cfg}
    device = device or pick_device()
    set_seed(seed)
    xd, ed = _device_graph(data, use_prov, device)
    model = HGT(c["hidden"], n_classes, c["heads"], c["layers"], data.metadata()).to(device)
    with torch.no_grad():
        model(xd, ed)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    yb, tr = y.to(device), train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        F.cross_entropy(model(xd, ed)[tr], yb[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return model(xd, ed).argmax(1).cpu()


def han_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    c = {**CFG, **cfg}
    device = device or pick_device()
    set_seed(seed)
    xd, ed = _device_graph(data, use_prov, device)
    model = HAN(c["hidden"], n_classes, c["heads"], data.metadata(), c["dropout"]).to(device)
    with torch.no_grad():
        model(xd, ed)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    yb, tr = y.to(device), train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        F.cross_entropy(model(xd, ed)[tr], yb[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return model(xd, ed).argmax(1).cpu()


def rgcn_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    c = {**CFG, **cfg}
    device = device or pick_device()
    set_seed(seed)
    order = list(data.node_types)
    hom_ei, edge_type, offset, total = _homogeneous_edge_index_typed(data)
    hom_ei, edge_type = hom_ei.to(device), edge_type.to(device)
    xd = {nt: data[nt].x.to(device) for nt in data.node_types}
    xd["Building"] = building_features(data, use_prov).to(device)
    model = RGCN(c["hidden"], n_classes, len(data.edge_types), order, c["dropout"]).to(device)
    with torch.no_grad():
        model(xd, order, hom_ei, edge_type)
    opt = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    b0, nb = offset["Building"], data["Building"].num_nodes
    yb, tr = y.to(device), train_mask.to(device)
    for _ in range(c["epochs"]):
        model.train(); opt.zero_grad()
        out = model(xd, order, hom_ei, edge_type)[b0:b0 + nb]
        F.cross_entropy(out[tr], yb[tr]).backward(); opt.step()
    model.eval()
    with torch.no_grad():
        return model(xd, order, hom_ei, edge_type)[b0:b0 + nb].argmax(1).cpu()


def _homogeneous_edge_index(data):
    """Flatten the hetero graph to one edge_index with per-type node offsets (for node2vec)."""
    offset, cur = {}, 0
    for nt in data.node_types:
        offset[nt] = cur; cur += data[nt].num_nodes
    eis = []
    for (s_, r_, t_) in data.edge_types:
        ei = data[s_, r_, t_].edge_index.clone()
        ei[0] += offset[s_]; ei[1] += offset[t_]; eis.append(ei)
    hom = torch.cat(eis, 1) if eis else torch.empty((2, 0), dtype=torch.long)
    return hom, offset, cur


def _probe_on(emb, y, train_mask):
    from sklearn.linear_model import LogisticRegression
    tr = train_mask.cpu().numpy()
    clf = LogisticRegression(max_iter=2000).fit(emb[tr], y.cpu().numpy()[tr])
    return torch.tensor(clf.predict(emb), dtype=torch.long)


def node2vec_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    """Shallow, structure-only embedding (no features, transductive) + logistic-regression probe."""
    from torch_geometric.nn import Node2Vec
    c = {**CFG, **cfg}; device = device or pick_device(); set_seed(seed)
    hom, offset, total = _homogeneous_edge_index(data)
    m = Node2Vec(hom.to(device), embedding_dim=c["emb_dim"], walk_length=c["walk_length"],
                 context_size=c["context_size"], walks_per_node=c["walks_per_node"],
                 num_negative_samples=1, num_nodes=total, sparse=True).to(device)
    loader = m.loader(batch_size=128, shuffle=True, num_workers=0)
    opt = torch.optim.SparseAdam(list(m.parameters()), lr=0.01)
    m.train()
    for _ in range(c["n2v_epochs"]):
        for pos, neg in loader:
            opt.zero_grad(); m.loss(pos.to(device), neg.to(device)).backward(); opt.step()
    m.eval()
    with torch.no_grad():
        z = m().cpu().numpy()
    b0, nb = offset["Building"], data["Building"].num_nodes
    return _probe_on(z[b0:b0 + nb], y, train_mask)


def metapath2vec_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    """Type-aware shallow embedding: walks follow the provenance metapath. + probe."""
    from torch_geometric.nn import MetaPath2Vec
    from neo4j_loader import METAPATH
    c = {**CFG, **cfg}; device = device or pick_device(); set_seed(seed)
    metapath = [mp for mp in METAPATH if tuple(mp) in set(data.edge_types)]
    m = MetaPath2Vec(data.edge_index_dict, embedding_dim=c["emb_dim"], metapath=metapath,
                     walk_length=c["walk_length"], context_size=c["context_size"],
                     walks_per_node=c["walks_per_node"], num_negative_samples=1,
                     num_nodes_dict={nt: data[nt].num_nodes for nt in data.node_types},
                     sparse=True).to(device)
    loader = m.loader(batch_size=128, shuffle=True, num_workers=0)
    opt = torch.optim.SparseAdam(list(m.parameters()), lr=0.01)
    m.train()
    for _ in range(c["n2v_epochs"]):
        for pos, neg in loader:
            opt.zero_grad(); m.loss(pos.to(device), neg.to(device)).backward(); opt.step()
    m.eval()
    with torch.no_grad():
        emb = m("Building").cpu().numpy()
    return _probe_on(emb, y, train_mask)


def _padded_homogeneous_features(data, order, offset, total):
    """Zero-pad every node type's feature matrix to the widest type's width, then stack into one
    [total, max_dim] tensor in `order`. This is the simplest way to hand DGI's homogeneous
    (x, edge_index) interface a single input across node types of different native width --
    deliberately not a learned projection, so DGI's only trainable part is its GNN encoder."""
    width = max(data[nt].x.size(1) for nt in order)
    x = torch.zeros(total, width, dtype=torch.float)
    for nt in order:
        b0 = offset[nt]
        xt = data[nt].x
        x[b0:b0 + xt.size(0), :xt.size(1)] = xt
    return x


class _DGIEncoder(torch.nn.Module):
    """Two-layer GraphSAGE encoder for DeepGraphInfomax -- unlike node2vec/metapath2vec (which learn
    a fixed per-node lookup table), this is a real GNN encoder: inductive, so it could in principle
    also serve unseen nodes/cities (unlike the shallow embeddings above)."""
    def __init__(self, hidden):
        super().__init__()
        self.c1 = SAGEConv((-1, -1), hidden)
        self.c2 = SAGEConv((-1, -1), hidden)

    def forward(self, x, edge_index):
        return self.c2(self.c1(x, edge_index).relu(), edge_index)


def _dgi_corruption(x, edge_index):
    perm = torch.randperm(x.size(0), device=x.device)
    return x[perm], edge_index


def _dgi_summary(z, *args, **kwargs):
    return torch.sigmoid(z.mean(dim=0))


def dgi_predict(data, y, train_mask, n_classes, seed, use_prov, device=None, **cfg):
    """Self-supervised pretraining (DGI): maximise agreement between node embeddings and a graph-level
    summary, contrasted against a corrupted (row-shuffled) graph, then freeze and probe -- same
    frozen-embedding protocol as node2vec/metapath2vec, but the encoder is a real (inductive) GNN."""
    c = {**CFG, **cfg}; device = device or pick_device(); set_seed(seed)
    order = list(data.node_types)
    hom_ei, offset, total = _homogeneous_edge_index(data)
    x = _padded_homogeneous_features(data, order, offset, total).to(device)
    hom_ei = hom_ei.to(device)
    dgi = DeepGraphInfomax(c["hidden"], _DGIEncoder(c["hidden"]), _dgi_summary, _dgi_corruption).to(device)
    opt = torch.optim.Adam(dgi.parameters(), lr=c["lr"])
    dgi.train()
    for _ in range(c["n2v_epochs"]):
        opt.zero_grad()
        pos_z, neg_z, summary = dgi(x, hom_ei)
        dgi.loss(pos_z, neg_z, summary).backward(); opt.step()
    dgi.eval()
    with torch.no_grad():
        z, _, _ = dgi(x, hom_ei)
    b0, nb = offset["Building"], data["Building"].num_nodes
    return _probe_on(z.cpu().numpy()[b0:b0 + nb], y, train_mask)


METHODS = {
    "probe": probe_predict,                 # F0  attribute-only (no graph)
    "node2vec": node2vec_predict,           # F1a shallow, structure-only
    "metapath2vec": metapath2vec_predict,   # F1b shallow, type-aware
    "dgi": dgi_predict,                     # F1c self-supervised GNN encoder, frozen + probed
    "gnn": gnn_predict,                     # F2  GraphSAGE (hetero)
    "gat": gat_predict,                     # F2  GAT (hetero)
    "hgt": hgt_predict,                     # F3  Heterogeneous Graph Transformer (source-typed)
    "han": han_predict,                     # F3  Heterogeneous Graph Attention Network (source-typed)
    "rgcn": rgcn_predict,                   # F3  Relational GCN (source-typed)
    "gnn_aware": gnn_aware_predict,         # F4  provenance-AWARE, confidence-weighted (Eq.1)
}


# ---------------------------------------------------------------- evaluation
def _eval_one(data, split_name, method, seed, use_prov, k, cfg, device, splitter):
    sp = splitter(data, seed, k=k)[split_name]
    train_fn = METHODS[method]
    y, ncl = sp["y"], sp["n_classes"]
    if split_name == "random":
        tr, _, te = sp["mask"]
        pred = train_fn(data, y, tr, ncl, seed, use_prov, device=device, **cfg)
        te = te.numpy()
        return oof_scores(y.numpy()[te], pred.numpy()[te], ncl)
    # spatial_cv: pool out-of-fold predictions
    n = data["Building"].num_nodes
    oof = np.full(n, -1)
    for tr, te in sp["folds"]:
        pred = train_fn(data, y, tr, ncl, seed, use_prov, device=device, **cfg)
        te = te.numpy(); oof[te] = pred.numpy()[te]
    m = oof >= 0
    return oof_scores(y.numpy()[m], oof[m], ncl)


def run_method(data, method="gnn", use_prov=False, seeds=(0, 1, 2, 3, 4),
               splits=("random", "spatial_cv"), k=5, device=None, splitter=make_splits, **cfg):
    """Return {split: {'macro_mean','macro_std','per_mean','n_classes','names'}} over seeds.
    `splitter` selects the classification target: `make_splits` (roof type, default) or
    `splits.make_splits_function` (building function/use) -- same training code, different label."""
    device = device or pick_device()
    out = {}
    for split_name in splits:
        macros, pers = [], []
        for s in seeds:
            macro, per = _eval_one(data, split_name, method, s, use_prov, k, cfg, device, splitter)
            macros.append(macro); pers.append(per)
        sp = splitter(data, seeds[0], k=k)[split_name]
        out[split_name] = {
            "macro_mean": float(np.mean(macros)), "macro_std": float(np.std(macros)),
            "per_mean": np.mean(np.array(pers), axis=0).round(3).tolist(),
            "n_classes": sp["n_classes"], "names": sp["names"],
        }
    return out


def oof_predictions(data, method, seed, use_prov=False, k=5, device=None, splitter=make_splits, **cfg):
    """Pooled out-of-fold predictions on the spatial_cv split (for per-node slicing).
    Returns (y_true[n], oof_pred[n] with -1 = unlabeled, n_classes, names)."""
    device = device or pick_device()
    sp = splitter(data, seed, k=k)["spatial_cv"]
    y, ncl = sp["y"], sp["n_classes"]
    oof = np.full(data["Building"].num_nodes, -1)
    for tr, te in sp["folds"]:
        pred = METHODS[method](data, y, tr, ncl, seed, use_prov, device=device, **cfg)
        te = te.numpy(); oof[te] = pred.numpy()[te]
    return y.numpy(), oof, ncl, sp["names"]


def print_result(tag, res):
    for split_name, r in res.items():
        per = dict(zip(r["names"], r["per_mean"]))
        print(f"  {tag:26s} [{split_name:10s}] macroF1={r['macro_mean']:.3f}±{r['macro_std']:.3f}"
              f"  per-class={per}")


if __name__ == "__main__":
    from neo4j_loader import load_from_neo4j
    dev = pick_device()
    print("device:", dev)
    data = load_from_neo4j(database="hamburg", city="hamburg", verbose=False)

    # majority floors (S4): reuse oof_scores via a constant predictor per split
    print("\n-- S5 agnostic: roof-type classification (seeds 0-2) --")
    print_result("F0 attribute probe", run_method(data, "probe", seeds=(0, 1, 2)))
    print_result("F2 GraphSAGE (hetero)", run_method(data, "gnn", seeds=(0, 1, 2), epochs=120))

    # scale-path sanity: 1-epoch mini-batch run must execute without error
    print("\n-- mini-batch path smoke (1 epoch) --")
    print_result("GraphSAGE minibatch", run_method(data, "gnn", seeds=(0,), epochs=1,
                                                    full_batch=False, batch_size=32,
                                                    num_neighbors=[10, 10]))
