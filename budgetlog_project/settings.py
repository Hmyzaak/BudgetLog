"""
Django settings for budgetlog_project project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6&x0thl9l4y!o3_9&l+0o4gr*rfjo#o_yevqu7gf(+#od@jt(0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'budgetlog',
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django_filters',
]

CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'budgetlog_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'budgetlog_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'cs'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# URL prefix pro statické soubory
STATIC_URL = 'static/'
"""
# Cesty, kde Django bude hledat další statické soubory
STATICFILES_DIRS = [
    BASE_DIR / "budgetlog" / "static",
]

# Adresář pro shromážděné statické soubory (při použití collectstatic)
STATIC_ROOT = BASE_DIR / "staticfiles"
"""
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 2

AUTH_USER_MODEL = "budgetlog.AppUser"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Pro testování lze použít místo "smtp" klíč "console", což použije pro generování emailu s odkazem konzoli
"""Simple Mail Transfer Protocol: backend je v tomto případě nastaven na smtp.EmailBackend, což znamená, 
že Django bude odesílat emaily přes externí SMTP server (např. Gmail SMTP)."""
DEFAULT_FROM_EMAIL = 'noreply@budgetlog.cz'
"""DEFAULT_FROM_EMAIL určuje výchozí adresu odesílatele, která se objeví ve všech emailech odesílaných aplikací, 
pokud výslovně není určeno jinak. To znamená, že když bude aplikace odesílat emaily (např. potvrzení registrace 
nebo reset hesla), uživatelé uvidí tuto adresu jako odesílatele."""

EMAIL_HOST = 'smtp.gmail.com'
"""EMAIL_HOST definuje adresu SMTP serveru, který bude použit pro odesílání emailů. Tento SMTP server musí být 
poskytovatelem emailových služeb nebo serverem, který má schopnost odesílat emaily."""
EMAIL_PORT = 587
"""Port 587 je standardní port pro SMTP s podporou TLS (šifrovaná komunikace). Některé SMTP servery používají jiný 
port, záleží na poskytovateli: Gmail a většina poskytovatelů používá port 587 pro SMTP s TLS."""
EMAIL_USE_TLS = True
"""Tato volba určuje, zda má být používáno TLS (Transport Layer Security) pro šifrování komunikace mezi vaší aplikací 
a SMTP serverem."""

EMAIL_HOST_USER = 'budgetlognoreply@gmail.com'
"""EMAIL_HOST_USER je uživatelské jméno (většinou emailová adresa), které se používá k přihlášení k SMTP serveru. 
Toto je emailová adresa, z níž se budou odesílat emaily."""
EMAIL_HOST_PASSWORD = 'nndvhfglfgdmogyl'  # Zde vložte 16místné heslo aplikace
"""Hesla aplikací umožňují přihlásit se k účtu Google ve starších aplikacích a službách, které nepodporují moderní 
bezpečnostní standardy."""