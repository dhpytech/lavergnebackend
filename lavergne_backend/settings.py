import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# 1. Load môi trường ngay lập tức
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Quản lý Apps
APPS_DIR = os.path.join(BASE_DIR, 'apps')
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)

# 3. Bảo mật
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-secret-key')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 't')
ALLOWED_HOSTS = ['*']

# 4. Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # My Apps
    'accounts', 'entries', 'safety', 'dashboards', 'itemcode',
    'stoptime', 'problems', 'dlnc_case', 'mail', 'employee',
    'shared', 'utils',

    # Third Party
    'django_filters',
    'rest_framework',
    'corsheaders',
]

# 5. MIDDLEWARE (QUAN TRỌNG: Thứ tự này mới fix được lỗi CORS trong ảnh của bạn)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lavergne_backend.urls' # Đã bỏ dấu ngoặc đơn dư thừa

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'lavergne_backend.wsgi.application'

# 6. DATABASE (Tự động nhận Public URL từ Railway cho máy local)
db_url = os.getenv('DATABASE_PUBLIC_URL') or os.getenv('DATABASE_URL')

if db_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=db_url,
            conn_max_age=600,
            ssl_require=not DEBUG
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 7. CORS & CSRF (Fix triệt để lỗi đỏ trong Console)
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "https://lavergnefrontend-production.up.railway.app",
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://lavergnefrontend-production.up.railway.app",
    "https://gunicorn-lavergnebackendwsgi-production.up.railway.app",
    "https://lavergnefrontend-production.up.railway.app",
]

# 8. Quốc tế hóa
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# 9. Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if os.path.exists(BASE_DIR / 'static') else []

# 10. REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
