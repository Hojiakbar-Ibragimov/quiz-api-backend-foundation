from ..exceptions import NotFoundError

class NoChangesDetected(Exception):
    pass

class UserNotFound(NotFoundError):
    pass

class UsernameAlreadyTaken(Exception):
    pass

class UnsupportedLanguage(Exception):
    pass