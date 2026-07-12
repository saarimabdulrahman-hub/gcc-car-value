class DubizzleError(Exception): pass
class PaginationExhaustedError(DubizzleError): pass
class ExtractionError(DubizzleError): pass
class MappingError(DubizzleError): pass
