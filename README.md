DBASE
=====

How to deploy
-------------
1. Install Python 3.8:
   ```bash
   $ sudo apt-get update
   $ sudo apt-get install software-properties-common python3.8 python3.8-venv python3.8-dev python3-pip apache2 libapache2-mod-wsgi-py3 libmysqlclient-dev
   ```
2. Copy the source code to the deployment server. Or clone with `git clone https://github.com/gafderks/dbase.git`
3. From within the project directory create a virtual environment:
   ```bash
   $ python3.8 -m venv .venv
   ```
4. Load the virtual environment and install the project dependencies.
   ```bash
   $ source .venv/bin/activate
   (.venv) $ pip install setuptools wheel
   (.venv) $ pip install -r requirements.txt 
   ```
5. Edit `/dbase/settings.py`:
    - Add the domain at which the application is served to `ALLOWED_HOSTS`.
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
6. Collect static files using `$ django-admin collectstatic`
7. Load the database configuration with `$ python manage.py migrate`
8. Create a superuser account using `$ django-admin createsuperuser`
9. Set up the apache web server by copying the file `deploy/apache.conf` to 
   `/etc/apache2/sites-available/example.com.conf` and completing the variables at the top. Preferably setup SSL with 
   e.g. LetsEncrypt.
