from ..exceptions import NotFoundError

class SessionNotActive(Exception):
    pass

class SessionNotFound(NotFoundError):
    pass

class ActiveSessionExists(Exception):
    pass

class NoHelpAvailable(Exception):
    pass