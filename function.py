# -*- coding: utf-8 -*-

""" rds_engine_settings """


import boto3

from botocore.vendored import requests
import json

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
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))


def get_db_engine_settings(db_engine_name, db_engine_version):
    """
    Function to return just the details about that DB Engine Version
    """

    client = boto3.client('rds')
    req = client.describe_db_engine_versions(
        Engine=db_engine_name,
        EngineVersion=db_engine_version
    )
    versions = req['DBEngineVersions']
    if not versions or len(versions) > 1:
        raise ValueError('No or too many possible results from given parameters')
    return versions[0]


def lambda_handler(event, context):
    """
    Function entry point
    """
    resources = event['ResourceProperties']

    if (event['RequestType'] == 'Delete') or \
       (event['RequestType'] == 'Update'):
        return send(event, context, SUCCESS, {})
    for key in ['EngineName', 'EngineVersion']:
        if not key in resources.keys():
            return send(event, context, FAILED, {})
    engine_name = resources['EngineName']
    engine_version = resources['EngineVersion']
    settings = get_db_engine_settings(engine_name, engine_version)
    if isinstance(settings, dict):
        return send(event, context, SUCCESS, settings)
