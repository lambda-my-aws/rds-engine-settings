#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import json

from function import get_db_engine_settings

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

