"""
Django settings for dbase project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    DEBUG_TOOLBAR=(bool, False),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
    DATA_UPLOAD_MAX_MEMORY_SIZE=(int, 10485760),  # For uploading HD images
    MEMCACHE_LOCATIONS=(list, ["127.0.0.1:11211"]),
    ADMINS=(list, []),
)
environ.Env.read_env(env_file=str(BASE_DIR / ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
DEBUG_TOOLBAR = env("DEBUG_TOOLBAR")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "django_gulp",
    "booking.apps.BookingConfig",
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "djmoney",
    "camera.apps.CameraConfig",
    "adminsortable",
    "django.contrib.humanize",
    "sorl.thumbnail",
    "ckeditor",
    "django_filters",
    "rules.apps.AutodiscoverRulesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    INSTALLED_APPS += ["django_extensions"]
    if DEBUG_TOOLBAR:
        INSTALLED_APPS += ["debug_toolbar"]
        MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware", *MIDDLEWARE]

ROOT_URLCONF = "dbase.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "dbase/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dbase.wsgi.application"


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {"default": env.db()}


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

AUTHENTICATION_BACKENDS = (
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
)


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = "nl"

TIME_ZONE = "Europe/Amsterdam"

USE_I18N = True

USE_L10N = True

USE_TZ = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": env("MEMCACHE_LOCATIONS"),
    }
}
if DEBUG:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache",}}

ADMINS = [tuple(x.split(":")) for x in env("ADMINS")]
EMAIL_CONFIG = env.email_url("EMAIL_URL", default="smtp://user@:password@localhost:25")
vars().update(EMAIL_CONFIG)
SERVER_EMAIL = env("SERVER_EMAIL", default="system@{}".format(ALLOWED_HOSTS[0]))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_DIRS = (BASE_DIR / "build", BASE_DIR / "dbase" / "static")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# Keep GIF and PNG images that are uploaded as the same format when thumbnailed
THUMBNAIL_PRESERVE_FORMAT = True

CRISPY_TEMPLATE_PACK = "bootstrap4"

LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = "index"
LOGIN_URL = "users:login"

AUTH_USER_MODEL = "users.User"

LOCALE_PATHS = [BASE_DIR / "dbase" / "locale"]

DATA_UPLOAD_MAX_MEMORY_SIZE = env("DATA_UPLOAD_MAX_MEMORY_SIZE")

CKEDITOR_BASEPATH = STATIC_URL + "ckeditor/ckeditor/"
CKEDITOR_CONFIGS = {
    "basic_ckeditor": {
        "toolbar": "basic_ckeditor",
        "toolbar_basic_ckeditor": [
            ["Bold", "Italic", "Underline", "-", "RemoveFormat",],
            ["NumberedList", "BulletedList", "-", "Image", "Youtube", "HorizontalRule"],
            ["Link", "Unlink"],
            ["Undo", "Redo"],
            ["Source"],
        ],
        "extraPlugins": ["youtube"],
        "removePlugins": ["iframe"],
        "allowedContent": True,
    }
}

INTERNAL_IPS = ["127.0.0.1", "localhost"]
