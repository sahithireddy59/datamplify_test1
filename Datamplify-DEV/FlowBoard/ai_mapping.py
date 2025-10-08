import re
import difflib
from .ai_llm import query_llm
from typing import List, Dict, Any, Tuple

# Basic synonyms for common business terms (can be expanded)
SYNONYMS = {
    'id': {'id', 'identifier', 'uid', 'guid', 'code', 'key'},
    'name': {'name', 'fullname', 'full_name', 'first_name', 'lastname', 'last_name'},
    'email': {'email', 'e_mail', 'mail'},
    'phone': {'phone', 'mobile', 'telephone', 'tel'},
    'date': {'date', 'dt', 'created_at', 'updated_at', 'timestamp'},
    'address': {'address', 'addr', 'location'},
    'amount': {'amount', 'amt', 'price', 'value', 'total'},
}

TYPE_FAMILIES = {
    'int': {'int', 'integer', 'bigint', 'smallint', 'serial'},
    'float': {'float', 'double', 'real', 'numeric', 'decimal'},
    'text': {'text', 'varchar', 'char', 'string', 'uuid'},
    'bool': {'bool', 'boolean'},
    'date': {'date', 'datetime', 'timestamp', 'timestamptz', 'time'},
}

def normalize_name(name: str) -> str:
    s = name or ''
    s = s.strip().lower()
    s = s.replace('-', '_').replace(' ', '_')
    # remove non-alnum underscores
    s = re.sub(r'[^a-z0-9_]+', '', s)
    # collapse repeats
    s = re.sub(r'_+', '_', s)
    return s


def family_of(t: str) -> str:
    if not t:
        return ''
    tl = t.strip().lower()
    for fam, members in TYPE_FAMILIES.items():
        if any(m in tl for m in members):
            return fam
    return tl


def type_compat_score(src_type: str, tgt_type: str) -> float:
    if not src_type or not tgt_type:
        return 0.5
    fs, ft = family_of(src_type), family_of(tgt_type)
    if fs == ft:
        return 1.0
    # common safe casts
    if (fs == 'int' and ft in {'float', 'text'}) or (fs == 'float' and ft == 'text'):
        return 0.8
    if (fs == 'text' and ft in {'int', 'float'}):
        return 0.6
    return 0.4


def synonym_boost(src_norm: str, tgt_norm: str) -> float:
    def tokens(s: str) -> List[str]:
        return [p for p in s.split('_') if p]
    s_tokens, t_tokens = tokens(src_norm), tokens(tgt_norm)
    score = 0.0
    for syn_group in SYNONYMS.values():
        if any(tok in syn_group for tok in s_tokens) and any(tok in syn_group for tok in t_tokens):
            score += 0.2
    return min(score, 0.4)


def lexical_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def suggest_mappings(
    source: List[Dict[str, Any]],
    target: List[Dict[str, Any]],
    max_sources_per_target: int = 1
) -> Dict[str, Any]:
    """
    Inputs:
      source: [{name: str, type: str, description?: str}]
      target: [{name: str, type: str, description?: str}]
    Returns:
      {
        mappings: [
          {target, source, transform, cast, confidence, rationale}
        ],
        unresolved: [{target, reasons}]
      }
    """
    src_rows = [
        {
            'name': s.get('name'),
            'type': s.get('type'),
            'norm': normalize_name(s.get('name', '')),
            'desc': (s.get('description') or '').lower(),
        }
        for s in source or []
    ]

    tgt_rows = [
        {
            'name': t.get('name'),
            'type': t.get('type'),
            'norm': normalize_name(t.get('name', '')),
            'desc': (t.get('description') or '').lower(),
        }
        for t in target or []
    ]

    mappings: List[Dict[str, Any]] = []
    unresolved: List[Dict[str, Any]] = []

    used_src = set()

    for tgt in tgt_rows:
        best: List[Tuple[float, Dict[str, Any]]] = []
        for src in src_rows:
            # base lexical similarity on normalized names
            lex = lexical_similarity(src['norm'], tgt['norm'])
            # token overlap
            tok_overlap = lexical_similarity('_'.join(sorted(set(src['norm'].split('_')))),
                                             '_'.join(sorted(set(tgt['norm'].split('_')))))
            # synonym boost if tokens share a synonym family
            syn = synonym_boost(src['norm'], tgt['norm'])
            # type compatibility
            tscore = type_compat_score(src['type'] or '', tgt['type'] or '')

            score = 0.55 * lex + 0.15 * tok_overlap + 0.15 * syn + 0.15 * tscore

            best.append((score, src))

        # sort descending
        best.sort(key=lambda x: x[0], reverse=True)
        chosen = []
        reasons = []

        for score, src in best[:max_sources_per_target]:
            if src['name'] in used_src:
                continue
            # heuristic threshold
            if score >= 0.62 or (score >= 0.55 and family_of(src['type']) == family_of(tgt['type'])):
                used_src.add(src['name'])
                cast = None
                fs, ft = family_of(src['type'] or ''), family_of(tgt['type'] or '')
                if fs and ft and fs != ft:
                    # propose safe cast
                    if fs == 'int' and ft == 'float':
                        cast = 'DOUBLE'
                    elif ft == 'text':
                        cast = 'TEXT'
                    elif ft == 'int':
                        cast = 'INTEGER'
                    elif ft == 'float':
                        cast = 'DOUBLE'
                    elif ft == 'date':
                        cast = 'TIMESTAMP'
                chosen.append({
                    'target': tgt['name'],
                    'source': src['name'],
                    'transform': None,
                    'cast': cast,
                    'confidence': round(float(score), 3),
                    'rationale': f"lex={round(lexical_similarity(src['norm'], tgt['norm']),3)}, type={fs}->{ft}"
                })

        if not chosen:
            unresolved.append({
                'target': tgt['name'],
                'reasons': ['no close lexical/semantic match']
            })
        else:
            mappings.extend(chosen)

    return {
        'mappings': mappings,
        'unresolved': unresolved
    }


