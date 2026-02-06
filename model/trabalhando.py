from conexao.databasePeewe import db
from model.trabalho import Trabalho as trb
from model.cliente import Cliente as clt
from model.responsavel import Responsavel as resp
from peewee import Model, ForeignKeyField, AutoField, FloatField, DateTimeField, BooleanField, CharField

class BaseModel(Model):
    class Meta:
        database = db

class Trabalhando(BaseModel):
    cd_trabalhando = AutoField(primary_key=True)
    cd_trabalho    = ForeignKeyField(trb, backref='historico_trabalhos', column_name='cd_trabalho')
    cd_cliente     = ForeignKeyField(clt, backref='trabalhos_contratados', column_name='cd_cliente')
    cd_responsavel = ForeignKeyField(resp, backref='responsavel_trabalho', column_name='cd_responsavel')
    vl_trabalho    = FloatField()
    dt_inicio      = DateTimeField(null=False)
    dt_finalizado  = DateTimeField()
    id_status      = CharField(max_length=1, default='A')
    class Meta:
        table_name = 'trabalhando'      