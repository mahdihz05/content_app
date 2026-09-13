from django.test import SimpleTestCase

from automation.exceptions import InvalidStateTransition
from automation.models import AutomationCommand, OutboxEvent, WorkflowExecution


class ExplicitStateTransitionTests(SimpleTestCase):
    def test_command_terminal_state_cannot_transition(self):
        command = AutomationCommand(status=AutomationCommand.Status.SUCCEEDED)
        with self.assertRaises(InvalidStateTransition):
            command.transition_to(AutomationCommand.Status.RUNNING)

    def test_outbox_retry_path_is_explicit(self):
        event = OutboxEvent(status=OutboxEvent.Status.FAILED)
        event.transition_to(OutboxEvent.Status.PENDING)
        self.assertEqual(event.status, OutboxEvent.Status.PENDING)

    def test_execution_cannot_skip_from_created_to_succeeded(self):
        execution = WorkflowExecution(status=WorkflowExecution.Status.CREATED)
        with self.assertRaises(InvalidStateTransition):
            execution.transition_to(WorkflowExecution.Status.SUCCEEDED)
