# -*- coding: utf-8 -*-

""" rds_engine_settings """

import os
import sys
import json
import boto3
import requests
import logging

def setup_logging():
    logger = logging.getLogger()
    for h in logger.handlers:
        logger.removeHandler(h)

    formatter = logging.Formatter("[%(levelname)s] %(asctime)s, %(funcName)s, %(message)s", "%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.addHandler(handler)

    try:
        LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
        logger.basicConfig(level=LOGLEVEL)
    except:
        logger.setLevel(logging.INFO)
    return logger


LOG = setup_logging()

SUCCESS = "SUCCESS"
FAILED = "FAILED"

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
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
        LOG.info(f"Successfully replied to CFN with status {responseStatus}: {response.reason}")
    except Exception as e:
        LOG.error("send(..) failed executing requests.put(..): " + str(e))


def get_db_engine_settings(db_engine_name, db_engine_version, serverless=False):
    """
    Function to return just the details about that DB Engine Version
    """
    LOG.info(f'Looking for the family of {db_engine_name}-{db_engine_version}')
    client = boto3.client('rds')
    req = client.describe_db_engine_versions(
        Engine=db_engine_name,
        EngineVersion=db_engine_version
    )
    versions = req['DBEngineVersions']
    if not versions:
        raise ValueError('No possible results from given parameters')
    if serverless:
        for version in versions:
            if version["SupportedEngineModes"] and 'serverless' in version['SupportedEngineModes']:
                return version
        raise ValueError(f'No parameters found for the {db_engine_name} {db_engine_version} supporting serverless')
    return versions[0]


def get_db_cluster_engine_parameter_group_defaults(engine_family):
    """
    Returns a dict of all the parameter group parameters and default values
    """

    client = boto3.client('rds')
    req = client.describe_engine_default_cluster_parameters(
        DBParameterGroupFamily=engine_family
    )
    params_return = {}
    if 'EngineDefaults' in req.keys():
        params = req['EngineDefaults']['Parameters']
        for param in params:
            if ('ParameterValue' in param.keys() and '{' not in param['ParameterValue']
                and 'IsModifiable' in param.keys() and param['IsModifiable'] is True):
                params_return[param['ParameterName']] = param['ParameterValue']
            if param['ParameterName'] == 'binlog_format':
                params_return[param['ParameterName']] = 'MIXED'
    return params_return


def generate_parameter_group_defaults(engine_family):
    """
    """

    if engine_family.startswith('aurora-'):
        LOG.info('Aurora based instance')
        LOG.info(f"Looking for parameters for {engine_family}")
        return get_db_cluster_engine_parameter_group_defaults(engine_family)
    else:
        return None


def lambda_handler(event, context):
    """
    Function entry point
    """
    resources = event['ResourceProperties']

    if (event['RequestType'] == 'Delete'):
        LOG.info('Nothing to do on DELETE')
        return send(event, context, SUCCESS, {})

    for key in ['EngineName', 'EngineVersion']:
        if not key in resources.keys():
            LOG.error(f'Failed to find required parameters for function - {key}')
            return send(event, context, FAILED, {})
    engine_name = resources['EngineName']
    engine_version = resources['EngineVersion']
    try:
        if 'Serverless' in resources.keys() and bool(resources['Serverless']) == 'true':
            LOG.info('Ensuring our requested engine works for serverless')
            settings = get_db_engine_settings(engine_name, engine_version, serverless=True)
        else:
            LOG.info('Looking for normal provisioned settings of the DB Engine')
            settings = get_db_engine_settings(engine_name, engine_version)
    except ValueError:
        LOG.error('Failed to get DB Engine family for given settings')
        return send(event, context, FAILED, {})

    LOG.info(f'Engine is {engine_name} - Version {engine_version}')
    if not isinstance(settings, dict):
        return send(event, context, FAILED, {})

    if 'GenerateParameterGroupSettings' in resources.keys():
        parameter_group_parameters = generate_parameter_group_defaults(settings['DBParameterGroupFamily'])
        if isinstance(parameter_group_parameters, dict):
            settings['ParameterGroupParameters'] = parameter_group_parameters
    LOG.info(json.dumps(settings))
    return send(event, context, SUCCESS, settings)
