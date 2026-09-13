from importlib import import_module


_MODELS = {
    'Campaign': '.campaign',
    'MessagingAccount': '.account',
    'MessageLog': '.message_log',
    'CampaignRecipient': '.recipient',
}

__all__ = list(_MODELS)


def __getattr__(name):
    module_name = _MODELS.get(name)
    if module_name is None:
        raise AttributeError(name)
    return getattr(import_module(module_name, __name__), name)
