from peewee import *
import datetime
from os import getenv
from dotenv import load_dotenv

load_dotenv()

db_url = getenv('DATABASE_URL')
db = PostgresqlDatabase(db_url)


# Define a model
class User(Model):
    user_id = AutoField()
    email = CharField(max_length=100)
    name = CharField(max_length=100)
    points = IntegerField()

    class Meta:
        database = db

class Todo(Model):
    task_id = AutoField()
    task = CharField(max_length=255)
    completed = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    user_id = ForeignKeyField(User, backref='todos')
    
    class Meta:
        database = db



db.connect()
db.create_tables([User, Todo])
