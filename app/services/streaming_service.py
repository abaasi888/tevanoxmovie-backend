import os
import boto3
from botocore.client import Config
from typing import Optional, Dict
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class HomeServerStreamingService:
    def __init__(self):
        self.host = settings.STORAGE_URL
        self.minio_client = boto3.client(
            's3',
            endpoint_url=settings.STORAGE_ENDPOINT,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        self.bucket = settings.STORAGE_BUCKET
    
    def get_streaming_url(self, video_path: str) -> Dict:
        if not video_path:
            return {'hls': None, 'dash': None, 'download': None}
        
        base_name = video_path.replace('\\', '/')
        if '.' in base_name:
            base_name = base_name.rsplit('.', 1)[0]
        file_name = os.path.basename(base_name)
        
        return {
            'hls': f"{self.host}/hls_vod/{file_name}.m3u8",
            'dash': f"{self.host}/dash_vod/{file_name}.mpd",
            'download': f"{self.host}/movies/{file_name}.mp4"
        }
    
    def generate_presigned_download_url(self, object_key: str, expires_in: int = 3600) -> Optional[str]:
        if not object_key:
            return None
        try:
            return self.minio_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_key},
                ExpiresIn=expires_in
            )
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None