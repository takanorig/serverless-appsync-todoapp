import logging
import uuid
from datetime import datetime, timezone

import boto3
from common import timestamp_util

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TodoService:
    """
    タスクのCRUD処理を行うクラス。
    """

    def __init__(self):
        self.__dynamodb = boto3.resource('dynamodb')
        self.__todo_table = self.__dynamodb.Table('todo')

    def find_todolist(self):
        """
        登録されているタスクを全て取得する。
        DynamoDBのscanを行うため、パフォーマンスに注意。
        """
        response = self.__todo_table.scan()
        todolist = response.get('Items')

        if todolist is None:
            todolist = []

        return todolist

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
        self.__todo_table.delete_item(Key={'todo_id': todo_id})

        return
