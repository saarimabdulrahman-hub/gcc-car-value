import boto3
from src.config import get_settings

settings = get_settings()


class RawStorage:
    """Stores raw HTML and parser output. S3 in production, local dev via endpoint override."""

    def __init__(self):
        if settings.environment == "development" and settings.s3_endpoint_url:
            self.s3 = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint_url,
                aws_access_key_id=settings.s3_access_key or "test",
                aws_secret_access_key=settings.s3_secret_key or "test",
                region_name=settings.s3_region,
            )
        else:
            self.s3 = boto3.client("s3", region_name=settings.s3_region)
        self.bucket = settings.s3_bucket

    def upload_text(self, key: str, text: str) -> str:
        """Store text content (HTML, JSON) at the given S3 key. Returns s3:// URI."""
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=text.encode("utf-8"),
            ContentType="text/html",
        )
        return f"s3://{self.bucket}/{key}"
