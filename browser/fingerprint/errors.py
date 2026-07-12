class FingerprintError(Exception): pass
class ProfileValidationError(FingerprintError): pass
class InconsistentProfileError(FingerprintError): pass
class ProfileNotFoundError(FingerprintError): pass
