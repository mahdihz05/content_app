import hashlib
import hmac
import secrets
import time
import uuid

from django.core import signing

from automation.exceptions import InvalidCallback, InvalidGrant
from automation.fingerprints import canonical_json


GRANT_SALT = 'automation.execution-grant.v1'
MAX_GRANT_TTL_SECONDS = 300
CALLBACK_CLOCK_SKEW_SECONDS = 300


def issue_execution_grant(*, execution, scopes, ttl_seconds=120, now=None):
    if not 1 <= ttl_seconds <= MAX_GRANT_TTL_SECONDS:
        raise ValueError(f'Grant lifetime must be 1-{MAX_GRANT_TTL_SECONDS} seconds.')
    issued_at = int(now if now is not None else time.time())
    claims = {
        'version': 'v1',
        'jti': str(execution.grant_jti),
        'command_id': str(execution.command.public_id),
        'execution_id': str(execution.public_id),
        'workspace_id': str(execution.workspace.public_id),
        'workflow_name': execution.workflow_name,
        'workflow_version': execution.workflow_version,
        'scopes': sorted(set(scopes)),
        'iat': issued_at,
        'exp': issued_at + ttl_seconds,
        'callback_secret': secrets.token_urlsafe(32),
    }
    return signing.dumps(claims, salt=GRANT_SALT, compress=True)


def verify_execution_grant(token, *, required_scope=None, now=None):
    try:
        claims = signing.loads(token, salt=GRANT_SALT, max_age=MAX_GRANT_TTL_SECONDS)
    except signing.BadSignature as exc:
        raise InvalidGrant('Execution grant signature is invalid or expired.') from exc
    current = int(now if now is not None else time.time())
    required = {
        'version', 'jti', 'command_id', 'execution_id', 'workspace_id',
        'workflow_name', 'workflow_version', 'scopes', 'iat', 'exp', 'callback_secret',
    }
    if not isinstance(claims, dict) or required - claims.keys():
        raise InvalidGrant('Execution grant claims are incomplete.')
    if claims['version'] != 'v1' or claims['iat'] > current or claims['exp'] <= current:
        raise InvalidGrant('Execution grant is outside its validity window.')
    if claims['exp'] - claims['iat'] > MAX_GRANT_TTL_SECONDS:
        raise InvalidGrant('Execution grant lifetime exceeds the maximum.')
    if required_scope and required_scope not in claims['scopes']:
        raise InvalidGrant('Execution grant does not include the required scope.')
    try:
        for name in ('jti', 'command_id', 'execution_id', 'workspace_id'):
            uuid.UUID(claims[name])
    except (ValueError, TypeError) as exc:
        raise InvalidGrant('Execution grant identifiers are invalid.') from exc
    return claims


def callback_body_hash(body):
    if isinstance(body, dict):
        body = canonical_json(body)
    return hashlib.sha256(body).hexdigest()


def callback_signature(*, callback_secret, timestamp, nonce, idempotency_key, body):
    message = '\n'.join((
        str(timestamp),
        str(nonce),
        idempotency_key,
        callback_body_hash(body),
    )).encode('utf-8')
    return hmac.new(callback_secret.encode('utf-8'), message, hashlib.sha256).hexdigest()


def verify_callback_signature(
    *, claims, timestamp, nonce, idempotency_key, body, signature, now=None
):
    current = int(now if now is not None else time.time())
    try:
        callback_time = int(timestamp)
        uuid.UUID(str(nonce))
    except (ValueError, TypeError) as exc:
        raise InvalidCallback('Callback timestamp or nonce is invalid.') from exc
    if abs(current - callback_time) > CALLBACK_CLOCK_SKEW_SECONDS:
        raise InvalidCallback('Callback timestamp is outside the accepted window.')
    if not idempotency_key or len(idempotency_key) > 128:
        raise InvalidCallback('Callback idempotency key is invalid.')
    try:
        expected = callback_signature(
            callback_secret=claims['callback_secret'],
            timestamp=callback_time,
            nonce=nonce,
            idempotency_key=idempotency_key,
            body=body,
        )
    except (TypeError, ValueError) as exc:
        raise InvalidCallback('Callback body must contain finite JSON values.') from exc
    if not hmac.compare_digest(expected, signature or ''):
        raise InvalidCallback('Callback signature is invalid.')
    return callback_body_hash(body)
