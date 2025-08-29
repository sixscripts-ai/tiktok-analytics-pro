from __future__ import annotations
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

def load_videos_any(path: str) -> List[Dict[str, Any]]:
    """Load videos from JSON, JSONL, or other formats."""
    p = Path(path)
    if not p.exists():
        return []
    
    text = p.read_text(encoding='utf-8', errors='ignore')
    if not text.strip():
        return []
    
    # Try JSON array first
    if text.lstrip().startswith('['):
        try:
            return json.loads(text)
        except Exception:
            pass
    
    # Try JSONL (one JSON object per line)
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    
    return rows

def canon_hashtag(tag: str) -> Optional[str]:
    """Normalize hashtag format."""
    if not tag:
        return None
    tag = tag.strip().lower()
    if tag.startswith('#'):
        tag = tag[1:]
    if not tag:
        return None
    return tag
