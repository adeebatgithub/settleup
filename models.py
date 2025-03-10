from peewee import (
    DateField,
    Model,
    SqliteDatabase,
    CharField,
    IntegerField,
    ForeignKeyField
)
from os import getenv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB = SqliteDatabase(getenv("DB_NAME"))

class BaseModel(Model):
    class Meta:
        database = DB

class User(BaseModel):
    name = CharField()
    phone = CharField(null=True)
    email = CharField(null=True)

class Debt(BaseModel):
    user = ForeignKeyField(User, backref="debt")
    amount = IntegerField()

class Payment(BaseModel):
    user = ForeignKeyField(User, backref="payment")
    date = DateField(default=datetime.now)
    amount = IntegerField()
    total = IntegerField()
    remark = CharField(null=True)

DB.connect()
DB.create_tables([
    User,
    Debt,
    Payment,
])
