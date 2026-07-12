class FeatureError(Exception): pass
class FeatureNotFoundError(FeatureError): pass
class DuplicateFeatureError(FeatureError): pass
class ValidationError(FeatureError): pass
