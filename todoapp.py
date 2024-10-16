from strawberry.extensions import QueryDepthLimiter
from model import Todo, User
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import typing

def todo_creator(root):
    user = root.user_id
    return User.get(User.user_id == user)

@strawberry.type
class Todos:
    task_id: int
    task: str
    completed: bool
    user_id: int
    user: "Users" = strawberry.field(resolver=todo_creator)
    created_at: str

def get_user_todos(root):
    db_result = Todo.select().where(Todo.user_id == root.user_id).execute()
    todos = [Todos(task_id=todo.task_id, task=todo.task, completed=todo.completed, created_at=todo.created_at, user_id=todo.user_id) for todo in db_result]
    return todos

@strawberry.type
class Users:
    user_id: int
    name: str
    email: str
    points: int
    todos: typing.List[Todos] = strawberry.field(resolver=get_user_todos)


@strawberry.input
class TodoFilter:
    # user_id: typing.Optional[int] = None
    completed: typing.Optional[bool] = None
    @property
    def filters(self):
        return {"completed": self.completed}
        # return {"completed": self.completed, "user_id": self.user_id}

def get_todos(where: typing.Optional[TodoFilter] = None, limit: typing.Optional[int] = None) -> typing.List[Todos]:
    if where and limit:
        db_result = Todo.select().where(Todo.completed == where.filters["completed"]).limit(limit).execute()
        todos = [Todos(task_id=todo.task_id, task=todo.task, completed=todo.completed, created_at=todo.created_at, user_id=todo.user_id.user_id) for todo in db_result]
        return todos
    elif where:
        db_result = Todo.select().where(Todo.completed == where.filters["completed"]).execute()
        todos = [Todos(task_id=todo.task_id, task=todo.task, completed=todo.completed, created_at=todo.created_at, user_id=todo.user_id.user_id) for todo in db_result]
        return todos
    elif limit:
        db_result = Todo.select().limit(limit).execute()
        todos = [Todos(task_id=todo.task_id, task=todo.task, completed=todo.completed, created_at=todo.created_at, user_id=todo.user_id.user_id) for todo in db_result]
        return todos
    else:
        db_result = Todo.select().execute()
        todos = [Todos(task_id=todo.task_id, task=todo.task, completed=todo.completed, created_at=todo.created_at, user_id=todo.user_id.user_id) for todo in db_result]
        return todos

def get_users(by_id: typing.Optional[int] = None) -> typing.Any:
    if by_id:
        user = User.get(User.user_id == by_id)
        return [Users(user_id=user.user_id, name=user.name, email=user.email, points=user.points)]
    db_result = User.select().execute()
    users = [Users(user_id=user.user_id, name=user.name, email=user.email, points=user.points) for user in db_result]
    return users

@strawberry.type
class Query:
    todos: typing.List[Todos] = strawberry.field(resolver=get_todos)
    users: typing.List[Users] = strawberry.field(resolver=get_users)



@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_todo(self, task: str, completed: bool, user_id: int) -> Todos:
        new_todo = Todo.create(task=task, completed=completed, user_id=user_id)
        return new_todo
    
    @strawberry.mutation
    def update_todo(self, task_id: int, completed: bool) -> Todos:
        todo = Todo.get(Todo.task_id == task_id)
        todo.completed = completed
        todo.save()
        return todo

    @strawberry.mutation
    def delete_todo(self, task_id: int) -> Todos:
        todo = Todo.get(Todo.task_id == task_id)
        todo.delete_instance()
        return todo
    
    @strawberry.mutation
    def add_user(self, name: str, email: str) -> Users:
        new_user = User.create(name=name, email=email, points=0)
        return new_user
    
    @strawberry.mutation
    def update_user(self, user_id: int, name: str, email: str) -> Users:
        user = User.get(User.user_id == user_id)
        user.name = name
        user.email = email
        user.save()
        return user

@strawberry.type
class Subscription:
    todo_created: typing.List[Todos] = strawberry.field(resolver=get_todos)

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription, extensions=[QueryDepthLimiter(max_depth=2)])


#production conig
graphql_app = GraphQLRouter(schema)

app = FastAPI()

@app.get("/")
def ping():
    return "pong"

app.include_router(graphql_app, prefix="/graphql")