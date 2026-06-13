# app/core/s3_service.py
import boto3
import uuid
from botocore.exceptions import ClientError
from botocore.config import Config
from app.core.config import settings


class S3Service:
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "application/pdf", "text/plain"}
    EXT_MAP = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif", "application/pdf": ".pdf", "text/plain": ".txt"}

    def __init__(self):
        self.bucket  = settings.AWS_S3_BUCKET_NAME
        self.region  = settings.AWS_REGION
        self.client  = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
        )

    async def upload_image(self, image_bytes: bytes, mime_type: str = "image/jpeg", folder: str = "uploads") -> str | None:
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"Unsupported MIME type: {mime_type}")
        key = f"{folder}/{uuid.uuid4().hex}{self.EXT_MAP.get(mime_type, '.jpg')}"
        try:
            self.client.put_object(
                Bucket=self.bucket, Key=key, Body=image_bytes,
                ContentType=mime_type
            )
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
        except ClientError as e:
            print(f"[S3] Upload failed: {e}")
            return None


s3_service = S3Service()