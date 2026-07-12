class DOMError(Exception): pass
class SelectorError(DOMError): pass
class ExtractionError(DOMError): pass
class ValidationError(DOMError): pass
class NodeNotFoundError(DOMError): pass
