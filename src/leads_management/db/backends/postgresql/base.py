import logging

import psycopg2
from django.db.backends.postgresql import base

logger = logging.getLogger(__name__)

import botocore
import botocore.session
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

import json

from django.conf import settings


class DatabaseCredentials:
    def __init__(self):
        logger.info("init secrets manager database credentials")
        client = botocore.session.get_session().create_client('secretsmanager')
        cache_config = SecretCacheConfig()
        self.cache_secrets_manager = SecretCache(config=cache_config, client=client)
        self.secret_id = settings.DATABASE_SECRETSMANAGER_ARN

    def get_conn_params_from_secrets_manager(self, conn_params):
        secret_json = self.cache_secrets_manager.get_secret_string(self.secret_id)
        secret_dict = json.loads(secret_json)
        username = secret_dict["username"]
        password = secret_dict["password"]
        conn_params['user'] = username
        conn_params['password'] = password

    # noinspection PyProtectedMember
    def refresh_now(self):
        secret_cache_item = self.cache_secrets_manager._get_cached_secret(self.secret_id)
        secret_cache_item._refresh_needed = True
        secret_cache_item._execute_refresh()


database_credentials = DatabaseCredentials()


class DatabaseWrapper(base.DatabaseWrapper):

    def get_new_connection(self, conn_params):
        try:
            logger.info("trying to get connection")
            database_credentials.get_conn_params_from_secrets_manager(conn_params)
            return super(DatabaseWrapper, self).get_new_connection(conn_params)
        except psycopg2.OperationalError as e:
            if f'FATAL:  password authentication failed for user "{conn_params["user"]}"' not in str(e):
                raise e
            logger.info("Authentication error. Going to refresh secret and try again.")
            database_credentials.refresh_now()
            database_credentials.get_conn_params_from_secrets_manager(conn_params)
            conn = super(DatabaseWrapper, self).get_new_connection(conn_params)
            logger.info("Successfully refreshed secret and established new database connection.")
            return conn
