"""Driver manager error hierarchy."""

class DriverError(Exception): pass
class DriverNotFoundError(DriverError): pass
class DriverUnavailableError(DriverError): pass
class DriverLaunchError(DriverError): pass
class CapabilityNotSupportedError(DriverError): pass
class DriverRegistrationError(DriverError): pass
class DriverHealthError(DriverError): pass
class CompatibilityError(DriverError): pass
