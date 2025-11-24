"""
Django settings for setup project.
"""

from pathlib import Path
import os
import dj_database_url # Importante para o Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-4vq+^y91crel^ul+j8hz)wk6gb#!ib5^p$@bw843lnf5^xnc9v'

# Em produção o ideal é False, mas para testar agora pode deixar True
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", # <--- ESSENCIAL PARA O RENDER (CSS)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'setup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'setup.wsgi.application'


# --- BANCO DE DADOS (CONFIGURAÇÃO HÍBRIDA) ---
# Funciona tanto no seu PC (Local) quanto no Render (Nuvem)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'clinica',        
        'USER': 'adminclinica',   
        'PASSWORD': '05072005',     
        'HOST': 'localhost',      
        'PORT': '',               
    }
}

# Isso aqui faz o Django usar o banco do Render automaticamente quando estiver na nuvem
db_from_env = dj_database_url.config(conn_max_age=500)
if db_from_env:
    DATABASES['default'].update(db_from_env)


# Password validation

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

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# --- ARQUIVOS ESTÁTICOS (CSS, IMAGENS, JS) ---

STATIC_URL = 'static/'

# Onde o Django junta os arquivos para o Render (Resolve seu erro de Build)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Compressão para o site carregar rápido
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Configuração de Uploads (Fotos de Perfil)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.Usuario'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'


# --- CONFIGURAÇÃO DE E-MAIL ---
# Se quiser que funcione na nuvem, use o SMTP do Gmail.
# Se quiser apenas testar sem enviar, use o Console.

# Opção A: Envia de verdade (Recomendado para Produção)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu.email.aqui@gmail.com'  # <--- COLOQUE SEU EMAIL AQUI
EMAIL_HOST_PASSWORD = 'senha de app aqui'     # <--- COLOQUE AQUELA SENHA DE 16 DIGITOS

# Opção B: Só imprime no terminal (Descomente abaixo se o Gmail der erro)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'