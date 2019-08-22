# -*- coding: utf-8 -*-

""" pgsql-auth-helper """

import sys
import logging
import pg8000
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def create_role(host, dbname, musername, mpassword, uusername, upassword, port=5432):
    """
    Creates a new PSQL role for the app to access the schema
    A. Connects to PGSQL
    B. Creates a new role
    """
    conn = pg8000.connect(host=host, database=dbname, port=port, user=musername, password=mpassword)
    conn.autocommit = True

    check_role_cmd = (f"SELECT rolname FROM pg_roles WHERE rolname='{uusername}'")
    create_user_cmd = (f"CREATE ROLE {uusername} WITH LOGIN PASSWORD '{upassword}'")
    cursor = conn.cursor()
    try:
        cursor.execute(check_role_cmd)
        exists = cursor.fetchone()
        if exists:
            logger.info(f"{exists[0]} already exists - skipping")
            cursor.close()
            return uusername
    except Exception as error:
        cursor.close()
        logger.info(error)

    cursor = conn.cursor()
    try:
        cursor.execute(create_user_cmd)
        cursor.close()
        return uusername
    except Exception as error:
        cursor.close()
        return None


def create_schema(host, dbname, musername, mpassword, uusername, schema_name, port=5432):
    """
    Creates a new PGSQL schema and grants access to the role to it as the owner
    A. Connects to PGSQL
    B. Creates if does not exist a new schema
    """
    conn = pg8000.connect(host=host, database=dbname, user=musername, password=mpassword, port=port)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.close()
    create_schema_cmd = (f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
    grant_all_to_schema_cmd = (f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema_name} TO {uusername}")
    cursor = conn.cursor()
    try:
        cursor.execute(create_schema_cmd)
        cursor.close()
        return True
    except Exception as error:
        try:
            cursor.execute(grant_all_to_schema_cmd)
            cursor.close()
            return True
        except Exception as error:
            logger.info(error)
            return False
        return False
