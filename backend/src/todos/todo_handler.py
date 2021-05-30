import logging


from .domain.todo_service import TodoService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_todolist_handler(event, context):
    todo_service = TodoService()
    todolist = todo_service.find_todolist()
    return todolist


def find_todo_handler(event, context):
    todo_id = event.get('arguments', {}).get('todo_id')
    todo_service = TodoService()
    todo = todo_service.find_todo(todo_id)
    return todo


def add_todo_handler(event, context):
    logger.info(event)

    todo_params = event.get('arguments', {})
    todo_service = TodoService()
    todo = todo_service.add_todo(todo_params)
    return todo


def update_todo_handler(event, context):
    logger.info(event)

    todo_params = event.get('arguments', {})
    todo_service = TodoService()
    todo = todo_service.update_todo(todo_params)
    return todo


def delete_todo_handler(event, context):
    todo_id = event.get('arguments', {}).get('todo_id')
    todo_service = TodoService()
    todo_service.delete_todo(todo_id)
    return
