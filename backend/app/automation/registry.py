from dataclasses import dataclass

from automation.exceptions import ContractValidationError, PolicyDenied
from automation.fingerprints import fingerprint


@dataclass(frozen=True)
class ToolSpec:
    name: str
    version: str
    effect: str
    workflow_name: str
    workflow_version: str
    input_schema: dict
    result_schema: dict


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    requires_approval: bool
    policy_version: str
    reason: str = ''
    facts: dict | None = None

    @property
    def fingerprint(self):
        return fingerprint({
            'allowed': self.allowed,
            'requires_approval': self.requires_approval,
            'policy_version': self.policy_version,
            'facts': self.facts or {},
        })


@dataclass(frozen=True)
class PreflightResult:
    spec: ToolSpec
    payload_fingerprint: str
    policy_fingerprint: str
    policy: PolicyDecision


def _is_type(value, expected):
    checks = {
        'object': lambda item: isinstance(item, dict),
        'array': lambda item: isinstance(item, list),
        'string': lambda item: isinstance(item, str),
        'integer': lambda item: isinstance(item, int) and not isinstance(item, bool),
        'number': lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        'boolean': lambda item: isinstance(item, bool),
        'null': lambda item: item is None,
    }
    return expected in checks and checks[expected](value)


def validate_schema(value, schema, path='$'):
    """Validate the intentionally small JSON Schema subset used by tool contracts."""
    errors = []
    expected = schema.get('type')
    if expected and not _is_type(value, expected):
        return [f'{path}: expected {expected}']
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{path}: value is not in enum')
    if expected == 'object' and isinstance(value, dict):
        properties = schema.get('properties', {})
        for name in schema.get('required', []):
            if name not in value:
                errors.append(f'{path}.{name}: required')
        if schema.get('additionalProperties') is False:
            for name in value.keys() - properties.keys():
                errors.append(f'{path}.{name}: additional property not allowed')
        for name, item in value.items():
            if name in properties:
                errors.extend(validate_schema(item, properties[name], f'{path}.{name}'))
    if expected == 'array' and isinstance(value, list):
        if 'minItems' in schema and len(value) < schema['minItems']:
            errors.append(f'{path}: too few items')
        if 'maxItems' in schema and len(value) > schema['maxItems']:
            errors.append(f'{path}: too many items')
        if 'items' in schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, schema['items'], f'{path}[{index}]'))
    if expected == 'string' and isinstance(value, str):
        if 'minLength' in schema and len(value) < schema['minLength']:
            errors.append(f'{path}: too short')
        if 'maxLength' in schema and len(value) > schema['maxLength']:
            errors.append(f'{path}: too long')
    if expected in {'integer', 'number'} and _is_type(value, expected):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{path}: below minimum')
        if 'maximum' in schema and value > schema['maximum']:
            errors.append(f'{path}: above maximum')
    return errors


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, spec):
        key = (spec.name, spec.version)
        if key in self._tools:
            raise ValueError(f'Tool already registered: {spec.name}@{spec.version}')
        if spec.effect not in {'read', 'draft', 'mutate_internal', 'consequential'}:
            raise ValueError(f'Invalid effect class: {spec.effect}')
        self._tools[key] = spec
        return spec

    def get(self, name, version):
        try:
            return self._tools[(name, version)]
        except KeyError as exc:
            raise ContractValidationError([f'Unknown tool: {name}@{version}']) from exc

    def preflight(self, *, name, version, payload, actor, workspace, policy_evaluator):
        spec = self.get(name, version)
        errors = validate_schema(payload, spec.input_schema)
        if errors:
            raise ContractValidationError(errors)
        decision = policy_evaluator(
            actor=actor,
            workspace=workspace,
            tool=spec,
            payload=payload,
        )
        if not isinstance(decision, PolicyDecision):
            raise TypeError('Policy evaluators must return PolicyDecision.')
        if not decision.allowed:
            raise PolicyDenied(decision.reason or 'Policy denied this tool call.')
        if spec.effect == 'consequential' and not decision.requires_approval:
            raise PolicyDenied('Consequential tools must require approval.')
        try:
            payload_fingerprint = fingerprint(payload)
            policy_fingerprint = decision.fingerprint
        except (TypeError, ValueError) as exc:
            raise ContractValidationError([
                'Payload and policy facts must be finite JSON values.'
            ]) from exc
        return PreflightResult(spec, payload_fingerprint, policy_fingerprint, decision)


registry = ToolRegistry()
