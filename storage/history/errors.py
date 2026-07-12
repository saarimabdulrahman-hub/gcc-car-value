class StorageError(Exception): pass
class ListingNotFoundError(StorageError): pass
class SnapshotConflictError(StorageError): pass
