rds_engine_settings
======

Lambda function to return all the settings for a given RDS DB Engine Version
-----

Usage example:


.. code-block::

   Resources:
     lambdaGetDBEngineVersion:
       Type: AWS::CloudFormation::CustomResource
       Version: '1.0'
       Properties:
         ServiceToken: !Ref RdsSettingsFunctionArn
	 EngineName: !Select
	   - 0
           - Fn::Split:
             - '--'
             - !Ref RdsEngineVersion
	 EngineVersion: !Select
           - 1
           - Fn::Split:
	     - '--'
             - !Ref RdsEngineVersion
	 Serverless: False
	 GenerateParameterGroupSettings: True

   Outputs:
     EngineFamily:
       Value: !GetAtt 'lambdaGetDBEngineVersion.DBParameterGroupFamily'



Parameters
----------

EngineName: The name of the engine

EngineVersion: Version of the engine

GenerateParameterGroupSettings: If you intend to create a new Parameter group and use as close as possible to the default values, it will return a dictionary for parameters. Defaults to False.

Serverless: Whether or not we are looking for the serverless settings for the RDS DB Engine. Avoids mistakes. Default to False

