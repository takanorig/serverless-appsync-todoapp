import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import And, Attr
from common import timestamp_util
from common.appsync_util import FilterInput

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_ITEMS = int(os.getenv('MAX_ITEMS', '1000'))


class TodoService:
    """
    タスクのCRUD処理を行うクラス。
    """

    def __init__(self):
        self.__dynamodb = boto3.resource('dynamodb')
        self.__todo_table = self.__dynamodb.Table('todo')

    def find_todolist(self, filters: [FilterInput] = None, next_token: str = None):
        """
        登録されているタスクを全て取得する。
        DynamoDBのscanを行うため、パフォーマンスに注意。
        """
        option = {}

        # FilterExpression
        if (filters is not None) and (len(filters) > 0):
            # FilterExpression を動的に生成
            filter_options = []
            for filter in filters:
                condition_fn = getattr(Attr(filter.attr), filter.condition)
                condition_value = filter.value
                if (condition_value is not None) and (condition_value.strip() == ''):
                    condition_value = None
                filter_exp = condition_fn(filter.value)
                filter_options.append(filter_exp)

            # And 条件で結合
            if (len(filter_options) > 1):
                option['FilterExpression'] = And(*filter_options)
            else:
                option['FilterExpression'] = filter_options[0]

        # ExclusiveStartKey
        if next_token is not None:
            option['ExclusiveStartKey'] = next_token

        # MAX件数を超えるまで繰り返し取得
        response = self.__todo_table.scan(**option)
        todolist = response.get('Items')
        while 'LastEvaluatedKey' in response:
            next_token = response.get('LastEvaluatedKey')
            tmp_option = dict(**option, **{'ExclusiveStartKey': next_token})
            response = self.__todo_table.scan(**tmp_option)
            todolist.extend(response.get('Items'))

            if len(todolist) > MAX_ITEMS:
                break

        if todolist is None:
            todolist = []

        return todolist, next_token

    def find_todo(self, todo_id: str):
        """
        指定されたIDのタスクを取得する。
        """
        response = self.__todo_table.get_item(Key={'todo_id': todo_id})
        todo = response.get('Item')

        return todo

    def add_todo(self, item: dict):
        """
        タスクを登録する。
        """
        todo_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        todo = {
            'todo_id': todo_id,
            'title': item.get('title'),
            'description': item.get('description'),
            'status': 'open',
            'assignee': None,
            'created_at': timestamp_util.isoformat(now),
            'updated_at': timestamp_util.isoformat(now),
        }

        self.__todo_table.put_item(Item=todo)

        return todo

    def update_todo(self, item: dict):
        """
        タスクを更新する。
        """
        todo_id = item['todo_id']
        now = datetime.now(tz=timezone.utc)

        todo = self.find_todo(todo_id)
        if todo is None:
            raise ValueError(f'Invalid todo_id. : {todo_id}')

        todo.update(item)
        todo['updated_at'] = timestamp_util.isoformat(now)

        self.__todo_table.put_item(Item=todo)

        return todo

    def delete_todo(self, todo_id: str):
        """
        指定されたIDのタスクを削除する。
        """
        response = self.__todo_table.delete_item(
            Key={'todo_id': todo_id},
            ReturnValues='ALL_OLD'
        )

        attr = response.get('Attributes', {})
        if attr.get('todo_id') is not None:
            deleted = True
        else:
            deleted = False

        return deleted
