import logging

from common.appsync_util import FilterInput

from domain.todo_service import TodoService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_todolist_handler(event, context):
    logger.info(event)

    filters = event.get('arguments', {}).get('filters')
    next_token = event.get('arguments', {}).get('next_token')

    filter_options = []
    if (filters is not None) and (len(filters) > 0):
        for filter in filters:
            filter_attr = list(filter.keys())[0]
            condition_dict = filter[filter_attr]
            condition_fn = list(condition_dict.keys())[0]
            condition_value = condition_dict[condition_fn]

            filter_input = FilterInput(attr=filter_attr, condition=condition_fn, value=condition_value)
            filter_options.append(filter_input)

    todo_service = TodoService()
    todolist, next_token = todo_service.find_todolist(filters=filter_options, next_token=next_token)

    response = {
        'todos': todolist,
        'next_token': next_token
    }
    return response


def find_todo_handler(event, context):
    todo_id = event.get('arguments', {}).get('todo_id')
    todo_service = TodoService()
    todo = todo_service.find_todo(todo_id)
    return todo


def add_todo_handler(event, context):
    logger.info(event)

    todo_params = event.get('arguments', {}).get('todo')
    todo_service = TodoService()
    todo = todo_service.add_todo(todo_params)
    return todo


def update_todo_handler(event, context):
    logger.info(event)

    todo_params = event.get('arguments', {}).get('todo')
    todo_service = TodoService()
    todo = todo_service.update_todo(todo_params)
    return todo


def delete_todo_handler(event, context):
    todo_id = event.get('arguments', {}).get('todo_id')
    todo_service = TodoService()
    deleted = todo_service.delete_todo(todo_id)
    return deleted
