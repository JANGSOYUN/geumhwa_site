"""
Django settings for geumhwa_site project.
Django 5.2.x 기준
"""
from pathlib import Path
import os

# ───────────────────────────────
# 기본 경로
# ───────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ───────────────────────────────
# 보안 / 환경 변수
# ───────────────────────────────
# 1️⃣ Django 기본 SECRET_KEY
SECRET_KEY = 'django-insecure-ay@p_&9hnq6npqf+*(a%-49axv%c%k9teov2^+#af%h6r^1bs@'

# 2️⃣ 환경 변수로 덮어쓰기 (운영 환경 전환 시)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", SECRET_KEY)

# 3️⃣ DEBUG / ALLOWED_HOSTS
DEBUG = True
#ALLOWED_HOSTS = ["13.209.48.247", "localhost", "127.0.0.1",]
ALLOWED_HOSTS = ['www.geumhwabox.com', 'geumhwabox.com', '13.209.48.247', 'localhost', '127.0.0.1', 'testserver']

# (선택) HTTPS 환경일 때 CSRF 신뢰 도메인 추가
CSRF_TRUSTED_ORIGINS = [
    f"https://{h.strip()}" for h in ALLOWED_HOSTS if "." in h
]
if not DEBUG:
    # HTTPS 도메인 붙였을 때만 추가
    # CSRF_TRUSTED_ORIGINS = ["https://geumhwa.co.kr", "https://www.geumhwa.co.kr"]
    pass

# ───────────────────────────────
# 앱 등록
# ───────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'storages',  # django-storages (S3 연동)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 정적 파일 서빙
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Cross-Origin-Opener-Policy 설정 (개발 환경용)
if DEBUG:
    SECURE_CROSS_ORIGIN_OPENER_POLICY = None  # 개발 환경에서는 비활성화
else:
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

ROOT_URLCONF = 'geumhwa_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # (필요 시 템플릿 폴더 추가)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'geumhwa_site.wsgi.application'

# ───────────────────────────────
# 데이터베이스
# ───────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ───────────────────────────────
# 비밀번호 검증
# ───────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ───────────────────────────────
# 국제화
# ───────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# ───────────────────────────────
# 정적 / 미디어 (S3 연동)
# ───────────────────────────────
# USE_S3 = os.getenv("USE_S3") == "1"
USE_S3 = False

if USE_S3:
    # 공통 설정
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "ap-northeast-2")
    AWS_STORAGE_BUCKET_NAME_STATIC = os.getenv("AWS_STORAGE_BUCKET_NAME_STATIC", "geumhwa-static-prod")
    AWS_STORAGE_BUCKET_NAME_MEDIA = os.getenv("AWS_STORAGE_BUCKET_NAME_MEDIA", "geumhwa-media-prod")

    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_ADDRESSING_STYLE = "virtual"
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False

    # Django 5.x STORAGES API
    STORAGES = {
        "default": {  # MEDIA (사용자 업로드)
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "bucket_name": AWS_STORAGE_BUCKET_NAME_MEDIA,
                "location": "media",
            },
        },
        "staticfiles": {  # STATIC (정적파일)
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "bucket_name": AWS_STORAGE_BUCKET_NAME_STATIC,
                "location": "static",
            },
        },
    }

    STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME_STATIC}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"
    # MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME_MEDIA}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/"

else:
    # 로컬 Whitenoise
    STATIC_URL = '/static/'
    #STATIC_URL = 'https://d26f6vvt8itdt8.cloudfront.net/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [BASE_DIR / 'static']
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ───────────────────────────────
# 기본 PK 필드
# ───────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ───────────────────────────────
# 운영 시 HTTPS 보안 옵션
# ───────────────────────────────
# if not DEBUG:
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # 지금은 HTTP라서 False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ───────────────────────────────
# 파일 업로드 크기 제한 (413 에러 방지)
# ───────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ───────────────────────────────
# 이메일 설정
# ───────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "geumhwa9300@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "yebt fsje resn bkma")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ───────────────────────────────
# 로깅
# ───────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.core.mail": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}