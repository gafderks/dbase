<img src="https://github.com/gafderks/dbase/raw/master/dbase/static/dbase/img/logo_121x110.png" alt="drawing" width="121px" style="display: block; margin-left: auto; margin-right: auto"/>

DBASE
=====
![Build Status](https://github.com/gafderks/dbase/actions/workflows/test.yml/badge.svg)
[![Codacy branch grade](https://img.shields.io/codacy/grade/a1fbb314106646d8bcb8eb52563c7725/master?logo=codacy)](https://www.codacy.com/manual/gafderks/dbase)
[![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/gafderks/dbase?logo=code%20climate)](https://codeclimate.com/github/gafderks/dbase/maintainability)
[![Test Coverage](https://img.shields.io/codeclimate/coverage/gafderks/dbase)](https://codeclimate.com/github/gafderks/dbase/test_coverage)
[![Updates](https://pyup.io/repos/github/gafderks/dbase/shield.svg)](https://pyup.io/repos/github/gafderks/dbase/)
[![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/gafderks/dbase?logo=snyk)](https://snyk.io/test/github/gafderks/dbase)
[![time tracker](https://wakatime.com/badge/github/gafderks/dbase.svg)](https://wakatime.com/badge/github/gafderks/dbase)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub License](https://img.shields.io/github/license/gafderks/dbase)](https://github.com/gafderks/dbase/blob/master/LICENSE)

__Manager for material booking.__



Installation
-------------
1. Install required packages:
   ```bash
   $ sudo apt-get update
   $ sudo apt-get install software-properties-common python3.6 python3.6-venv python3.6-dev python3-pip apache2 libapache2-mod-wsgi-py3 libmysqlclient-dev
   $ sudo apt-get install libjpeg62 libjpeg62-dev zlib1g-dev memcached
   ```
2. Copy the source code to the deployment server. Or clone with `git clone https://github.com/gafderks/dbase.git`
3. From within the project directory create a virtual environment and install the project dependencies:
   ```bash
   $ pip install pipenv
   $ pipenv install
   ```
4. Copy the file `.env.example` to `.env` and fill in the settings.
5. Activate the virtual environment with `pipenv shell`.
6. Collect static files using `(dbase) $ python manage.py collectstatic`
7. Compile the translation files using `(dbase) $ python manage.py compilemessages`
8. Load the database configuration with `(dbase) $ python manage.py migrate`
9. Create a superuser account using `(dbase) $ python manage.py createsuperuser`
10. Import materials, categories, filters, roles and groups using 
   `(dbase) $ python manage.py creategroups && python manage.py importfilters && python manage.py importmaterial`
11. Set up the apache web server by copying the file `deploy/apache.conf` to 
   `/etc/apache2/sites-available/example.com.conf` and completing the variables at the top. Preferably setup SSL with 
   e.g. LetsEncrypt.

Roadmap
-------

##### Must have
- [X] Make games orderable
- [X] Export to Excel
- [X] Button material is not listed, put in comments. Material field nullable.
    - [X] MB can convert unlisted material into material

##### Should have 
- [X] Mobile check-off list that stores the check-off status in local storage.
    - [X] Hold checkbox for indeterminate state
    - [X] Check-all / uncheck all button
- [ ] User role for 'Bestuur' that can change users but not roles.
- [ ] Mijn Dongense Jeugdraad integration
- [ ] Details for parts of days, e.g. ~location~, times.
- [ ] Improve printing
- [ ] Prune default permissions that are not checked against, also update management import roles: https://docs.djangoproject.com/en/3.0/ref/models/options/#django.db.models.Options.default_permissions

##### Could have 
- [ ] Suggested material bookings. If you book 'Rambler' it suggests electricity cords.
- [ ] Enable simultaneous editing of bookings and games
- [X] Info button next to bookings for opening material info modal.
    - [X] For MB: include shortcut for altering material (e.g. category, GM)
- [ ] Contributors file
- [X] Camera app for quickly adding photos of materials
- [ ] Import games from other events
- [ ] Admin functionality for converting a Material into a MaterialAlias

##### Won't have  


