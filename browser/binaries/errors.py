class BinaryError(Exception): pass
class BinaryNotFoundError(BinaryError): pass
class BinaryInvalidError(BinaryError): pass
class BinaryPlatformError(BinaryError): pass
class BinaryVersionError(BinaryError): pass
class BinaryRegistrationError(BinaryError): pass
