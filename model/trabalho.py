from conexao.databasePeewe import db
from peewee import Model, CharField, AutoField, FloatField

class BaseModel(Model):
    class Meta:
        database = db

class Trabalho(BaseModel):
    cd_trabalho = AutoField(primary_key=True)
    nm_trabalho = CharField(max_length=100, unique=True)
    ds_trabalho = CharField(max_length=240)
    qt_tempo = FloatField(null=False, default=1)
    class Meta:
        table_name = 'trabalho'        