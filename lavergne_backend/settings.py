import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# Đường dẫn gốc
BASE_DIR = Path(__file__).resolve().parent.parent
# Chuyển tất cả app vào thư mục apps
# sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
APPS_DIR = os.path.join(BASE_DIR, 'apps')
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)
# Bảo mật
SECRET_KEY = 'your-secret-key'
ALLOWED_HOSTS = ['*']

# Ứng dụng
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Thêm các app của bạn ở đây
    'accounts',
    'entries',
    'safety',
    'dashboards',
    'itemcode',
    'stoptime',
    'problems',
    'dlnc_case',
    'mail',
    'employee',
    'shared',

    # Third Party
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = ('lavergne_backend.urls')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Nếu bạn dùng template
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

# DATABASE
# DEBUG = True cho local, False cho server
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DB_NAME', 'railway'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'ETaUowiMGcnEYuGyvPTZzTsCyINlDxYM'),
            'HOST': os.getenv('DB_HOST', 'maglev.proxy.rlwy.net'),
            'PORT': os.getenv('DB_PORT', '45153'),
        }
    }

if DEBUG:
    load_dotenv()
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:8000')
else:
    load_dotenv()
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://gunicorn-lavergnebackendwsgi-production.up.railway.app')

# Quốc tế hóa
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# STATIC
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MEDIA (nếu dùng upload ảnh)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://lavergnefrontend-production.up.railway.app",
]
CORS_ALLOW_CREDENTIALS = True


# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://gunicorn-lavergnebackendwsgi-production.up.railway.app",
]

CORS_ALLOW_ALL_ORIGINS = True

