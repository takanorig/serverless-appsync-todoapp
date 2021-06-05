import unittest
from uuid import UUID

from moto import mock_dynamodb2
from tests import appsync_testutil
from tests.todo_test_setup import TodoTestSetup

from todos import todo_handler


@mock_dynamodb2
class TestTodoHandler(unittest.TestCase):

    __test_setup = TodoTestSetup()

    def setUp(self):
        self.__test_setup.setUpAll()

    def tearDown(self):
        self.__test_setup.cleanAll()

    def test_find_todolist_handler__normal(self):
        # Prepare
        todolist = self.__test_setup.get_todolist()
        args = {}
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        response = todo_handler.find_todolist_handler(event, None)
        actual_todolist = response.get('todos')

        # Assert
        self.assertEqual(3, len(actual_todolist))
        self.assertListEqual(todolist, actual_todolist)

    def test_find_todolist_handler__filter_hit(self):
        # Prepare
        todolist = self.__test_setup.get_todolist()
        args = {
            'filters': [{'status': {'eq': 'open'}}]
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        response = todo_handler.find_todolist_handler(event, None)
        actual_todolist = response.get('todos')

        # Assert
        self.assertEqual(3, len(actual_todolist))
        self.assertListEqual(todolist, actual_todolist)

    def test_find_todolist_handler__filter_nohit(self):
        # Prepare
        args = {
            'filters': [{'status': {'ne': 'open'}}]
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        response = todo_handler.find_todolist_handler(event, None)
        actual_todolist = response.get('todos')

        # Assert
        self.assertEqual(0, len(actual_todolist))

    def test_find_todolist_handler__filter2_hit(self):
        # Prepare
        args = {
            'filters': [
                {'status': {'eq': 'open'}},
                {'assignee': {'eq': 'user1@example.com'}},
            ]
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        response = todo_handler.find_todolist_handler(event, None)
        actual_todolist = response.get('todos')

        # Assert
        self.assertEqual(1, len(actual_todolist))
        self.assertEqual('open', actual_todolist[0]['status'])
        self.assertEqual('user1@example.com', actual_todolist[0]['assignee'])

    def test_find_todolist_handler__filter_emptyvalue(self):
        # Prepare
        args = {
            'filters': [{'status': {'eq': ''}}]
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        response = todo_handler.find_todolist_handler(event, None)
        actual_todolist = response.get('todos')

        # Assert
        self.assertEqual(0, len(actual_todolist))

    def test_find_todolist_handler__filter_nonevalue(self):
        # Prepare
        args = {
            'filters': [{'status': {'eq': None}}]
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        response = todo_handler.find_todolist_handler(event, None)
        actual_todolist = response.get('todos')

        # Assert
        self.assertEqual(0, len(actual_todolist))

    def test_find_todolist_handler__nexttoken(self):
        # Prepare
        # リストの途中から取得できるようにする。
        todolist = self.__test_setup.get_todolist()
        todo = todolist[1]
        args = {
            'next_token': {'todo_id': todo['todo_id']}
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        response = todo_handler.find_todolist_handler(event, None)
        actual_todolist = response.get('todos')

        # Assert
        self.assertEqual(1, len(actual_todolist))
        self.assertEqual(todolist[2]['todo_id'], actual_todolist[0]['todo_id'])

    def test_find_todo_handler__normal(self):
        # Prepare
        todolist = self.__test_setup.get_todolist()
        todo = todolist[0]
        args = {
            'todo_id': todo['todo_id']
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        actual_todo = todo_handler.find_todo_handler(event, None)

        # Assert
        self.assertDictEqual(todo, actual_todo)

    def test_find_todo_handler__none(self):
        # Prepare
        args = {
            'todo_id': 'dummy'
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        actual_todo = todo_handler.find_todo_handler(event, None)

        # Assert
        self.assertIsNone(actual_todo)

    def test_add_todo_handler__normal(self):
        # Prepare
        args = {
            'todo': {
                'title': 'Add todo test',
                'description': 'Add example',
            }
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        actual_todo = todo_handler.add_todo_handler(event, None)

        # Assert
        self.assertEqual(4, UUID(actual_todo['todo_id']).version)
        self.assertEqual(args['todo']['title'], actual_todo['title'])
        self.assertEqual(args['todo']['description'], actual_todo['description'])
        self.assertEqual('open', actual_todo['status'])
        self.assertIsNotNone(actual_todo['created_at'])
        self.assertIsNotNone(actual_todo['updated_at'])
        self.assertEqual(actual_todo['created_at'], actual_todo['updated_at'])

    def test_update_todo_handler__normal(self):
        # Prepare
        todolist = self.__test_setup.get_todolist()
        todo = todolist[0]
        args = {
            'todo': {
                'todo_id': todo['todo_id'],
                'title': 'Update todo test',
            }
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        actual_todo = todo_handler.update_todo_handler(event, None)

        # Assert
        self.assertEqual(args['todo']['todo_id'], actual_todo['todo_id'])
        self.assertEqual(args['todo']['title'], actual_todo['title'])
        self.assertIsNotNone(actual_todo['description'])
        self.assertIsNotNone(actual_todo['created_at'])
        self.assertIsNotNone(actual_todo['updated_at'])
        self.assertGreater(actual_todo['updated_at'], actual_todo['created_at'])

    def test_update_todo_handler__none(self):
        with self.assertRaises(ValueError):
            # Prepare
            args = {
                'todo': {
                    'todo_id': 'dummy',
                    'title': 'Update todo test',
                }
            }
            auth = {
                'email': 'test_add@example.com'
            }
            event = appsync_testutil.create_event(args=args, auth=auth)

            # Execute
            todo_handler.update_todo_handler(event, None)

            # Assert
            self.fail('Not raise the excetption.')

    def test_delete_todo_handler__normal(self):
        # Prepare
        pre_todolist = self.__test_setup.get_todolist()
        todo = pre_todolist[0]
        args = {
            'todo_id': todo['todo_id']
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        actual_deleted = todo_handler.delete_todo_handler(event, None)
        todolist_response = todo_handler.find_todolist_handler(event, None)
        post_todolist = todolist_response.get('todos')

        # Assert
        self.assertEqual(True, actual_deleted)
        self.assertEqual(3, len(pre_todolist))
        self.assertEqual(2, len(post_todolist))

    def test_delete_todo_handler__none(self):
        # Prepare
        pre_todolist = self.__test_setup.get_todolist()
        args = {
            'todo_id': 'dummy'
        }
        auth = {
            'email': 'test_add@example.com'
        }
        event = appsync_testutil.create_event(args=args, auth=auth)

        # Execute
        actual_deleted = todo_handler.delete_todo_handler(event, None)

        # Assert
        self.assertEqual(False, actual_deleted)
        post_todolist = self.__test_setup.get_todolist()
        self.assertListEqual(pre_todolist, post_todolist)
