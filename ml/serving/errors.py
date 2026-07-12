class ServingError(Exception): pass
class ModelNotLoadedError(ServingError): pass
class DeploymentError(ServingError): pass
class RoutingError(ServingError): pass
