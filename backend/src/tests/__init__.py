import os
import sys

sys.path.append('../')

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
os.environ['AWS_ACCESS_KEY_ID'] = 'DO_NOT_CHANGE_THIS_VALUE'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'DO_NOT_CHANGE_THIS_VALUE'

os.environ['AWS_XRAY_SDK_ENABLED'] = 'false'

os.environ['COGNITO_USER_POOL_ID'] = 'TEST_USER_POOL_ID'
os.environ['COGNITO_CLIENT_ID'] = 'TEST_COGNITO_CLIENT_ID'
