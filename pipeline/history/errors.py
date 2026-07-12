class HistoryError(Exception): pass
class FingerprintError(HistoryError): pass
class SnapshotError(HistoryError): pass
