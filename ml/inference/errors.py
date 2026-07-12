class InferenceError(Exception): pass
class ValidationError(InferenceError): pass
class AuditError(InferenceError): pass
