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

   Outputs:
     EngineFamily:
       Value: !GetAtt 'lambdaGetDBEngineVersion.DBParameterGroupFamily'


