from conexao.databasePeewe import db
from trabalhando import trbd
from responsavel import resp
from peewee import Model, ForeignKeyField, AutoField, TimestampField, BooleanField

class BaseModel(Model):
    class Meta:
        database = db

class Execucao(BaseModel):
    cd_execucao    = AutoField(primary_key=True)
    cd_trabalhando = ForeignKeyField(trbd, backref='historico_trabalhos', column_name='cd_trabalhando')
    cd_responsavel = ForeignKeyField(resp, backref='quem_responsavel_pela_execucao', column_name='cd_responsavel')
    dt_execucao    = TimestampField(null=False)
    id_presente    = BooleanField()
    class Meta:
        table_name = 'execucao'      