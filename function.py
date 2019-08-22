# -*- coding: utf-8 -*-

""" pgsql-auth-helper """

import logging
import boto3
import json
import requests

from psql import (
    create_role,
    create_schema
)

from secrets import get_creds

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_response(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']
    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData
    json_responseBody = json.dumps(responseBody)
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))


def lambda_handler(event, context):
    """
    pgsql-auth-helper Lambda Handler
    """
    resources = event['ResourceProperties']

    master_password_arn = resources['MasterPasswordArn']
    app_password_arn = resources['AppPasswordArn']
    schema_name = resources['SchemaName']

    secrets_client = boto3.client('secretsmanager')
    master_creds = json.loads(get_creds(master_password_arn, secrets_client)['SecretString'])
    app_creds = json.loads(get_creds(app_password_arn, secrets_client)['SecretString'])

    logging.info(f"DB Host : {master_creds['host']}")
    logging.info(f"DB Engine {master_creds['engine']}")

    username = create_role(
        host=master_creds['host'],
        dbname=master_creds['engine'],
        musername=master_creds['username'],
        mpassword=master_creds['password'],
        uusername=app_creds['username'],
        upassword=app_creds['password'],
        port=master_creds['port']
    )
    logging.info(f'Create role done - {username} - moving to the schema')
    if username:
        result = create_schema(
            host=master_creds['host'],
            dbname=master_creds['engine'],
            musername=master_creds['username'],
            mpassword=master_creds['password'],
            uusername=app_creds['username'],
            schema_name=schema_name,
            port=master_creds['port']
        )
        if result:
            logging.info('Username and schema created successfully')
            return send_response(event, context, 'SUCCESS', {})
        else:
            logging.info('Username and schema creation failed')
    else:
        logging.info('User/Role creation failed')
    return send_response(event, context, 'FAILED', {})
