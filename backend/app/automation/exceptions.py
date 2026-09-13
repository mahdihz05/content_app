class AutomationError(Exception):
    code = 'automation_error'


class ContractValidationError(AutomationError):
    code = 'contract_invalid'

    def __init__(self, errors):
        self.errors = errors
        super().__init__('Tool contract validation failed.')


class PolicyDenied(AutomationError):
    code = 'policy_denied'


class ApprovalRequired(AutomationError):
    code = 'approval_required'


class ApprovalInvalid(AutomationError):
    code = 'approval_invalid'


class IdempotencyConflict(AutomationError):
    code = 'idempotency_conflict'


class InvalidStateTransition(AutomationError):
    code = 'invalid_state_transition'


class InvalidGrant(AutomationError):
    code = 'invalid_grant'


class InvalidCallback(AutomationError):
    code = 'invalid_callback'


class CallbackReplay(AutomationError):
    code = 'callback_replay'
