#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import json

from function import get_db_engine_settings, generate_parameter_group_defaults

def test_working_function():
    db_engine_name = 'aurora-postgresql'
    db_engine_version = '9.6.12'

    expected_result = {
        "Engine": "aurora-postgresql",
        "EngineVersion": "9.6.12",
        "DBParameterGroupFamily": "aurora-postgresql9.6",
        "DBEngineDescription": "Aurora (PostgreSQL)",
        "DBEngineVersionDescription": "Aurora PostgreSQL (compatible with PostgreSQL 9.6.12)",
        "ValidUpgradeTarget": [],
        "ExportableLogTypes": [
            "postgresql"
        ],
        "SupportsLogExportsToCloudwatchLogs": True,
        "SupportsReadReplica": False,
        "SupportedEngineModes": [
            "provisioned"
        ],
        "SupportedFeatureNames": [],
        "Status": "available"
    }

    result = get_db_engine_settings(db_engine_name, db_engine_version)
    assert expected_result == result


def test_does_not_exist_test():
    db_engine_name = 'aurora-postgresql'
    db_engine_version = '9.6.10'

    result = False

    try:
        result = get_db_engine_settings(db_engine_name, db_engine_version)
    except ValueError as error:
        result = True
        pass
    assert result



def test_parameter_group_parameters():
    db_engine_name = 'aurora-mysql'
    db_engine_version = '5.7'
    result = get_db_engine_settings(db_engine_name, db_engine_version, serverless=False)
    print(json.dumps(result, indent=4))
    params = generate_parameter_group_defaults(result['DBParameterGroupFamily'])
    print(json.dumps(params, indent=4))
    expected_params = {
        "binlog_format": "MIXED",
        "default_password_lifetime": "0",
        "gtid-mode": "OFF_PERMISSIVE",
        "master-info-repository": "TABLE",
        "server_audit_logging": "0",
        "server_audit_logs_upload": "0"
    }
    assert params == expected_params

if __name__ == '__main__':
    test_parameter_group_parameters()
