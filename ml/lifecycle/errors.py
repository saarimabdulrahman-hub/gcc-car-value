class LifecycleError(Exception): pass
class WorkflowError(LifecycleError): pass
class ApprovalError(LifecycleError): pass
class PromotionError(LifecycleError): pass
