
from __future__ import annotations
from typing import List, Dict, Any, Optional
from pathlib import Path
import json, csv, datetime as dt

try:
    import pandas as pd
except Exception:
    pd = None

def _norm_date(s) -> Optional[str]:
    if s is None: return None
    try:
        if isinstance(s, (int,float)):
            return dt.datetime.utcfromtimestamp(int(s)).isoformat()
        ss = str(s)
        if ss.endswith('Z'): ss = ss[:-1]
        return dt.datetime.fromisoformat(ss).isoformat()
    except Exception:
        return None

def _norm_int(x) -> Optional[int]:
    if x is None: return None
    try:
        return int(float(str(x).replace(',','').strip().lower().replace('k','e3').replace('m','e6').replace('b','e9')))
    except Exception:
        try:
            return int(x)
        except Exception:
            return None

def _dedupe(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for r in rows:
        key = r.get('video_id') or r.get('url')
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out

def normalize_videos(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        r2 = dict(r)
        r2['views'] = _norm_int(r.get('views') or r.get('play_count'))
        r2['likes'] = _norm_int(r.get('likes'))
        r2['comments'] = _norm_int(r.get('comments'))
        r2['shares'] = _norm_int(r.get('shares'))
        r2['create_time'] = _norm_date(r.get('create_time') or r.get('created_at') or r.get('timestamp'))
        out.append(r2)
    return _dedupe(out)

def export(rows: List[Dict[str, Any]], path: str, fmt: Optional[str] = None):
    p = Path(path)
    fmt = fmt or p.suffix.lower().lstrip('.')
    if fmt in ('jsonl',):
        with p.open('w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    elif fmt in ('json', ''):
        p.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')
    elif fmt == 'csv':
        if not rows:
            p.write_text('', encoding='utf-8')
            return
        with p.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=sorted(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)
    elif fmt in ('xlsx','xls'):
        if pd is None:
            raise RuntimeError('pandas required for Excel export')
        df = pd.DataFrame(rows)
        df.to_excel(p, index=False)
    elif fmt == 'pdf':
        # lightweight PDF via pandas -> html -> weasyprint/reportlab would be nicer; keep simple fallback
        if pd is None:
            raise RuntimeError('pandas required for PDF export fallback')
        df = pd.DataFrame(rows)
        html = df.to_html(index=False)
        p_html = p.with_suffix('.html')
        p_html.write_text(html, encoding='utf-8')
        # leave HTML; PDF step depends on external tools; document this limitation
    else:
        raise ValueError(f'Unsupported format: {fmt}')

def process(input_path: str, output_path: str, fmt: Optional[str]=None, where: Optional[str]=None, order: Optional[str]=None) -> Dict[str, Any]:
    text = Path(input_path).read_text(encoding='utf-8', errors='ignore')
    rows = []
    if text.lstrip().startswith('['):
        rows = json.loads(text)
    else:
        for line in text.splitlines():
            line=line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    rows = normalize_videos(rows)

    # basic filter: Python expression with 'r' as row dict (use responsibly)
    if where:
        filt = []
        for r in rows:
            try:
                if eval(where, {}, {'r': r}):
                    filt.append(r)
            except Exception:
                pass
        rows = filt

    # ordering: comma-separated fields, prefix '-' for desc
    if order:
        keys = [k.strip() for k in order.split(',') if k.strip()]
        def keyfunc(r):
            out=[]
            for k in keys:
                desc = k.startswith('-')
                kk = k[1:] if desc else k
                out.append((not desc, r.get(kk)))
            return tuple(out)
        rows = sorted(rows, key=lambda r: tuple(
            (-1 if k.startswith('-') else 1, r.get(k[1:] if k.startswith('-') else k))
            for k in keys
        ))

    export(rows, output_path, fmt=fmt)
    return {'count': len(rows), 'out': output_path}

if __name__ == '__main__':
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--format', default=None, help='json|jsonl|csv|xlsx|pdf')
    ap.add_argument('--where', default=None, help="Python expr with 'r' as row, e.g., r['views']>10000")
    ap.add_argument('--order', default=None, help='Fields comma-separated; prefix - for desc')
    args = ap.parse_args()
    res = process(args.inp, args.out, fmt=args.format, where=args.where, order=args.order)
    print(json.dumps(res, indent=2))
