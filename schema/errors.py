class SchemaError(Exception): pass
class ValidationError(SchemaError): pass
class MissingRequiredFieldError(ValidationError): pass
class InvalidFieldError(ValidationError): pass
class SchemaVersionError(SchemaError): pass
