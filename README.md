DBASE
=====

How to deploy
-------------

1. Copy the source code to the deployment server.
2. Edit `/dbase/settings.py`:
    - **Update `SECRET_KEY`** to a long random string.
    - Configure a database like:
      ```python 
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.mysql',
              'NAME': 'zomerspelen_dbase',
              'USER': 'zomerspelen_dbase',
              'PASSWORD': '#',
              'HOST': 'localhost',
              'PORT': '3306'
           }
      } 
      ```
    - Set storage roots for media and static:
      ```python 
      MEDIA_ROOT = '/var/www/example.com/static/'
      STATIC_ROOT = '/var/www/example.com/media/'       
      ```
3. Collect static files using `$ django-admin collectstatic`