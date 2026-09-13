from django.test import SimpleTestCase

from automation.exceptions import ContractValidationError, PolicyDenied
from automation.registry import PolicyDecision, ToolRegistry, ToolSpec


class ToolRegistryTests(SimpleTestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.spec = self.registry.register(ToolSpec(
            name='content.publish',
            version='1',
            effect='consequential',
            workflow_name='content.publish',
            workflow_version='1',
            input_schema={
                'type': 'object',
                'required': ['content_id'],
                'additionalProperties': False,
                'properties': {'content_id': {'type': 'string', 'minLength': 1}},
            },
            result_schema={'type': 'object'},
        ))

    def test_schema_rejects_missing_and_unknown_fields(self):
        with self.assertRaises(ContractValidationError) as caught:
            self.registry.preflight(
                name='content.publish', version='1', payload={'extra': True},
                actor=object(), workspace=object(),
                policy_evaluator=lambda **kwargs: PolicyDecision(True, True, '1'),
            )
        self.assertEqual(len(caught.exception.errors), 2)

    def test_consequential_policy_cannot_omit_approval(self):
        with self.assertRaises(PolicyDenied):
            self.registry.preflight(
                name='content.publish', version='1', payload={'content_id': '123'},
                actor=object(), workspace=object(),
                policy_evaluator=lambda **kwargs: PolicyDecision(True, False, '1'),
            )

    def test_fingerprints_are_stable_for_key_order(self):
        schema = dict(self.spec.input_schema)
        schema['properties'] = {'content_id': {'type': 'string'}, 'destination': {'type': 'string'}}
        schema['required'] = ['content_id', 'destination']
        registry = ToolRegistry()
        registry.register(ToolSpec('tool', '1', 'draft', 'workflow', '1', schema, {'type': 'object'}))
        evaluate = lambda **kwargs: PolicyDecision(True, False, 'policy-1', facts={'role': 'owner'})
        first = registry.preflight(name='tool', version='1', payload={'content_id': '1', 'destination': 'x'}, actor=object(), workspace=object(), policy_evaluator=evaluate)
        second = registry.preflight(name='tool', version='1', payload={'destination': 'x', 'content_id': '1'}, actor=object(), workspace=object(), policy_evaluator=evaluate)
        self.assertEqual(first.payload_fingerprint, second.payload_fingerprint)
        self.assertEqual(first.policy_fingerprint, second.policy_fingerprint)
