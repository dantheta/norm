
class NORMException(Exception): pass

class ObjectNotFound(NORMException): pass
class ObjectExists(NORMException): pass

class InvalidFieldError(NORMException): pass
