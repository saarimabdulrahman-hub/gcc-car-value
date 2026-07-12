class ChallengeError(Exception): pass
class RecoveryExhaustedError(ChallengeError): pass
class UnknownChallengeTypeError(ChallengeError): pass
class InvalidPolicyError(ChallengeError): pass
