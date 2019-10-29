#!/bin/bash

if [ ! -f thundercloud/config/config.yml ]
then
  export SERVER_FQDN
  export DBPASS
  export DBUSER
  export DBHOST
  python setup.py
fi

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py runserver 0.0.0.0:8080
