from conexao.databasePeewe import db
from peewee import Model, DateField, CharField, AutoField

class BaseModel(Model):
    class Meta:
        database = db

class Cliente(BaseModel):
    cd_cliente = AutoField()
    nm_cliente = CharField(max_length=100,  index=True)
    ds_email   = CharField(max_length=180, unique=True)
    ds_telefone= CharField(max_length=20,  unique=True)
    dt_aniversario = DateField(null=True)
    class Meta:
        table_name = 'cliente'        
        
