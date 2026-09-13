from rest_framework.exceptions import APIException


class WorkspaceAccessDenied(APIException):
    status_code = 403
    default_detail = 'The selected workspace is unavailable.'
    default_code = 'workspace_access_denied'


class WorkspaceNotSelected(APIException):
    status_code = 409
    default_detail = 'No default workspace is configured.'
    default_code = 'workspace_not_selected'
