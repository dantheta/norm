
class NORMException(Exception): pass

class ObjectNotFound(NORMException): pass
class ObjectExists(NORMException): pass

class NotUpdatableError(NORMException): pass

class InvalidFieldError(NORMException): pass
