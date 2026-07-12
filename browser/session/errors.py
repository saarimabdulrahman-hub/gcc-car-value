class SessionError(Exception): pass
class SessionNotFoundError(SessionError): pass
class SessionExpiredError(SessionError): pass
class CookieValidationError(SessionError): pass
class StorageStateError(SessionError): pass
class PolicyViolationError(SessionError): pass
