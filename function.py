# -*- coding: utf-8 -*-

""" pgsql-auth-helper """


import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from awslambda_handler.eventparser import EventParser
from awslambda_handler.responder import Responder

def lambda_handler(event, context):
    """
    pgsql-auth-helper Lambda Handler
    """
    parser = EventParser(event)
    responder = Responder(parser)


