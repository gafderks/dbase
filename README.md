<img src="https://github.com/gafderks/dbase/raw/master/booking/static/booking/logo_121x110.png" alt="drawing" width="121px" style="display: block; margin-left: auto; margin-right: auto"/>

DBASE
=====
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a1fbb314106646d8bcb8eb52563c7725)](https://www.codacy.com/manual/gafderks/dbase?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=gafderks/dbase&amp;utm_campaign=Badge_Grade)
[![time tracker](https://wakatime.com/badge/github/gafderks/dbase.svg)](https://wakatime.com/badge/github/gafderks/dbase)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/gafderks/dbase)

__Manager for material booking.__



Installation
-------------
1. Install Python 3.6:
   ```bash
   $ sudo apt-get update
   $ sudo apt-get install software-properties-common python3.6 python3.6-venv python3.6-dev python3-pip apache2 libapache2-mod-wsgi-py3 libmysqlclient-dev
   ```
2. Copy the source code to the deployment server. Or clone with `git clone https://github.com/gafderks/dbase.git`
3. From within the project directory create a virtual environment:
   ```bash
   $ python3.6 -m venv .venv
   ```
4. Load the virtual environment and install the project dependencies.
   ```bash
   $ source .venv/bin/activate
   (.venv) $ pip install --upgrade pip
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
6. Collect static files using `(.venv) $ django-admin collectstatic`
7. Load the database configuration with `(.venv) $ python manage.py migrate`
8. Create a superuser account using `(.venv) $ django-admin createsuperuser`
9. Import materials, categories, roles and groups using 
   `(.venv) $ python manage.py creategroups && python manage.py importmaterial`
10. Set up the apache web server by copying the file `deploy/apache.conf` to 
   `/etc/apache2/sites-available/example.com.conf` and completing the variables at the top. Preferably setup SSL with 
   e.g. LetsEncrypt.

Roadmap
-------
- Suggested material bookings. If you book 'Rambler' it suggests electricity cords.