def parse_nl_mappings(
    instruction: str,
    source_columns: List[str],
    target_columns: List[str]
) -> Dict[str, Any]:
    """
    Parse simple natural language mapping instructions into mapping objects.
    Supports patterns:
      - "map X to Y"
      - "Y from X" / "Y = X" / "Y <- X"
      - "Y as concat(a,' ',b)" or "map concat(a,b) to Y"
      - "cast X to INT as Y" / "Y as cast(X as INT)"
    Returns { mappings: [...], unresolved: [...] }
    """
    text = (instruction or '').strip()
    if not text:
        return {'mappings': [], 'unresolved': []}

    import json
    # Normalize spacing
    s = re.sub(r"\s+", " ", text.lower())

    # Helper to best-match a column name from provided lists
    all_sources_norm = {normalize_name(c): c for c in (source_columns or [])}
    all_targets_norm = {normalize_name(c): c for c in (target_columns or [])}

    def match_col(name: str, pool: Dict[str, str]) -> Optional[str]:
        n = normalize_name(name)
        if n in pool:
            return pool[n]
        # fuzzy fallback
        if pool:
            cand = difflib.get_close_matches(n, list(pool.keys()), n=1, cutoff=0.7)
            if cand:
                return pool[cand[0]]
        return name  # return as-is if nothing matches

    mappings: List[Dict[str, Any]] = []

    # Split by connectors like ';' or ' and '
    parts = re.split(r";|\band\b", s)
    for part in parts:
        p = part.strip()
        if not p:
            continue

        # 1) map X to Y
        m = re.match(r"^map\s+(.+?)\s+to\s+([a-zA-Z0-9_]+)$", p)
        if m:
            expr, tgt = m.group(1).strip(), m.group(2).strip()
            # If expr looks like concat or cast, keep as transform; else treat as direct source
            if re.search(r"\bconcat\b|\bcast\b|\+|\-|\*|\/|\(|\)", expr):
                mappings.append({
                    'target': match_col(tgt, all_targets_norm),
                    'source': None,
                    'transform': expr,
                    'cast': None,
                    'confidence': 0.9,
                    'rationale': 'parsed: map <expr> to <target>'
                })
            else:
                mappings.append({
                    'target': match_col(tgt, all_targets_norm),
                    'source': match_col(expr, all_sources_norm),
                    'transform': None,
                    'cast': None,
                    'confidence': 0.9,
                    'rationale': 'parsed: map <source> to <target>'
                })
            continue

        # 2) Y from X / Y = X / Y <- X
        m = re.match(r"^([a-z0-9_]+)\s*(?:from|=|<-)+\s*(.+)$", p)
        if m:
            tgt, src = m.group(1).strip(), m.group(2).strip()
            mappings.append({
                'target': match_col(tgt, all_targets_norm),
                'source': match_col(src, all_sources_norm),
                'transform': None,
                'cast': None,
                'confidence': 0.9,
                'rationale': 'parsed: <target> from <source>'
            })
            continue

        # 3) Y as concat(...)
        m = re.match(r"^([a-z0-9_]+)\s+as\s+(.+)$", p)
        if m:
            tgt, expr = m.group(1).strip(), m.group(2).strip()
            mappings.append({
                'target': match_col(tgt, all_targets_norm),
                'source': None,
                'transform': expr,
                'cast': None,
                'confidence': 0.9,
                'rationale': 'parsed: <target> as <expr>'
            })
            continue

        # 4) cast X to INT as Y
        m = re.match(r"^cast\s+([a-z0-9_]+)\s+to\s+([a-z0-9_()]+)\s+as\s+([a-z0-9_]+)$", p)
        if m:
            src, dtype, tgt = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            mappings.append({
                'target': match_col(tgt, all_targets_norm),
                'source': match_col(src, all_sources_norm),
                'transform': None,
                'cast': dtype.upper(),
                'confidence': 0.88,
                'rationale': 'parsed: cast <source> to <type> as <target>'
            })
            continue

        # If nothing matched and looks like JSON array, try to parse directly
        try:
            data = json.loads(p)
            if isinstance(data, dict) and 'mappings' in data:
                for m1 in data['mappings']:
                    mappings.append(m1)
                continue
        except Exception:
            pass

        # Fallback: ignore unrecognized part
        continue

    return {'mappings': mappings, 'unresolved': []}
