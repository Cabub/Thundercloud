import os
import yaml
from base64 import b64encode
from random import choices

# use environment variables to generate default config file
config = {
    'SECRET_KEY': ''.join(choices(b64encode(os.urandom(64)).decode(), k=64)),
    'ALLOWED_HOSTS': [os.environ['SERVER_FQDN']],
    'DEBUG_MODE': os.environ.get('DEBUG_MODE', 'false') == 'true',
    'DATABASE_HOSTNAME': os.environ['DBHOST'],
    'DATABASE_USER': os.environ['DBUSER'],
    'DATABASE_PASSWORD': os.environ['DBPASS']
}

with open('thundercloud/server/config/config.yml', 'w') as fs:
    print(yaml.dump(config), end='', file=fs)
