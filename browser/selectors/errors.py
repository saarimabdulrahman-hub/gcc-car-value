class SelectorError(Exception): pass
class InvalidSelectorError(SelectorError): pass
class SelectorNotFoundError(SelectorError): pass
class DuplicateSelectorError(SelectorError): pass
class SelectorCompilationError(SelectorError): pass
