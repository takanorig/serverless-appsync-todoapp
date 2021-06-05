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

    def test_find_todolist_handler_normal(self):
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

    def test_find_todo_handler_normal(self):
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

    def test_find_todo_handler_none(self):
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

    def test_delete_todo_handler_normal(self):
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
        todo_handler.delete_todo_handler(event, None)
        todolist_response = todo_handler.find_todolist_handler(event, None)
        post_todolist = todolist_response.get('todos')

        # Assert
        self.assertEqual(3, len(pre_todolist))
        self.assertEqual(2, len(post_todolist))

    def test_delete_todo_handler_none(self):
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
        todo_handler.delete_todo_handler(event, None)

        # Assert
        post_todolist = self.__test_setup.get_todolist()
        self.assertListEqual(pre_todolist, post_todolist)
