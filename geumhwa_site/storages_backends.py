from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

# 정적 파일용 스토리지
class StaticStorage(S3Boto3Storage):
    location = "static"  # S3 내 경로 prefix
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME_STATIC
    default_acl = None  # 공개 범위는 버킷 정책 또는 CloudFront로 제어

# 미디어 파일용 스토리지
class MediaStorage(S3Boto3Storage):
    location = "media"
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME_MEDIA
    default_acl = None  # 비공개
    file_overwrite = False  # 같은 파일 이름이면 덮어쓰기 금지