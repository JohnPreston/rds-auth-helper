# -*- coding: utf-8 -*-

""" pgsql-auth-helper """

import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from function import logger

if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def create_schema(host, dbname, musername, mpassword, uusername, schema_name, port=5432):
    """
    Creates a new PGSQL schema and grants access to the role to it as the owner
    A. Connects to PGSQL
    B. Creates if does not exist a new schema
    """
    conn_string = f"dbname='{dbname}' user='{musername}' host='{host}' port='{port}'"
    logger.info(conn_string)
    conn_string += f" password='{mpassword}'"
    conn = psycopg2.connect(conn_string)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    create_schema_cmd = (f"CREATE SCHEMA IF NOT EXISTS {schema_name} AUTHORIZATION {uusername};")
    grant_all_to_schema_cmd = (f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema_name} TO {uusername}")
    try:
        cursor.execute(create_schema_cmd)
        return True
    except Exception as error:
        try:
            cursor.execute(grant_all_to_schema_cmd)
            return True
        except Exception as error:
            logger.info(error)
            return False
        return False


def create_role(host, dbname, musername, mpassword, uusername, upassword, port=5432):
    """
    Creates a new PSQL role for the app to access the schema
    A. Connects to PGSQL
    B. Creates a new role
    """
    conn_string = f"dbname='{dbname}' user='{musername}' host='{host}' port='{port}'"
    logger.info(conn_string)
    conn_string += f" password='{mpassword}'"
    conn = psycopg2.connect(conn_string)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    check_role_cmd = (f"SELECT rolname FROM pg_roles WHERE rolname='{uusername}'")
    create_user_cmd = (f"CREATE ROLE {uusername} WITH LOGIN PASSWORD '{upassword}'")
    try:
        cursor.execute(check_role_cmd)
        exists = cursor.fetchone()
        if exists:
            logger.info(f"{exists[0]} already exists - skipping")
            return uusername
    except Exception as error:
        logger.info(error)

    try:
        cursor.execute(create_user_cmd)
        return uusername
    except Exception as error:
        return None


if __name__ == '__main__':
    host='localhost'
    dbname='newdb3'
    musername='postgres'
    mpassword='abcd'
    uusername='newuser4'
    upassword='newpassword3'
    schema_name='newschema2'

    username=create_role(
        host,
        dbname,
        musername,
        mpassword,
        uusername,
        upassword,
        port='32769'
    )
    if username:
        result = create_schema(
            host,
            dbname,
            musername,
            mpassword,
            uusername,
            schema_name,
            port='32769'
        )

        if result:
            logging.info('Username and schema created successfully')
        else:
            logging.info('Username and schema creation failed')

    else:
        logging.info('User/Role creation failed')

