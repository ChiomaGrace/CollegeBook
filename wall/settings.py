"""
Django settings for wall project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from pathlib import Path
import os
import cloudinary #to save uploaded images in heroku/deployment stage
import cloudinary_storage #to save uploaded images in heroku/deployment stage
from decouple import config #to hide/retrieve my cloud config that are below in the settings.py
# import dj_database_url #for deployment
# import environ
import mimetypes


# env = environ.Env()

# environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent #Use this for local



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

#The below code shows the error messages in deployment/heroku
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
#         },
#     },
# }
#The above code shows the error messages in deployment/heroku

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '29st2j=m_g=qpxaerv#q9j%9*e7!vo4!u79(f$6q@-6jg7a1+h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True #for locally
# DEBUG = False #for deployment

ALLOWED_HOSTS = [
    # '.vercel.app', 
    # '.now.sh',
    '*',
    # 'collegebook.railway.app'
    # 'collegebookbychi.herokuapp.com'
    '0.0.0.0',
    'localhost',
]


# Application definition

INSTALLED_APPS = [
    'wallApp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",  # added so media files save/stay in deployment
    'django.contrib.staticfiles',
    'cloudinary', #added so media files save/stay in deployment
    'cloudinary_storage', #added so media files save/stay in deployment
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', #added this line in order to serve static files in deployment
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # I added this line. This provides the ability to reference the MEDIA_URL variable in template directories.
            ],
        },
    },
]

WSGI_APPLICATION = 'wall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#

#The below code is the database used for deployment (Render PostgreSQL)
# DATABASES = {
#     'default': dj_database_url.parse(env('DATABASE_URL'))
# }
#The above code is the database used for deployment (Render PostgreSQL)

#The below code is the database used for deployment (Vexel/Railway)
# DATABASES = {'default': dj_database_url.config(default='postgresql://postgres:A7SX8Twku67VOwimSgEq@containers-us-west-144.railway.app:5792/railway')}
# DATABASE_URL = "postgresql://postgres:V6FtoLQxnDkiGkjqwkAU@containers-us-west-59.railway.app:6071/railway"
# DATABASES['default'] = dj_database_url.config()
# DATABASES = {
#     'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=1800)
# }
#The above code is the database used for deployment (Vexel Railway)


#The below code is the database used for local environment
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
#The above code is the database used for local environment


# The below code is configuring the database for railway deployment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ["PGDATABASE"],
        'USER': os.environ["PGUSER"],
        'PASSWORD': os.environ["PGPASSWORD"],
        'HOST': os.environ["PGHOST"],
        'PORT': os.environ["PGPORT"],
    }
}
# The above code is configuring the database for railway deployment

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'

TIME_ZONE = 'America/Los_Angeles'

USE_TZ = True

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

#The below code is added so media files save/stay in deployment
CLOUDINARY_STORAGE ={
            'CLOUD_NAME': 'chioma-grace-apps',
            'API_KEY': '855871784712111',
            'API_SECRET': '1jwGl_GQdfBEI4zHt7LKexi2BR8'
}
# cloudinary.config( 
#   	cloud_name = "chioma-grace-apps",
#   	api_key = "855871784712111",
#   	api_secret = "1jwGl_GQdfBEI4zHt7LKexi2BR8"
# )
DEFAULT_FILE_STORAGE='cloudinary_storage.storage.MediaCloudinaryStorage'
# STATICFILES_STORAGE = 'cloudinary_storage_storage.StaticHashedCloudinaryStorage' #This enables the media files to be saved/stored
#The above code is added so media files save/stay in deployment

STATIC_URL = '/static/' #This url is how a client or browser can access static files. Example: https://www.example.com/staticFiles/nameOfImg.jpg.

# STATIC_ROOT = BASE_DIR / "staticfiles_build" / "static" #added this in order for static files to deploy on vercel. this generates where static files are placed after running the manage.py collectstatic command
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') #added this in order for static files to deploy on vercel. this generates where static files are placed after running the manage.py collectstatic command
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') #added this in order for static files to deploy on heroku. this generates where static files are placed after running the manage.py collectstatic command
# MEDIA_URLS ='/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "wallApp/static"), #baseDir references the "home" so for me starting at collegebook
    # os.path.join(BASE_DIR, "wallApp/static/CSS"), #baseDir references the "home" so for me starting at collegebook
    os.path.join(BASE_DIR, "wallApp/static/Images"),
    # os.path.join(BASE_DIR, "wallApp/static/JavaScript"),
)

# STATICFILES_DIRS = os.path.join(BASE_DIR, 'static'),
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# #I added the below lines of code for deployment #
MEDIA_ROOT= os.path.join(BASE_DIR, 'media/') # contains the absolute path to the file system where media files will be uploaded to store the images on the computer.
# MEDIA_ROOT= os.path.join(BASE_DIR, '/media/') # contains the absolute path to the file system where media files will be uploaded to store the images on the computer.
MEDIA_URL= "/media/"  #is the reference URL for browser to access the files over Http.

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'#This enables the app to now serve static assets directly from Gunicorn in production

# The below code solves the collectstatic multiple paths error
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',    #causes verbose duplicate notifications in django 1.9
)
# The above code solves the collectstatic multiple paths error

mimetypes.add_type("text/css", ".css")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
