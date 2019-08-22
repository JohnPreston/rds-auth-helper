# -*- coding: utf-8 -*-

""" pgsql-auth-helper """

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_creds(master_secrets_arn, client):
    """
    Retrieves the RDS secrets from SecretsManager
    """
    try:
        res = client.get_secret_value(SecretId=master_secrets_arn)
        logger.info("Successfully retrieved credentials")
        logger.info(res['Name'])
        return res
    except Exception as error:
        logger.error(error)
        return None
