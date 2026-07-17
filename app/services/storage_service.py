import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import Optional, Dict, BinaryIO, List
import logging
import uuid
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.endpoint = settings.STORAGE_ENDPOINT
        self.access_key = settings.STORAGE_ACCESS_KEY
        self.secret_key = settings.STORAGE_SECRET_KEY
        self.bucket = settings.STORAGE_BUCKET
        
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_key=self.secret_key,
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            )
        )
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info(f"✅ Bucket '{self.bucket}' exists on your PC")
        except ClientError:
            try:
                self.client.create_bucket(Bucket=self.bucket)
                logger.info(f"✅ Created bucket '{self.bucket}' on your PC")
            except Exception as e:
                logger.error(f"❌ Failed to create bucket: {e}")
    
    def upload_movie(self, file_data: BinaryIO, movie_id: str, category: str,
                     vj_name: str = None, genre: str = None, sub_genre: str = None,
                     filename: str = None) -> Dict:
        if category == 'ugandan':
            path = f"movies/Ugandan"
        elif category == 'english':
            path = f"movies/English"
            if sub_genre:
                path = f"{path}/{sub_genre.capitalize()}"
        elif category == 'luganda_translated':
            vj_folder = vj_name.replace(' ', '_') if vj_name else 'Unknown_VJ'
            path = f"movies/Luganda_Translated/{vj_folder}"
            if sub_genre:
                path = f"{path}/{sub_genre.capitalize()}"
        elif category == 'swahili_translated':
            vj_folder = vj_name.replace(' ', '_') if vj_name else 'Unknown_VJ'
            path = f"movies/Swahili_Translated/{vj_folder}"
            if sub_genre:
                path = f"{path}/{sub_genre.capitalize()}"
        else:
            path = f"movies/{category}"
        
        ext = filename.split('.')[-1] if filename else 'mp4'
        file_name = f"{movie_id}.{ext}"
        file_path = f"{path}/{file_name}"
        
        content_type = 'video/mp4'
        if ext.lower() in ['mkv', 'avi', 'mov']:
            content_type = f'video/{ext}'
        
        self.upload_file(file_data, file_path, content_type)
        
        url = f"{self.endpoint}/{self.bucket}/{file_path}"
        
        logger.info(f"✅ Movie saved to your PC: {file_path}")
        
        return {
            'file_path': file_path,
            'url': url,
            'filename': file_name
        }
    
    def upload_movie_poster(self, file_data: BinaryIO, movie_id: str) -> Dict:
        file_path = f"posters/{movie_id}.jpg"
        self.upload_file(file_data, file_path, 'image/jpeg')
        return {
            'poster_path': file_path,
            'poster_url': f"{self.endpoint}/{self.bucket}/{file_path}"
        }
    
    def delete_movie(self, file_path: str, poster_path: str = None):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_path)
            logger.info(f"✅ Deleted movie from your PC: {file_path}")
        except Exception as e:
            logger.error(f"❌ Error deleting movie: {e}")
        
        if poster_path:
            try:
                self.client.delete_object(Bucket=self.bucket, Key=poster_path)
                logger.info(f"✅ Deleted poster from your PC: {poster_path}")
            except Exception as e:
                logger.error(f"❌ Error deleting poster: {e}")
    
    def upload_series_episode(self, file_data: BinaryIO, series_id: str,
                              season: int, episode: int, category: str,
                              vj_name: str = None, filename: str = None) -> Dict:
        path = f"series/{series_id}"
        if season:
            path = f"{path}/Season_{season}"
        
        ext = filename.split('.')[-1] if filename else 'mp4'
        file_name = f"s{season:02d}e{episode:02d}.{ext}"
        file_path = f"{path}/{file_name}"
        
        content_type = 'video/mp4'
        if ext.lower() in ['mkv', 'avi']:
            content_type = f'video/{ext}'
        
        self.upload_file(file_data, file_path, content_type)
        
        return {
            'file_path': file_path,
            'url': f"{self.endpoint}/{self.bucket}/{file_path}"
        }
    
    def upload_music(self, file_data: BinaryIO, music_id: str, category: str,
                     musician_name: str = None, genre: str = None,
                     filename: str = None) -> Dict:
        if category == 'ugandan':
            path = f"music/Ugandan"
        elif category == 'international':
            path = f"music/International"
        else:
            path = f"music/{category}"
        
        if musician_name:
            musician_folder = musician_name.replace(' ', '_')
            path = f"{path}/{musician_folder}"
        
        if genre:
            path = f"{path}/{genre}"
        
        ext = filename.split('.')[-1] if filename else 'mp3'
        file_name = f"{music_id}.{ext}"
        file_path = f"{path}/{file_name}"
        
        content_type = 'audio/mpeg'
        if ext.lower() in ['wav', 'flac', 'aac']:
            content_type = f'audio/{ext}'
        
        self.upload_file(file_data, file_path, content_type)
        
        return {
            'file_path': file_path,
            'url': f"{self.endpoint}/{self.bucket}/{file_path}"
        }
    
    def upload_music_cover(self, file_data: BinaryIO, music_id: str) -> Dict:
        file_path = f"covers/{music_id}.jpg"
        self.upload_file(file_data, file_path, 'image/jpeg')
        return {
            'cover_path': file_path,
            'cover_url': f"{self.endpoint}/{self.bucket}/{file_path}"
        }
    
    def upload_file(self, file_data: BinaryIO, file_path: str, content_type: str = None) -> str:
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_fileobj(file_data, self.bucket, file_path, ExtraArgs=extra_args)
            logger.info(f"✅ File saved to your PC: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Error uploading file to your PC: {e}")
            raise
    
    def file_exists(self, file_path: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError:
            return False
    
    def delete_file(self, file_path: str):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_path)
            logger.info(f"✅ Deleted from your PC: {file_path}")
        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}")
    
    def generate_streaming_url(self, file_path: str, expires_in: int = 3600) -> str:
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': file_path},
                ExpiresIn=expires_in
            )
        except Exception as e:
            logger.error(f"❌ Error generating streaming URL: {e}")
            return None