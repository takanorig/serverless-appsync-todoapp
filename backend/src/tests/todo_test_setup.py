import uuid
from datetime import datetime, timezone

import boto3
from common import timestamp_util
from moto import mock_dynamodb2


@mock_dynamodb2
class TodoTestSetup():
    def __init__(self):
        self.__dynamodb = boto3.resource('dynamodb')
        self.__todolist = []

    def setUpAll(self):
        self.create_dynamodb_table()
        self.setup_dynamodb_data()

    def cleanAll(self):
        self.delete_dynamodb_table()
        self.__todolist = []

    def create_dynamodb_table(self):
        self.__dynamodb.create_table(
            TableName='todo',
            AttributeDefinitions=[
                {'AttributeName': 'todo_id', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'todo_id', 'KeyType': 'HASH'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

    def setup_dynamodb_data(self):
        for index in range(3):
            todo_id = str(uuid.uuid4())
            todo_title = 'TODO #' + str(index + 1)
            todo_assignee = 'user' + str(index + 1) + '@example.com'
            self._add_todo(todo_id, todo_title, todo_assignee)

    def delete_dynamodb_table(self):
        self.__dynamodb.Table('todo').delete()

    def get_todolist(self):
        return self.__todolist

    def _add_todo(self, todo_id, todo_title, todo_assignee):
        todo_table = self.__dynamodb.Table('todo')

        now = datetime.now(tz=timezone.utc)
        todo = {
            'todo_id': todo_id,
            'title': todo_title,
            'description': 'Todo content.',
            'status': 'open',
            'assignee': todo_assignee,
            'created_at': timestamp_util.isoformat(now),
            'updated_at': timestamp_util.isoformat(now),
        }

        todo_table.put_item(Item=todo)

        self.__todolist.append(todo)
