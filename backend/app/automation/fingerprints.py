import hashlib
import json


def canonical_json(value):
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(',', ':'),
        sort_keys=True,
    ).encode('utf-8')


def fingerprint(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()
