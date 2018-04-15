import configparser

from peewee import *

config = configparser.ConfigParser()
config.read('config.ini')

connection = MySQLDatabase(config["Credentials"]["database"], user=config["Credentials"]["user"], password=config["Credentials"]["password"], host=config["Credentials"]["host"], use_unicode=True, charset="utf8mb4")


class LoggedMessage(Model):
    messageid = BigIntegerField(primary_key=True)
    content = CharField(max_length=2048, collation="utf8mb4_general_ci", null=True)
    author = BigIntegerField()
    timestamp = FloatField()
    channel = BigIntegerField()

    class Meta:
        database = connection


class LoggedAttachment(Model):
    id = BigIntegerField(primary_key=True)
    url = CharField()
    isImage = BooleanField()
    messageid = BigIntegerField()

    class Meta:
        database = connection


class CustomCommand(Model):
    id = PrimaryKeyField()
    serverid = BigIntegerField()
    trigger = CharField(max_length=20, collation="utf8mb4_general_ci")
    response = CharField(max_length=2000, collation="utf8mb4_general_ci")

    class Meta:
        database = connection


def init():
    connection.connect()
    connection.create_tables([LoggedMessage, CustomCommand, LoggedAttachment])
    connection.close()
