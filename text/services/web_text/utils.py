import json
import urllib.parse
from typing import Dict


def parse_kv_response(text: str) -> Dict[str, str]:
    text = text.strip()
    if not text:
        return {}

    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    if '&' in text and '=' in text:
        parsed = urllib.parse.parse_qs(text, keep_blank_values=True, strict_parsing=False)
        return {k: v[0] for k, v in parsed.items()}

    data: Dict[str, str] = {}
    for line in text.splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            data[k.strip()] = v.strip()
    return data