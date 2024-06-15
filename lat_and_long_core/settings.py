from typing import Optional
import os,dj_database_url,datetime,ast,warnings,django_cache_url
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from datetime import timedelta
from django.core.validators import URLValidator
from pytimeparse import parse
from typing import List, Optional

from typing import Optional



def get_list(text):
    return [item.strip() for item in text.split(",")]

def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value

def get_url_from_env(name, *, schemes=None) -> Optional[str]:
    if name in os.environ:
        value = os.environ[name]
        message = f"{value} is an invalid value for {name}"
        URLValidator(schemes=schemes, message=message)(value)
        return value
    return None

# load_dotenv()
load_dotenv(find_dotenv(), override=True, verbose=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR: str = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = get_bool_from_env("DEBUG", False)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY and DEBUG:
    warnings.warn("SECRET_KEY not configured, using a random temporary key.")
    SECRET_KEY = get_random_secret_key()

def get_list(value: Optional[str]) -> list[str]:
    if value is None:
        return []
    return [v.strip() for v in value.split(',') if v.strip()]

# Assuming get_list is a function that converts a comma-separated string to a list
def get_list(value: Optional[str]) -> List[str]:
    if value:
        return value.split(',')
    return []



ALLOWED_HOSTS = [
    '127.0.0.1',
    '*',
]
# settings.py


CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1",
]


CORS_ALLOW_ALL_ORIGINS = True  

# Set CORS_ALLOW_CREDENTIALS based on your requirements
CORS_ALLOW_CREDENTIALS = True







# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'apps.user',
    'apps.authentication',
    'apps.lat_long',

]

THIRD_PARTY_APPS = [
    'drf_yasg',
    'debug_toolbar',
    'django_extensions',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    "corsheaders",
    'django_acl',
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS  + THIRD_PARTY_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'lat_and_long_core.urls'


context_processors = [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
]



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': context_processors,
        },
    },
]

WSGI_APPLICATION = 'lat_and_long_core.wsgi.application'


# Database

DB_CONN_MAX_AGE = int(os.environ.get("DB_CONN_MAX_AGE", 600))

# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": dj_database_url.config(
        default=f"postgres://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PASSWORD')}@{os.environ.get('DATABASE_HOST')}:{os.environ.get('DATABASE_PORT')}/{os.environ.get('DATABASE_NAME')}", 
        conn_max_age=600,
        conn_health_checks=True,
    ),
    "replica": dj_database_url.config(
        default=f"postgres://{os.environ.get('DATABASE_USER')}:{os.environ.get('DATABASE_PASSWORD')}@{os.environ.get('DATABASE_READER_HOST')}:{os.environ.get('DATABASE_PORT')}/{os.environ.get('DATABASE_NAME')}", 
        conn_max_age=600,
        conn_health_checks=True,
    )
}





# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "user.Users"


SWAGGER_SETTINGS = {
    'DEFAULT_API_URL' : os.environ.get('SWAGGER_DEFAULT_API_URL', ""),
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'lat_and_long_core.exceptions.exceptions.handle_exception',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 2,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'lat_and_long_core.utils.auth_handler.UserCustomAuthenticator'
]


ATOMIC_REQUESTS=True




SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=20),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=50),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'eShVmYq3t6w9z$C&E)H@McQfTjWnZr4u7x!A%D*G-JaNdRgUkXp2s5v8y/B?E(H+',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': datetime.timedelta(days=20),
    'SLIDING_TOKEN_REFRESH_LIFETIME': datetime.timedelta(days=50),
}



REST_PAGINATED_PAGE_SIZE        = os.environ.get('REST_PAGINATED_PAGE_SIZE','')

DATA_UPLOAD_MAX_MEMORY_SIZE     = 524288000000
DATA_UPLOAD_MAX_NUMBER_FIELDS   = 10000






#Additional
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
        
    },
    'loggers': {
        'django': {
            'handlers': ['console','file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console','file'],
            'propagate': False,
        },
        
    }
}









STATIC_URL = 'staticfiles/'
STATIC_ROOT  = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'),
)


MEDIA_URL = "/media/"
MEDIA_ROOT =  os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')



def get_host():
    from django.contrib.sites.models import Site

    return Site.objects.get_current().domain


def default_image():
    return f"default/default-image/default-image-for-no-image.png" 


EFAULT_IMAGE = default_image



EMAIL_BACKEND         = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST            = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER       = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD   = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_DOMAIN          = os.environ.get('EMAIL_DOMAIN')
EMAIL_PORT            = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS         = get_bool_from_env("EMAIL_USE_TLS", False)
DEFAULT_FROM_EMAIL    = os.environ.get('DEFAULT_FROM_EMAIL')





if 'EMAIL_SENDER_NAME' in os.environ:
    EMAIL_SENDER_NAME = os.environ.get('EMAIL_SENDER_NAME')
else:
    EMAIL_SENDER_NAME = 'System'




APPEND_SLASH = False

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CACHE_URL = os.environ.setdefault("CACHE_URL", REDIS_URL)
CACHES = {"default": django_cache_url.config()}
CACHES["default"]["TIMEOUT"] = parse(os.environ.get("CACHE_TIMEOUT", "7 days"))
