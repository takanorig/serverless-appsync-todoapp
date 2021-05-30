import os

AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')


def create_event(args=None, auth=None):
    event = {}
    if args:
        event['arguments'] = args
    if auth:
        event['identity'] = {
            'claims': auth
        }
    return event
