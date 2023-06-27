"""
WSGI config for wall project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wall.settings')

from django.core.wsgi import get_wsgi_application

# from whitenoise.django import DjangoWhiteNoise #added this to show static files in deployment stage

application = get_wsgi_application()

# application = DjangoWhiteNoise(application) #added this to show static files in deployment stage

app= application #added this to deploy to vercel