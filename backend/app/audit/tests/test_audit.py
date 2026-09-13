from django.test import TestCase

from audit.models import AuditEvent, REDACTED
from automation.tests.factories import create_workspace
from user.models import CustomUser


class AuditEventTests(TestCase):
    def setUp(self):
        self.actor = CustomUser.objects.create_user('09120000041', 'password')
        self.workspace = create_workspace(self.actor, 'audit')

    def test_payload_is_recursively_redacted_without_mutating_input(self):
        payload = {'token': 'secret', 'nested': [{'api_key': 'key', 'safe': 'value'}]}
        event = AuditEvent.objects.append(
            workspace=self.workspace,
            actor=self.actor,
            event_type='test.created',
            target_type='test',
            payload=payload,
        )
        self.assertEqual(event.payload['token'], REDACTED)
        self.assertEqual(event.payload['nested'][0]['api_key'], REDACTED)
        self.assertEqual(event.payload['nested'][0]['safe'], 'value')
        self.assertEqual(payload['token'], 'secret')

    def test_instance_update_and_delete_are_rejected(self):
        event = AuditEvent.objects.append(
            workspace=self.workspace,
            event_type='test.created',
            target_type='test',
        )
        event.event_type = 'changed'
        with self.assertRaises(TypeError):
            event.save()
        with self.assertRaises(TypeError):
            event.delete()

    def test_queryset_update_and_delete_are_rejected(self):
        event = AuditEvent.objects.append(
            workspace=self.workspace,
            event_type='test.created',
            target_type='test',
        )
        with self.assertRaises(TypeError):
            AuditEvent.objects.filter(pk=event.pk).update(event_type='changed')
        with self.assertRaises(TypeError):
            AuditEvent.objects.filter(pk=event.pk).delete()

    def test_bulk_create_redacts_and_bulk_update_is_rejected(self):
        event = AuditEvent(
            workspace=self.workspace,
            event_type='test.created',
            target_type='test',
            payload={'password': 'not-for-storage'},
        )
        AuditEvent.objects.bulk_create([event])
        event.refresh_from_db()
        self.assertEqual(event.payload['password'], REDACTED)
        with self.assertRaises(TypeError):
            AuditEvent.objects.bulk_update([event], ['event_type'])
