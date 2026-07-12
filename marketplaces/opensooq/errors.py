class OpenSooqError(Exception): pass
class PaginationExhaustedError(OpenSooqError): pass
class ExtractionError(OpenSooqError): pass
class InvalidCountryError(OpenSooqError): pass
