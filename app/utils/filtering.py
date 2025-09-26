
from __future__ import annotations
from typing import Dict, Any, List
def _get_path(d: Dict[str, Any], path: str) -> Any:
    cur: Any = d
    for part in path.split('.'):
        if isinstance(cur, dict) and part in cur: cur = cur[part]
        else: return None
    return cur
def apply_filters(items: List[dict], query: Dict[str, Any]) -> List[dict]:
    def match(it: dict) -> bool:
        for k, v in query.items():
            if v is None: continue
            if k in ('page','per_page','search'): continue
            if k.startswith('metadata.unharmonized.'):
                sub = (it.get('metadata') or {}).get('unharmonized') or {}
                path = k.split('.', 2)[2] if '.' in k else ''
                cur = sub
                for part in path.split('.') if path else []:
                    if isinstance(cur, dict) and part in cur: cur = cur[part]
                    else: cur = None; break
                if cur is None: return False
                if isinstance(cur, list):
                    if v not in cur: return False
                else:
                    if cur != v: return False
                continue
            val = _get_path(it, f"metadata.{k}.value")
            if val is None: return False
            if isinstance(val, list):
                if v not in val: return False
            else:
                if val != v: return False
        return True
    return [it for it in items if match(it)]
