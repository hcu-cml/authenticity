import sys as _sys, os as _os
_root = _os.path.dirname(_os.path.abspath(__file__))
for _d in ('shared', 't1_imputation', 't2_classification', 't3_matching', 'crosscity', 'figures'):
    _p = _os.path.join(_root, _d)
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
