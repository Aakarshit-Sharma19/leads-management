import json

import boto3
from logging import getLogger
from os import getenv

logger = getLogger('secrets')

client = boto3.client('secretsmanager')

#  Get db creds
logger.info('Attempting to get secret')
_db_secret_string = client.get_secret_value(
    SecretId=getenv('DB_SECRET_ARN')
)

DB_CREDENTIALS: dict = json.loads(_db_secret_string['SecretString'])
