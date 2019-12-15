DBASE
=====

How to deploy
-------------

1. Copy the source code to the deployment server. Or clone with `git clone https://github.com/gafderks/dbase.git`
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
4. Set up the apache web server by copying the file `deploy/apache.conf` to 
   `/etc/apache2/sites-available/example.com.conf` and completing the variables at the top. Preferably setup SSL with 
   e.g. LetsEncrypt.
