#!/bin/bash

if [ ! -f thundercloud/config/congig.yml ] then
  export $SERVER_HOSTNAME
  export $SERVER_DOMAIN
  export $DBPASS
  export $DBUSER
  export $DBHOST
  ./setup.py
fi

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py runserver 0.0.0.0:8080
