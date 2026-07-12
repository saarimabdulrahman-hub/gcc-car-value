class TrainingError(Exception): pass
class ModelNotFoundError(TrainingError): pass
class ExperimentError(TrainingError): pass
class EvaluationError(TrainingError): pass
